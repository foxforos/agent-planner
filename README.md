# Agent Planner

A CLI tool for structuring and managing projects, with built-in validation and automated diagnostics.
Plans are generated using LLM integration (OpenAI API).



## Overview

Agent Planner is a command-line application designed to help organize projects, generate structured plans, and maintain consistency between memory and filesystem.

It includes validation tools, automated fixes, logging, and a modular architecture built for extensibility.



## Features

- Complete project lifecycle management (create, rename, delete, view, open, tagging)
- Automatic project naming and validation
- Structured document generation
- Persistent memory system (`memory.json`)
- Diagnostic tool (`doctor`) to detect issues:
  - missing files
  - orphan files
  - invalid records
  - duplicate names
- Safe fix system (`doctor_fix`) with confirmation and backup
- Logging system for traceability
- Full test suite with pytest
- Docker support



## Installation

Clone the repository:

```bash
git clone <your-repo-url>
cd Agent_Planner_v1
```

(Optional) Create virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```




## Usage

Run commands via CLI:

```bash
agent-planner "<command>"
```

### Examples

```bash
# Create a project
agent-planner "crea progetto: my_project"

# Show all projects
agent-planner "mostra progetti"

# Rename a project
agent-planner "modifica progetto: old_name: new_name"

# Delete a project (dry-run)
agent-planner "elimina progetto: my_project --dry-run"

# Search projects
agent-planner "cerca: keyword"

# Add tags
agent-planner "aggiungi tag: my_project : tag1, tag2"

# Run diagnostics
agent-planner "doctor"

# Fix issues
agent-planner "doctor_fix"
```

For a full list of available commands:

```bash
agent-planner help
```



## Example

```bash
python agent.py "crea progetto: docker_integration"
```

This will:
- create a new project entry in `memory.json`
- generate a corresponding document in `/docs`



## Project Structure

Agent_Planner_v1/
│
├── agent.py
├── planner.py
├── config.py
├── models.py
├── doc_builder.py
├── logger_config.py
│
├── memory.json
├── docs/
│   └── _orphaned/
├── backups/
├── logs/
├── templates/
│
├── tests/
├── Dockerfile
├── run.ps1
└── README_DOCKER.md



## Testing

Run tests locally:

```bash
pytest
```

Run tests in Docker:

```bash
docker run --rm -v ${PWD}:/app --entrypoint pytest agent-planner
```



## Docker

The project can be executed in a containerized environment.

See: `README_DOCKER.md`



## Notes

- CLI commands with spaces must be wrapped in quotes
- Interactive commands require a terminal (Docker uses `-it`)



## Future Improvements

- More flexible CLI parsing
- Extended template system
- Improved UX for commands


