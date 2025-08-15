from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import requests
import os
from src.config import RCSB_URL
from src.logger import Logger
from src.request_model import PdbRequest

log = Logger.get_logger()
router = APIRouter(
    prefix="/input",
    tags=["Input Management - PDB Files & Data"]
)

# Local storage path
LOCAL_STORAGE_PATH = "./data/input"
os.makedirs(LOCAL_STORAGE_PATH, exist_ok=True)

@router.post("/pdb_id/", 
    summary="Download PDB file from RCSB by ID",
    description="""
    Download a PDB (Protein Data Bank) file from rcsb.org by providing a PDB ID.
    
    **What this endpoint does:**
    - Fetches PDB file from RCSB database
    - Stores file locally for processing
    - Returns local file path for access
    
    **Use Cases:**
    - Protein structure analysis
    - Molecular modeling workflows
    - Structural biology research
    - Drug design projects
    
    **Input:** PDB ID (e.g., "1ABC", "7XYZ")
    **Output:** File storage path and local access
    """,
    response_description="PDB file download result with storage path",
    responses={
        200: {"description": "PDB file downloaded successfully"},
        400: {"description": "Missing PDB ID"},
        404: {"description": "PDB file not found on RCSB"},
        500: {"description": "Internal server error during download"}
    }
)
async def download_pdb_by_id(request: PdbRequest):
    """Download PDB file from rcsb.org by providing PDB ID"""
    
    if not request.pdb_id:
        return JSONResponse(content={"status": "error", "message": "PDB ID is required"}, status_code=400)

    try:
        pdb_id = request.pdb_id
        pdb_url = f"{RCSB_URL}{pdb_id}.pdb"

        log.info(f"Downloads from {RCSB_URL}")
        response = requests.get(pdb_url)
        if response.status_code != 200:
            return JSONResponse(status_code=404, content={"status": "error", "message": f"PDB file {pdb_id} not found on RCSB PDB"})

        response_data = response.content
        filename = f"{pdb_id}.pdb"
        file_path = os.path.join(LOCAL_STORAGE_PATH, filename)

        with open(file_path, "wb") as f:
            f.write(response_data)

        result = {
            "message": f"PDB file {filename} has been downloaded successfully",
            "local_file_path": file_path
        }
        return JSONResponse(content={"status": "success", "data": result}, status_code=200)
    except Exception as e:
        error_message = str(e) if str(e) else "Unknown error occurred"
        log.error(f"Error download_pdb_by_id: {error_message}")
        return JSONResponse(content={"status": "error", "message": "Error encountered during processing. Please review the application log for detailed information"}, status_code=500)


@router.post("/upload/", 
    summary="Upload PDB file for processing",
    description="""
    Upload a PDB file and save it locally for later use with bioinformatics tools.
    
    **What this endpoint does:**
    - Accepts PDB file uploads
    - Stores file in local storage system
    - Provides local file path for access
    
    **Use Cases:**
    - Custom protein structure uploads
    - Batch processing workflows
    - Integration with external tools
    - Research collaboration
    
    **Input:** PDB file upload
    **Output:** File storage confirmation and local path
    """,
    response_description="PDB file upload result with storage path",
    responses={
        200: {"description": "PDB file uploaded successfully"},
        500: {"description": "Internal server error during upload"}
    }
)
async def upload_pdb_file(file: UploadFile = File(...)):
    """Upload PDB file and save it locally to use it later with diffab"""
    try:
        filename = file.filename
        file_path = os.path.join(LOCAL_STORAGE_PATH, filename)
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        result = {
            "message": f"PDB file {filename} has been uploaded successfully",
            "local_file_path": file_path
        }
        return JSONResponse(content={"status": "success", "data": result}, status_code=200)
    except Exception as e:
        error_message = str(e) if str(e) else "Unknown error occurred"
        log.error(f"Error upload_pdb_file: {error_message}")
        return JSONResponse(content={"status": "error", "message": "Error encountered during processing. Please review the application log for detailed information"}, status_code=500) 