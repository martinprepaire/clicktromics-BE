from fastapi import APIRouter, Depends

from fastapi.responses import JSONResponse
from bio_core import JobType, JobDocument, PipelineName, BaseJobManager, PipelineClient, Logger, get_storage_adapter, S3Service, get_s3_service, StorageAdapter
from src.utility import cleanup_temp_files
from src.config import DEFAULT_SEQUENCE
from src.request_model import PeptideJobRequest
import tempfile
import json

log = Logger.get_logger()

router = APIRouter(prefix="/gan", tags=["Peptide generating job"])

@router.post("")
async def submitgan_job(
    request: PeptideJobRequest,
    job_manager: BaseJobManager = Depends(lambda: BaseJobManager()),
    adapter: StorageAdapter = Depends(get_storage_adapter),
    s3: S3Service = Depends(get_s3_service),
):  
    """
       Submit a long-running process and provide a unique job ID to track the status of the process.
        - peptide: Can be used directly with the correct provided data.
            input: Gene protein sequence with the desired peptide length.
            output: Peptide sequence.
    """
        
    try:
        job = JobDocument(type=JobType(name=PipelineName.GAN))
        log.info(f"Creating Job: {job}")

        peptide_length = min(request.peptide_length, 50)
        num_binders = 1
        if 15 == peptide_length:
            num_binders = 5
        elif 15 < peptide_length < 20:
            num_binders = 4
        elif 20 == peptide_length:
            num_binders = 3
        elif 20 < peptide_length < 25:
            num_binders = 2
        elif 25 <= peptide_length:
            num_binders = 1

        job.inputs = {
            "peptide_length": peptide_length,
            "num_binders": num_binders,
            "protein_seq": request.peptide_protein_sequence,
            "top_k": 3
        }

        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tf:
            tf.write(json.dumps(job.inputs).encode('utf-8'))
            tmp_path = tf.name

        objectname = "peptide_generation/" + job.job_id + "/" + s3.generate_valid_object_name("peptide_generation_input.json")
        adapter.upload(tmp_path, objectname)
        
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
                files=[tmp_path]
            )