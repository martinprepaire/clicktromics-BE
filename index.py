from fastapi import FastAPI, APIRouter
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import logging

load_dotenv()
from src.config import ALLOW_ORIGINS, MONGO_URL
from src.mongo_client import SandboxMongo

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        SandboxMongo._initialize_client()
        SandboxMongo._initialize_sync_client()
        logging.info("✅ MongoDB client initialized successfully.")
    except Exception as e:
        logging.error(f"❌ Error during application startup: {str(e)}")
        logging.error(f"❌ Error during application startup: MONGO_URL = {MONGO_URL}")
    yield

app = FastAPI(
    title="Sandbox API - Bioinformatics Developer Playground",
    description="""
# 🧬 Bioinformatics Developer Sandbox API

A comprehensive API for bioinformatics research, drug discovery, and computational biology workflows.

## 🚀 **Available Services**

### **Core Bioinformatics Tools**
- **Genetic Analysis**: Variant calling, annotation, and analysis
- **Microbiome Analysis**: Microbial community profiling and analysis
- **Blood Analysis**: Clinical blood test analysis and interpretation
- **Pharmacogenomics**: Drug-gene interaction analysis

### **🔧 Clicktromics Suite (NEW!)**
Advanced tools for drug discovery and molecular design:

#### **ADMET AI** 
Predict drug-like properties including Lipinski's Rule of Five, QED scores, and molecular descriptors.

#### **SMILES Converter**
Convert SMILES strings to various molecular formats:
- 2D MOL files
- 3D SDF files  
- Molecular images

#### **Click Chemistry**
Generate drug conjugates:
- **ADC (Antibody Drug Conjugates)**: Link antibodies to cytotoxic drugs
- **PDC (Peptide Drug Conjugates)**: Link peptides to therapeutic payloads

#### **File Management**
- **File Upload/Download**: S3 and local storage support
- **PDB Management**: Download from RCSB, upload custom structures
- **Data Processing**: File validation and content parsing

#### **Advanced Search**
- **Antibody Search**: Find antibodies by target or category
- **Disease Search**: Search disease databases
- **Gene Search**: Gene information retrieval
- **Organ Search**: Anatomical data access

#### **Molecular Modeling Jobs**
- **Boltz**: Protein structure prediction
- **DiffAb**: Antibody design and optimization
- **Homelette**: Antibody modeling
- **Musite**: Phosphorylation site prediction
- **Peptide Generation**: Peptide synthesis workflows
- **Gnina**: Molecular docking simulations

## 🔬 **Use Cases**
- Drug discovery and optimization
- Molecular property prediction
- Structure-activity relationship analysis
- Conjugate drug design
- Protein structure analysis
- Bioinformatics research and development

## 📚 **API Documentation**
- Interactive docs available at `/docs`
- ReDoc documentation at `/redoc`
- All endpoints include request/response examples

## 🔒 **Authentication**
Basic authentication required for all endpoints.
""",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    root_path="/sandbox",
    lifespan=lifespan,
    contact={
        "name": "Bioinformatics Developer Sandbox",
        "email": "support@bioinformatics-sandbox.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from src.api import router as root_router
from src.api.jobs import router as job_api_router
from src.api.jobs.boltz import router as boltz_router
from src.api.jobs.diffab import router as diffab_router
from src.api.jobs.homelette import router as homelette_router
from src.api.jobs.musite import router as musite_router
from src.api.jobs.gnina import router as gnina_router
from src.api.jobs.peptide_generating import router as peptide_generating_router
from src.api.jobs.blood_test import router as blood_router
from src.api.jobs.vep_ensemple import router as vep_ensemple_route
from src.api.jobs.variant_calling_bam import router as variant_calling_bam_route
from src.api.jobs.variant_calling_fastq import router as variant_calling_fastq_route
from src.api.jobs.microbiome import router as microbiome_route
from src.api.jobs.genetic_annotation import router as genetic_annotation_route
from src.api.jobs.genetic import router as genetic_route
from src.api.jobs.url_download import router as url_download_route

from src.api.search import router as search_route

# Add the new Clicktromics API routers
from src.api.admet_ai import router as admet_router
from src.api.smiles_converter import router as smiles_converter_router
from src.api.click_chemistry import router as click_chemistry_router
from src.api.upload import router as upload_router
from src.api.input import router as input_router
from src.api.organs import router as organs_router

api_router = APIRouter(prefix="/v1")
job_router = APIRouter(prefix="/jobs")

# Include existing job routers
job_router.include_router(boltz_router)
job_router.include_router(diffab_router)
job_router.include_router(homelette_router)
job_router.include_router(musite_router)
job_router.include_router(gnina_router)
job_router.include_router(peptide_generating_router)
job_router.include_router(variant_calling_bam_route)
job_router.include_router(variant_calling_fastq_route)
job_router.include_router(vep_ensemple_route)
job_router.include_router(genetic_annotation_route)
job_router.include_router(microbiome_route)
job_router.include_router(blood_router)
job_router.include_router(genetic_route)
job_router.include_router(url_download_route)
job_router.include_router(job_api_router)

# Include existing routers
api_router.include_router(search_route)
api_router.include_router(job_router)
api_router.include_router(root_router)

# Include the new Clicktromics APIs (without the /v1 prefix)
app.include_router(admet_router)
app.include_router(smiles_converter_router)
app.include_router(click_chemistry_router)
app.include_router(upload_router)
app.include_router(input_router)
app.include_router(organs_router)

app.include_router(api_router)