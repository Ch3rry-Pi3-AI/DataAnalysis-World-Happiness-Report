import os
import shutil
import zipfile
import kagglehub

def get_world_happiness_data():

    # Determine project and data directories
    project_dir = os.getcwd()
    data_dir = os.path.join(project_dir, 'data/bronze')

    # Create data directory
    os.makedirs(data_dir, exist_ok=True)

    # Download dataset
    archive_path = kagglehub.dataset_download(
        "ajaypalsinghlo/world-happiness-report-2021/versions/2"
    )

    # Helper to extract CSVs
    def _copy_csv(source_path: str):
        
        if os.path.isdir(source_path):
            
            for root, _, files in os.walk(source_path):
                rel = os.path.relpath(root, source_path)
                dest_dir = os.path.join(data_dir, rel)
                os.makedirs(dest_dir, exist_ok=True)

                for fname in files:

                    if fname.lower().endswith('.csv'):
                        src = os.path.join(root, fname)
                        dst = os.path.join(dest_dir, fname)
                        shutil.copy2(src, dst)

    _copy_csv(archive_path)

if __name__ == "__main__":
    print("OK")
    get_world_happiness_data()