import os
import socket
import subprocess
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

def resolve_db_host(default_host: str, port: int) -> str:
    """Smartly resolve database host between localhost and WSL if on Windows."""
    # First, test if default_host:port is directly reachable
    try:
        with socket.create_connection((default_host, port), timeout=0.8):
            return default_host
    except Exception:
        pass

    # If on Windows and default_host was localhost/127.0.0.1, check WSL IP
    if default_host in ("localhost", "127.0.0.1") and os.name == "nt":
        try:
            res = subprocess.check_output(["wsl", "hostname", "-I"], text=True, stderr=subprocess.DEVNULL)
            wsl_ip = res.strip().split()[0]
            with socket.create_connection((wsl_ip, port), timeout=0.8):
                return wsl_ip
        except Exception:
            pass

    return default_host

class Settings:
    _raw_host: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_NAME: str = os.getenv("DB_NAME", "devops_db")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")
    
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", "8000"))
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    @property
    def DB_HOST(self) -> str:
        return resolve_db_host(self._raw_host, self.DB_PORT)

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

settings = Settings()
