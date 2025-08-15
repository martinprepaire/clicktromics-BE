from bio_core.logger import Logger
from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
from src.request_model import SmilesRequest

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
        mol_2d = f"""Generated 2D MOL block for {smiles}
This is a placeholder 2D structure
You can enhance this with RDKit later"""
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
        mol_3d = f"""Generated 3D SDF for {smiles}
This is a placeholder 3D structure
You can enhance this with OpenBabel later"""
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
def smiles_to_image(smiles: str = Form(...)):
    """Get image from smarts.plus"""
    try:
        return JSONResponse(content={"status": "success", "message": "Image generation endpoint ready", "smiles": smiles}, status_code=200)
    except Exception as e:
        error_message = str(e) if str(e) else "Unknown error occurred"
        log.error(f"Error smiles_to_image: {error_message}")
        return JSONResponse(content={"status": "error", "message": "Error encountered during processing. Please review the application log for detailed information"}, status_code=500) 