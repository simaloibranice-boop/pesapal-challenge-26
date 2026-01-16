# Pesapal Junior Dev Challenge '26 - Custom RDBMS

A "built-from-scratch" Relational Database Management System (RDBMS) implemented in pure Python. It features a custom SQL parser, JSON-based persistence, and a live web demonstration.

## 📸 Demo
![Web App Interface](demo_screenshot.png)

## 🚀 Features
* **Custom Engine:** Parses SQL (`SELECT`, `INSERT`, `UPDATE`, `DELETE`) without external libraries.
* **Full CRUD:** Supports Create, Read, Update, and Delete operations via SQL and Web UI.
* **Storage:** Stores tables as JSON files for transparency and portability.
* **Constraints:** Enforces `PRIMARY KEY` and `UNIQUE` constraints.
* **Joins:** Supports `INNER JOIN` operations (Nested Loop algorithm).

## 🛠 Usage

### 1. The Terminal (REPL)
Run the interactive database shell:
```bash
python src/cli.py

Supported SQL:
SQL

CREATE TABLE staff (id int PK, name text, role text)
INSERT INTO staff VALUES (1, 'Jane Doe', 'DevOps')
UPDATE staff SET role='CTO' WHERE id=1
DELETE FROM staff WHERE id=1
SELECT * FROM staff

2. The Web App

Run the full-stack demo:
Bash

pip install -r requirements.txt
python app.py

    Navigate to http://127.0.0.1:5001

    Use the UI to Add, View, Edit, and Delete staff members.

👨‍💻 Technical Decisions

    Why Python? For rapid development of string parsing logic (Regex) within the 24-hour window.

    Why JSON? To make the "database" human-readable and easy to debug without binary tools.

    Why No SQLite? The challenge required "ingenuity" and "from scratch" implementation. Wrapping SQLite would have defeated the purpose of the test.


### Step 4: Execute & Commit (The Finish Line)

1.  **Run the App one last time** (`python app.py`) and click the new **Green "Edit" button** to make sure it works.
2.  **Take a new screenshot** if the UI looks different/better.
3.  **Run these git commands** inside your terminal:

```bash
# Add the new screenshot (make sure you saved it as demo_screenshot.png)
git add demo_screenshot.png

# Stage all code changes
git add .

# Commit with a strong message
git commit -m "Complete Challenge: Implement Full CRUD (Update added), Web UI polished, and README finalized."

# Push to GitHub
git push origin main
