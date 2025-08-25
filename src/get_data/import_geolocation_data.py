import pandas as pd
from pathlib import Path


def fetch_geolocation_data(
        cache_folder: Path = Path("data/bronze"),
        filename: str = "geolocation.csv",
        verbose: bool = False
) -> Path:
    """
    Download and cache geolocation data for countries, saving a filtered CSV
    into the project's bronze (raw) data folder.

    Parameters
    ----------
    cache_folder : pathlib.Path, optional
        Path to the folder where the geolocation data should be stored
        (default: 'data/bronze').
    filename : str, optional
        Name of the CSV file to save locally (default: 'geolocation.csv').

    Returns
    -------
    pathlib.Path
        Path to the cached or newly downloaded CSV file.

    Notes
    -----
    - If the file already exists in the cache folder, it is returned directly.
    - The downloaded dataset is filtered to include only:
      country code, country name, latitude, and longitude.
    """

    # ----------------------------------------------------------------------
    # Step 1: Ensure cache directory exists
    # ----------------------------------------------------------------------

    cache_folder = Path(cache_folder)
    cache_folder.mkdir(parents=True, exist_ok=True)

    # Compute the full output path for the CSV file
    output_path = cache_folder / filename

    # If the file already exists, return it immediately
    if output_path.exists():
        if verbose:
            print(f"✅ Success: Using cached geolocation data in the 🥉 bronze folder\n")
        return output_path

    if verbose:
        print(f"Cache folder created/confirmed at: {cache_folder}\n")

    # ----------------------------------------------------------------------
    # Step 2: Download the countries CSV
    # ----------------------------------------------------------------------

    url = (
        "https://raw.githubusercontent.com/google/dspl/master/"
        "samples/google/canonical/countries.csv"
    )

    try:
        # Read the remote CSV directly into a Pandas DataFrame
        df = pd.read_csv(url)
        if verbose:
            print("Stored CSV as Pandas DataFrame:")
            print(df.head(), "\n")  # preview the first few rows
    except Exception as e:
        # Wrap error in clearer RuntimeError for debugging
        raise RuntimeError(f"Failed to download geolocation data: {e}")

    # ----------------------------------------------------------------------
    # Step 3: Clean and filter the DataFrame
    # ----------------------------------------------------------------------

    # Rename the 'name' column to 'country_name' for clarity
    df = df.rename(columns={"name": "country_name"})

    # Keep only the relevant fields for merging later
    df = df[["country", "country_name", "latitude", "longitude"]]
    if verbose:
        print("Filtered to relevant fields\n")

    # ----------------------------------------------------------------------
    # Step 4: Save cleaned DataFrame to bronze folder
    # ----------------------------------------------------------------------

    df.to_csv(output_path, index=False)
    if verbose:
        print(f"Geolocation data saved to {output_path}\n")

    # ----------------------------------------------------------------------
    # Step 5: Completion message
    # ----------------------------------------------------------------------

    print("✅ Success: Geolocation dataset saved in the 🥉 bronze folder\n")

    # Return the path to the saved file
    return output_path


# Allow standalone execution (useful for testing/debugging)
if __name__ == "__main__":

    # Setting verbose=True makes the script explain itself while it runs
    fetch_geolocation_data()
