def generate_prompt(files, question):
    prompt = ""
    for file in files:
        prompt += f"Filename: {file['filename']}\nCode:\n{file['content']}\n\n"
    prompt += f"---\n{question}"
    return prompt