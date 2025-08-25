# Initial Project Setup

This branch establishes the initial project structure. It contains a minimal Python package under `src/`, an application entry point, and configuration files. No data import modules are included in this branch.

---

## Project Structure

```
project-root/
├── app.py
├── src/
│   ├── __init__.py
├── README.md
├── requirements.txt
├── pyproject.toml
├── uv.lock
├── .gitignore
```

> Note: The `.venv/` folder is intentionally ignored and not committed.

---

## Environment and Dependency Management (uv)

This project uses `uv` for Python project bootstrapping, virtual environments, and dependency management.

### 1) Create the project files

If starting from scratch, initialise the project:

```bash
uv init
```

### 2) Create a virtual environment

```bash
uv venv
```

### 3) Activate the virtual environment (Bash)

```bash
source .venv/Scripts/activate
```

> Use the `source` command as shown above. If you are on a POSIX-style environment where activation scripts live in `bin/`, the equivalent would be `source .venv/bin/activate`.

### 4) Install dependencies from `requirements.txt`

With the virtual environment active:

```bash
uv add -r requirements.txt
```

This will install all packages defined in `requirements.txt` into the active environment and update `pyproject.toml`/`uv.lock` accordingly.

### 5) Deactivate the virtual environment

When you are done:

```bash
deactivate
```

---

## Notes

* Keep application code inside `src/`.
* Use `app.py` as a simple entry point for local runs or quick checks.
* Dependencies should be tracked in `requirements.txt` and managed via `uv` as shown above.
