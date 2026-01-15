from flask import Flask, request, session, redirect, url_for, render_template
import sqlite3
from game import make_tables, set_game, addTerritory
app = Flask(__name__)
app.secret_key = "secret_key_testing"
DB_FILE = "conquest.db"

def initialize_db():
  make_tables()
  set_game()
  addTerritory("Alaska", 1, 1)
  addTerritory("Northwest Territory", 1, 1)
  addTerritory("Greenland", 1, 1)
  addTerritory("Iceland", 1, 1)

@app.route("/", methods=['GET'])
def index():
  if 'username' in session:
    return redirect(url_for('menu'))
  return render_template("login.html", text="")

@app.route("/login", methods=["GET", "POST"])
def login():
  if request.method == 'GET':
    if 'username' in session:
      return redirect(url_for('menu'))
    return render_template("login.html", text="")
    
  username = request.form.get("username", "").strip()
  password = request.form.get("password", "")
  
  db = sqlite3.connect(DB_FILE)
  c = db.cursor()
  c.execute("SELECT username, password FROM users WHERE username = ?", (username,))
  user = c.fetchone()
  db.close()
  if not user or user[1] != password:
    text = "Login failed. Check username/password"
    return render_template('login.html', text=text)
  
  session['username'] = username
  return redirect(url_for('menu'))

@app.route("/register", methods=["GET", "POST"])
def register():
  if request.method == 'GET':
    if 'username' in session:
      return redirect(url_for('menu'))
    return render_template("register.html", text="")
  
  username = request.form.get("username", "").strip()
  password = request.form.get("password", "")
  
  if not username or not password:
    text = "Username and password cannot be empty!"
    return render_template('register.html', text=text)
  
  db = sqlite3.connect(DB_FILE)
  c = db.cursor()
  c.execute("SELECT username FROM users WHERE username = ?", (username,))
  existing_user = c.fetchone()

  if existing_user:
    db.close()
    text = "Username already take!"
    return render_template('register.html', text=text)
  
  c.execute("INSERT INTO users (username, password, games) VALUES (?, ?, ?);", (username, password, 0))
  db.commit()
  db.close()

  session['username'] = username
  return redirect(url_for('menu'))

@app.route("/menu", methods=["GET", "POST"])
def menu():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template("menu.html", username=session['username'])

@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route("/game-test")
def game_test():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("game.html")

if __name__ == "__main__":
    initialize_db()
    app.debug = True
    app.run(port=5000)
