import os
import json
import requests
import redis
import time
import shutil

# Set up Redis connection
redis_client = redis.Redis(host='athena.local', port=6379, db=0)

# Load configuration from llm_proxy/config.json
with open('llm_proxy/config.json', 'r') as config_file:
    config = json.load(config_file)
# Load AI_API_KEY from llm_proxy/.env
with open('llm_proxy/.env', 'r') as envfile:
    for line in envfile:
        if line.startswith('AI_API_KEY='):
            os.environ['AI_API_KEY'] = line.split('=')[1].strip()
            break
def log_to_redis(request_data, response_text):
    """Log request and response data to Redis."""
    query = request_data["messages"][-1]["content"]
    timestamp = int(time.time())
    redis_client.lpush("outbound_tokens", f"{timestamp}: {query}")
    if response_text:
        redis_client.lpush("inbound_tokens", f"{timestamp}: {response_text}")

def read_codebase():
    """Read the entire codebase, ignoring .env files and .venv directory."""
    codebase_content = []
    for root, dirs, files in os.walk('.'):
        # Skip .venv directory
        if '.venv' in dirs:
            dirs.remove('.venv')
        for file in files:
            # Ignore .env files
            if file.endswith('.env'):
                continue
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    codebase_content.append(f"File: {file_path}\n{content}\n{'='*50}")
            except Exception as e:
                print(f"Error reading file {file_path}: {e}")
    return '\n'.join(codebase_content)

def dump_codebase_to_file(content):
    """Dump the codebase content to codebase.txt."""
    with open('codebase.txt', 'w', encoding='utf-8') as f:
        f.write(content)

def generate_table_of_contents(codebase_content):
    """Send a request to the LLM to generate the table of contents."""
    url = config['url']
    headers = {
        "Authorization": f"Bearer {os.environ['AI_API_KEY']}",
        "Content-Type": config['content_type']
    }
    system_prompt = """
      You are an AI specialist tasked with analyzing a text dump of a codebase and generating a detailed table of contents in JSON format. The output should follow this structure:
        {
        "project": "<inferred project name>",
        "description": "<inferred project description>",
        "files": {
            "<file_path>": {
            "description": "<brief description of the file>",
            "functions": {
                "<function_name>": {
                "purpose": "<what the function does>",
                "dependencies": ["<list of modules, functions, or services it depends on>"],
                "location": "Lines <start_line>-<end_line>"
                },
                ...
            },
            "classes": {
                "<class_name>": {
                "purpose": "<what the class does>",
                "dependencies": ["<list of modules, functions, or services it depends on>"],
                "location": "Lines <start_line>-<end_line>"
                },
                ...
            } or "none": "No classes defined in this file."
            },
            ...
        },
        "dependencies": {
            "external_libraries": ["<list of unique external libraries used>"],
            "environment": ["<list of environment variables required>"],
            "network": ["<list of network dependencies, e.g., APIs or services>"],
            "tools": ["<list of tools used, e.g., Docker>"]
        }
        }

        Instructions:
        - **Project Information:**
        - Infer the "project" name and "description" from the codebase content (e.g., from a main script, README, or overall functionality). If unclear, use a generic name and description like "Codebase Analysis Project" and "A project for analyzing code structure."
        
        - **Files Section:**
        - Identify all files in the codebase and use their relative paths (e.g., "./makeTOC.py") as keys, sorted alphabetically.
        - For each file:
            - Provide a "description" summarizing its purpose or content.
            - Under "functions," list all defined functions, sorted alphabetically by name. For each function:
            - "purpose": A concise explanation of its role.
            - "dependencies": List imported modules, called functions, or external services it relies on.
            - "location": Line numbers where the function is defined (e.g., "Lines 19-25").
            - Under "classes," list all defined classes with the same details as functions (purpose, dependencies, location). If no classes exist, include "none": "No classes defined in this file."

        - **Dependencies Section:**
        - Aggregate dependencies across the codebase:
            - "external_libraries": Unique external libraries or modules imported (e.g., "Flask", "requests").
            - "environment": Environment variables referenced (e.g., "AI_API_KEY from .env").
            - "network": External services or APIs called (e.g., "llm_network").
            - "tools": Tools implied or mentioned (e.g., "Docker" if Dockerfiles are present).

        - **Assumptions and Guidance:**
        - Assume the text dump includes markers (e.g., "--- ./file_path ---") to separate files, enabling file boundary and line number identification.
        - For non-code files (e.g., config.json, Dockerfile), adapt the structure: omit "functions" and "classes" if inapplicable, and use alternative fields like "settings" or "instructions" as needed.

        Ensure the JSON is well-formed, with all required fields populated based on the codebase analysis.
    """
    request_data = {
        "model": "grok-3-beta",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Generate a table of contents for this codebase:\n{codebase_content}"}
        ],
        "temperature": 0
    }
    log_to_redis(request_data, None)
    response = requests.post(url, headers=headers, json=request_data, stream=False)
    if response.status_code != 200:
        error_msg = f"Error: {response.status_code} - {response.text}"
        print(error_msg)
        log_to_redis(request_data, None)
        return None
    response_data = response.json()
    try:
        response_text = response_data["choices"][0]["message"]["content"]
        log_to_redis(request_data, response_text)
        return response_text
    except (KeyError, IndexError):
        print("No response content from LLM")
        log_to_redis(request_data, None)
        return None

def save_table_of_contents(content):
    """Save the table of contents to table_of_contents.json, creating a backup if it exists."""
    if os.path.exists('table_of_contents.json'):
        shutil.copy2('table_of_contents.json', 'toc_backup.json')
    with open('table_of_contents.json', 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    """Main function to execute the table of contents generation."""
    print("Reading codebase...")
    codebase_content = read_codebase()
    print("Dumping codebase to file...")
    dump_codebase_to_file(codebase_content)
    print("Generating table of contents...")
    toc_content = generate_table_of_contents(codebase_content)
    if toc_content:
        print("Saving table of contents...")
        save_table_of_contents(toc_content)
        print("Table of contents generated and saved successfully.")
    else:
        print("Failed to generate table of contents.")
    # Delete codebase.txt
    print("Deleting codebase.txt...")
    os.remove('codebase.txt')
    # Run makeMermaid.py 
    print("Running makeMermaid.py...")
    os.system('python makeMermaid.py')
    print("makeMermaid.py completed.")
if __name__ == "__main__":
    main() 