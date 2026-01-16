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
  #game.addTerritory(None, "Alaska", 1, 1)
  #game.addTerritory(None, "Northwest Territory", 2, 5)
  #game.attackTerritory("Alaska", 2, "Northwest Territory")

def getTurn():
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    turn = c.execute("SELECT turn FROM games").fetchone()[0]
    db.close()
    return turn

def requireTurn(player):
    turn = getTurn()
    if turn != 0 and turn != player:
        return False
    return True

def alivePlayer(c, player: int) -> bool:
    unoccupied = c.execute("SELECT COUNT(*) FROM territories WHERE armies = 0").fetchone()[0]
    if unoccupied > 0:
        return True

    s = c.execute(f"SELECT p{player} FROM games").fetchone()[0] or ""
    owned = [x.strip() for x in s.split(",") if x.strip()]
    return len(owned) > 0


def nextAliveTurn(c, current: int, players: int) -> int:
    for _ in range(players):
        current = (current % players) + 1
        if alivePlayer(c, current):
            return current
    return current


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
    text = "Username already taken!"
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
    
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    c.execute("UPDATE territories SET armies = 0")
    c.execute(
        "UPDATE games SET armies = ?, p1 = ?, p2 = ?, p3 = ?, p4 = ?, p5 = ?, p6 = ?, turn = ?",
        ("0, 0, 0, 0, 0, 0", "", "", "", "", "", "", 0)
    )
    db.commit()
    db.close()

    if request.method == "POST":
        players = int(request.form.get("players", 2))
        players = max(2, min(players, 6))
        session['players'] = players

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

@app.route("/api/start", methods=['POST'])
def start():
    players = session.get('players', 2)
    session['turnsCompleted'] = 0
    startingArmies = {2:40, 3:35, 4:30, 5:25, 6:20}
    starting = startingArmies[players]

    pools = [starting] * players + [0] * (6 - players)
    armiesStr = ", ".join(str(x) for x in pools)

    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    c.execute("UPDATE games SET turn = ?, armies = ?", (1, armiesStr))
    db.commit()
    db.close()
    return jsonify(success=True, players=players, armies=pools)

@app.route("/api/map", methods=['GET'])
def returnMap():
    return jsonify(game.getMapInfo())

@app.route("/api/getPlayers", methods=['GET'])
def returnPlayer():
    return jsonify(game.getPlayers())

@app.route('/api/addTerritory', methods=['POST'])
def addTerritory():
    data = request.get_json()

    territory = data["territory"]
    player = int(data["player"])
    army = int(data.get("army", 1))
    home = data.get("home", None)

    if not requireTurn(player):
        return jsonify(success=False, error="Not your turn")
    
    if home is None:
        db = sqlite3.connect(DB_FILE)
        c = db.cursor()
        armiesStr = c.execute("SELECT armies FROM games").fetchone()[0]
        db.close()

        pools = [int(x.strip()) for x in armiesStr.split(",") if x.strip() != ""]
        while len(pools) < 6:
            pools.append(0)

        if pools[player - 1] < army:
            print("ADD:", "player", player, "home", home, "army", army, "pools", pools)
            return jsonify(success=False, error="No armies left in pool")

    game.addTerritory(home, territory, player, army)
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

@app.route('/api/move', methods=['POST'])
def move():
    data = request.get_json()
    home = data["home"]
    territory = data["territory"]
    player = int(data["player"])
    army = int(data.get("army", 1))

    if not requireTurn(player):
        return jsonify(success=False, error="Not your turn")
    
    game.addTerritory(home, territory, player, army)
    return jsonify(success=True)

@app.route('/api/attackTerritory', methods=['POST'])
def attackTerritory():
    data = request.get_json()
    result = game.attackTerritory(data['territory'], data['player'], data['origin'])
    return jsonify(out=result["outcome"], captured=result["captured"])

@app.route('/api/availableAttack', methods=['POST'])
def availableAttack():
    data = request.get_json()
    out = game.availableAttack(data['territory'], data['player'])
    return jsonify(out=out)

@app.route('/api/state', methods=['GET'])
def state():
  db = sqlite3.connect(DB_FILE)
  c = db.cursor()

  terr_rows = c.execute("SELECT name, armies FROM territories").fetchall()
  game_row = c.execute("SELECT armies, p1, p2, p3, p4, p5, p6, turn FROM games").fetchone()
  pools = [int(x.strip()) for x in game_row[0].split(",") if x.strip() != '']
  db.close()

  owners = {}
  for index, player in enumerate(game_row[1:7], start=1):
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

  # --- winner detection ---
  total_territories = len(out)
  counts = {i: 0 for i in range(1, 7)}
  for info in out.values():
      owner = info.get("owner", 0)
      if owner in counts:
          counts[owner] += 1

  winner = 0
  for p, cnt in counts.items():
      if total_territories > 0 and cnt == total_territories:
          winner = p
          break

  return jsonify(territories=out, turn=game_row[7], pools=pools, armies=pools, winner=winner)

@app.route('/api/endTurn', methods=['POST'])
def endTurn():
    players = session.get('players', 2)

    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    turn = c.execute("SELECT turn FROM games").fetchone()[0]
    nextTurn = nextAliveTurn(c, turn, players)
    
    c.execute("UPDATE games SET turn = ?", (nextTurn,))
    db.commit()
    db.close()

    session['turns_completed'] = session.get('turns_completed', 0) + 1

    if session['turns_completed'] >= players:
        game.addArmy(nextTurn)

    return jsonify(turn=nextTurn)

@app.route('/api/nextTurn', methods=['POST'])
def nextTurn():
   players = session.get('players', 2)
   db = sqlite3.connect(DB_FILE)
   c = db.cursor()
   turn = c.execute("SELECT turn FROM games").fetchone()[0]
   nextTurn = nextAliveTurn(c, turn, players)
   c.execute("UPDATE games SET turn = ?", (nextTurn,))
   db.commit()
   db.close()

   return jsonify(turn=nextTurn)

@app.route('/api/reset', methods=['POST'])
def reset():
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()

    c.execute("UPDATE territories SET armies = 0")

    c.execute("UPDATE games SET armies = ?, p1 = ?, p2 = ?, p3 = ?, p4 = ?, p5 = ?, p6 = ?, turn = ?", ("0, 0, 0, 0, 0, 0", "", "", "", "", "", "", 0))

    db.commit()
    db.close()

    return jsonify(success=True)

if __name__ == "__main__":
    initialize_db()
    app.debug = True
    app.run(port=5000)
