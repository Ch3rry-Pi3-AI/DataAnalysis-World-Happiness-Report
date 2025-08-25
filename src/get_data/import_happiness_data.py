import os
import shutil
import zipfile
import kagglehub

def get_world_happiness_data(verbose: bool = False, data_folder: str = 'data/bronze'):
    """
    Download and extract the World Happiness Report 2021 dataset using Kagglehub, 
    saving all CSV files into the project's bronze (raw) data folder.

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

    # ----------------------------------------------------------------------
    # Step 1: Determine directories
    # ----------------------------------------------------------------------

    # os.getcwd() gives the *current working directory* from which Python was launched.
    project_dir = os.getcwd()  # current working directory of the project

    # We join this with the relative 'data_folder' to produce an absolute path.
    data_dir = os.path.join(project_dir, data_folder)  # bronze layer path

    # Ensure the data directory exists (create if missing)
    os.makedirs(data_dir, exist_ok=True)

    if verbose:
        print(f"\nProject directory: {project_dir}\n")
        print(f"Data directory created at: {data_dir}\n")

    # ----------------------------------------------------------------------
    # Step 2: Download dataset archive from KaggleHub
    # ----------------------------------------------------------------------
    
    # Download the dataset using KaggleHub
    archive_path = kagglehub.dataset_download(
        "ajaypalsinghlo/world-happiness-report-2021/versions/2"
    )

    if verbose:
        print(f"Downloaded archive path: {archive_path}\n")

    # ----------------------------------------------------------------------
    # Step 3: Define helper to copy or extract CSV files
    # ----------------------------------------------------------------------
    def _copy_csv(source_path: str):
        """
        Copy CSVs from the KaggleHub download into the bronze folder.
        Handles both directory-style downloads and compressed zip archives.

        This function intentionally:
        - preserves any subfolder structure (for clarity/auditing),
        - overwrites existing CSVs (to ensure the latest download is used),
        - avoids extracting non-CSV files.
        """

        # Case A: KaggleHub provided a folder path
        if os.path.isdir(source_path):

            # Walk through all folders and files in the dataset
            for root, _, files in os.walk(source_path):

                # Keep the relative structure when copying into bronze folder
                rel = os.path.relpath(root, source_path)
                dest_dir = os.path.join(data_dir, rel)
                os.makedirs(dest_dir, exist_ok=True)

                # Walk through all files
                for fname in files:
                    if fname.lower().endswith('.csv'):

                        # Build source and desination paths
                        src = os.path.join(root, fname)
                        dst = os.path.join(dest_dir, fname)

                        # Copy the file into the bronze folder
                        shutil.copy2(src, dst)

                        if verbose:
                            print(f"Copied {dst}\n")

        # Case B: KaggleHub provided a zip archive
        else:

            # Open the ZIP file for reading
            with zipfile.ZipFile(source_path, 'r') as z:

                # Loop over every file path inside the archive
                for member in z.namelist():

                    # Only process CSV files
                    if member.lower().endswith('.csv'):

                        # Build the destination path inside the bronze folder
                        dst_path = os.path.join(data_dir, member)

                        # Make sure destination subfolders exist
                        os.makedirs(os.path.dirname(dst_path), exist_ok=True)

                        # Overwrite if file already exists
                        if os.path.exists(dst_path):
                            os.remove(dst_path)

                        # Extract: Read bytes from the ZIP entry and write them to the destination file
                        with z.open(member) as srcf, open(dst_path, 'wb') as dstf:
                            dstf.write(srcf.read())

                        if verbose:
                            print(f"Extracted {dst_path}\n")

    # ----------------------------------------------------------------------
    # Step 4: Run CSV extraction
    # ----------------------------------------------------------------------
    _copy_csv(archive_path)

    # ----------------------------------------------------------------------
    # Step 5: Completion message
    # ----------------------------------------------------------------------
    print(f"✅ Success: World Happiness datasets saved in the 🥉 bronze folder\n")


# Allow standalone execution (useful for testing/debugging)
if __name__ == "__main__":
    
    # Setting verbose=True makes the script explain itself while it runs
    get_world_happiness_data(verbose=True)