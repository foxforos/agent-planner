\# Agent Planner — Docker Usage



\## Overview



This project can be executed inside a Docker container, allowing it to run in an isolated and portable environment without relying on the local Python setup.



\---



\## Build the Image



From the project root, run:



```bash

docker build -t agent-planner .

```



\---



\## Run the Application



\### Option 1 — Direct Docker Command



```bash

docker run -v ${PWD}:/app agent-planner "crea progetto: nome\_progetto"

```



\### Option 2 — Using PowerShell Script (Recommended)



```powershell

.\\run.ps1 "crea progetto: nome\_progetto"

```



\---



\## Data Persistence



By default, Docker containers are stateless.



This project uses a volume to persist data:



```bash

\-v ${PWD}:/app

```



This ensures that:



\* `memory.json` is updated on the host machine

\* `docs/` files are created locally

\* logs and backups are preserved



\---



\## How It Works



\* Docker builds an image containing Python and all dependencies

\* The container executes `agent.py`

\* The project directory is mounted inside the container at `/app`



\---


## Running Tests in Docker

The project test suite can also be executed inside Docker.

Use:

```powershell
docker run --rm -v ${PWD}:/app --entrypoint pytest agent-planner



\## Notes



\* Docker must be running before executing any command

\* The PowerShell script (`run.ps1`) is a wrapper around the Docker command for convenience

\* Without the volume (`-v`), all generated data would be lost after execution



\---



\## Example



```powershell

.\\run.ps1 "crea progetto: esempio"

```



This will:



\* create a new project

\* update `memory.json`

\* generate files inside `docs/`



\---



