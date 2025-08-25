# Data Import – World Happiness & Geolocation

This branch of the project is focused on **importing raw datasets** into the bronze layer.
The following two datasets are imported here and will later be merged during processing:

* World Happiness Report 2021
* Geolocation Data (country codes, names, latitude, longitude)



## Project Structure

The new modules are stored in `src/get_data/`:

```
project-root/
├── app.py
├── src/
│   ├── __init__.py
│   ├── get_data/
│   │   ├── __init__.py
│   │   ├── import_happiness_data.py
│   │   └── import_geolocation_data.py
└── data/           # created at runtime
    └── bronze/
```

* `import_happiness_data.py` → Downloads and extracts the World Happiness Report 2021 dataset.
* `import_geolocation_data.py` → Downloads and caches the geolocation dataset.
* `app.py` → Updated to provide a single entry point for running data imports.



## How to Run

You can import the data in three different ways depending on your workflow:

### 1) Run via the app entry point (recommended)

From the project root:

```bash
python app.py
```

This will call both import scripts from a central location.



### 2) Run the happiness data import directly

From the project root:

```bash
python -m src.get_data.import_happiness_data
```



### 3) Run the geolocation data import directly

From the project root:

```bash
python -m src.get_data.import_geolocation_data
```



## Output

* World Happiness CSVs and Geolocation CSV will be stored under the `data/bronze/` folder.
* Each script provides clear step-by-step logging (when `verbose=True`) and finishes with a completion message.



## Notes

* These scripts are designed for the bronze stage of the medallion architecture.
* Data stored here is raw and may be transformed later in the silver and gold stages.
* All modules follow a consistent style with NumPy docstrings, step banners, and beginner-friendly comments.
