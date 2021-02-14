import logging
import os

log = logging.getLogger(__name__)


def get_config(name: str, default: str = '') -> str:
    if name.upper() in os.environ:
        log.info("Loaded config '%s' from env var", name)
        return os.environ[name.upper()]

    try:
        with open(f'/{name.lower()}') as config_file:
            log.info("Loaded docker config '%s'", name)
            return config_file.read().strip()

    except FileNotFoundError:
        log.error("Failed to load config '%s'", name.lower())
        return default


def get_secret(name: str, default: str = '') -> str:
    if name.upper() in os.environ:
        log.info("Loaded secret '%s' from env var", name)
        return os.environ[name.upper()]

    try:
        with open(f'/run/secrets/{name.lower()}') as secret_file:
            log.info("Loaded docker secret '%s'", name)
            return secret_file.read().strip()

    except FileNotFoundError:
        log.error("Failed to load secret '%s'", name.lower())
        return default
