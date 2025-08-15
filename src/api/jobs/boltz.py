from fastapi import APIRouter, Depends, Form

from fastapi.responses import JSONResponse
from bio_core import JobType, JobDocument, PipelineName, BaseJobManager, PipelineClient, Logger, get_storage_adapter, S3Service, get_s3_service, StorageAdapter
from src.config import DEFAULT_SEQUENCE
from src.utility import cleanup_temp_files
import tempfile
import json

log = Logger.get_logger()
router = APIRouter(prefix="/boltz", tags=["Boltz job"])

@router.post("")
async def submit_boltz_job(
    protein_sequence : str = Form(DEFAULT_SEQUENCE, description="Protein sequence to be processed by Boltz."),
    job_manager: BaseJobManager = Depends(lambda: BaseJobManager()),
    adapter: StorageAdapter = Depends(get_storage_adapter),
    s3: S3Service = Depends(get_s3_service),
):  
    """
       Submit a long-running process and provide a unique job ID to track the status of the process.
        - boltz: Can be used directly with the correct provided data.
            input: Protein sequence.
            output: Boltz-generated PDB file.
    """
        
    try:
        job = JobDocument(type=JobType(name=PipelineName.BOLTZ))
        log.info(f"Creating Job: {job}")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tf:
            tf.write(json.dumps({"sequences": [protein_sequence]}).encode('utf-8'))
            json_tmp_path = tf.name

        objectname = "boltz/" + job.job_id + "/" + s3.generate_valid_object_name("boltz_input.json")
        adapter.upload(json_tmp_path, objectname)

        job.inputs = {
            "sequence": protein_sequence,
            "json_file": objectname
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
            files=[json_tmp_path]
        )