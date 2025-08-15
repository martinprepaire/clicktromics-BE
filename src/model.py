# Simplified model module for now
ADMET_MODEL = None

def load_admet_model() -> None:
    """Loads the models into memory."""
    global ADMET_MODEL
    # Placeholder for now - you can enhance this later
    ADMET_MODEL = {"status": "loaded"}

def get_admet_model():
    """Get the ADMET-AI model."""
    return ADMET_MODEL 