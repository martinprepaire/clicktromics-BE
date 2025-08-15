from fastapi import APIRouter, Depends, Form
from bio_core import Logger

from fastapi.responses import JSONResponse
from bio_core import JobType, JobDocument, PipelineName, BaseJobManager, PipelineClient, Logger

log = Logger.get_logger()

router = APIRouter(prefix="/url_download", tags=["URL Download job"])


@router.post("")
async def submit_job(
    url: str = Form(...),
    job_manager: BaseJobManager = Depends(lambda: BaseJobManager())
):  
    """
       Submit a long-running process and provide a unique job ID to track the status of the process.
        - url_download: download file from third party / link.
    """
        
    try:
        job = JobDocument(type=JobType(name=PipelineName.URL_DOWNLOAD))
        log.info(f"Creating Job: {job}")
        job.inputs = {
                "file": url
        } 
        task = PipelineClient.submit_pipeline(job, url)
        job.task_id = task.id
        await job_manager.save(job)

        return JSONResponse(content={"status": "success", "data":{"job_id": job.job_id, "message": "Job submitted successfully"}}, status_code=200)
    except Exception as e:
        error_message = str(e) or "Unknown error occurred"
        log.error(f"Error in submit_job: {error_message}")
        return JSONResponse(
            content={"status": "error", "message": f"Error encountered during processing: {error_message}"},
            status_code=500,
        )