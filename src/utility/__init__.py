import os
import shutil
from src.logger import Logger
import uuid

log = Logger.get_logger()

def cleanup_temp_files(output_dir, files: list):
    if output_dir and os.path.exists(output_dir):
        log.info(f"Temporary dir {output_dir} removed.")
        shutil.rmtree(output_dir)
    for file in files:
        if file and os.path.exists(file):
            log.info(f"Temporary {file} removed.")
            os.remove(file)

def generate_unique_job_id() -> str:
    """Generate a unique 7-character alphanumeric job ID"""
    return str(uuid.uuid4())[:7].replace('-', '').upper()

def get_homelette_Object(ID: str) -> str:
   return f"homelette/{ID}/model_1.pdb"
