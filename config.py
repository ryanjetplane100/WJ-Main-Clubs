# config.py
import os
import secrets

# App configs
SECRET_KEY = secrets.token_hex(32)
UPLOAD_FOLDER_IMAGES = os.path.join(os.path.dirname(__file__), 'static', 'images')
UPLOAD_FOLDER_DATA = os.path.join(os.path.dirname(__file__), 'static', 'data')
REFERENCE_CLUBS_INFO = os.path.join(UPLOAD_FOLDER_DATA, 'clubs_information.csv')
REFERENCE_FEATURED_CLUBS_INFO = os.path.join(UPLOAD_FOLDER_DATA, 'featured_clubs_information.csv')
ALLOWED_EXTENSIONS = {'csv'}

# Image configs
#base_url = "https://raw.githubusercontent.com/WJ-Machine-Learning-and-CS-Club/wjclubs_2024_fixed_image_names/main/updated_images/"
base_url ="https://raw.githubusercontent.com/WJ-Machine-Learning-and-CS-Club/club-website-alpha/main/static/images/"
extensions = ['.jpg', '.png', '.jpeg', '.webp', '.svg']
default_image=os.path.join('images', 'unknown.png')
default_img = "unknown.png"
featured_header="Featured "
expected_columns_allclubs = ["Club Name", "Sponsor email address","Purpose", "Select all the days of the week that your club meets", "When does your club meet other than lunch or after school? (If you do not please put N/A)", "Club Meeting Location", "Club Meeting Frequency", "Social Media Handles (optional)"]
expected_columns_featured = ["Club Name", "Description"]
