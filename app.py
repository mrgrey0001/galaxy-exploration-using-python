from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import hashlib

app = Flask(__name__)

# Hashing function for passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to sign up a user
def sign_up_user(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    hashed_password = hash_password(password)
    
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# Function to sign in a user
def sign_in_user(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    hashed_password = hash_password(password)

    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_password))
    user = cursor.fetchone()

    conn.close()
    return user is not None

# Home page (redirects to login)
@app.route('/')
def home():
    return render_template('home.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if sign_in_user(username, password):
            return redirect(url_for('dashboard'))  # Redirect to dashboard after login
        else:
            return "Invalid username or password"
    
    return render_template('login.html')

# Sign-Up route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            return "Passwords do not match."

        if sign_up_user(username, password):
            return redirect(url_for('login'))
        else:
            return "Username already exists. Please try a different one."

    return render_template('signup.html')

# Dashboard route to show galaxy names
@app.route('/dashboard')
def dashboard():
    galaxies = [
        'STARS', 'PLANETS', 'MILKYWAY', 'SOLAR SYSTEM', 'BLACKHOLE', 
        'GALAXY'
    ]
    return render_template('dashboard.html', galaxies=galaxies)

@app.route('/galaxy/<galaxy_name>')
def galaxy_detail(galaxy_name):
    try:
        # Render the specific galaxy's HTML file
        return render_template(f'galaxies/{galaxy_name}.html', galaxy_name=galaxy_name)
    except:
        return "Galaxy not found", 404
if __name__ == '__main__':
    # Create database if it doesn't exist
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL
                    )''')
    conn.close()
    
    app.run(debug=True)
