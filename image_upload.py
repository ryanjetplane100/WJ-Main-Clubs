import os
import requests
import pandas as pd
import shutil
import re
import config

local_image_folder = config.UPLOAD_FOLDER_IMAGES
local_data_folder = config.UPLOAD_FOLDER_DATA
ref_club_file_path = config.REFERENCE_CLUBS_INFO
ref_featured_club_file_path = config.REFERENCE_FEATURED_CLUBS_INFO
base_url = config.base_url
extensions = config.extensions
default_image = config.default_image
default_img = config.default_img
featured_header = config.featured_header

# Function to check if the file exists locally
def check_local_file(club_name):
    print("club_name: ", club_name)
    club_name=re.sub(r'[^A-Za-z0-9\s]', '', club_name)
    club_name = club_name.strip()
    club_name_underscored = club_name.replace(" ", "_")
    # SOmething to remove special characters
    print("Passing last fail point?")
    for ext in extensions:
        local_path = os.path.join(local_image_folder, f"{club_name_underscored}{ext}")
        if os.path.exists(local_path):
            return os.path.join("images", f"{club_name_underscored}{ext}")
    return None

def check_github_file(club_name):
    club_name=re.sub(r'[^A-Za-z0-9\s]', '', club_name)
    club_name = club_name.strip()
    club_name_underscored = club_name.replace(" ", "_")

    # Iterate over extensions
    for ext in extensions:
        url = f"{base_url}{club_name_underscored}{ext}"
        print("Checking: " + url)

        # First, check if the file exists
        response = requests.head(url)
        if response.status_code == 200:
            # If file exists, attempt to download it
            response = requests.get(url)
            directory = local_image_folder  # Change this to your target directory

            # Ensure the directory exists
            if not os.path.exists(directory):
                os.makedirs(directory)

            filename = os.path.join(directory, club_name_underscored + ext)

            # Save the content to a file if request is successful
            if response.status_code == 200:
                with open(filename, 'wb') as file:
                    file.write(response.content)
                print(f"File saved to {filename}")
                return os.path.join("images", f"{club_name_underscored}{ext}")  # Return the file path

            else:
                print(f"Failed to download file. Status code: {response.status_code}")

    # Return None if no file found for any extension
    return None

def getDefaultFile():
    if not (os.path.exists(f'{local_image_folder}{default_img}')):
        default_url = f"{base_url}{default_img}"
        response = requests.head(default_url)
        if response.status_code == 200:
            # If file exists, attempt to download it
            response = requests.get(default_url)  # Use the correct URL here
            directory = local_image_folder  # Change this to your target directory

            # Ensure the directory exists
            if not os.path.exists(directory):
                os.makedirs(directory)

            filename = os.path.join(directory, default_img)

            # Save the content to a file if request is successful
            if response.status_code == 200:
                with open(filename, 'wb') as file:
                    file.write(response.content)
                print(f"File saved to {filename}")
                return f"{default_img}"  # Return the file path

            else:
                print(f"Failed to download file. Status code: {response.status_code}")

# Function to find image or return default
def find_image(club_name):
    # Check local first
    local_file = check_local_file(club_name)
    if local_file:
        return local_file

    # If not found locally, check GitHub
    github_file = check_github_file(club_name)
    if github_file:
        return github_file

    if not (os.path.exists(default_image)):
        getDefaultFile()
    # Fallback to default image
    return default_image

def find_image_featured(club_name):
    club_name=featured_header+club_name
    print("LOOK HERE:"+club_name)
    # Check GitHub bc prob small amount of files
    github_file = check_github_file(club_name)
    if github_file:
        return github_file

    if not (os.path.exists(default_image)):
        getDefaultFile()
    # Fallback to default image
    return default_image

def download_images(input_file_path):
    # Load your CSV and apply the function to find images
    df = pd.read_csv(input_file_path)
    df=df[df['Club Name'].notna()]
    df['Image Path'] = df['Club Name'].apply(find_image)

    # Save the updated CSV
    df.to_csv(ref_club_file_path, index=False)

    print("Uploading Process Complete")

# Sample csv https://docs.google.com/spreadsheets/d/1O1HgusQAGpD4NWDSuLeK833E8LxUjmtTyqkWX23vshQ/edit?gid=0#gid=0
def download_images_featured(input_file_path):
    # Load your CSV and apply the function to find images
    df = pd.read_csv(input_file_path)
    df=df[df['Club Name'].notna()]
    df['Image Path'] = df['Club Name'].apply(find_image_featured)#find_image edit this function to  work for other stuff. )

    # Save the updated CSV
    df.to_csv(ref_featured_club_file_path, index=False)

    print("Uploading Carousel Pictures Process Complete")

def preprocess_file(new_file_path):
    df = pd.read_csv(new_file_path)
    df.to_csv(ref_club_file_path, index=False)
    os.remove(new_file_path)

def preprocess_file_featured(new_file_path):
    df = pd.read_csv(new_file_path)
    df.to_csv(ref_featured_club_file_path, index=False)
    os.remove(new_file_path)


def delete_all_files(directory):
    # Check if the directory exists
    if os.path.exists(directory):
        # Iterate over all the files and directories
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            try:
                # Remove files or directories
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)  # Delete file or symlink
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # Delete directory
            except Exception as e:
                return f"Failed to delete {file_path}. Reason: {e}", 500

    return "All files deleted successfully", 200

# Check File Validity
def check_columns(file_path, expected_columns):
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        return f"File '{file_path}' not found."
    except pd.errors.EmptyDataError:
        return "The file is empty."
    except pd.errors.ParserError:
        return "Error parsing file. Please check the file format."

    missing_columns = [col for col in expected_columns if col not in df.columns]

    if missing_columns:
        return f"Missing columns: {', '.join(missing_columns)}"
    else:
        return True