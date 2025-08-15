from fastapi import APIRouter, Depends, Form

from fastapi.responses import JSONResponse
from bio_core import JobType, JobDocument, PipelineName, BaseJobManager, PipelineClient, Logger, get_storage_adapter, S3Service, get_s3_service, StorageAdapter, convert
from src.utility import cleanup_temp_files
import tempfile
import json

log = Logger.get_logger()

router = APIRouter(prefix="/homelette", tags=["Homelette job"])

@router.post("")
async def submit_homelette_job(
    file: str = Form(...),
    job_manager: BaseJobManager = Depends(lambda: BaseJobManager()),
    adapter: StorageAdapter = Depends(get_storage_adapter),
    s3: S3Service = Depends(get_s3_service),
):  
    """
       Submit a long-running process and provide a unique job ID to track the status of the process.
        - homelette: Used only after a successful Diffab job.
            input:  Diffab-generated PDB file.
            output: Homelette-generated PDB file.
    """
        
    try:
        job = JobDocument(type=JobType(name=PipelineName.HOMELETTE))
        log.info(f"Creating Job: {job}")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdb") as tf:
            adapter.download(file, tf.name)
            pdb_tmp_path = tf.name

        with open(pdb_tmp_path, "rb") as f:
            chain = convert(f, "homelette")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tf:
            tf.write(json.dumps({**chain}).encode('utf-8'))
            json_tmp_path = tf.name

        objectname = "homelette_genearted/" + job.job_id + "/" + s3.generate_valid_object_name("homelette_input.json")
        adapter.upload(json_tmp_path, objectname)

        job.inputs = {
            **chain
        }
        
        task = PipelineClient.submit_pipeline(job, objectname)
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
    finally:
        cleanup_temp_files(
                output_dir="",
                files=[pdb_tmp_path, json_tmp_path]
            )