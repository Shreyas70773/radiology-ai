import click
import httpx
import json
import textwrap

# --- Configuration ---
API_BASE_URL = "http://127.0.0.1:8000"

# --- Pre-written Student Reports for Demonstration ---
# We'll use these as the "student input" for our sample cases.
STUDENT_REPORTS = {
    "CASE001": "Impression: Lungs are clear. No acute findings.",
    "CASE002": "Findings: There is some stuff in the right lung. Looks like pneumonia. Heart is big.",
    "CASE003": "Patient has shortness of breath. There is fluid in the lungs."
}

def print_feedback(feedback: dict):
    """Formats and prints the advanced feedback in a clean, readable way."""
    
    click.secho("\n--- Automated Feedback Report ---", fg='cyan', bold=True)
    
    score = feedback.get('overall_score', 0)
    color = 'green' if score >= 75 else 'yellow' if score >= 60 else 'red'
    click.secho(f"\nOverall Score: {score}/100", fg=color, bold=True)

    def print_section(title, items, color):
        if items:
            click.secho(f"\n{title}:", fg=color, bold=True)
            for item in items:
                # Use textwrap for nice formatting of long lines
                wrapped_text = textwrap.fill(f"  • {item}", width=80, subsequent_indent='    ')
                click.echo(wrapped_text)

    print_section("✅ Correct Observations", feedback.get('correct_observations'), 'green')
    print_section("❌ Missed Findings", feedback.get('missed_findings'), 'red')
    print_section("⚠️ Misinterpretations / Errors", feedback.get('misinterpretations'), 'red')
    print_section("✍️ Clarity and Style", feedback.get('clarity_and_style'), 'yellow')
    print_section("💡 General Tips", feedback.get('tips'), 'cyan')
    
    click.echo("-" * 40)


@click.group()
def cli():
    """A CLI tool to interact with the Radiology Report Analysis API."""
    pass

@cli.command(name="list", help="List all available cases from the library.")
def list_cases():
    """Fetches and displays all cases from the case library."""
    click.echo("Fetching available cases from the API...")
    try:
        with httpx.Client() as client:
            response = client.get(f"{API_BASE_URL}/cases")
            response.raise_for_status()
            cases = response.json()
        
        click.secho("\n--- Case Library ---", fg='cyan', bold=True)
        for case in cases:
            click.secho(f"Case ID: {case['case_id']}", fg='yellow')
            click.echo(f"  History: {case['patient_history']}")
            click.echo(f"  Expert Findings: {', '.join(case['expert_findings'])}\n")
            
    except httpx.RequestError as e:
        click.secho(f"Error: Could not connect to the API at {API_BASE_URL}. Is the server running?", fg='red')
    except httpx.HTTPStatusError as e:
        click.secho(f"Error: API returned a status of {e.response.status_code}", fg='red')

@cli.command(name="analyze", help="Analyze pre-written student reports for all cases.")
def analyze_all():
    """
    Submits the pre-written student reports for all cases and displays
    the advanced feedback for each.
    """
    click.echo("Analyzing pre-written student reports for all available cases...")
    
    try:
        with httpx.Client(timeout=60.0) as client:
            # First, get the list of all cases
            list_response = client.get(f"{API_BASE_URL}/cases")
            list_response.raise_for_status()
            cases = list_response.json()

            for case in cases:
                case_id = case['case_id']
                if case_id not in STUDENT_REPORTS:
                    click.secho(f"\nSkipping {case_id}: No pre-written student report found.", fg='yellow')
                    continue
                
                student_text = STUDENT_REPORTS[case_id]
                
                click.secho(f"\n\n>>> Analyzing Case: {case_id}", bold=True, fg='white')
                click.echo(f"    Expert Findings: {case['expert_findings']}")
                click.echo(f"    Student's Report: \"{student_text}\"")
                
                # Make the analysis request
                payload = {"case_id": case_id, "student_report_text": student_text}
                response = client.post(f"{API_BASE_URL}/analyze", json=payload)
                response.raise_for_status()
                
                result = response.json()
                print_feedback(result.get('advanced_feedback', {}))
                
    except httpx.RequestError as e:
        click.secho(f"Error: Could not connect to the API at {API_BASE_URL}. Is the server running?", fg='red')
    except httpx.HTTPStatusError as e:
        click.secho(f"Error: API returned a status of {e.response.status_code}. Details: {e.response.text}", fg='red')

if __name__ == "__main__":
    cli()