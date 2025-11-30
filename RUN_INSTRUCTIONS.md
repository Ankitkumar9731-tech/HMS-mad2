# How to Run the Hospital Management System

## Prerequisites

- Python 3.7 or higher installed on your system
- pip (Python package installer)

## Step 1: Install Dependencies

Open a terminal/command prompt in the project directory and run:

```bash
pip install -r requirements.txt
```

This will install:

- Flask (web framework)
- Flask-SQLAlchemy (database ORM)
- Werkzeug (password hashing and utilities)

## Step 2: Run the Application

Simply run:

```bash
python app.py
```

Or on some systems:

```bash
python3 app.py
```

## Step 3: Access the Application

Once the server starts, you should see output like:

```
 * Running on http://127.0.0.1:5000
 * Running on http://localhost:5000
```

Open your web browser and navigate to:

```
http://localhost:5000
```

or

```
http://127.0.0.1:5000
```

## Step 4: Login

### Default Admin Credentials:

- **Username:** `admin`
- **Password:** `admin123`

**Note:** The admin user is automatically created when you first run the application.

### For Testing:

1. **As Admin:** Login with the credentials above
2. **As Doctor:** Admin must create doctor accounts first
3. **As Patient:** Click "Register" to create a new patient account

## Troubleshooting

### Port Already in Use

If you see an error about port 5000 being in use:

- Close any other Flask applications running
- Or modify `app.py` to use a different port:
  ```python
  app.run(debug=True, port=5001)
  ```

### Module Not Found Errors

Make sure all dependencies are installed:

```bash
pip install --upgrade -r requirements.txt
```

### Database Issues

If you encounter database errors:

- Delete `hospital.db` file (if it exists)
- Restart the application - it will create a fresh database

### Import Errors

Make sure you're running from the project root directory:

```bash
cd "C:\Users\mk034\OneDrive\Documents\Desktop\HMS mad1"
python app.py
```

## Development Mode

The application runs in debug mode by default, which means:

- Auto-reloads when you make code changes
- Shows detailed error messages
- Not suitable for production

## Stopping the Server

Press `Ctrl + C` in the terminal to stop the server.
