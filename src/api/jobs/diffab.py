from fastapi import APIRouter, Depends, Form

from fastapi.responses import JSONResponse
from bio_core import JobType, JobDocument, PipelineName, BaseJobManager, PipelineClient, Logger, get_storage_adapter, S3Service, get_s3_service, StorageAdapter
from src.utility import cleanup_temp_files
from src.config import DEFAULT_SEQUENCE
from pydantic import BaseModel
import tempfile
import json

log = Logger.get_logger()

router = APIRouter(prefix="/diffab", tags=["Diffab job"])

@router.post("")
async def submit_job(
    file: str = Form(...),
    job_manager: BaseJobManager = Depends(lambda: BaseJobManager()),
    adapter: StorageAdapter = Depends(get_storage_adapter),
    s3: S3Service = Depends(get_s3_service),
):  
    """
       Submit a long-running process and provide a unique job ID to track the status of the process.
        - diffab: Used after a successful input response or successful Boltz job.
            input: PDB file from input or Boltz.
            output: Diffab-generated PDB file.
    """
        
    try:
        job = JobDocument(type=JobType(name=PipelineName.DIFFAB))
        log.info(f"Creating Job: {job}")

        job.inputs = {
                "pdb_file": file,
                "n": 1
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