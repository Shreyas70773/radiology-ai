# SimuRad: An AI-Powered Platform for Radiology Report Simulation

## Abstract

SimuRad is a comprehensive, full-stack educational platform designed to enhance medical training through interactive radiology report simulation. The system employs multimodal artificial intelligence techniques to analyze student-generated radiological reports against established clinical cases, providing immediate, structured feedback on diagnostic accuracy, clinical clarity, and report completeness. This implementation combines a high-performance FastAPI backend with a lightweight Flask frontend to deliver a scalable, interactive learning environment for medical education.

[![Project Status](https://img.shields.io/badge/status-prototype_complete-green.svg)](https://shields.io/)
[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://shields.io/)
[![Frameworks](https://img.shields.io/badge/frameworks-FastAPI_&_Flask-purple.svg)](https://shields.io/)
[![AI Engine](https://img.shields.io/badge/AI-PyTorch_&_Transformers-orange.svg)](https://shields.io/)

---

## System Overview

### Core Features

- **Interactive Case-Based Learning**: Practice environment utilizing real-world clinical cases with corresponding X-ray imaging data from the NIH ChestX-ray8 dataset
- **Multimodal AI Analysis**: Integration of Vision Transformer models for radiological image analysis with specialized Natural Language Processing models (Microsoft CXR-BERT, RadBERT, spaCy) for comprehensive text understanding
- **Five-Pillar Assessment Framework**: Structured feedback system evaluating:
  1. Diagnostic accuracy and correct observations
  2. Identification of missed clinical findings
  3. Analysis of potential misinterpretations
  4. Assessment of report clarity and professional writing style
  5. Provision of actionable improvement recommendations
- **Microservice Architecture**: Decoupled system design ensuring scalability and maintainability

### Technical Architecture

| Component | Technology Stack | Function |
|-----------|------------------|----------|
| **AI Backend Service** | FastAPI | Asynchronous model serving and inference processing |
| **Web Frontend** | Flask | User interface and interaction management |
| **Deep Learning Framework** | PyTorch, Hugging Face Transformers | Core AI model implementation and execution |
| **Natural Language Processing** | spaCy | Text processing, sentence segmentation, negation detection |
| **Data Management** | Pandas | Clinical dataset curation and manipulation |
| **Medical Dataset** | NIH ChestX-ray8 | Clinical case repository and imaging data |

---

## Installation Guide

### Prerequisites

**System Requirements:**
- Python 3.9 or higher
- Git version control system
- Minimum 8GB available disk space for AI models
- Stable internet connection for initial model downloads

**Recommended Hardware:**
- 16GB RAM or higher
- CUDA-compatible GPU (optional, for accelerated inference)

### Step 1: Repository Setup

Clone the project repository to your local development environment:

```bash
git clone https://github.com/Shreyas70773/radiology-ai.git
cd radiology-ai
```

### Step 2: Python Environment Configuration

Create an isolated Python virtual environment to manage dependencies:

**Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**macOS/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

### Step 3: Dependency Installation

Install required Python packages and language models:

```bash
# Install core dependencies
pip install -r requirements.txt

# Install spaCy NLP library
pip install spacy

# Download English language model
python -m spacy download en_core_web_sm
```

### Step 4: Model Cache Configuration

**Important**: AI models require several gigabytes of storage. Configure a custom cache directory to manage storage efficiently.

1. Create a directory with sufficient storage capacity:
   ```bash
   # Example paths - adjust based on your system
   # Windows: D:\huggingface_cache
   # macOS/Linux: /path/to/huggingface_cache
   ```

2. Set the HF_HOME environment variable:

   **Windows:**
   - Open System Properties → Advanced → Environment Variables
   - Add new user variable:
     - Variable Name: `HF_HOME`
     - Variable Value: `D:\huggingface_cache` (your chosen path)

   **macOS/Linux:**
   ```bash
   # Add to ~/.bashrc or ~/.zshrc
   export HF_HOME=/path/to/your/cache
   ```

3. **Restart your terminal** to apply the environment variable changes.

### Step 5: Dataset Preparation

#### Clinical Data Acquisition
1. Download the NIH ChestX-ray8 metadata file:
   - Access the [official Kaggle dataset](https://www.kaggle.com/nih-chest-xrays/data)
   - Download `Data_Entry_2017.csv`
   - Place the file in the project root directory

#### Image Data Download
Execute the provided script to download required case images:

```bash
python download_images.py
```

This process will:
- Create the `static/images/` directory structure
- Download and organize necessary radiological images
- Verify data integrity

---

## System Execution

The application operates as a distributed system requiring two concurrent services.

### Terminal Session 1: AI Backend Initialization

Start the FastAPI AI inference service:

```bash
# Ensure virtual environment is activated
uvicorn api_service:app --reload
```

**Expected Output:**
- Model initialization logs
- Service startup confirmation
- API endpoint availability notification

### Terminal Session 2: Frontend Service Launch

Initialize the Flask web application:

```bash
# Ensure virtual environment is activated
python frontend_app.py
```

### Application Access

Navigate to the following URL in your web browser:
```
http://127.0.0.1:5000
```

The SimuRad platform interface will be accessible for educational interaction.

---

## System Validation

### Functional Testing
1. Verify both services are running without errors
2. Confirm web interface loads correctly
3. Test case selection and image display
4. Validate report submission and AI feedback generation

### Performance Monitoring
- Monitor memory usage during model loading
- Verify inference response times
- Check system stability under continuous operation

---

## Development Roadmap

### Phase 1: Current Implementation
- ✅ Core AI model integration
- ✅ Basic web interface
- ✅ Five-pillar feedback system
- ✅ NIH dataset integration

### Phase 2: Planned Enhancements
- **Expanded Case Library**: Integration of additional clinical datasets with difficulty stratification
- **User Analytics**: Implementation of progress tracking and performance analytics
- **Advanced UI/UX**: User experience optimization based on medical student feedback
- **Assessment Validation**: Clinical validation of AI feedback accuracy

### Phase 3: Research Extensions
- Integration with hospital PACS systems
- Multi-language support for international medical education
- Advanced computer vision techniques for pathology detection
- Collaborative learning features for peer review

---

## Citation and Acknowledgments

This project utilizes several key datasets and models:

- **NIH ChestX-ray8 Dataset**: Wang, X. et al. "ChestX-ray8: Hospital-scale Chest X-ray Database and Benchmarks"
- **Microsoft CXR-BERT**: Specialized BERT model for chest X-ray report analysis
- **RadBERT**: Domain-adapted BERT for radiological text processing

---

## Contact and Support

For technical support, feature requests, or academic collaboration inquiries, please contact the development team through the project repository's issue tracking system.

**Project Repository**: [https://github.com/Shreyas70773/radiology-ai](https://github.com/Shreyas70773/radiology-ai)
