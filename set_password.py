"""Set (or reset) the admin password. Run on the server:  venv/bin/python set_password.py
The password is typed here, never stored in plain text: only its hash goes into the database."""
import getpass
import os
import sqlite3

os.environ.setdefault("PRODUCTION", "1")  # never fall back to the local default password while setting a real one

from werkzeug.security import generate_password_hash

import app  # creates the database on a first run

while True:
    pw = getpass.getpass("New admin password (8+ characters): ")
    if len(pw) < 8:
        print("Too short, try again.")
    elif pw != getpass.getpass("Type it again: "):
        print("The two did not match, try again.")
    else:
        break
con = sqlite3.connect(app.DB_PATH)
con.execute("INSERT OR REPLACE INTO settings(key,value) VALUES('admin_hash',?)", (generate_password_hash(pw),))
con.commit()
con.close()
print("Saved. Sign in at /admin.")
