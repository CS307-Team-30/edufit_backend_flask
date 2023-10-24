edufit_backend_flask is a revised version of the backend as the team had troubles with express.js.
This version is intended for use in the final product.

Notable files:

app.py
- Contains main functionality of the backend.

config.py
- Loads environmental variables and sets miscellaneous properties for app.py.

models.py
- Handles the structure of the database, including objects and classes.

requirements.txt
- List of libraries and imports to be included.
- Use command "pip install -r .\requirements.txt" to download all items in the list in one go.

.env
- Handles environmental variables and constants.

instance/db.sqlite
- Holds the database.
- If the file does not exist, it will be created upon program run.
- If the file does exist, the program will load it. (Data is saved when server is shut off.)
- Delete db.sqlite to reset the database.