import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    # Discord configuration
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))

    # GitHub configuration
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    GITHUB_API_URL = "https://api.github.com/user/repos"

    # Application configuration
    CHECK_INTERVAL = 1  # seconds
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    REPOSITORIES_FILE = os.path.join(DATA_DIR, "repositories.json")

    @staticmethod
    def ensure_directories():
        """Ensure all required directories exist."""
        os.makedirs(Config.DATA_DIR, exist_ok=True)
