class Config:
    """
    Load configuration values from the environment.
    """

    def __init__(self, env):
        self.envelope_dir = env.get('ENVELOPE_DIR')
        self.asset_dir = env.get('ASSET_DIR')
        self.content_service_url = env.get('CONTENT_SERVICE_URL')
        self.content_service_apikey = env.get('CONTENT_SERVICE_APIKEY')
