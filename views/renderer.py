from playwright.sync_api import sync_playwright

def render_html(html_body, mermaid_code):
    return f"""
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

def html_to_pdf(html_content, output_path):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html_content, wait_until="networkidle")
        page.pdf(path=output_path, format="A4")
        browser.close()