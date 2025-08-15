from fastapi import APIRouter, Depends, Form, HTTPException
import traceback

from fastapi.responses import JSONResponse
from bio_core import JobType, JobDocument, PipelineName, BaseJobManager, PipelineClient, Logger, GeneticAnnotationPipelineType
log = Logger.get_logger()

from typing import Optional
from enum import Enum

router = APIRouter(prefix="/genetic", tags=["Genetic File Processing job"])

@router.post("",
    summary="Submit a Genetic File Processing Job",
    description="""
Submit a long-running background job for processing genetic data from VCF or FASTQ files.  
This endpoint handles three pipeline types:
- `vcf2result`: Processes a single `.vcf` or `.vcf.gz` file (Vep → Annotation).
- `bam2results`: Processes a `.bam` files (Variant Calling BAM → Vep → Annotation).
- `fastq2results`: Processes a pair of `.fastq` or `.fastq.gz` files (Variant Calling FATSQ → Variant Calling BAM  → Vep → Annotation).

### Input Parameters (multipart/form-data):
- **first_file** (`str`, required): Path or identifier of the first uploaded file.
  - For `vcf2result`: a `.vcf` or `.vcf.gz` file.
  - For `bam2results`: a `.bam`.
  - For `fastq2results`: the first `.fastq` or `.fastq.gz` file.
- **second_file** (`str`, optional): Only required for `fastq2results`. Second `.fastq` or `.fastq.gz` file.
- **flag** (`PipelineType`, required): Type of pipeline to execute.
  - `vcf2result` for VCF-based analysis.
  - `bam2results` for BAM-based analysis.
  - `fastq2results` for FASTQ-based analysis.

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
    first_file: str = Form(...),
    second_file: Optional[str] = Form(None),
    flag: GeneticAnnotationPipelineType = Form(...),
    job_manager: BaseJobManager = Depends(lambda: BaseJobManager())
):  
    try:
        if flag.value == GeneticAnnotationPipelineType.FASTQ.value:
            if not second_file:
                raise HTTPException(status_code=400, detail=f"second_file should not be empty when selecting {GeneticAnnotationPipelineType.FASTQ.value}")
        
        job = JobDocument(type=JobType(name=PipelineName.GENETIC))
        log.info(f"Creating Job: {job}")

        job.inputs = {
                "files": [first_file, second_file ] if second_file else [first_file]
        }
        
        if second_file:
            task = PipelineClient.submit_pipeline(job, flag, first_file, second_file)
        else:
            task = PipelineClient.submit_pipeline(job, flag, first_file)

        job.task_id = task.id
        await job_manager.save(job)

        return JSONResponse(content={"status": "success", "data":{"job_id": job.job_id, "message": "Job submitted successfully"}}, status_code=200)
    except Exception as e:
        error_message = str(e) or "Unknown error occurred"
        tb = traceback.format_exc()
        log.error(f"Error in submit_job: {error_message}\nTraceback:\n{tb}")
        return JSONResponse(
            content={"status": "error", "message": f"Error encountered during processing: {error_message}"},
            status_code=500,
        )