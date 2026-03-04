"""
Configuration - loads API keys from .env file.
This is the only file that knows where secrets are stored.
Every other file imports keys from here.
"""

import os

def load_env():
    """Read the .env file and load keys into the program."""
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_env()

CANLII_API_KEY = os.environ.get('CANLII_API_KEY', '')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
BASE_CANLII_URL = "https://api.canlii.org/v1"
BASE_CANLII_WEB = "https://www.canlii.org"
