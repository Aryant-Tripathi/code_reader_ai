import argparse
import os
from dotenv import load_dotenv
from controllers.document_controller import DocumentGeneratorController
from system_prompt import SYSTEM_PROMPT

# Load .env (if you use GEMINI_API_KEY there)
load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="Generate code documentation from any project")
    parser.add_argument('--path', type=str, required=True, help='Path to the project directory')
    parser.add_argument('--query', type=str, required=True, help='Query or instruction for LLM')
    parser.add_argument('--output', type=str, help='Custom path to save the generated PDF (optional)')
    args = parser.parse_args()

    # Get API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print(" GEMINI_API_KEY is missing. Make sure it is set in the .env file or environment variables.")
        return

    # Generate docs
    controller = DocumentGeneratorController(repo_path=args.path, api_key=api_key)
    try:
        result = controller.generate(user_input=args.query, system_prompt=SYSTEM_PROMPT, output_path=args.output)
        print(" Document generated successfully!")
        print(f" PDF saved at: {result['pdf_path']}")
        print("\n HTML + Diagram Preview:\n")
        print(result['html'])  # Optional: show preview
    except Exception as e:
        print("Error occurred:", e)

if __name__ == "__main__":
    main()