"""
manage.py
This script is used to manage the Flask application.
It provides a CLI entrypoint for running the application and executing various commands.
"""

from flask.cli import FlaskGroup
from app import create_app

app = create_app()
cli = FlaskGroup(app)

if __name__ == "__main__":
    cli()
