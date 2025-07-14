import json
from models.analyzer import CodeAnalyzer
from utils.prompt_generator import generate_prompt
from utils.cleaner import clean_json_string, sanitize_mermaid_code
from views.renderer import render_html, html_to_pdf
from openai import OpenAI
import tempfile, os

class DocumentGeneratorController:
    def __init__(self, repo_path, api_key):
        self.repo_path = repo_path
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")

    def generate(self, user_input, system_prompt, output_path=None):

        analyzer = CodeAnalyzer(self.repo_path)
        files = analyzer.read_codebase()
        prompt = generate_prompt(files, user_input)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]

        response = self.client.chat.completions.create(
            model="gemini-2.0-flash",
            messages=messages
        )

        raw_output = response.choices[0].message.content
        cleaned = clean_json_string(raw_output)
        json_output = json.loads(cleaned)
        html_body = json_output.get("html_response", "")
        mermaid_code = sanitize_mermaid_code(json_output.get("mermaid_code", ""))

        full_html = render_html(html_body, mermaid_code)

        if output_path:
            pdf_path = output_path
        else:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
                pdf_path = temp_pdf.name

        html_to_pdf(full_html, pdf_path)

        return {
            "html": full_html,
            "json": json_output,
            "pdf_path": pdf_path
        }


