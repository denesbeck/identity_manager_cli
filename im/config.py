"""This module provides the config functionality of the Identity Manager application"""
# im/config.py

import configparser
import typer

from pathlib import Path
from rich import print

from im import DIR_ERROR, FILE_ERROR, SUCCESS, __app_name__

CONFIG_DIR_PATH = Path(typer.get_app_dir(__app_name__))
CONFIG_FILE_PATH = CONFIG_DIR_PATH / "config.ini"

config = configparser.ConfigParser()


def init() -> int:
    try:
        CONFIG_DIR_PATH.mkdir(exist_ok=True)
    except OSError:
        return DIR_ERROR
    try:
        CONFIG_FILE_PATH.touch(exist_ok=True)
    except OSError:
        return FILE_ERROR
    return SUCCESS


def save_database_config(host: str, port: str, username: str, password: str) -> int:
    config["Database"] = {"host": host, "port": port, "username": username, "password": password}
    try:
        with CONFIG_FILE_PATH.open("w") as file:
            config.write(file)
    except OSError:
        return FILE_ERROR
    return SUCCESS


def show_database_config() -> int:
    data = _read_database_config()
    print(f"""
        [bold]host:[/bold] [green]{data['host']}[/green]
        [bold]port:[/bold] [green]{data['port']}[/green]
        [bold]username:[/bold] [green]{data['username']}[/green]
        [bold]password:[/bold] [green]{data['password']}[/green]
          """)
    return SUCCESS
    

def delete_database_config() -> int:
    try:
        CONFIG_FILE_PATH.unlink()
        CONFIG_DIR_PATH.rmdir()
        print("[green]Config file has been successfully deleted.[/green]")
    except OSError:
        return FILE_ERROR
    return SUCCESS


def _read_database_config() -> dict:
    config.read(CONFIG_FILE_PATH)
    data = dict(config["Database"])
    return data
