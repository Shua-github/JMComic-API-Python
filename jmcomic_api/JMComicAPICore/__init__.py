from .FastAPI_APP import FastAPI_App
def run(config_path,host,port):
    FastAPI_App(config_path=config_path)._run(host=host,port=port)
def return_app(config_path):
    app = FastAPI_App(config_path=config_path).app
    return app
