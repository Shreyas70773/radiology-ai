import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Model configurations
    RADBERT_MODEL = os.getenv("RADBERT_MODEL", "StanfordAIMI/RadBERT")
    CHEXBERT_MODEL = os.getenv("CHEXBERT_MODEL", "microsoft/BiomedVLP-CXR-BERT-specialized")    
    # Performance settings
    MAX_LENGTH = 512
    BATCH_SIZE = 1
    DEVICE = "cuda" if os.getenv("USE_GPU", "false").lower() == "true" else "cpu"
    
    # Confidence thresholds
    MIN_CONFIDENCE = 0.6
    HIGH_CONFIDENCE = 0.85
    
    # API settings
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", 8000))
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Cache settings
    ENABLE_CACHE = os.getenv("ENABLE_CACHE", "true").lower() == "true"
    CACHE_TTL = int(os.getenv("CACHE_TTL", 3600))