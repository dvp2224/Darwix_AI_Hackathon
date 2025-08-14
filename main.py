import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def update_comments_in_code(code_content):
    """Send code to Groq LLaMA-3 to improve comments."""
    prompt = f"""
You are an expert code reviewer.
Update and improve all comments in the following code to make them clearer and more helpful.
Do not change the functionality.

Code:
{code_content}
"""
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": "You are a helpful programming assistant."},
            {"role": "user", "content": prompt}
        ],
    )
    return response.choices[0].message["content"]

if __name__ == "__main__":
    # Read the original file
    with open("input_code.py", "r") as file:
        original_code = file.read()

    # Get updated comments
    updated_code = update_comments_in_code(original_code)

    # Save updated file
    with open("output_code.py", "w") as file:
        file.write(updated_code)

    print("✅ Comments updated! Check 'output_code.py'")
