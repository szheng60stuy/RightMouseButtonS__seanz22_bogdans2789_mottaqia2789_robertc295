# Conquest by RightMouseButtonS
# Roster:
Sean Zheng - PM <br>
Bogdan Sotnikov - Devo 1 <br>
Robert Chen - Devo 2 <br>
Mottaqi A - Devo 3 <br>

# Description:
A simplified version of Risk involving 2-6 players. Players start out with a set number of armies and take turns placing their armies across 42 territories on a world map until all armies have been placed. At the start of each turn, each player places additional armies (territory / 3 rounded down but at least 3 armies) and can choose to attack or move troops across adjacent/connected owned territories. When attacking, the attacker can roll 1, 2, or 3 die while the defender rolls up to 2. The highest die is chosen and a lower roll (defender wins ties)  results in a loss of one army each (rolling 2 lower dice means losing 2 armies). The attack continues when the attacker has 1 army left or chooses to stop, or when the defender loses all of their armies in that occupied territory, after which the attacker takes over that territory. During each turn, players can earn bonus armies if they have continent bonuses, earned by owning all territories in a continent. The game ends when there is one player standing. 

# Install guide:
To clone the repo, open the terminal and enter:

```
git clone git@github.com:szheng60stuy/RightMouseButtonS__seanz22_bogdans2789_mottaqia2789_robertc295.git
```

To open a virtual environment:

```
python3 -m venv venv
```

Activate the venv:

For Windows:
```
venv/Scripts/activate
```

For Linux:
```
. venv/bin/activate
```

Install requirements:

```
pip install -r RightMouseButtonS__seanz22_bogdans2789_mottaqia2789_robertc295/requirements.txt
```

# Launch codes:
Enter this command:
```
python RightMouseButtonS__seanz22_bogdans2789_mottaqia2789_robertc295/app/__init__.py
```

Enter in a browser:
```
http://127.0.0.1:5000
```
