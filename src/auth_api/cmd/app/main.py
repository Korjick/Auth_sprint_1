import typer

from auth_api.cmd.app.service import service_cli
from auth_api.cmd.app.db import db_cli

app = typer.Typer(
    name="cmd",
    help="Auth API CLI",
    add_completion=False,
)
app.add_typer(db_cli, name='db')
app.add_typer(service_cli, name='service')


def main() -> None:
    app()


if __name__ == "__main__":
    main()

