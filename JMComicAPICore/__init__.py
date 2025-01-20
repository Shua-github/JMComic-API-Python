from .app import FastAPI_app
def run(config_path,host,port):
    FastAPI_app(config_path=config_path)._run(host=host,port=port)
def return_app(config_path):
    app = FastAPI_app(config_path=config_path).app
    return app
