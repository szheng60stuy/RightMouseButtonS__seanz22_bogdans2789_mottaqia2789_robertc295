from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello_world():
    print("the __name__ of this module is... ")
    print(__name__)
    return "No hablo queso!"

if __name__ == "__main__":
    app.debug = True
    app.run(port=5000)
