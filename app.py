import os
import re
import json
import html
import tempfile
from flask import Flask, request, render_template_string, send_file
from dotenv import load_dotenv
from openai import OpenAI
from playwright.sync_api import sync_playwright

# Load .env
load_dotenv()

# Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
REPO_DIR = "/Users/aryanttripathi/Desktop/GEN AI/CODE_READER/sample_directory"

# OpenAI Client
client = OpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# Flask App
app = Flask(__name__)

def read_directory(directory_path):
    file_data = []
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_data.append({
                        "filename": file_path,
                        "content": f.read()
                    })
    return file_data


def generate_prompt(files, question):
    prompt = ""
    for file in files:
        prompt += f"Filename: {file['filename']}\nCode:\n{file['content']}\n\n"
    prompt += f"---\n{question}"
    return prompt


def convert_html_to_pdf(html: str, output_path: str):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html, wait_until="networkidle")
        page.pdf(path=output_path, format="A4")
        browser.close()


def clean_json_string(raw_text):
    return re.sub(r"^```(?:json)?\n(.*)\n```$", r"\1", raw_text.strip(), flags=re.DOTALL)

def sanitize_mermaid_code(raw_mermaid: str) -> str:
    with_newlines = raw_mermaid.replace("\\n", "\n")
    return html.unescape(with_newlines)


@app.route('/', methods=['GET', 'POST'])
def index():
    parsed_output = ""
    html_content = ""
    pdf_path = None

    if request.method == 'POST':
        user_input = request.form.get('user_input')

        if user_input:
            files = read_directory(REPO_DIR)
            prompt = generate_prompt(files, user_input)

            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]

            #       print("\n📤 Prompt Sent to LLM:\n", prompt)

            try:
                response = client.chat.completions.create(
                    model="gemini-2.0-flash",
                    messages=messages
                )

                raw_output = response.choices[0].message.content
                #print("\n Raw LLM Output:\n", raw_output)

                cleaned_output = clean_json_string(raw_output)
                json_output = json.loads(cleaned_output)
                parsed_output = json.dumps(json_output, indent=4)

                html_body = json_output.get("html_response", "")
                mermaid_code = json_output.get("mermaid_code", "")
                mermaid_code = sanitize_mermaid_code(mermaid_code)
                #print("After fix mermaid_code:", mermaid_code)

                # Embed mermaid code inside the HTML body
                full_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="utf-8">
                    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
                    <script>mermaid.initialize({{ startOnLoad: true }});</script>
                </head>
                <body>
                    {html_body}
                    <div class="mermaid">
                        {mermaid_code}
                    </div>
                </body>
                </html>
                """

                html_content = full_html

                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
                    convert_html_to_pdf(full_html, temp_pdf.name)
                    pdf_path = temp_pdf.name

            except json.JSONDecodeError as json_err:
                print("\n JSON Decode Error:\n", json_err)
                parsed_output = f"JSON decode error. Raw output:\n{raw_output}"
            except Exception as e:
                print("\n General Error:\n", e)
                parsed_output = f"Error: {str(e)}"


    return render_template_string(TEMPLATE,
                                  response=parsed_output,
                                  html_preview=html_content,
                                  pdf_path=pdf_path)


@app.route('/download_pdf')
def download_pdf():
    pdf_temp_path = request.args.get("path")
    if pdf_temp_path and os.path.exists(pdf_temp_path):
        return send_file(pdf_temp_path, as_attachment=True, download_name="document.pdf")
    return "PDF not found", 404


TEMPLATE = """
<!doctype html>
<html>
<head>
  <title>GenAI Document Assistant</title>
</head>
<body>
  <h1>Talk to LLM</h1>
  <form method="post">
    <label for="user_input">Enter your query:</label><br>
    <input type="text" id="user_input" name="user_input" style="width: 300px;" required>
    <input type="submit" value="Ask">
  </form>

  {% if response %}
    <h2>JSON Response:</h2>
    <div style="white-space: pre-wrap; border: 1px solid #ccc; padding: 10px;">{{ response }}</div>
  {% endif %}

  {% if html_preview %}
    <h2>HTML Document Preview:</h2>
    <div style="border: 1px solid #ccc; padding: 10px;">{{ html_preview | safe }}</div>
  {% endif %}

  {% if pdf_path %}
    <br><a href="/download_pdf?path={{ pdf_path }}">Download PDF</a>
  {% endif %}
</body>
</html>
"""

# System Prompt
SYSTEM_PROMPT = """
You are an AI document generation assistant tasked with analyzing a repository of code files and generating a structured HTML document.
Follow these specific guidelines:

1. **Analysis of Files:**
   - Access and examine all files in the provided repository.
   - Identify the programming languages used in each file.
   - Determine the purpose of the code in each file.
   - Note any conditions, functions, or significant lines of code that are critical to understanding the file's functionality.

2. **HTML Document Structure:**
   - Create an HTML document with the following sections:
     - **Title:** Indicate the name of the repository.
     - **Overview:** A brief description of the repository's purpose.
     - **File Listings:** For each file, include:
       - **File Name:** Clearly displayed and bolded.
       - **Programming Language:** Indicate the language used, bolded.
       - **Purpose:** A concise summary of the file's function.
       - **Key Conditions/Functions:** Bullet points listing important conditions and functions present in the code.
       - **Modifications:** Suggest potential changes or improvements that could be made to the program.

3. **Formatting Requirements:**
   - Use bullet points for lists and key details.
   - Bold important terms and headings for clarity.
   - Ensure the document is clear, concise, and easy to navigate.

4. **Final Document Review:**
   - Ensure the document is free of grammatical errors.
   - Verify that all details are accurate and reflective of the analyzed code.

5. **Mermaid Diagram Integration:**
   - Include a new JSON field titled "Diagram" that uses Mermaid syntax for visualization.
   - Generate a diagram that represents the relationships or flow of the code based on your analysis.
   - Ensure the Mermaid code is correctly formatted for rendering in compatible viewers.

Output a single raw JSON object only, with only two fields,
one is pure html and other one is pure mermaid language. 
Html should be present with no markdown, no commentary, and no extra characters.
And also add mermaid diagram integration support with other field.

Respond only with a raw JSON object. Do NOT wrap it in triple backticks or markdown formatting or add any json field.
For example, response json looks like this:

{
    "html_response": "{<h1> pure html response </h1> }",
    "mermaid_code": "<mermaid code>"
} 

"""

if __name__ == '__main__':
    app.run(debug=True, port=9099)