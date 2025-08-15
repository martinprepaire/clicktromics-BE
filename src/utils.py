import uuid
import hashlib
import requests
import os
from datetime import datetime, timezone
from src.logger import Logger
from src.config import RCSB_URL, CPU_THRESHOLD, RAM_THRESHOLD
from fastapi import HTTPException

log = Logger.get_logger()

def validate_file_type(file_path: str, allowed_types: list) -> bool:
    """Verify if file matches allowed types (e.g., ['PDF', 'VCF'])."""
    try:
        import magic
        mime = magic.Magic(mime=True)
        detected_type = mime.from_file(file_path)
        return any(allowed in detected_type for allowed in allowed_types)
    except ImportError:
        # If python-magic is not available, use file extension
        file_ext = os.path.splitext(file_path)[1].lower()
        allowed_extensions = ['.txt', '.csv', '.xml', '.vcf', '.pdf', '.json', '.pdb', '.png', '.jpg', '.jpeg']
        return file_ext in allowed_extensions

def verify_checksum(file_data: bytes, client_hash: str):
    """Verify file checksum if provided"""
    if not client_hash:
        return True  # No hash provided, skip verification
    
    server_hash = hashlib.sha256(file_data).hexdigest()
    return server_hash == client_hash

def get_homelette_Object(ID: str) -> str:
    return f"homelette/{ID}/model_1.pdb"

def generate_unique_job_id() -> str:
    """Generate a unique 7-character alphanumeric job ID"""
    return str(uuid.uuid4())[:7].replace('-', '').upper()

def convert_time_to_date(time: float) -> str:
    """Get the current time in UTC and convert to UTC+4, then to readable format"""
    utc_time = datetime.fromtimestamp(time, tz=timezone.utc)
    return utc_time.strftime('%Y-%m-%d %H:%M:%S')

def parse_fasta_to_sequences(fasta_content: str) -> list[str]:
    sequences = []
    current_sequence = ""
    for line in fasta_content.split('\n'):
        if not line.startswith('>'):
            current_sequence += line.strip()
    if current_sequence:
        sequences.append(current_sequence)
    return sequences

def get_remote_file_content(url: str, decoding = True):
    response = requests.get(url)
    if response.status_code == 200 and decoding:
        return response.content.decode('utf-8')
    elif response.status_code == 200:
        return response.content
    else:
        log.error(f"Failed to download file {url}. Status code: {response.status_code}")

def download_pdb_file(pdb_id: str):
    """Download a PDB file from RCSB PDB."""
    try:
        pdb_url = f"{RCSB_URL}{pdb_id}.pdb"
        log.info(f"Downloads from {RCSB_URL} for pdb id {pdb_id}")
        response = requests.get(pdb_url)
    except Exception as e:
        error_message = str(e) if str(e) else "Unknown error occurred"
        log.error(f"Error download_pdb: {error_message}")
        raise HTTPException(detail=f"Error download_pdb: {error_message}", status_code=500)

    if response.status_code != 200:
        raise HTTPException(status_code=404, detail=f"PDB file {pdb_id} not found on RCSB PDB")

    return response.content

def transform_keys(d):
    """Transform dictionary keys from snake_case to Title Case"""
    if not isinstance(d, dict):
        return d  # Base case: not a dict, return as is

    new_dict = {}
    for key, value in d.items():
        new_key = key.replace('_', ' ').title()
        new_dict[new_key] = transform_keys(value) if isinstance(value, dict) else value
    return new_dict 