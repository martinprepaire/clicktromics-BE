from src.logger import Logger
from fastapi import APIRouter , Depends, Query
from fastapi.responses import JSONResponse

from src.repo.drug import DrugRepo
from src.repo.antibody import AntibodyRepo
from src.repo.disease import DiseaseRepo
from src.repo.malacard import MalacardRepo
from src.utility import get_homelette_Object
from src.request_model import SearchAntibodyRequest
from src.config import DEFAULT_BUCKET_NAME, USE_AWS, LOCAL_STORAGE_PATH
import os

log = Logger.get_logger()
router = APIRouter(prefix="/search", tags=["Search"])

@router.post("/antibody")
async def search_antibody(
    request_body: SearchAntibodyRequest,
    repo: AntibodyRepo = Depends(lambda: AntibodyRepo())
):
    """Search for antibody in our database"""
    try:
        # Validate input
        if not request_body.input:
            log.info("Input is empty, please provide valid input")
            return JSONResponse(
                content={"status": "error", "message": "Input is empty, please provide valid input"}, 
                status_code=400
            )
        
        if not request_body.category:
            log.info("Category is empty, please provide valid category")
            return JSONResponse(
                content={"status": "error", "message": "Category is empty, please provide valid category"}, 
                status_code=400
            )
        
        log.info(f"Searching for antibodies with input: {request_body.input}, category: {request_body.category}")
        
        # Search for antibodies based on category
        if request_body.category == "target":
            antibodies = await repo.find_by_target(request_body.input, request_body.page, request_body.page_size)
        else:
            antibodies = await repo.find(request_body.input, request_body.page, request_body.page_size)

        log.info(f"Found {antibodies.total} antibodies in database")

        if antibodies.total == 0:
            return JSONResponse(
                status_code=404, 
                content={"status": "error", "message": "No antibodies found in database"}
            )
        
        # Process results and check for PDB files
        processed_results = []
        for antibody in antibodies.results:
            try:
                homelette_file = get_homelette_Object(antibody.ID)
                
                # Check if PDB file exists (simplified logic for now)
                pdb_exists = False
                if USE_AWS:
                    # TODO: Implement S3 check when AWS is configured
                    log.warning("AWS S3 check not implemented yet")
                    pdb_exists = False
                else:
                    local_path = os.path.join(LOCAL_STORAGE_PATH, homelette_file)
                    pdb_exists = os.path.exists(local_path)
                    log.debug(f"Checking local path: {local_path} - Exists: {pdb_exists}")
                
                if pdb_exists:
                    antibody_data = {
                        **antibody.model_dump(),
                        "pdb_file": homelette_file
                    }
                    antibody_data.pop("targets", None)
                    processed_results.append(antibody_data)
                else:
                    log.warning(f"PDB file not found for antibody {antibody.ID}: {homelette_file}")
                    
            except Exception as e:
                log.error(f"Error processing antibody {antibody.ID}: {str(e)}")
                continue

        if not processed_results:
            log.warning(f"No PDB files found for antibodies: {[ab.ID for ab in antibodies.results]}")
            return JSONResponse(
                status_code=404, 
                content={"status": "error", "message": "Antibodies found but PDB files not available"}
            )

        log.info(f"Search completed successfully, found {len(processed_results)} antibodies with PDB files")
        
        # Update results with processed data
        antibodies.results = processed_results
        return JSONResponse(
            content={"status": "success", "data": antibodies.dict()}, 
            status_code=200
        )

    except Exception as e:
        error_message = str(e) or "Unknown error occurred"
        log.error(f"Error in search_antibody: {error_message}")
        return JSONResponse(
            content={"status": "error", "message": f"Error encountered during processing: {error_message}"},
            status_code=500,
        )
    
@router.get("/diseases/category")
async def search_diseases_by_category(
    name: str = Query(..., description="Disease categories name"),
    repo: DiseaseRepo = Depends(lambda: DiseaseRepo()),
    mala_repo: MalacardRepo = Depends(lambda: MalacardRepo()),
):
    try:
        if name is None or name == "":
            return JSONResponse(status_code=400, content={"status": "error", "message":"name is empty"})
        
        matches = await repo.find_category_by_query_list(name.lower())
        diseases = []

        for match in matches:
            doc = await mala_repo.find_disease_by_name(match.name)
            if doc:
                diseases.append(match.model_dump())

        return JSONResponse(content={"status": "success", "data": {
           "query": name,
           "matches": diseases
        }}, status_code=200)
    
    except Exception as e:
        error_message = str(e) or "Unknown error occurred"
        log.error(f"Error in submit_job: {error_message}")
        return JSONResponse(
            content={"status": "error", "message": f"Error encountered during processing: {error_message}"},
            status_code=500,
        )

@router.post("/disease/{name}/drugs")
async def search_drugs_by_disease(
    name: str,
    repo: MalacardRepo = Depends(lambda: MalacardRepo()),
    drug_repo: DrugRepo = Depends(lambda: DrugRepo())
):
    try:
        if name is None or name == "":
            return JSONResponse(status_code=400, content={"status": "error", "message":"name is empty"})
        
        doc = await repo.find_disease_by_name(name)
    
        if not doc:
            return JSONResponse(status_code=404, content={"status": "error", "message":f"{name} Not Found"})
        
        nutraceutical = []
        drugs = []
        for drug in  doc.drugs:
            if "Nutraceutical" in drug.status:
                nutraceutical.append(drug.drug_name)
            else:
                drug_info = await drug_repo.find_by_name(drug.drug_name)
                if drug_info:
                    drugs.append(drug_info.model_dump())

        log.info(len(drugs))
        return JSONResponse(content={"status": "success", "data":{
            'nutraceutical': nutraceutical,
            'drugs': drugs
        }}, status_code=200)
    
    except Exception as e:
        error_message = str(e) or "Unknown error occurred"
        log.error(f"Error in search_disease: {error_message}")
        return JSONResponse(
            content={"status": "error", "message": f"Error encountered during processing: {error_message}"},
            status_code=500,
        )
    
@router.post("/disease/{name}/genes")
async def search_genes_by_disease(
    name: str,
    repo: MalacardRepo = Depends(lambda: MalacardRepo()),
    antibody_repo: AntibodyRepo = Depends(lambda: AntibodyRepo())
):
    try:
        if name is None or name == "":
            return JSONResponse(status_code=400, content={"status": "error", "message":"name is empty"})
        
        doc = await repo.find_disease_by_name(name)
    
        if not doc:
            return JSONResponse(status_code=404, content={"status": "error", "message":f"{name} Not Found"})
        
        genes = []
        for gene in  doc.genes:
            exists = await antibody_repo.count_by_target(gene.gene_name)
            if exists:
                genes.append(gene.model_dump())

        return JSONResponse(content={"status": "success", "data": genes}, status_code=200)
    
    except Exception as e:
        error_message = str(e) or "Unknown error occurred"
        log.error(f"Error in search_disease: {error_message}")
        return JSONResponse(
            content={"status": "error", "message": f"Error encountered during processing: {error_message}"},
            status_code=500,
        )