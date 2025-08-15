from fastapi import APIRouter, Query, Depends

from fastapi.responses import JSONResponse
from bio_core import JobDocument, PipelineName, JobStatusEnum, BaseJobManager, Celery, terminate_job, Logger, PipelineName, PipelineFactory, PipelineMetadata
from celery.result import AsyncResult
from celery import states
from typing import List

log = Logger.get_logger()
router = APIRouter(prefix="", tags=["Job Management"])

@router.get("/info", response_model=PipelineMetadata)
async def get_job_status(
    pipline_name: PipelineName = Query(..., description="Name of the pipeline to get info for"),
):
    """Get the data of a specific pipline"""
    try:
        pipeline = PipelineFactory.create(pipline_name)
        if not pipeline:
            log.error(f"Pipeline not found with the name: {pipline_name}")
            return JSONResponse(status_code=404, content={"status": "error", "message": "Pipeline not found"})

        info = pipeline.get_info()
        return JSONResponse(content={"status": "success", "data": info}, status_code=200)
    except Exception as e:
        error_message = str(e) if str(e) else "Unknown error occurred"
        log.error(f"Error get_job_status for pipeline {pipline_name}: {str(error_message)}")
        return JSONResponse(content={"status": "error", "message": "Error encountered during processing. Please review the application log for detailed information"}, status_code=500)

@router.get("/status/{job_id}", response_model=JobDocument)
async def get_job_status(
    job_id: str,
    job_manager: BaseJobManager = Depends(lambda: BaseJobManager())
):
    """Get the data of a specific job"""
    try:
        job = await job_manager.find_by_job_id(job_id)
        if not job:
            log.error(f"Job not found with the ID: {job_id}")
            return JSONResponse(status_code=404, content={"status": "error", "message": "Job not found"})

        return JSONResponse(content={"status": "success", "data": job.model_dump()}, status_code=200)
    except Exception as e:
        error_message = str(e) if str(e) else "Unknown error occurred"
        log.error(f"Error get_job_status with {job_id}: {str(error_message)}")
        return JSONResponse(content={"status": "error", "message": "Error encountered during processing. Please review the application log for detailed information"}, status_code=500)

@router.get("/", response_model=List[JobDocument])
async def get_jobs(
    page: int = Query(0, alias="page", ge=0, description="Number of the result page"),
    batch_size: int = Query(5, ge=1, le=100, alias="batch_size", description="Number of rows in page"),
    stage_status: str = Query(None, description="Filter by current job stage status"),
    job_type: PipelineName = Query(None, description="Filter by job type"),
    sort_desc: bool = Query(True, description="Sort by timestamp descending"),
    job_manager: BaseJobManager = Depends(lambda: BaseJobManager())
):
    """Get the data of jobs"""
    try:
        query = {}

        # Optional filter by stage.status
        if stage_status:
            query["stage.status"] = stage_status.upper()
        if job_type:
            query["type.name"] = job_type.lower()

        # Sort by timestamp
        sort_order = -1 if sort_desc else 1
        skip = page * batch_size
        results = await job_manager.get(query, sort_order, skip, batch_size)

        return JSONResponse(content={"status": "success", "data": [result.model_dump() for result in results]}, status_code=200)
    except Exception as e:
        error_message = str(e) if str(e) else "Unknown error occurred"
        log.error(f"Error get_jobs: {str(error_message)}")
        return JSONResponse(content={"status": "error", "message": "Error encountered during processing. Please review the application log for detailed information"}, status_code=500)

@router.put("/{job_id}/cancel")
async def cancel_task(
    job_id: str,
    job_manager: BaseJobManager = Depends(lambda: BaseJobManager())
):
    """Cancel running task"""
    job = await job_manager.find_by_job_id(
        job_id
    )

    if not job:
        log.error(f"Job not found with the ID: {job_id}")
        return JSONResponse(status_code=404, content={"status": "error", "message": "Job not found"})

    task_id = job.task_id

    if not task_id:
        log.error(f"Job {job.job_id} has no task_id.")
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "Job has no associated task ID."}
        )

    if  job.status in [JobStatusEnum.FAILED.value, JobStatusEnum.CANCELLED.value, JobStatusEnum.SUCCEEDED.value]:
        log.error(f"Task not found or already completed")
        return JSONResponse(status_code=404, content={"status": "error", "message": "Task not found or already completed"})

    try:
        result = AsyncResult(task_id, app=Celery.get_client())
        job.status = JobStatusEnum.CANCELING.value
        await job_manager.update(job)

        if result.state in [states.PENDING, states.RECEIVED]:
            result.revoke(terminate=False, wait=True, timeout=10)
            log.info(f"Task with ID {task_id} revoked before execution.")

        elif result.state in [states.STARTED]:
            result.revoke(terminate=True, signal="SIGUSR1", wait=True, timeout=10)
            log.info(f"Task with ID {task_id} forcefully terminated.")
        
        job.status = JobStatusEnum.CANCELLED.value
        await job_manager.update(job)

        if job.batch_id and terminate_job(job.batch_id) == None:
            raise Exception("Failed to cancel")

        log.info(f"Task with ID {job_id} canceled successfully.")
        return JSONResponse(content={"status": "success", "data": f"Task with ID {job_id} canceled successfully."}, status_code=200)

    except Exception as e:
        error_message = str(e) or "Unknown error occurred"
        log.error(f"Error in submit_job: {error_message}")
        return JSONResponse(
            content={"status": "error", "message": f"Error encountered during processing: {error_message}"},
            status_code=500,
        )