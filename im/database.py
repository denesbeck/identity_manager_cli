"""This module provides the database functionality of the Identity Manager application"""
# im/database.py

import uuid
import hashlib

from im import config, DB_WRITE_ERROR, DB_READ_ERROR, SUCCESS

from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.console import Console

import time
import psycopg2

console = Console()


def init():
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True
    ) as progress:
        progress.add_task(description="Creating database...", total=None)
        progress.add_task(description="Creating table...", total=None)
        time.sleep(2)
        _create_database()
        _create_table()


def destroy():
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True
    ) as progress:
        progress.add_task(description="Dropping database...", total=None)
        time.sleep(2)
        return _drop_database()


def add_user(first_name: str, last_name: str, email: str, password: str):
    connection = _connect("identity_manager")
    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
    try:
        cursor = connection.cursor()
        cursor.execute("""
                        INSERT INTO users
                        (uuid, first_name, last_name, email, password)
                        VALUES (%s,%s,%s,%s,%s);
                       """, (str(uuid.uuid4()), first_name, last_name, email, hashed_password))
        connection.commit()
        cursor.close()
        print('[green]User has been successfully registered.[/green]')
        return SUCCESS
    except psycopg2.DatabaseError as error:
        print(error)
        return DB_WRITE_ERROR
    finally:
        if connection is not None:
            connection.close()


def update_user(uuid: str, first_name: str, last_name: str, email: str, password: str) -> int:
    connection = _connect("identity_manager")
    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
    try:
        cursor = connection.cursor()
        cursor.execute("""
                        UPDATE users
                        SET first_name = %s, last_name = %s, email = %s, password = %s
                        WHERE uuid = %s;
                       """, (first_name, last_name, email, hashed_password, uuid))
        connection.commit()
        cursor.close()
        print('[green]User has been successfully updated.[/green]')
        return SUCCESS
    except psycopg2.DatabaseError as error:
        print(error)
        return DB_WRITE_ERROR
    finally:
        if connection is not None:
            connection.close()


def delete_user(uuid: str) -> int:
    connection = _connect("identity_manager")
    try:
        cursor = connection.cursor()
        cursor.execute("""
                        DELETE
                        FROM users
                        WHERE uuid = %s;
                       """, (uuid,))
        connection.commit()
        cursor.close()
        print('[green]User has been successfully deleted.[/green]')
        return SUCCESS
    except psycopg2.DatabaseError as error:
        print(error)
        return DB_WRITE_ERROR
    finally:
        if connection is not None:
            connection.close()


def get_user(uuid: str):
    connection = _connect("identity_manager")
    try:
        cursor = connection.cursor()
        cursor.execute("""
                        SELECT uuid, first_name, last_name, email, password
                        FROM users
                        WHERE uuid = %s;
                       """, (uuid,))
        res = cursor.fetchone()
        cursor.close()

        if res is None:
            return print("[red]User doesn't exist.[/red]")

        table = Table("uuid", "first_name", "last_name", "email", "password")
        table.add_row(*res)
        console.print(table)
        return SUCCESS
    except psycopg2.DatabaseError as error:
        print(error)
        return DB_READ_ERROR
    finally:
        if connection is not None:
            connection.close()


def list_users():
    connection = _connect("identity_manager")
    try:
        cursor = connection.cursor()
        cursor.execute("""
                        SELECT uuid, first_name, last_name, email, password
                        FROM users;
                       """)
        res = cursor.fetchall()
        cursor.close()

        table = Table("uuid", "first_name", "last_name", "email", "password")

        for row in res:
            table.add_row(*row)

        console.print(table)
        return SUCCESS
    except psycopg2.DatabaseError as error:
        print(error)
        return DB_READ_ERROR
    finally:
        if connection is not None:
            connection.close()


def _connect(database: str = 'postgres', autoclose: bool = False):
    credentials = config._read_database_config()
    connection = None
    try:
        connection = psycopg2.connect(user=credentials["username"],
                                      password=credentials["password"],
                                      host=credentials["host"],
                                      port=credentials["port"],
                                      database=database)
        return connection
    except psycopg2.DatabaseError as error:
        print(error)
        return DB_READ_ERROR
    finally:
        if database == 'postgres' and autoclose and connection is not None:
            connection.close()


def _create_database():
    connection = _connect()
    try:
        connection.autocommit = True
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE identity_manager;")
        cursor.close()
        return SUCCESS
    except psycopg2.DatabaseError as error:
        print(error)
        return DB_WRITE_ERROR
    finally:
        if connection is not None:
            connection.close()


def _create_table():
    connection = _connect("identity_manager")
    try:
        cursor = connection.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS users
                       (uuid uuid NOT NULL,
                       first_name TEXT NOT NULL,
                       last_name TEXT NOT NULL,
                       email TEXT NOT NULL,
                       password TEXT NOT NULL);""")
        connection.commit()
        cursor.close()
        return SUCCESS
    except psycopg2.DatabaseError as error:
        print(error)
        return DB_WRITE_ERROR
    finally:
        if connection is not None:
            connection.close()


def _drop_database():
    connection = _connect(autoclose=False)
    try:
        connection.autocommit = True
        cursor = connection.cursor()
        cursor.execute("DROP DATABASE identity_manager;")
        cursor.close()
        return SUCCESS
    except psycopg2.DatabaseError as error:
        print(error)
        return DB_WRITE_ERROR
    finally:
        if connection is not None:
            connection.close()
