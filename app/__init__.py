from flask import Flask, request, session, redirect, url_for, render_template
import sqlite3
app = Flask(__name__)

app.secret_key = "secret_key_testing"
DB_FILE = "risk.db"

def initialize_db():
  db = sqlite3.connect(DB_FILE)
  c = db.cursor()

  c.execute("CREATE TABLE IF NOT EXISTS users(username TEXT PRIMARY KEY NOT NULL, password TEXT NOT NULL, games INTEGER);")

  db.commit()
  db.close()

@app.route("/", methods=['GET', 'POST'])
def index():
  if 'username' in session:
    return render_template("login.html")
  else:
    text = ""
    return render_template("login.html", text=text)

@app.route("/login", methods=["GET", "POST"])
def login():
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    db.close()

    if user == None or user[0] != username or user[1] != password:
      print("username/password do not match our records")
      text = "login failed, create new acc?"
      return render_template('login.html', text=text)
    elif user[0] == username and user[1] == password:
      session['username'] = username
      return redirect(url_for('menu'))
    else:
      return redirect(url_for('index'))
  return redirect(url_for('index'))

@app.route("/register", methods=["GET", "POST"])
def register():
  if request.method == 'POST':
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    username = request.form['username']
    password = request.form['password']

    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    existing_user = c.fetchone()

    if existing_user:
      db.close()
      text = "username already taken, try another one!"
      return render_template('register.html', text = text)

    c.execute(
        "INSERT INTO users VALUES (?, ?, ?)",
        (username, password, 0)
    )
    db.commit()
    db.close()
    session['username'] = username
    return redirect(url_for('menu'))
  return render_template('register.html')


@app.route("/menu", methods=["GET", "POST"])
def menu():
    if 'username' not in session:
        return redirect(url_for('index'))
    return render_template("menu.html", username=session['username'])

if __name__ == "__main__":
    initialize_db()
    app.debug = True
    app.run(port=5000)
