# club-website

use DownGit to download individual files or folders off Github

## PHP (current)

Run with PHP's built-in server:

```
php -S 0.0.0.0:8080 -t . router.php
```

## Flask (legacy)

virtual
'''
.\myenv\Scripts\activate
'''

# windows
'''
python -m flask run
'''
# mac
'''
python app.py
'''

## Also: Recommend creating venv
'''
pip install -r requirements.txt
'''

## Admin credentials

Set the admin username and a Werkzeug password hash before starting Flask:

'''
export ADMIN_USERNAME='your-admin-username'
export ADMIN_PASSWORD_HASH='your-generated-werkzeug-hash'
'''

Generate the hash in a secure environment with `generate_password_hash` from Werkzeug. Do not commit the plaintext password or the generated hash.
