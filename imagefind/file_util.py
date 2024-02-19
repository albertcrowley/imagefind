import os
import sys
from typing import List


def find_jpeg_files(directory: str) -> List[str]:
    """
    Find all JPEG files under a given directory.
    Args:
        directory (str): The directory to search for JPEG files.
    Returns:
        List[str]: A list of file paths for JPEG files found under the directory.
    """
    jpeg_files = []  # List to store found JPEG files
    # Walk through the directory
    found = 0
    for root, _, files in os.walk(directory):
        for file in files:
            # Check if the file has a JPEG extension
            if file.lower().endswith(('.jpg', '.jpeg')):
                # If so, add the file path to the list
                jpeg_files.append(os.path.join(root, file))
                found += 1
                if (found % 100) == 0:
                    sys.stdout.write('\r')
                    sys.stdout.write('Found  ' + str(found) + ' files to scan')
                    sys.stdout.flush()
    sys.stdout.write('\r')
    sys.stdout.write('Found  ' + str(found) + ' files to scan')
    sys.stdout.flush()
    return jpeg_files


