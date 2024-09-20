token = None
channels = None

def initialize(config, environment):
    global token, channels

    token = config["token"]
    channels = {
        "pso2-general": config["channels"][environment]["pso2-general"],
        "pso2-submissions": config["channels"][environment]["pso2-submissions"],
        "pso2-alerts": config["channels"][environment]["pso2-alerts"],
        "pso2-modmail": config["channels"][environment]["pso2-modmail"],
        "pso2-reports": config["channels"][environment]["pso2-reports"],
        "pso2-modlog": config["channels"][environment]["pso2-modlog"],
        "pso2-imageprocessing": config["channels"][environment]["pso2-imageprocessing"]
    }
