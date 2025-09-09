from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import asyncio
import time
import logging
from datetime import datetime
import pandas as pd
from typing import List, Dict, Set

from models import RadBERTAnalyzer, CheXBertExtractor, RuleBasedAnalyzer, VisionAnalyzer # Import the new VisionAnalyzer
from feedback_generator import AdvancedFeedbackGenerator
from config import Config
from fastapi.middleware.cors import CORSMiddleware


# --- Basic Setup ---
logging.basicConfig(level=Config.LOG_LEVEL, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
app = FastAPI(title="Radiology Report Analysis API - Multimodal", version="2.0.0")

origins = [
    "http://localhost",
    "http://localhost:5000",
    "http://127.0.0.1:5000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Global Instances & Data ---
radbert_analyzer: RadBERTAnalyzer
chexbert_extractor: CheXBertExtractor
rule_based_analyzer: RuleBasedAnalyzer
vision_analyzer: VisionAnalyzer # Add instance for the vision model
feedback_generator: AdvancedFeedbackGenerator
case_library: Dict[str, Dict] = {}

# --- App Events ---
@app.on_event("startup")
async def startup_event():
    global radbert_analyzer, chexbert_extractor, rule_based_analyzer, vision_analyzer, feedback_generator, case_library
    logger.info("Initializing models and building case library from NIH dataset...")
    
    # --- Step 1: Initialize all AI Models ---
    radbert_analyzer = RadBERTAnalyzer()
    chexbert_extractor = CheXBertExtractor()
    rule_based_analyzer = RuleBasedAnalyzer()
    vision_analyzer = VisionAnalyzer() # Initialize the vision model
    feedback_generator = AdvancedFeedbackGenerator()
    
    # --- Step 2: Build the Case Library from NIH Data ---
    try:
        # Load the master data file
        df = pd.read_csv("Data_Entry_2017.csv")
        
        # Load the list of case filenames we want to use
        with open("selected_cases.txt", "r") as f:
            selected_filenames = [line.strip() for line in f if line.strip()]

        # Filter the DataFrame to only our selected cases
        selected_cases_df = df[df['Image Index'].isin(selected_filenames)]

        for _, row in selected_cases_df.iterrows():
            case_id = row['Image Index'].split('.')[0] # e.g., "00013118_005"
            
            # The "Finding Labels" from the CSV are our expert text findings
            # We normalize them to match our internal format (lowercase, underscore, no negation)
            expert_text_labels = {label.lower().replace('_', '') for label in row['Finding Labels'].split('|')}
            if "nofinding" in expert_text_labels: # Handle the "No Finding" case
                expert_text_labels = set() # It has no positive findings

            case_library[case_id] = {
                "case_id": case_id,
                "image_path": f"/static/images/{row['Image Index']}",
                "patient_info": f"{row['Patient Age']} year old {row['Patient Gender']}",
                "expert_text_findings": list(expert_text_labels)
            }
        logger.info(f"Successfully built library with {len(case_library)} cases from the NIH dataset.")
    except FileNotFoundError:
        logger.error("FATAL: Data_Entry_2017.csv or selected_cases.txt not found. Please download and place them in the project root.")
        # In a real app, you might want to exit or handle this more gracefully
    except Exception as e:
        logger.error(f"Failed to build case library: {e}", exc_info=True)

# --- API Endpoints ---

# ADD: Root endpoint for testing
@app.get("/", summary="API Health Check")
async def root():
    return {
        "message": "Radiology Analysis API is running",
        "status": "healthy",
        "cases_loaded": len(case_library),
        "version": "2.0.0"
    }

@app.get("/cases", summary="Get a list of all available cases")
async def get_all_cases():
    return list(case_library.values())

@app.get("/case/{case_id}", summary="Get details for a single case")
async def get_case(case_id: str):
    # Handle both full filename and case_id formats
    case_id_base = case_id.split('.')[0]
    if case_id_base not in case_library:
        raise HTTPException(status_code=404, detail=f"Case not found: {case_id}")
    return case_library[case_id_base]

class AnalyzeRequest(BaseModel):
    case_id: str
    student_report_text: str

@app.post("/analyze", summary="Analyze a student's report against an expert's findings")
async def analyze_report(request: AnalyzeRequest):
    start_time = time.time()
    
    # Handle both full filename and case_id formats
    case_id_base = request.case_id.split('.')[0]
    if case_id_base not in case_library:
        raise HTTPException(status_code=404, detail=f"Case ID '{case_id_base}' not found in the library")
    
    case_data = case_library[case_id_base]
    expert_text_findings: Set[str] = set(case_data["expert_text_findings"])
    
    try:
        # --- Step 1: Analyze the Student's Text Report ---
        text_analysis_tasks = [
            asyncio.to_thread(radbert_analyzer.analyze, request.student_report_text),
            asyncio.to_thread(chexbert_extractor.extract_labels, request.student_report_text),
            asyncio.to_thread(rule_based_analyzer.analyze, request.student_report_text)
        ]
        radbert_results, chexbert_results, fallback_results = await asyncio.gather(*text_analysis_tasks)

        student_analysis = {
            "radbert": radbert_results, "chexbert": chexbert_results,
            "fallback": fallback_results, "report_text": request.student_report_text
        }

        # --- Step 2: Analyze the Case Image with the Vision Model ---
        image_path = case_data["image_path"]
        # Convert the web path to actual file path
        actual_image_path = image_path.replace("/static/", "static/")
        visual_findings: Set[str] = set(await asyncio.to_thread(vision_analyzer.analyze_image, actual_image_path))

        # --- Step 3: Create the "Gold Standard" Ground Truth ---
        # The union of what the expert wrote AND what the AI saw in the image.
        gold_standard_findings: List[str] = list(expert_text_findings.union(visual_findings))
        
        # Generate the advanced feedback using this new, ultimate ground truth
        feedback_data = feedback_generator.generate_feedback(student_analysis, gold_standard_findings)
        
        return {
            "case_id": case_id_base,
            "gold_standard_findings": gold_standard_findings,
            "student_analysis_results": student_analysis,
            "advanced_feedback": feedback_data,
            "processing_time_ms": (time.time() - start_time) * 1000,
        }
    except Exception as e:
        logger.error(f"Analysis failed for case {case_id_base}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")