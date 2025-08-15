from fastapi import APIRouter, Depends, Form
from bio_core import Logger

from fastapi.responses import JSONResponse
from bio_core import JobType, JobDocument, PipelineName, BaseJobManager, PipelineClient, Logger

log = Logger.get_logger()

from enum import Enum

router = APIRouter(prefix="/microbiome", tags=["Microbiome File Processing job"])

class MethodEnum(str, Enum):
    SHOTGUN = "shotgun"
    _16S = "16s"


@router.post("",
    summary="Submit a Microbiome File Processing job",
    description="""
Submit a long-running background job for processing genetic data from VCF or FASTQ files.  
This endpoint handles two pipeline types:
- `shotgun`: Processes a pair of `.fastq` or `.fastq.gz` files (Microbiome SHOTGUN).
- `16s`: Processes a pair of `.fastq` or `.fastq.gz` files (Microbiome SHOTGUN).

### Input Parameters (multipart/form-data):
- **file_r1** (`str`, required): the first `.fastq` or `.fastq.gz` file.
- **file_r2** (`str`, required): the second `.fastq` or `.fastq.gz` file.
- **method** (`Method`, required): Type of pipeline to execute.
  - `shotgun`
  - `16s`

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
    file_r1: str = Form(...),
    file_r2: str = Form(...),
    method: MethodEnum = Form(...),
    job_manager: BaseJobManager = Depends(lambda: BaseJobManager())
):  
    """
       Submit a long-running process and provide a unique job ID to track the status of the process.
        - microbiome: Used after uploading a fast file (.fastq) or compressed FASTQ file (.fastq.gz).
            input: fast file (.fastq) or compressed FASTQ file (.fastq.gz).
            output: Text file (.txt) in case shotgun or csv and tsv in case 16s .
    """
    try:
        job = JobDocument(type=JobType(name=PipelineName.MICROBIOME))
        log.info(f"Creating Job: {job}")
        job.inputs = {
                "file": [
                    file_r1,
                    file_r2
                ]
        } 

        task = PipelineClient.submit_pipeline(job, file_r1, file_r2, method.value)
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