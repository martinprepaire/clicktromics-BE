from fastapi import APIRouter, Depends, Form
from bio_core import Logger

from fastapi.responses import JSONResponse
from bio_core import JobType, JobDocument, PipelineName, BaseJobManager, PipelineClient, Logger

log = Logger.get_logger()

router = APIRouter(prefix="/variant/fastq", tags=["Variant matching job"])


@router.post("")
async def submit_job(
    file_r1: str = Form(...),
    file_r2: str = Form(...),
    job_manager: BaseJobManager = Depends(lambda: BaseJobManager())
):  
    """
       Submit a long-running process and provide a unique job ID to track the status of the process.
        - variant_calling_matching: Used after uploading a fast file (.fastq) or compressed FASTQ file (.fastq.gz).
            input: fast file (.fastq) or compressed FASTQ file (.fastq.gz).
            output: BAM file (.bam).
    """
        
    try:
        job = JobDocument(type=JobType(name=PipelineName.FASTQ_PROCESSING))
        log.info(f"Creating Job: {job}")
        job.inputs = {
                "file": [
                    file_r1,
                    file_r2
                ]
        } 
        task = PipelineClient.submit_pipeline(job, file_r1, file_r2)
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