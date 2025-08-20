from src.logger import Logger
from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse, FileResponse
from src.request_model import SmilesRequest
from rdkit import Chem
import requests
import time, base64
from src.utils import generate_unique_job_id

log = Logger.get_logger()
router = APIRouter(prefix="/smiles-converter", tags=["SMILES Converter - Molecular Format Conversion"])

@router.post('/2d-smi', 
    summary="Convert SMILES to 2D MOL Format",
    description="""
    Convert a SMILES string to 2D molecular structure format (MOL file).
    
    **What this endpoint does:**
    - Parses SMILES string for molecular structure
    - Generates 2D molecular coordinates
    - Outputs in standard MOL file format
    
    **Use Cases:**
    - Molecular visualization
    - Structure analysis
    - Chemical database preparation
    - Molecular modeling workflows
    
    **Input:** SMILES string representing a chemical compound
    **Output:** 2D molecular structure in MOL format
    """,
    response_description="2D molecular structure in MOL format",
    responses={
        200: {"description": "Successful conversion to 2D format"},
        400: {"description": "Invalid or empty SMILES string"},
        500: {"description": "Internal server error during conversion"}
    }
)
def predict_2d_smi(request: SmilesRequest):
    """From SMILES string to a 2D smi data format"""
    if not request.smiles:
        log.info(f"smiles is empty, please provide valid smiles")
        return JSONResponse(content={"status": "error", "message": "smiles is empty, please provide valid smiles"}, status_code=400)
    try:
        smiles = request.smiles
        log.info(f"Generate smi file for smiles: {smiles}")
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES! Could not parse SPACC into a molecule.")
        # Generate 2D MOL block from RDKit
        mol_2d = Chem.MolToMolBlock(mol)
        return JSONResponse(content={"status": "success", "data": mol_2d}, status_code=200)
    except Exception as e:
        error_message = str(e) if str(e) else "Unknown error occurred"
        log.error(f"Error predict_2d_smi : {error_message}")
        return JSONResponse(content={"status": "error", "message": "Error encountered during processing. Please review the application log for detailed information"}, status_code=500)

@router.post('/3d-sdf', 
    summary="Convert SMILES to 3D SDF Format",
    description="""
    Convert a SMILES string to 3D molecular structure format (SDF file).
    
    **What this endpoint does:**
    - Parses SMILES string for molecular structure
    - Generates 3D molecular coordinates
    - Outputs in standard SDF file format
    
    **Use Cases:**
    - 3D molecular modeling
    - Docking studies
    - Molecular dynamics simulations
    - Structure-based drug design
    
    **Input:** SMILES string representing a chemical compound
    **Output:** 3D molecular structure in SDF format
    """,
    response_description="3D molecular structure in SDF format",
    responses={
        200: {"description": "Successful conversion to 3D format"},
        400: {"description": "Invalid or empty SMILES string"},
        500: {"description": "Internal server error during conversion"}
    }
)
def predict_3d_sdf(request: SmilesRequest):
    """From SMILES string to a 3D sdf data format"""
    if not request.smiles:
        log.info(f"smiles is empty, please provide valid smiles")
        return JSONResponse(content={"status": "error", "message": "smiles is empty, please provide valid smiles"}, status_code=400)
    try:
        smiles = request.smiles
        log.info(f"Generate 3D sdf for smiles: {smiles}")
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES! Could not parse SPACC into a molecule.")
        # Generate 3D coordinates using RDKit
        mol_3d = Chem.AddHs(mol)
        mol_3d = Chem.MolToMolBlock(mol_3d)
        return JSONResponse(content={"status": "success", "data": mol_3d}, status_code=200)
    except Exception as e:
        error_message = str(e) if str(e) else "Unknown error occurred"
        log.error(f"Error predict_3d_sdf : {error_message}")
        return JSONResponse(content={"status": "error", "message": "Error encountered during processing. Please review the application log for detailed information"}, status_code=500)

@router.post('/to-image', 
    summary="Convert SMILES to Molecular Image",
    description="""
    Convert a SMILES string to a molecular structure image.
    
    **What this endpoint does:**
    - Parses SMILES string for molecular structure
    - Generates 2D molecular visualization
    - Outputs as image file (PNG/JPG)
    
    **Use Cases:**
    - Publication graphics
    - Presentation materials
    - Chemical documentation
    - Educational content
    
    **Input:** SMILES string representing a chemical compound
    **Output:** Molecular structure image
    """,
    response_description="Molecular structure image",
    responses={
        200: {"description": "Successful image generation"},
        500: {"description": "Internal server error during image generation"}
    }
)
def smiles_to_image(request: SmilesRequest):
    """Get image from smarts.plus"""
    temp_image_path = None  # Initialize variable to track the temporary file path
    if not request.smiles:
        log.info(f"smiles is empty, please provide valid smiles")
        return JSONResponse(content={"status": "error", "message": "smiles is empty, please provide valid smiles"}, status_code=400)
    
    try:
        smiles = request.smiles
        wait_time = 1
        max_attempts = 10
        api_key = 'iuZteMsIr4HiYjINMjTei-idaVJ9bnmxghZh6ZpOoXo'

        data = {
            "query": {
                "smarts": smiles,
                "parameters": {
                    "file_format": "png",
                    "legend_mode": 0,
                    "labels_for_atoms": False,
                    "smartstrim_active": False,
                    "visualization_mode": 0,
                    "smarts_string_into_picture": True,
                    "visualization_of_default_bonds": 0
                }
            }
        }

        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': api_key
        }

        response = requests.post('https://api.smarts.plus/smartsView/', headers=headers, json=data)

        if response.status_code == 202:
            job_id = response.json().get('job_id')
            log.info("🕒 Waiting for image preparation...")
            for _ in range(max_attempts):
                time.sleep(wait_time)
                poll = requests.get(f'https://api.smarts.plus/smartsView/?job_id={job_id}')
                if poll.status_code == 200:
                    image_base64 = poll.json().get("result", {}).get("image")
                    if image_base64:
                        image_bytes = base64.b64decode(image_base64)
                        # Save image bytes to a temporary file
                        temp_image_path = f"temp_{generate_unique_job_id()}.png"
                        with open(temp_image_path, "wb") as image_file:
                            image_file.write(image_bytes)

                        # Return the image file as a response
                        return FileResponse(temp_image_path, media_type="image/png", filename="smarts_image.png")
            log.error("❌ Image preparation took too long.")
            return JSONResponse(content={"status": "error", "data": f"Image preparation took too long."}, status_code=500)
        elif response.status_code == 200:
            image_base64 = response.json()["result"]["image"]
            image_bytes = base64.b64decode(image_base64)
        else:
            log.error("❌ Error:", response.status_code, response.text)
            return JSONResponse(content={"status": "error", "data": f"Error:  {response.text}"}, status_code=500)

        # Save image bytes to a temporary file
        temp_image_path = f"temp_{generate_unique_job_id()}.png"
        with open(temp_image_path, "wb") as image_file:
            image_file.write(image_bytes)

        # Return the image file as a response
        return FileResponse(temp_image_path, media_type="image/png", filename="smarts_image.png")

    except Exception as e:
        error_message = str(e) if str(e) else "Unknown error occurred"
        log.error(f"Error predict_from_pdb_file: {error_message}")
        return JSONResponse(content={"status": "error", "message": "Error encountered during processing. Please review the application log for detailed information"}, status_code=500)
    # finally:
    #     if temp_image_path and os.path.exists(temp_image_path):
    #         os.remove(temp_image_path)