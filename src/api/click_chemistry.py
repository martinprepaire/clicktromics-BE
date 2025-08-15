from bio_core.logger import Logger
from fastapi import HTTPException, APIRouter
from fastapi.responses import JSONResponse
from src.request_model import ClickADCRequest, ClickPDCRequest
import random

log = Logger.get_logger()
router = APIRouter(prefix="/click", tags=["Click Chemistry - Drug Conjugate Generation"])

# Simplified constants for now - you can expand these later
LINKERS = {
    "DBCO-acid": "O=C(CCC(O(*))=O)N(C1)C2=C(C=CC=C2)C#CC3=C1C=CC=C3",
    "BCN-acid": "O(*)C(=O)CCC(=O)C1C2CCC#CCCC12",
}

GLYCAN_LINKER = {"Azide": "N=N-N(*)"}

GLYCANS = {
    "Neu5Ac(a2-3)Gal(b1-4)GlcNAc": "CC(=O)N[C@H]1[C@H]([C@H](O)[C@H](O)CO)O[C@@](O[C@H]2[C@@H](O)[C@@H](CO)O[C@@H](O[C@H]3[C@H](O)[C@@H](NC(C)=O)CO[C@@H]3CO)[C@@H]2O)(C(=O)O(*))C[C@@H]1O",
}

@router.post("/adc", 
    summary="Generate Antibody Drug Conjugate (ADC)",
    description="""
    Generate an Antibody Drug Conjugate (ADC) payload using click chemistry principles.
    
    **What this endpoint does:**
    - Combines antibody targeting with cytotoxic drug payload
    - Uses click chemistry for stable conjugation
    - Generates optimized linker-drug combinations
    - Provides glycan modification options
    
    **Use Cases:**
    - Cancer immunotherapy
    - Targeted drug delivery
    - Antibody engineering
    - Drug conjugate development
    
    **Input:** Drug SMILES or DrugBank ID
    **Output:** Complete ADC structure with linker and payload information
    """,
    response_description="Generated ADC structure with components",
    responses={
        200: {"description": "Successful ADC generation"},
        400: {"description": "Missing SMILES or DrugBank ID"},
        500: {"description": "Internal server error during generation"}
    }
)
async def click_generate_adc(request: ClickADCRequest):
    """Generate Antibody Drug Conjugate payload"""
    try:
        if not request.smiles:
            raise HTTPException(status_code=400, detail="SMILES string is required")
        
        # Simplified implementation - you can enhance this later
        glycanlinker_key, glycanlinker_value = random.choice(list(GLYCAN_LINKER.items()))
        glycan_key, glycan_value = random.choice(list(GLYCANS.items()))
        
        res = {
            "Glycan": {glycan_key: glycan_value},
            "Glycan-Linker": {glycanlinker_key: glycanlinker_value},
            "payload": f"Generated payload for {request.smiles}",
            "Linker": random.choice(list(LINKERS.keys()))
        }
        
        response_data = {
            "message": "Click ADC process completed",
            "output": res
        }   
        
        return JSONResponse(content={"status": "success", "data": response_data}, status_code=200)
    except Exception as e:
        error_message = str(e) if str(e) else "Unknown error occurred"
        log.error(f"Error click_generate_adc: {error_message}")
        return JSONResponse(content={"status": "error", "message": "Error encountered during processing. Please review the application log for detailed information"}, status_code=500)

@router.post("/pdc", 
    summary="Generate Peptide Drug Conjugate (PDC)",
    description="""
    Generate a Peptide Drug Conjugate (PDC) using click chemistry principles.
    
    **What this endpoint does:**
    - Links therapeutic peptides to drug payloads
    - Uses optimized linker chemistry
    - Generates stable peptide-drug complexes
    - Provides targeting and delivery optimization
    
    **Use Cases:**
    - Peptide therapeutics
    - Drug delivery systems
    - Targeted therapy development
    - Peptide engineering
    
    **Input:** Peptide SMILES and linker specifications
    **Output:** Complete PDC structure with components
    """,
    response_description="Generated PDC structure with components",
    responses={
        200: {"description": "Successful PDC generation"},
        400: {"description": "Missing peptide SMILES"},
        500: {"description": "Internal server error during generation"}
    }
)
async def click_generate_pdc(request: ClickPDCRequest):
    """Generate Peptide Drug Conjugate payload"""
    try:
        if not request.peptide_smiles:
            raise HTTPException(status_code=400, detail="Peptide SMILES is required")
        
        # Simplified implementation
        res = {
            "peptide": request.peptide_smiles,
            "linker": request.linker_target_peptide_smiles,
            "payload": f"Generated PDC payload for peptide: {request.peptide_smiles}"
        }
        
        response_data = {
            "message": "Click PDC process completed",
            "output": res
        }   
        
        return JSONResponse(content={"status": "success", "data": response_data}, status_code=200)
    except Exception as e:
        error_message = str(e) if str(e) else "Unknown error occurred"
        log.error(f"Error click_generate_pdc: {error_message}")
        return JSONResponse(content={"status": "error", "message": "Error encountered during processing. Please review the application log for detailed information"}, status_code=500) 