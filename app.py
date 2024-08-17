# Developer - M. Shafraz Jiffry
# Date & Time - 17/08/2024 03.00 pm 
# User Account CRUD Service

import re
from flask import Flask, request, jsonify
import sqlite3
from sqlite3 import Error

app = Flask(__name__)

# Database connection
def create_connection():
    conn = None
    try:
        conn = sqlite3.connect('users.db')
        return conn
    except Error as e:
        print(e)
    return conn

# Initialize the database
def init_db():
    conn = create_connection()
    with conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        password TEXT NOT NULL,
                        active INTEGER NOT NULL)''')

# Create a new user with validations
@app.route('/users', methods=['POST'])
def create_user():
    conn = create_connection()
    user = request.json

    # Validation: Check if all required fields are provided
    if not user.get('username') or not user.get('password') or 'active' not in user:
        return jsonify({"error": "Username, password, and active status are required"}), 400

    # Validation: Check username length
    if len(user['username']) < 3 or len(user['username']) > 20:
        return jsonify({"error": "Username must be between 3 and 20 characters"}), 400

    # Validation: Check password strength
    if len(user['password']) < 8 or not re.search(r'[A-Za-z]', user['password']) or not re.search(r'[0-9]', user['password']) or not re.search(r'[!@#$%^&*(),.?":{}|<>]', user['password']):
        return jsonify({"error": "Password must be at least 8 characters long, contain letters, numbers, and at least one special character"}), 400

    # Validation: Check active field
    if user['active'] not in [0, 1]:
        return jsonify({"error": "Active status must be 0 (inactive) or 1 (active)"}), 400

    # Check if the username already exists
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username=?", (user['username'],))
    existing_user = cur.fetchone()

    if existing_user:
        return jsonify({"error": "Username already exists"}), 400

    # If all validations pass, insert the new user
    sql = '''INSERT INTO users (username, password, active) 
             VALUES (?, ?, ?)'''
    cur.execute(sql, (user['username'], user['password'], user['active']))
    conn.commit()
    return jsonify({"id": cur.lastrowid}), 201

# Read all users
@app.route('/users', methods=['GET'])
def get_users():
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")
    rows = cur.fetchall()
    return jsonify(rows)

# Read a single user with ID validation
@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    # Validation: Check if id is positive
    if id <= 0:
        return jsonify({"error": "Invalid user ID"}), 400

    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id=?", (id,))
    row = cur.fetchone()
    if row:
        return jsonify(row)
    return jsonify({"error": "User not found"}), 404

# Update a user with validations
@app.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    # Validation: Check if id is positive
    if id <= 0:
        return jsonify({"error": "Invalid user ID"}), 400

    conn = create_connection()
    user = request.json

    # Validation: Check if user exists
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id=?", (id,))
    existing_user = cur.fetchone()
    if not existing_user:
        return jsonify({"error": "User not found"}), 404

    # Validation: At least one field to update must be provided
    if not user.get('username') and not user.get('password') and 'active' not in user:
        return jsonify({"error": "At least one field (username, password, active) must be provided to update"}), 400

    # Validation: Check username if provided
    if user.get('username'):
        if len(user['username']) < 3 or len(user['username']) > 20:
            return jsonify({"error": "Username must be between 3 and 20 characters"}), 400

        cur.execute("SELECT * FROM users WHERE username=? AND id<>?", (user['username'], id))
        duplicate_user = cur.fetchone()
        if duplicate_user:
            return jsonify({"error": "Username already exists"}), 400

    # Validation: Check password if provided
    if user.get('password'):
        if len(user['password']) < 8 or not re.search(r'[A-Za-z]', user['password']) or not re.search(r'[0-9]', user['password']) or not re.search(r'[!@#$%^&*(),.?":{}|<>]', user['password']):
            return jsonify({"error": "Password must be at least 8 characters long, contain letters, numbers, and at least one special character"}), 400

    # Validation: Check active if provided
    if 'active' in user and user['active'] not in [0, 1]:
        return jsonify({"error": "Active status must be 0 (inactive) or 1 (active)"}), 400

    # Update the user if all validations pass
    sql = '''UPDATE users 
             SET username=?, password=?, active=? 
             WHERE id=?'''
    cur.execute(sql, (
        user.get('username', existing_user[1]),  # default to current username if not provided
        user.get('password', existing_user[2]),  # default to current password if not provided
        user.get('active', existing_user[3]),    # default to current active status if not provided
        id
    ))
    conn.commit()
    return jsonify({"message": "User updated successfully"})

# Delete a user with ID validation
@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    # Validation: Check if id is positive
    if id <= 0:
        return jsonify({"error": "Invalid user ID"}), 400

    conn = create_connection()
    sql = 'DELETE FROM users WHERE id=?'
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id=?", (id,))
    existing_user = cur.fetchone()
    if not existing_user:
        return jsonify({"error": "User not found"}), 404

    cur.execute(sql, (id,))
    conn.commit()
    return jsonify({"message": "User deleted successfully"})

# Main function to run the app
if __name__ == '__main__':
    init_db()  # Initialize the database
    app.run(debug=True)
