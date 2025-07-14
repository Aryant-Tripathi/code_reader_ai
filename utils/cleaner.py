import html
import re

def clean_json_string(raw_text):
    return re.sub(r"^```(?:json)?\n(.*)\n```$", r"\1", raw_text.strip(), flags=re.DOTALL)

def sanitize_mermaid_code(raw_mermaid: str) -> str:
    with_newlines = raw_mermaid.replace("\\n", "\n")
    return html.unescape(with_newlines)