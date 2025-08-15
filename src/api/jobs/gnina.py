from fastapi import APIRouter, Depends, Query, HTTPException

from fastapi.responses import JSONResponse
from bio_core import JobType, JobDocument, PipelineName, BaseJobManager, PipelineClient, Logger, get_storage_adapter, S3Service, get_s3_service, StorageAdapter
from src.utility import cleanup_temp_files
from typing import Optional
from src.request_model import DockingJobRequest
import tempfile
import json

log = Logger.get_logger()

router = APIRouter(prefix="/gnina", tags=["Gnina job"])

@router.post("/")
async def submit_gnina_job(
    request: DockingJobRequest,
    job_manager: BaseJobManager = Depends(lambda: BaseJobManager()),
    adapter: StorageAdapter = Depends(get_storage_adapter),
    s3: S3Service = Depends(get_s3_service),
):  
    """
       Submit a long-running process and provide a unique job ID to track the status of the process.
        - gnina: Used for docking payload with antibody, only after a successful click response and successful Homelette job.
            input: Homelette PDB file and Musite JSON file.
            output: Gnina-generated PDB file and JSON file (affinity result).
    """
        
    try:
        job = JobDocument(type=JobType(name=PipelineName.GNINA))
        log.info(f"Creating Job: {job}")

        resNumber = ""
        if request.musite_file:
            if request.musite_res_number:

                with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tf:
                    adapter.download(request.musite_file, tf.name)
                    json_tmp_path = tf.name

                with open(json_tmp_path, "r") as f:
                    file_content = json.loads(f.read())

                if len(file_content["residue"]) >= request.musite_res_number > 0:
                    resNumber = file_content["residue"][request.musite_res_number - 1]["resNumber"]
                else:
                    raise HTTPException(status_code=400, detail=f"musite_res_number is not correct should be bigger than 0 and not more than {len(file_content["residue"])}")
            else:
                raise HTTPException(status_code=400, detail="Could not found musite_res_number, please send musite_res_number when adding musite_file")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tf:
            tf.write(json.dumps({"spacc": request.spacc, "resNumber": resNumber}).encode('utf-8'))
            json_input_tmp_path = tf.name

        objectname = "gnina/" + job.job_id + "/" + s3.generate_valid_object_name("gnina_input.json")
        adapter.upload(json_input_tmp_path, objectname)
        
        job.inputs = {
            "payload": {
                "SPACC": request.spacc
            },
            "compound":{
                "pdb_file": request.pdb_file,
                "musite_json_file": request.musite_file or ""
            }
        }

        task = PipelineClient.submit_pipeline(job, request.pdb_file, objectname)
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
                files=[json_tmp_path, json_input_tmp_path]
            )