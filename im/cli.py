"""This module provides the CLI functionality of the Identity Manager application"""
# im/cli.py

import typer

from rich import print
from rich.prompt import Confirm

from im import config, database, SUCCESS

app = typer.Typer()
config_app = typer.Typer()
users_app = typer.Typer()

app.add_typer(config_app, name="config")
app.add_typer(users_app, name="users")


@config_app.command()
def init():
    """Initialize the database."""
    host = typer.prompt("Host")
    port = typer.prompt("Port")
    username = typer.prompt("Username")
    password = typer.prompt("Password", hide_input=True,
                            confirmation_prompt=True)

    config.init()
    config.save_database_config(host, port, username, password)
    database.init()


@config_app.command()
def read():
    """Read the database config."""
    config.show_database_config()


@config_app.command()
def delete():
    """Delete the database."""
    if not config.CONFIG_FILE_PATH.exists():
        return print("[red]Config file already deleted.[/red]")

    delete = Confirm.ask(
        "Are you sure you want to [red]DELETE[/red] the database config? :skull:")
    if delete:
        if database.destroy() == SUCCESS:
            config.delete_database_config()
    else:
        raise typer.Abort()


@config_app.command()
def test_connection():
    """Test the database connection."""
    try:
        database._connect(autoclose=True)
        print("[green]Connection successful.[/green]")
    except:
        print(f"[red]Connection failed.[/red]")


@users_app.command(help="Register a user.")
def add():
    first_name = typer.prompt("First name")
    last_name = typer.prompt("Last name")
    email = typer.prompt("Email")
    password = typer.prompt("Password", hide_input=True,
                            confirmation_prompt=True)

    database.add_user(first_name, last_name, email, password)


@users_app.command(help="Update user data.")
def update(uuid: str = typer.Option(..., "--id", show_default=False, prompt=True)):
    first_name = typer.prompt("First name")
    last_name = typer.prompt("Last name")
    email = typer.prompt("Email")
    password = typer.prompt("Password", hide_input=True,
                            confirmation_prompt=True)

    database.update_user(uuid, first_name, last_name, email, password)


@users_app.command(help="Delete a user.")
def delete(uuid: str = typer.Option(..., "--id", show_default=False, prompt=True)):
    database.delete_user(uuid)


@users_app.command(help="Retrieve the data of a specific user.")
def get(uuid: str = typer.Option(..., "--id", show_default=False, prompt=True)):
    database.get_user(uuid)


@users_app.command(help="List all users.")
def list():
    database.list_users()
