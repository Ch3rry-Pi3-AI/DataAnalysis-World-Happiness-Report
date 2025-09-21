# Data Import – World Happiness

This branch of the project is focused on **importing raw datasets** into the bronze layer.
The following dataset is imported here and will later be processed:

* World Happiness Report 2021

## Project Structure

The new modules are stored in `src/get_data/`:

```
project-root/
├── app.py
├── src/
│   ├── __init__.py
│   ├── get_data/                               🆕 (NEW)
│   │   ├── __init__.py                         🆕
│   │   └── import_happiness_data.py            🆕
└── data/           
    └── bronze/     # raw input datasets        🆕
```

* `import_happiness_data.py` → Downloads and extracts the World Happiness Report 2021 dataset.
* `app.py` → Updated to provide a single entry point for running data imports.

## How to Run

You can import the data in two different ways depending on your workflow:

### 1) Run via the app entry point (recommended)

From the project root:

```bash
python app.py
```

This will call the import script from a central location.

### 2) Run the happiness data import directly

From the project root:

```bash
python -m src.get_data.import_happiness_data
```

## Output

* World Happiness CSVs will be stored under the `data/bronze/` folder.
* The script provides clear step-by-step logging (when `verbose=True`) and finishes with a completion message.

## Notes

* This script is designed for the bronze stage of the medallion architecture.
* Data stored here is raw and may be transformed later in the silver and gold stages.
* All modules follow a consistent style with NumPy docstrings, step banners, and beginner-friendly comments.