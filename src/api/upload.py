from fastapi import APIRouter, Depends, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse, FileResponse
import json, tempfile, os, traceback
from typing import Optional
import hashlib
import uuid
from src.logger import Logger

log = Logger.get_logger()
router = APIRouter(prefix="/upload", tags=["File Upload & Download Service"])

ALLOWED_CONTENT_TYPES = [
    "text/plain",      # TXT, MD
    "text/csv",        # CSV
    "text/xml",        # XML
    "text/vcard",      # VCF
    "application/pdf", # PDF
    "application/octet-stream", # BAM/BIN
    "application/json",# JSON
    "application/xml", # XML
    "application/epub+zip", # EPUB
    "application/vcf", # VCF
    "application/gzip",# GZ, VCF.GZ
    "application/x-gzip",
    "image/png",
    "image/jpeg",
    "image/jpg",
]

# Local storage path
LOCAL_STORAGE_PATH = "./data/upload"
os.makedirs(LOCAL_STORAGE_PATH, exist_ok=True)

def remove_file(path: str):
    if os.path.exists(path):
        os.remove(path)

def validate_file_type(file_path: str, allowed_types: list) -> bool:
    """Verify if file matches allowed types"""
    file_ext = os.path.splitext(file_path)[1].lower()
    allowed_extensions = ['.txt', '.csv', '.xml', '.vcf', '.pdf', '.json', '.pdb', '.png', '.jpg', '.jpeg', '.bam', '.bin']
    return file_ext in allowed_extensions

def verify_checksum(file_data: bytes, client_hash: str):
    """Verify file checksum if provided"""
    if not client_hash:
        return True  # No hash provided, skip verification
    
    server_hash = hashlib.sha256(file_data).hexdigest()
    return server_hash == client_hash

def generate_valid_filename(filename: str):
    """Generate a valid filename with unique identifier"""
    name, ext = os.path.splitext(filename)
    unique_id = str(uuid.uuid4())[:8]
    return f"{name}_{unique_id}{ext}"

@router.post(
    "/upload",
    summary="Upload a file to Local Storage",
    description="""
Upload a single file via multipart/form-data.  
Validates file type and optional client-provided checksum, then stores locally.

**Form fields**  
- **file** (`UploadFile`, required): The file to upload.  
- **hash** (`str`, optional): Client's checksum for integrity check.

**Behavior**  
1. Write uploaded content to a temporary file.  
2. If `hash` is provided, verify checksum; on mismatch, returns 400.  
3. Validate file extension against allowed list; on unsupported type, returns 400.  
4. Upload to local storage under `data/upload/{generated_filename}`.  
5. Return the storage path for retrieval.
""",
    responses={
        200: {
            "description": "File uploaded successfully",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "data": {
                            "message": "File uploaded successfully",
                            "file": "data/upload/myfile.vcf"
                        }
                    }
                }
            }
        },
        400: {
            "description": "Bad request (checksum mismatch or unsupported file type)",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Unsupported file type: application/zip"
                    }
                }
            }
        },
        500: {
            "description": "Internal server error during upload",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Error encountered during processing: <details>"
                    }
                }
            }
        },
    },
)
async def upload(
    file: UploadFile = File(..., description="The file to upload (any supported type)"),
    hash: Optional[str] = Form(None, description="Optional checksum for integrity check"),
):
    try:
        # Save to temp and verify checksum
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            content = await file.read()
            tf.write(content)
            temp_path = tf.name

        if not verify_checksum(content, hash):
            raise HTTPException(status_code=400, detail="Checksum mismatch")

        if not validate_file_type(temp_path, ALLOWED_CONTENT_TYPES):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file.content_type}"
            )

        # Generate unique filename and save locally
        filename = generate_valid_filename(file.filename)
        file_path = os.path.join(LOCAL_STORAGE_PATH, filename)
        
        with open(file_path, "wb") as f:
            f.write(content)

        objectname = f"data/upload/{filename}"
        
        return JSONResponse(
            status_code=200,
            content={"status": "success", "data": {"message": "File uploaded successfully", "file": objectname}}
        )

    except HTTPException:
        raise
    except Exception as e:
        tb = traceback.format_exc()
        log.error(f"Error in upload: {e}\n{tb}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Error encountered during processing: {str(e)}"}
        )
    finally:
        remove_file(temp_path)


@router.get(
    "/download",
    summary="Download raw file by object name",
    description="""
Retrieve a previously uploaded file by its storage key.  
Streams the file from local storage and returns as `application/octet-stream`.
""",
    responses={
        200: {
            "description": "Raw file download",
            "content": {"application/octet-stream": {}}
        },
        500: {
            "description": "Error during download",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Error encountered during processing: <details>"
                    }
                }
            }
        },
    },
)
async def download(
    objectname: str,
    background_tasks: BackgroundTasks,
):
    try:
        # Convert objectname to local file path
        if objectname.startswith("data/upload/"):
            local_path = objectname.replace("data/upload/", LOCAL_STORAGE_PATH + "/")
        else:
            local_path = os.path.join(LOCAL_STORAGE_PATH, objectname)
        
        if not os.path.exists(local_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Create temp copy for response
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            with open(local_path, "rb") as src:
                tf.write(src.read())
            temp_path = tf.name

        # schedule file cleanup after response
        background_tasks.add_task(remove_file, temp_path)
        return FileResponse(temp_path, filename=os.path.basename(objectname))

    except HTTPException:
        raise
    except Exception as e:
        tb = traceback.format_exc()
        log.error(f"Error in download: {e}\n{tb}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Error encountered during processing: {str(e)}"}
        )


@router.get(
    "/download-content",
    summary="Download file and return its parsed content",
    description="""
Download a file and return its contents.  
If the file contains valid JSON, it is parsed and returned as JSON; otherwise returned as plain text.
""",
    responses={
        200: {
            "description": "Parsed file content",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "data": {"foo": "bar"}  # or raw text
                    }
                }
            }
        },
        500: {
            "description": "Error during content retrieval",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Error encountered during processing: <details>"
                    }
                }
            }
        },
    },
)
async def download_content(
    objectname: str,
):
    temp_path = None
    try:
        # Convert objectname to local file path
        if objectname.startswith("data/upload/"):
            local_path = objectname.replace("data/upload/", LOCAL_STORAGE_PATH + "/")
        else:
            local_path = os.path.join(LOCAL_STORAGE_PATH, objectname)
        
        if not os.path.exists(local_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        with open(local_path, "r") as f:
            raw = f.read()
        
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = raw

        return JSONResponse(content={"status": "success", "data": parsed}, status_code=200)

    except HTTPException:
        raise
    except Exception as e:
        tb = traceback.format_exc()
        log.error(f"Error in download_content: {e}\n{tb}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Error encountered during processing: {str(e)}"}
        )
    finally:
        if temp_path:
            remove_file(temp_path) 