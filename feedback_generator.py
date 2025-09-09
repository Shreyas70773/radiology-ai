from typing import Dict, List

class AdvancedFeedbackGenerator:
    
    def _check_report_style(self, report_text: str) -> List[str]:
        """Analyzes the text for unprofessional language and provides style tips."""
        style_feedback = []
        text_lower = report_text.lower()
        
        # Rule 1: Check for unprofessional or uncertain phrasing
        unprofessional_phrases = ["i think", "looks like", "maybe a", "stuff", "bad finding"]
        for phrase in unprofessional_phrases:
            if phrase in text_lower:
                style_feedback.append(f"The phrase '{phrase}' is unprofessional. Aim for objective, confident language (e.g., 'consistent with' or 'suggestive of').")

        # Rule 2: Check for conciseness
        word_count = len(report_text.split())
        if word_count < 15:
            style_feedback.append("The report is very brief. Ensure all relevant positive and negative findings are documented.")
        elif word_count > 100:
            style_feedback.append("The report is quite long. Strive for clarity and conciseness, especially in the impression.")
            
        return style_feedback

    def generate_feedback(self, student_analysis: Dict, expert_findings: List[str]) -> Dict:
        """
        Generates feedback across 5 key areas by comparing the student's analysis
        to the expert's ground truth findings.
        """
        # --- Step 1: Parse the Ground Truth ---
        expert_positives = {f for f in expert_findings if not f.startswith('-')}
        expert_negatives = {f.lstrip('-') for f in expert_findings if f.startswith('-')}

        # --- Step 2: Parse the Student's Findings from their report ---
        student_positives = {f['type'] for f in student_analysis['fallback']['findings'] if not f.get('negated')}
        student_negatives = {f['type'] for f in student_analysis['fallback']['findings'] if f.get('negated')}

        # --- Step 3: Evaluate and Generate Feedback Categories ---
        
        # Category 1: Correct Observations
        correct_observations = list(student_positives.intersection(expert_positives))
        correct_negations = list(student_negatives.intersection(expert_negatives))
        
        # Category 2: Missed Findings
        missed_findings = list(expert_positives - student_positives)
        missed_negations = list(expert_negatives - student_negatives)
        
        # Category 3: Misinterpretations
        misinterpretations = list(student_positives - expert_positives)
        # Also check if the student said something was positive when it should have been negative
        negation_errors = list(student_positives.intersection(expert_negatives))

        # Category 4: Clarity and Style
        clarity_and_style_feedback = self._check_report_style(student_analysis['report_text'])
        
        # Category 5: General Tips
        general_tips = [
            "Always conclude with a concise 'Impression' section summarizing the most critical findings.",
            "When describing a finding, try to mention its location (e.g., 'right lower lobe')."
        ]

        # --- Step 4: Assemble the Final Feedback and Score ---
        final_feedback = {
            "correct_observations": correct_observations + [f"Absence of {n}" for n in correct_negations],
            "missed_findings": missed_findings + [f"Missed stating the absence of {n}" for n in missed_negations],
            "misinterpretations": misinterpretations + [f"Incorrectly identified {n} (should be absent)" for n in negation_errors],
            "clarity_and_style": clarity_and_style_feedback,
            "tips": general_tips
        }
        
        # A more robust scoring model
        score = 100
        score -= len(missed_findings) * 15
        score -= len(missed_negations) * 5 # Less penalty for missing a negative
        score -= len(misinterpretations) * 20
        score -= len(negation_errors) * 25 # High penalty for this error
        score -= len(clarity_and_style_feedback) * 5

        final_feedback['overall_score'] = max(0, min(100, score))
        
        return final_feedback