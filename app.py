from flask import Flask, request, redirect, render_template_string
import sys
import os

# Fix import path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from core import PesapalDB

app = Flask(__name__)
db = PesapalDB()

# Ensure table exists
if 'users' not in db.tables:
    db.execute("CREATE TABLE users (id int PK, name text, role text)")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pesapal Challenge Demo</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; max-width: 800px; margin: 2rem auto; padding: 0 1rem; color: #333; }
        h1 { border-bottom: 2px solid #eee; padding-bottom: 10px; }
        table { width: 100%; border-collapse: collapse; margin-top: 2rem; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        th, td { text-align: left; padding: 12px; border-bottom: 1px solid #ddd; }
        th { background-color: #f8f9fa; }
        form { background: #f8f9fa; padding: 1.5rem; border-radius: 8px; border: 1px solid #ddd; }
        input, select { padding: 8px; margin-right: 10px; border: 1px solid #ccc; border-radius: 4px; }
        button { padding: 8px 16px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #0056b3; }
        .action-link { margin-right: 10px; text-decoration: none; font-weight: bold; }
        .edit { color: #28a745; }
        .delete { color: #dc3545; }
    </style>
</head>
<body>
    <h1>PesapalDB Manager</h1>
    
    <form action="/add" method="POST">
        <h3>Add New Developer</h3>
        <input type="text" name="id" placeholder="ID (e.g. 1)" required>
        <input type="text" name="name" placeholder="Name" required>
        <select name="role">
            <option value="Frontend">Frontend</option>
            <option value="Backend">Backend</option>
            <option value="DevOps">DevOps</option>
        </select>
        <button type="submit">Insert Record</button>
    </form>

    <h2>Current Staff</h2>
    <table>
        <thead>
            <tr><th>ID</th><th>Name</th><th>Role</th><th>Actions</th></tr>
        </thead>
        <tbody>
            {% for row in rows %}
            <tr>
                <td>{{ row.id }}</td>
                <td>{{ row.name }}</td>
                <td>{{ row.role }}</td>
                <td>
                    <a href="/edit/{{ row.id }}" class="action-link edit">Edit</a>
                    <a href="/delete/{{ row.id }}" class="action-link delete">Delete</a>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""

EDIT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><title>Edit User</title>
<style>
    body { font-family: sans-serif; max-width: 500px; margin: 2rem auto; padding: 1rem; }
    form { background: #f9f9f9; padding: 2rem; border-radius: 5px; border: 1px solid #ddd; }
    input, select { width: 100%; padding: 8px; margin-bottom: 10px; box-sizing: border-box; }
    button { background: #28a745; color: white; padding: 10px; width: 100%; border: none; cursor: pointer; }
</style>
</head>
<body>
    <h2>Edit User (ID: {{ id }})</h2>
    <form action="/update_exec" method="POST">
        <input type="hidden" name="id" value="{{ id }}">
        <label>Update Name:</label>
        <input type="text" name="name" placeholder="New Name">
        <label>Update Role:</label>
        <select name="role">
            <option value="Frontend">Frontend</option>
            <option value="Backend">Backend</option>
            <option value="DevOps">DevOps</option>
        </select>
        <button type="submit">Update User</button>
    </form>
    <p><a href="/">Cancel</a></p>
</body>
</html>
"""

@app.route('/')
def index():
    data = db.execute("SELECT * FROM users")
    if isinstance(data, str): data = []
    # Sort data by ID just for looks
    data = sorted(data, key=lambda x: int(x.get('id', 0)))
    return render_template_string(HTML_TEMPLATE, rows=data)

@app.route('/add', methods=['POST'])
def add_user():
    id = request.form.get('id')
    name = request.form.get('name')
    role = request.form.get('role')
    db.execute(f"INSERT INTO users VALUES ({id}, '{name}', '{role}')")
    return redirect('/')

@app.route('/delete/<id>')
def delete_user(id):
    db.execute(f"DELETE FROM users WHERE id={id}")
    return redirect('/')

@app.route('/edit/<id>')
def edit_user(id):
    return render_template_string(EDIT_TEMPLATE, id=id)

@app.route('/update_exec', methods=['POST'])
def update_exec():
    id = request.form.get('id')
    name = request.form.get('name')
    role = request.form.get('role')
    
    # We execute two updates because our simple engine handles one col at a time
    if name:
        db.execute(f"UPDATE users SET name='{name}' WHERE id={id}")
    if role:
        db.execute(f"UPDATE users SET role='{role}' WHERE id={id}")
        
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, port=5001)
