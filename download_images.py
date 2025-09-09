import os
import requests
from tqdm import tqdm

# The base URL where these specific NIH images are publicly hosted on a GitHub repository
BASE_URL = "https://raw.githubusercontent.com/ChexNet/ChexNet/master/images/"

# The specific images you identified
IMAGE_FILENAMES = [
    # Pneumonia Cases
    "00000061_015.png",
    "00000144_001.png",
    "00000165_001.png",
    # Edema Cases
    "00000459_042.png",
    "00000459_043.png",
    "00000459_044.png",
]

# The directory where we will save the images
TARGET_DIR = os.path.join("static", "images")

def download_images():
    """
    Downloads the specified NIH chest x-ray images into the static/images folder.
    """
    print(f"--- Starting Image Download ---")
    
    # Create the target directory if it doesn't exist
    os.makedirs(TARGET_DIR, exist_ok=True)
    print(f"Ensured directory exists: {TARGET_DIR}")

    for filename in IMAGE_FILENAMES:
        file_path = os.path.join(TARGET_DIR, filename)
        
        # Check if the file already exists to avoid re-downloading
        if os.path.exists(file_path):
            print(f"Skipping {filename} (already exists).")
            continue

        # Construct the full URL for the image
        url = BASE_URL + filename
        
        try:
            print(f"Downloading {filename}...")
            response = requests.get(url, stream=True)
            response.raise_for_status() # Raise an exception for bad status codes

            # Get the total file size for the progress bar
            total_size = int(response.headers.get('content-length', 0))
            
            # Write the image to a file with a progress bar
            with open(file_path, 'wb') as f, tqdm(
                desc=filename,
                total=total_size,
                unit='iB',
                unit_scale=True,
                unit_divisor=1024,
            ) as bar:
                for data in response.iter_content(chunk_size=1024):
                    size = f.write(data)
                    bar.update(size)

            print(f"Successfully downloaded {filename}")

        except requests.RequestException as e:
            print(f"ERROR: Failed to download {filename}. Reason: {e}")

if __name__ == "__main__":
    download_images()
    print("\n--- Download Complete ---")
    print(f"Please verify the images are in your '{TARGET_DIR}' folder.")