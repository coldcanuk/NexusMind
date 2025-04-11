# NexusMind Codebase Analysis and Visualization Tool

## Overview
NexusMind is a comprehensive toolset designed to help developers understand and visualize their codebase structure. It automates the process of reading a codebase, generating a detailed table of contents using AI, and creating visual diagrams with Mermaid to represent the codebase structure. Additionally, it includes a proxy service for interacting with AI APIs and logging interactions via Redis.

## Features
- **Codebase Analysis**: Reads through the entire codebase, ignoring specified directories and files (like `.venv` and `.env`), to compile content for analysis.
- **Table of Contents Generation**: Utilizes an AI API to generate a structured table of contents in JSON format, providing descriptions, functions, and dependencies for each file.
- **Visualization with Mermaid**: Converts the table of contents into a visual diagram using Mermaid, saved as `codebase_structure.mmd`, to help visualize the relationships between files and components.
- **AI API Proxy Service**: A Flask-based proxy (`llm_proxy/proxy.py`) that handles requests to an AI service, supporting both streaming and non-streaming interactions, with logging to Redis for tracking.
- **Redis Logging**: Both the main tool and proxy service log interactions to Redis, allowing for monitoring and debugging of API calls and responses.

## Project Structure
- **`makeTOC.py`**: The core script for reading the codebase, interfacing with the AI API to generate the table of contents, and saving the results.
- **`makeMermaid.py`**: Generates a Mermaid diagram from the table of contents JSON, providing a visual representation of the codebase structure.
- **`llm_proxy/`**: Contains the proxy service for AI API interactions, including configuration, Docker setup, and the main proxy application.
- **`llm_redis/`**: Configuration for the Redis service used for logging API interactions.
- **`table_of_contents.json`**: The output file containing the AI-generated table of contents for the codebase.
- **`codebase_structure.mmd`**: The Mermaid diagram file representing the visual structure of the codebase.

## Getting Started
1. **Setup Environment**: Ensure you have Python installed along with necessary dependencies. Use the `requirements.txt` in `llm_proxy/` for the proxy service.
2. **Configuration**: Configure API keys and endpoints in `llm_proxy/config.json` and `.env` files. Example files are provided.
3. **Run Analysis**: Execute `makeTOC.py` to read your codebase and generate the table of contents.
   ```bash
   python makeTOC.py
   ```
4. **Generate Visualization**: Run `makeMermaid.py` to create a Mermaid diagram from the table of contents.
   ```bash
   python makeMermaid.py
   ```
5. **Deploy Proxy Service**: Use Docker Compose in `llm_proxy/` to deploy the proxy service for AI API interactions.
   ```bash
   cd llm_proxy && docker-compose up
   ```

## Dependencies
- Python libraries: `requests`, `redis`, `Flask`, and others as listed in `llm_proxy/requirements.txt`.
- Docker for containerization of the proxy and Redis services.
- Access to an AI API (like xAI) for generating the table of contents.

## Visual Representation
The project structure can be visualized using the Mermaid diagram generated in `codebase_structure.mmd`. This diagram shows the relationships between scripts, functions, dependencies, and external services.

## Contributing
Contributions to NexusMind are welcome. Please feel free to fork the repository, make changes, and submit pull requests for enhancements or bug fixes.

## License
[Specify your license here, if applicable]

## Contact
[Provide contact information or links to project repository for further information or support]
