from .app import FastAPIApp
def run(config_path,host,port):
    FastAPIApp(config_path=config_path)._run(host=host,port=port)
def return_app(config_path):
    app = FastAPIApp(config_path=config_path).app
    return app
