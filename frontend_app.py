from flask import Flask, render_template, request, jsonify
import httpx
import json
import logging

# --- Configuration ---
AI_BACKEND_URL = "http://127.0.0.1:8000"

# Initialize the Flask application
app = Flask(__name__, static_url_path='/static')

# Set up logging for better debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Debug route to list all routes
@app.route("/debug/routes")
def list_routes():
    """Debug endpoint to show all available routes"""
    import urllib
    output = []
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods)
        line = urllib.parse.unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, rule))
        output.append(line)
    
    response = "Available routes:\n" + "\n".join(sorted(output))
    return f"<pre>{response}</pre>"

@app.route("/")
def index():
    """
    Main page. Fetches the list of all cases from the AI backend
    and renders the user interface with proper case data.
    """
    try:
        with httpx.Client(timeout=30.0) as client:
            # First, check if the backend is running
            logger.info("Checking backend health...")
            health_response = client.get(f"{AI_BACKEND_URL}/")
            health_response.raise_for_status()
            logger.info(f"Backend health check passed: {health_response.json()}")
            
            # Then get the cases
            logger.info("Fetching cases from backend...")
            response = client.get(f"{AI_BACKEND_URL}/cases")
            response.raise_for_status()
            all_cases = response.json()
            logger.info(f"Received {len(all_cases)} cases from backend")
                
            if not all_cases:
                return """
                <h1>Error: No Cases Available</h1>
                <p>The AI backend returned no cases. This usually means:</p>
                <ul>
                    <li>Data_Entry_2017.csv is missing from the project root</li>
                    <li>selected_cases.txt is missing from the project root</li>
                    <li>The image files are missing from static/images/</li>
                </ul>
                <p>Check the backend logs for more details.</p>
                <p><a href="/debug/routes">View available routes</a></p>
                """, 500
        
            # --- START OF THE FIX ---
            # The JavaScript in index.html expects a single JSON object containing all case data.
            # We will pass the entire `all_cases` list as a JSON string to the template.
            # The template variable `cases_data` matches the `{{ cases_data | safe }}` in your HTML.
            cases_json = json.dumps(all_cases)
            logger.info(f"Passing all case data to template. First case ID: {all_cases[0]['case_id']}")
        
            return render_template(
                "index.html", 
                cases_data=cases_json
            )
            # --- END OF THE FIX ---
        
    except httpx.ConnectError as e:
        logger.error(f"Backend connection error: {e}")
        return f"""
        <h1>Backend Connection Error</h1>
        <p>Could not connect to the AI backend server at <code>{AI_BACKEND_URL}</code></p>
        <p>Please ensure:</p>
        <ol>
            <li>The FastAPI server is running: <code>uvicorn api_service:app --reload --port 8000</code></li>
            <li>The server is accessible at the correct port</li>
        </ol>
        <p><a href="/debug/routes">View available routes</a></p>
        """, 500
    except httpx.TimeoutException:
        logger.error("Backend timeout")
        return "<h1>Backend Timeout</h1><p>The AI backend is taking too long to respond. This usually means the models are still loading.</p>", 500
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        return f"<h1>Request Error</h1><p>Network error: {str(e)}</p>", 500
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        logger.error(f"Data format error: {e}")
        return f"<h1>Data Format Error</h1><p>The case library from the AI backend seems to be empty or malformed.</p><p>Error details: {str(e)}</p>", 500

# --- REMOVED ---
# The /get_case/<case_id> route is no longer needed because the JavaScript
# now has all the case data from the initial page load. Removing it simplifies the app.

@app.route("/get_feedback", methods=["POST"])
def get_feedback():
    """
    Forward feedback request to the AI backend.
    This now works correctly because the JavaScript sends the REAL case_id.
    """
    logger.debug("get_feedback called")
    data = request.json
    logger.debug(f"Received data: {data}")
    
    # This `case_id` will now be correct, e.g., "00000061_015"
    case_id = data.get("case_id")
    student_report = data.get("student_report_text")
    
    if not case_id or not student_report:
        logger.error("Missing required fields")
        return jsonify({"error": "Missing case_id or student_report_text"}), 400
    
    try:
        with httpx.Client(timeout=120.0) as client:
            url = f"{AI_BACKEND_URL}/analyze"
            payload = {"case_id": case_id, "student_report_text": student_report}
            logger.info(f"Calling backend analyze endpoint with correct case_id: {case_id}")
            
            response = client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            logger.info(f"Analysis complete for case {case_id}")
            return jsonify(result)
    
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error in get_feedback {e.response.status_code}: {e.response.text}")
        error_detail = "Unknown error"
        try:
            error_data = e.response.json()
            error_detail = error_data.get("detail", str(e))
        except:
            error_detail = e.response.text
        return jsonify({
            "error": f"Backend returned error {e.response.status_code}",
            "details": error_detail
        }), e.response.status_code
    except Exception as e:
        logger.error(f"An unexpected error occurred in get_feedback: {e}")
        return jsonify({"error": "An internal server error occurred", "details": str(e)}), 500

if __name__ == "__main__":
    # Runs the Flask app. Open your browser to http://127.0.0.1:5000
    app.run(debug=True, port=5000)