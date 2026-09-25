from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
import os
import csv
import regular_search
import random
import image_upload
import pandas as pd
import config
from user import User
from datetime import timedelta

app = Flask(__name__)
app.config.from_object(config)  # Load all configurations from config.py
allowed_extensions=config.ALLOWED_EXTENSIONS
expected_columns_allclubs=config.expected_columns_allclubs
expected_columns_featured=config.expected_columns_featured
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)
app.config['SESSION_COOKIE_DURATION'] = timedelta(hours=24)
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(hours=24)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

admin_user_test = User.from_password_hash(
    1,
    os.environ["ADMIN_USERNAME"],
    os.environ["ADMIN_PASSWORD_HASH"],
)

@login_manager.user_loader
def load_user(user_id):
    if user_id == "1":
        return admin_user_test
    else:
        return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Check if credentials match admin user
        if username == admin_user_test.username and admin_user_test.verify_password(password):
            #login_user(admin_user_test)
            session.permanent = True
            login_user(admin_user_test, remember=True)
            return redirect(url_for('admin'))

        flash("Invalid username or password", "danger")

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

def validate_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in allowed_extensions

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    # Check if the POST request has the file part
    if 'file' not in request.files:
        flash('No file part.', 'danger')
        return redirect(url_for('admin'))

    file = request.files['file']

    # If the user does not select a file, the browser may submit an empty part
    if file.filename == '':
        flash('No selected file.', 'danger')
        return redirect(url_for('admin'))

    if file and validate_file(file.filename):
        # this is to prevent malicious stuff
        filename = secure_filename(file.filename)
        # Save the file to the upload folder
        filepath=os.path.join(app.config['UPLOAD_FOLDER_DATA'], filename)
        file.save(filepath)
        flash('File successfully uploaded!', 'success')

        action = request.args.get("action")
        if action == 'all-clubs':
            csv_check=image_upload.check_columns(filepath, expected_columns_allclubs)
            if csv_check!=True:
                flash(csv_check, 'danger')
                return redirect(url_for('admin'))
            image_upload.preprocess_file(filepath)
            ref_club_file_path = app.config['REFERENCE_CLUBS_INFO']
            image_upload.download_images(ref_club_file_path)
        elif action == 'featured-clubs':
            csv_check=image_upload.check_columns(filepath, expected_columns_featured)
            if csv_check!=True:
                flash(csv_check, 'danger')
                return redirect(url_for('admin'))
            image_upload.preprocess_file_featured(filepath)
            ref_featured_club_file_path = app.config['REFERENCE_FEATURED_CLUBS_INFO']
            image_upload.download_images_featured(ref_featured_club_file_path)
        else:
            flash('Invalid action.', 'danger')


        return redirect(url_for('admin'))
    flash('Invalid file type.', 'danger')
    return redirect(url_for('admin'))

@app.route('/delete',methods=['POST'])
@login_required
def delete_files():
    folder = app.config['UPLOAD_FOLDER_IMAGES']
    image_upload.delete_all_files(os.path.join(folder))
    flash('Files successfully deleted!', 'success')
    return redirect(url_for('admin'))

def generate_html(csv_file, clubsToDisplay=None):
    clubs = []
    total_index=0

    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        rows = []
        for index, row in enumerate(reader):
            if row['Sponsor Replied'] == "True" and row['Added to Website'] == "True":
                rows.append(row)
                total_index+=1
    rows=pd.DataFrame(rows)
    if clubsToDisplay is None:
        clubsToDisplay = list(range(len(rows)))
        indexes_to_randomize = [i for i in clubsToDisplay]
        randomized_indexes = random.sample(indexes_to_randomize, len(indexes_to_randomize))
        clubsToDisplay = randomized_indexes

    for index in clubsToDisplay:
        if 0 <= index < len(rows):
            clubs.append(rows.iloc[index])

    return clubs, len(clubs), total_index

@app.route('/')
@app.route('/index')
def index():
    return redirect(url_for('clubslist'))

@app.route('/admin')
@login_required
def admin():
    files = sorted(os.listdir(app.config['UPLOAD_FOLDER_IMAGES']))
    return render_template('admin.html', files=files)
# Route for handling the button click

@app.route('/clubslist')
def clubslist():
    ref_club_file_path = app.config['REFERENCE_CLUBS_INFO']
    clubs, total_clubs, num_clubs = generate_html(ref_club_file_path)
    return render_template('clubs.html', clubs=clubs, total_clubs=total_clubs, num_clubs=num_clubs)


@app.route('/clubslist/<user_query>')
def clubslistCustom(user_query):
    club_list = regular_search.get_contains_string(user_query).index
    ref_club_file_path = app.config['REFERENCE_CLUBS_INFO']
    clubs, total_clubs, num_clubs = generate_html(ref_club_file_path, club_list)
    return render_template('clubs.html', clubs=clubs, total_clubs=total_clubs, num_clubs=num_clubs)

@app.errorhandler(404)
def page_not_found(e):
    # Redirect to homepage or render a custom page
    return redirect(url_for('index'))

if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=8000)
    app.run(host='0.0.0.0', debug=True)
