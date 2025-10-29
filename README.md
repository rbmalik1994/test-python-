# Python Multi-Project Workspace

This workspace is designed for developing and testing multiple Python projects.

## Structure
- `project1/` - First Python project
- `project2/` - Second Python project
- `tests/` - Shared tests for all projects
- `requirements.txt` - Shared dependencies

## Getting Started
1. Add your Python code to the respective project folders (e.g., `project1/`, `project2/`).
2. Place shared or project-specific tests in the `tests` directory.
3. List dependencies in `requirements.txt` and install them with:
	```zsh
	pip install -r requirements.txt
	```