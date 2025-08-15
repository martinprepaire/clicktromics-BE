from fastapi import APIRouter, Depends, Form
from bio_core import Logger

from fastapi.responses import JSONResponse
from bio_core import JobType, JobDocument, PipelineName, BaseJobManager, PipelineClient, Logger

log = Logger.get_logger()

router = APIRouter(prefix="/bloodtest", tags=["Blood File Processing job"])

@router.post("",
    summary="Submit a Blood File Processing job",
    description="""
Submit a long-running background job for processing blood test data from pdf or image.  

### Input Parameters (multipart/form-data):
- **file** (`str`, required): Path or identifier of the pdf (.pdf) or image (.png/.jpeg/.jpg) uploaded file.

### Behavior:
- A job is created and stored in the system.
- Corresponding Celery tasks are chained and executed
- A unique `job_id` is returned to track the job.

### Responses:
- `200 OK`: Job successfully submitted.
  ```json
  {
    "status": "success",
    "data": {
      "job_id": "<uuid>",
      "message": "Job submitted successfully"
    }
  }
  """
)
async def submit_job(
    file: str = Form(...),
    job_manager: BaseJobManager = Depends(lambda: BaseJobManager())
):  
    """
       Submit a long-running process and provide a unique job ID to track the status of the process.
        - bloodtest: Used after uploading a pdf file (.pdf) or image (.png/.jpeg/.jpg).
            input: pdf file (.pdf) or image (.png/.jpeg/.jpg).
            output: JSON file containing matched biomarkers.
    """
    try:
        job = JobDocument(type=JobType(name=PipelineName.BLOOD_TEST))
        log.info(f"Creating Job: {job}")
        job.inputs = {
                "file": file
        } 

        task = PipelineClient.submit_pipeline(job, file.split(","))
        job.task_id = task.id
        await job_manager.save(job)

        return JSONResponse(content={"status": "success", "data":{"job_id": job.job_id, "message": "Job submitted successfully"}}, status_code=200)
    except Exception as e:
        error_message = str(e) or "Unknown error occurred"
        log.error(f"Error in /bloodtest: {error_message}")
        return JSONResponse(
            content={"status": "error", "message": f"Error encountered during processing: {error_message}"},
            status_code=500,
        )