# NexusMind Codebase Analysis and Visualization Tool

## Overview
NexusMind is a project centered around two Docker containers, `llm_proxy` and `llm_redis`. These containers are designed to act as your personal proxy to your favorite LLM, logging all inbound and outbound tokens to Redis for future use. At this time, only non-streaming interactions are supported, with plans to add a streaming option in the future. Additionally, NexusMind includes a table of contents generator that creates a JSON file, which is then used to produce a Mermaid file for visualizing the codebase structure.

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
1. **Configuration**: Configure API keys and endpoints in `llm_proxy/config.json` and `.env` files. Example files are provided.
2. **Deploy**: `cd llm_proxy`; `docker-compose up -d` && `cd llm_redis`; `docker-compose up -d`
3. **Run Analysis**: Execute `makeTOC.py` to read your codebase and generate the table of contents.


## Dependencies
- Python libraries: `requests`, `redis`, `Flask`, and others as listed in `llm_proxy/requirements.txt`.
- Docker for containerization of the proxy and Redis services.
- Access to an AI API (like xAI) for generating the table of contents.

## Visual Representation
The project structure can be visualized using the Mermaid diagram generated in `codebase_structure.mmd`. This diagram shows the relationships between scripts, functions, dependencies, and external services.

## Contributing
Contributions to NexusMind are welcome. Please feel free to fork the repository, make changes, and submit pull requests for enhancements or bug fixes.

## License
MIT

## Contact
Eventually....