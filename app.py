import importlib.metadata

first_commit = "Project Structure Creation Stage\n"

# Packages to check
packages = [
    # Core data analysis + numerical computing
    "pandas",
    "numpy",

    # Visalisation / App
    "plotly",
    "dash",
    "dash-bootstrap-components",

    # Geo helpers
    "pycountry",

    # Data download
    "kagglehub",

    #Utilities
    "python-dotenv",
    "requests",
]

if __name__ == "__main__":
    print(first_commit)
    print("[ Package Versions]")

    for pkg in packages:
        try:
            version = importlib.metadata.version(pkg)
            print(f"{pkg:25} {version}")
        except:
            version = importlib.metadata.version(pkg)
            print(f"{pkg:25} not installed")