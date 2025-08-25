import os
import shutil
import zipfile
import kagglehub

def get_world_happiness_data(verbose: bool = False, data_folder: str = 'data/bronze'):
    """
    Download and extract the World Happiness Report 2021 dataset
    using Kagglehub, and copy CSVs into a local data directory.

    Parameters
    ----------
    verbose: bool, optional
        If True, print detailed progress messages (default: False).
    data_folder: str, optional
        Relative folder path where CSVs will be stored (default: 'data/bronze').

    Returns
    -------
    None
        This function has no return value. CSV files are saved into the target folder.

    Notes
    -----
    - Handles both directory-style and zip archive KaggleHub downloads
    - Creates the target folder if it does not exist.
    - Overwrites existing CSVs if found in the destination folder.
    """

    # Determine project and data directories
    project_dir = os.getcwd()
    data_dir = os.path.join(project_dir, data_folder)

    # Create data directory
    os.makedirs(data_dir, exist_ok=True)

    if verbose:
        print(f"\nProject directory: {project_dir}\n")
        print(f"Data directory created at: {data_dir}\n")

    # Download dataset
    archive_path = kagglehub.dataset_download(
        "ajaypalsinghlo/world-happiness-report-2021/versions/2"
    )

    if verbose:
        print(f"Downloaded archive path: {archive_path}\n")

    # Helper to extract CSVs
    def _copy_csv(source_path: str):
        
        # Extract CSV files
        if os.path.isdir(source_path):
            # Handle folder source
            for root, _, files in os.walk(source_path):
                rel = os.path.relpath(root, source_path)
                dest_dir = os.path.join(data_dir, rel)
                os.makedirs(dest_dir, exist_ok=True)

                for fname in files:
                    if fname.lower().endswith('.csv'):
                        src = os.path.join(root, fname)
                        dst = os.path.join(dest_dir, fname)
                        shutil.copy2(src, dst)

                        if verbose:
                            print(f"Copied {dst}\n")

        else:

            # Handle zip archive source
            with zipfile.ZipFile(source_path, 'r') as z:

                for member in z.namelist():
                    if member.lower().endswith('.csv'):
                        dst_path = os.path.join(data_dir, member)
                        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                        if os.path.exists(dst_path):
                            os.remove(dst_path)
                        with z.open(member) as srcf, open(dst_path, 'wb') as dstf:
                            dstf.write(srcf.read())
                        
                        if verbose:
                            print(f"Extracted {dst_path}\n")

    _copy_csv(archive_path)

    # Completion message
    print(f"✅ Success: Both multi-year and 2021 datasets saved in the 🥉 folder\n")

if __name__ == "__main__":
    get_world_happiness_data()