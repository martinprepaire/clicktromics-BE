from fastapi import APIRouter, Depends, Form
from bio_core import Logger

from fastapi.responses import JSONResponse
from bio_core import JobType, JobDocument, PipelineName, BaseJobManager, PipelineClient, Logger

log = Logger.get_logger()

router = APIRouter(prefix="/annotation", tags=["Annotation job"])


@router.post("")
async def submit_job(
    file: str = Form(...),
    job_manager: BaseJobManager = Depends(lambda: BaseJobManager())
):  
    """
       Submit a long-running process and provide a unique job ID to track the status of the process.
        - annotation: Used after uploading a text/vcard file (.vcf) or compressed VCF file (.vcf.gz).
            input: Text/vcard file (.vcf) or compressed VCF file (.vcf.gz).
            output: JSON file containing summery.
    """
        
    try:
        job = JobDocument(type=JobType(name=PipelineName.GENETIC_ANNOTATION))
        log.info(f"Creating Job: {job}")
        job.inputs = {
                "file": file
        } 
        task = PipelineClient.submit_pipeline(job, file)
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