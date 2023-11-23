from flask import Flask

from logIngestor.logIngestor import logIngestor

app = Flask(__name__)
app.register_blueprint(logIngestor,url_prefix = '/')

if __name__ == "__main__":
    app.run(port=3000,debug=True)