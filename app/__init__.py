from flask import Flask, request, session, redirect, url_for, render_template, jsonify
import sqlite3
import game
app = Flask(__name__)
app.secret_key = "secret_key_testing"
DB_FILE = "conquest.db"

def initialize_db():
  game.make_tables()
  db = sqlite3.connect(DB_FILE)
  c = db.cursor()
  count = c.execute("SELECT COUNT(*) FROM games").fetchone()[0]
  db.close()
  if count == 0:
    game.set_game()
  # set_game() #test purposes
  # addTerritory("Alaska", 1, 1)
  # addTerritory("Northwest Territory", 1, 1)
  # addTerritory("Greenland", 1, 1)
  # addTerritory("Iceland", 1, 1)
  # addTerritory("Ontario", 1, 1)
  # addTerritory("Western United States", 1, 1)
  # addTerritory("Ukraine", 1, 1)
  # # test purposes


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

@app.route("/api/map", methods=['GET'])
def returnMap():
    return jsonify(game.getMapInfo())

@app.route('/api/addTerritory', methods=['POST'])
def addTerritory():
    data = request.get_json()
    game.addTerritory(data['territory'], data['player'], data['army'])
    return jsonify(success=True)

@app.route('/api/availableSet', methods=['POST'])
def availableSet():
    out = game.availableSet()
    return jsonify(out=out)

@app.route('/api/availableMove', methods=['POST'])
def availableMove():
    data = request.get_json()
    out = game.availableMove(data['territory'], data['player'])
    return jsonify(out=out)

@app.route('/api/attackTerritory', methods=['POST'])
def attackTerritory():
    data = request.get_json()
    game.attackTerritory(data['territory'], data['player'], data['origin'])
    return jsonify(success=True)

@app.route('/api/availableAttack', methods=['POST'])
def availableAttack():
    data = request.get_json()
    out = game.availableAttack(data['player'])
    return jsonify(out=out)

@app.route('/api/state', methods=['GET'])
def state():
  db = sqlite3.connect(DB_FILE)
  c = db.cursor()

  terr_rows = c.execute("SELECT name, armies FROM territories").fetchall()
  game_row = c.execute("SELECT p1, p2, p3, p4, p5, p6, turn FROM games").fetchone()
  db.close()

  owners = {}
  for index, player in enumerate(game_row[0:6], start=1):
      if not player:
          continue
      for territory in player.split(", "):
         territory = territory.strip()
         if territory:
             owners[territory] = index
  out = {}
  for name, armies in terr_rows:
      out[name] = {
          "armies": armies,
          "owner": owners.get(name, 0)
      }
  return jsonify(territories=out, turn=game_row[6])

if __name__ == "__main__":
    initialize_db()
    app.debug = True
    app.run(port=5000)
