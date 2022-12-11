from flask import Flask,jsonify
from logging.config import dictConfig

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": "default",
            },
            "file_app": {
                "class": "logging.FileHandler",
                "filename": "app.log",
                "formatter": "default",
            }
        },
        "root": {"level": "DEBUG", "handlers": ["console", "file_app"]},
    }
)


app = Flask(__name__)

@app.route("/")
def hello():
    app.logger.info("Success for hello world")
    return "Hello World!"

@app.route("/status")
def status():
    result = { "result": "healthy"}
    return jsonify(result);

@app.route("/metrics")
def metrics():
    data = {
        "status": "success",
        "code": 0,
        "UserCount": 141,
        "UserCountActive": 23
    }
    return jsonify(data);

if __name__ == "__main__":
    
    ## basic course exemple
    ##logging.basicConfig(filename='app.log',level=logging.DEBUG)

    app.run(host='0.0.0.0', debug=True)
