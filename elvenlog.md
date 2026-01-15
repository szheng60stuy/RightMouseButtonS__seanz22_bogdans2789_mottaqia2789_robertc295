* Chatbot: ChatGPT
 - link: https://chatgpt.com/share/69685566-7874-8013-9a91-2d325627452f
* Input: 
 - Me and my group are recreating a simplified version of risk. Provide a python dictionary that includes all the territories in risk, attached by a list of territories they are connected to, with the continent group they belong in as the first item in that list. For example "Alaska" : ["North America", "Kamchatka", "Northwest Territory", "Alberta"]

* Output: 
 - risk_map = {
    # --- North America ---
    "Alaska": ["North America", "Northwest Territory", "Alberta", "Kamchatka"],
    "Northwest Territory": ["North America", "Alaska", "Alberta", "Ontario", "Greenland"],
    "Greenland": ["North America", "Northwest Territory", "Ontario", "Quebec", "Iceland"],
    "Alberta": ["North America", "Alaska", "Northwest Territory", "Ontario", "Western United States"],
    "Ontario": ["North America", "Northwest Territory", "Greenland", "Quebec", "Eastern United States", "Western United States", "Alberta"],
    "Quebec": ["North America", "Ontario", "Greenland", "Eastern United States"],
    "Western United States": ["North America", "Alberta", "Ontario", "Eastern United States", "Central America"],
    "Eastern United States": ["North America", "Ontario", "Quebec", "Western United States", "Central America"],
    "Central America": ["North America", "Western United States", "Eastern United States", "Venezuela"],

    # --- South America ---
    "Venezuela": ["South America", "Central America", "Brazil", "Peru"],
    "Peru": ["South America", "Venezuela", "Brazil", "Argentina"],
    "Brazil": ["South America", "Venezuela", "Peru", "Argentina", "North Africa"],
    "Argentina": ["South America", "Peru", "Brazil"],

    # --- Europe ---
    "Iceland": ["Europe", "Greenland", "Great Britain", "Scandinavia"],
    "Scandinavia": ["Europe", "Iceland", "Northern Europe", "Ukraine"],
    "Great Britain": ["Europe", "Iceland", "Scandinavia", "Northern Europe", "Western Europe"],
    "Northern Europe": ["Europe", "Great Britain", "Scandinavia", "Ukraine", "Southern Europe", "Western Europe"],
    "Western Europe": ["Europe", "Great Britain", "Northern Europe", "Southern Europe", "North Africa"],
    "Southern Europe": ["Europe", "Western Europe", "Northern Europe", "Ukraine", "Middle East", "Egypt"],

    # --- Africa ---
    "North Africa": ["Africa", "Brazil", "Western Europe", "Southern Europe", "Egypt", "East Africa", "Congo"],
    "Egypt": ["Africa", "North Africa", "Southern Europe", "Middle East", "East Africa"],
    "East Africa": ["Africa", "Egypt", "North Africa", "Congo", "South Africa", "Madagascar", "Middle East"],
    "Congo": ["Africa", "North Africa", "East Africa", "South Africa"],
    "South Africa": ["Africa", "Congo", "East Africa", "Madagascar"],
    "Madagascar": ["Africa", "South Africa", "East Africa"],

    # --- Asia ---
    "Ural": ["Asia", "Ukraine", "Siberia", "China", "Afghanistan"],
    "Siberia": ["Asia", "Ural", "Yakutsk", "Irkutsk", "Mongolia", "China"],
    "Yakutsk": ["Asia", "Siberia", "Irkutsk", "Kamchatka"],
    "Kamchatka": ["Asia", "Yakutsk", "Irkutsk", "Mongolia", "Japan", "Alaska"],
    "Irkutsk": ["Asia", "Siberia", "Yakutsk", "Kamchatka", "Mongolia"],
    "Mongolia": ["Asia", "Siberia", "Irkutsk", "Kamchatka", "Japan", "China"],
    "Japan": ["Asia", "Kamchatka", "Mongolia"],
    "Afghanistan": ["Asia", "Ukraine", "Ural", "China", "India", "Middle East"],
    "Middle East": ["Asia", "Southern Europe", "Egypt", "East Africa", "Afghanistan", "India"],
    "India": ["Asia", "Middle East", "Afghanistan", "China", "Siam"],
    "China": ["Asia", "Ural", "Siberia", "Mongolia", "India", "Siam", "Afghanistan"],
    "Siam": ["Asia", "India", "China", "Indonesia"],
    "Ukraine": ["Asia", "Scandinavia", "Northern Europe", "Southern Europe", "Ural", "Afghanistan"],

    # --- Australia ---
    "Indonesia": ["Australia", "Siam", "New Guinea", "Western Australia"],
    "New Guinea": ["Australia", "Indonesia", "Western Australia", "Eastern Australia"],
    "Western Australia": ["Australia", "Indonesia", "New Guinea", "Eastern Australia"],
    "Eastern Australia": ["Australia", "Western Australia", "New Guinea"]
}

