import os
import sys
import subprocess
import google.generativeai as genai
from datetime import datetime

# Configure Gemini API
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

def get_code_diff():
    """Get the code diff from Git."""
    try:
        diff = subprocess.check_output(
            ["git", "diff", "origin/main...HEAD"], universal_newlines=True
        )
        return diff if diff.strip() else "No code changes detected."
    except subprocess.CalledProcessError:
        return "Error fetching diff."

def analyze_code_with_gemini(code_diff):
    """Analyze code changes with Gemini model."""
    model = genai.GenerativeModel("gemini-1.5-pro")
    prompt = f"""
    You are a senior empathetic code reviewer.
    Review the following pull request changes:
    ---
    {code_diff}
    ---
    Output in this structure:
    ## Strengths
    (bullet points)
    ## Suggestions
    (bullet points)
    ## Questions
    (bullet points)
    ## LABEL_SIGNAL:
    JSON with one key 'label' and value one of ['ready-to-merge','needs-work','major-changes']
    """
    response = model.generate_content(prompt)
    return response.text

def save_review_history(pr_number, review_text, label):
    """Append review details to review_history.md for auditing."""
    history_file = "review_history.md"
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    entry = f"""
---
**PR #{pr_number}**  
**Date:** {timestamp}  
**Label:** {label}

{review_text}
---
"""
    with open(history_file, "a", encoding="utf-8") as f:
        f.write(entry)

def main():
    pr_number = os.environ.get("PR_NUMBER", "Unknown")
    code_diff = get_code_diff()
    review_text = analyze_code_with_gemini(code_diff)

    # Extract label from review text
    label = "needs-work"  # Default fallback
    if "LABEL_SIGNAL:" in review_text:
        try:
            import json
            label_json = review_text.split("LABEL_SIGNAL:")[1].strip()
            label_data = json.loads(label_json)
            label = label_data.get("label", label)
        except Exception:
            pass

    # Save review history
    save_review_history(pr_number, review_text, label)

    # Print for GitHub Actions to capture
    print("REVIEW_OUTPUT_START")
    print(review_text)
    print("REVIEW_OUTPUT_END")
    print(f"LABEL_SIGNAL:{label}")

if __name__ == "__main__":
    main()
