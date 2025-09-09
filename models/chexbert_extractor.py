import torch
from transformers import AutoTokenizer, AutoModel
from typing import Dict, List
import logging
from config import Config

logger = logging.getLogger(__name__)

class CheXBertExtractor:
    LABELS = [
        "No Finding", "Enlarged Cardiomediastinum", "Cardiomegaly",
        "Lung Opacity", "Lung Lesion", "Edema", "Consolidation",
        "Pneumonia", "Atelectasis", "Pneumothorax", "Pleural Effusion",
        "Pleural Other", "Fracture", "Support Devices"
    ]
    
    def __init__(self):
        self.device = Config.DEVICE
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(Config.CHEXBERT_MODEL, trust_remote_code=True)
            self.model = AutoModel.from_pretrained(Config.CHEXBERT_MODEL, trust_remote_code=True).to(self.device)
            self.model.eval()
            self.label_embeddings = self._get_embeddings(self.LABELS)
            logger.info(f"CheXbert extractor initialized successfully with {Config.CHEXBERT_MODEL}")
        except Exception as e:
            logger.error(f"Failed to load CheXbert: {e}", exc_info=True)
            self.model = None

    def _get_embeddings(self, text_list: List[str]) -> torch.Tensor:
        inputs = self.tokenizer.batch_encode_plus(
            batch_text_or_text_pairs=text_list, add_special_tokens=True, padding='longest', return_tensors='pt'
        ).to(self.device)
        with torch.no_grad():
            # --- START OF THE FINAL FIX ---
            # The model's custom function does not accept 'token_type_ids'.
            # We must pass the arguments it expects by name instead of unpacking the whole dictionary.
            return self.model.get_projected_text_embeddings(
                input_ids=inputs['input_ids'], 
                attention_mask=inputs['attention_mask']
            )
            # --- END OF THE FINAL FIX ---

    def extract_labels(self, report_text: str) -> Dict:
        if not self.model:
            return {"error": "CheXbert not available", "labels": [], "confidence": 0.0}
        
        try:
            report_embedding = self._get_embeddings([report_text])
            sim = torch.nn.functional.cosine_similarity(report_embedding, self.label_embeddings)
            
            all_labels_with_scores = []
            for i, label_name in enumerate(self.LABELS):
                all_labels_with_scores.append({
                    "label": label_name,
                    "confidence": sim[i].item(),
                    "category": self._get_category(label_name)
                })
            
            all_labels_with_scores.sort(key=lambda x: x["confidence"], reverse=True)
            
            overall_confidence = all_labels_with_scores[0]['confidence'] if all_labels_with_scores else 0.0

            return {
                "labels": all_labels_with_scores,
                "confidence": overall_confidence,
                "model": "CheXbert-Embedding-Similarity"
            }
        except Exception as e:
            logger.error(f"CheXbert embedding analysis failed: {e}", exc_info=True)
            return {"error": str(e), "labels": [], "confidence": 0.0}

    def _get_category(self, label: str) -> str:
        categories = { "cardiac": ["Cardiomegaly", "Enlarged Cardiomediastinum"], "lung": ["Lung Opacity", "Lung Lesion", "Consolidation", "Atelectasis"], "pleural": ["Pleural Effusion", "Pleural Other", "Pneumothorax"], "infection": ["Pneumonia", "Edema"], "structural": ["Fracture", "Support Devices"], "normal": ["No Finding"] }
        for cat, labels in categories.items():
            if label in labels: return cat
        return "other"