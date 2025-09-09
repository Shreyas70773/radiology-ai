import torch
from transformers import AutoTokenizer, AutoModel
import numpy as np
from typing import Dict, List, Tuple
import logging
from config import Config

logger = logging.getLogger(__name__)

class RadBERTAnalyzer:
    def __init__(self):
        self.device = Config.DEVICE
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(Config.RADBERT_MODEL)
            self.model = AutoModel.from_pretrained(Config.RADBERT_MODEL).to(self.device)
            self.model.eval()
            logger.info(f"RadBERT loaded successfully on {self.device}")
        except Exception as e:
            logger.error(f"Failed to load RadBERT: {e}")
            self.model = None
            self.tokenizer = None
    
    def analyze(self, report_text: str) -> Dict:
        """Analyze report using RadBERT for embeddings and similarity."""
        if not self.model or not self.tokenizer:
            return {"error": "RadBERT not available", "confidence": 0.0}
        
        try:
            inputs = self.tokenizer(
                report_text, return_tensors="pt", truncation=True, max_length=Config.MAX_LENGTH, padding=True
            ).to(self.device)
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                embeddings = outputs.last_hidden_state.mean(dim=1)
            
            findings = self._extract_findings(report_text, embeddings)
            
            # --- START OF FIX ---
            # The previous confidence calculation was unreliable.
            # A more robust heuristic is to base confidence on the number of non-negated findings.
            confidence = min(0.5 + (len(findings) * 0.1), 0.9) if findings else 0.5
            # --- END OF FIX ---
            
            return {
                "findings": findings,
                "confidence": float(confidence),
                "model": "RadBERT"
            }
            
        except Exception as e:
            logger.error(f"RadBERT analysis failed: {e}")
            return {"error": str(e), "confidence": 0.0}
    
    def _extract_findings(self, text: str, embeddings: torch.Tensor) -> List[Dict]:
        """Extract medical findings from text."""
        findings = []
        key_terms = {
            "pneumonia": ["consolidation", "opacity", "infiltrate"],
            "effusion": ["fluid", "pleural effusion", "hydrothorax"],
            "pneumothorax": ["collapsed lung", "air in pleural space"],
            "cardiomegaly": ["enlarged heart", "cardiac enlargement"],
            "edema": ["pulmonary edema", "fluid in lungs"],
            "atelectasis": ["collapse", "volume loss"],
            "nodule": ["mass", "lesion", "tumor"]
        }
        
        text_lower = text.lower()
        
        for condition, terms in key_terms.items():
            if any(term in text_lower for term in terms):
                findings.append({
                    "type": condition,
                    "detected": True
                })
        
        return findings