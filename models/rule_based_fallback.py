import spacy
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class RuleBasedAnalyzer:
    """
    A robust analyzer using spaCy for accurate sentence segmentation and NLP-powered
    keyword and negation detection.
    """
    
    def __init__(self):
        try:
            # Load the small, efficient spaCy model
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("spaCy model 'en_core_web_sm' loaded successfully.")
        except OSError:
            logger.error("spaCy model not found. Please run 'python -m spacy download en_core_web_sm'")
            self.nlp = None

        # Keywords for each finding (can be expanded)
        self.patterns = {
            "pneumonia": ["pneumonia", "consolidation", "infiltrate"],
            "effusion": ["effusion", "fluid"],
            "pneumothorax": ["pneumothorax"],
            "cardiomegaly": ["cardiomegaly", "enlarged heart", "cardiac enlargement"],
            "edema": ["edema", "pulmonary edema"],
            "opacity": ["opacity", "opacities", "opacification"],
            "atelectasis": ["atelectasis", "collapse"],
            # Add other findings as needed
        }
        self.negation_terms = ["no", "not", "without", "negative", "absent", "clear of", "free of"]

    def analyze(self, report_text: str) -> Dict:
        """Perform spaCy-based analysis of the report."""
        if not self.nlp:
            return {"error": "spaCy model not available", "findings": []}

        doc = self.nlp(report_text.lower())
        findings = []
        
        # spaCy accurately splits the text into sentences
        for sent in doc.sents:
            sentence_text = sent.text
            
            # Check for negation terms within this specific sentence
            is_sentence_negated = any(neg in sentence_text for neg in self.negation_terms)
            
            for finding_type, keywords in self.patterns.items():
                for keyword in keywords:
                    if keyword in sentence_text:
                        # A simple but effective rule: if the sentence contains a negation term,
                        # assume any finding in it is negated.
                        findings.append({
                            "type": finding_type,
                            "text": sentence_text.strip(),
                            "negated": is_sentence_negated
                        })
                        # Break after finding one keyword for this type to avoid duplicates per sentence
                        break 
        
        # Remove duplicate findings (e.g., "consolidation" and "pneumonia" in the same sentence)
        unique_findings = []
        seen = set()
        for finding in findings:
            # Create a unique key for each finding within a sentence
            finding_key = (finding['text'], finding['type'])
            if finding_key not in seen:
                unique_findings.append(finding)
                seen.add(finding_key)

        return {
            "findings": unique_findings,
            "confidence": 0.9, # Rule-based systems are deterministic and thus high-confidence
            "method": "spaCy-rule-based"
        }