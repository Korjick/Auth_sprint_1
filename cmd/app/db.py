import os
from pathlib import Path

import typer
from alembic import command as alembic_cmd
from alembic.config import Config

from internal.infrastructure.settings import Settings

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def _alembic_config(env_file: str) -> Config:
    os.environ["ENV_FILE"] = str(Path(env_file).resolve())
    cfg = Config(_PROJECT_ROOT / "alembic.ini")
    cfg.set_main_option("script_location", str(_PROJECT_ROOT / "alembic"))
    return cfg


db_cli = typer.Typer(
    name='db',
    help='Database migrations CLI',
    add_completion=False,
)


@db_cli.command("upgrade")
def db_upgrade(
        env_file: str = typer.Option(".env", "--env-file", "-e",
                                     help="Path to .env"),
        revision: str = typer.Argument("head", help="Revision (e.g head)"),
) -> None:
    try:
        Settings.from_env(env_file)
    except (FileNotFoundError, ValueError) as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)
    cfg = _alembic_config(env_file)
    alembic_cmd.upgrade(cfg, revision)
    typer.echo(f"Migrations applied up to revision {revision!r}.")


@db_cli.command("downgrade")
def db_downgrade(
        env_file: str = typer.Option(".env", "--env-file", "-e",
                                     help="Path to .env"),
        revision: str = typer.Argument("-1", help="Revision (e.g -1 or base)"),
) -> None:
    try:
        Settings.from_env(env_file)
    except (FileNotFoundError, ValueError) as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)
    cfg = _alembic_config(env_file)
    alembic_cmd.downgrade(cfg, revision)
    typer.echo(f"Migrations downgraded to revision {revision!r}.")


@db_cli.command("revision")
def db_revision(
        env_file: str = typer.Option(".env", "--env-file", "-e",
                                     help="Path to .env"),
        message: str = typer.Option(..., "--message", "-m",
                                    help="Revision description"),
        autogenerate: bool = typer.Option(False, "--autogenerate", "-a",
                                          help="Auto-generation by models"),
) -> None:
    try:
        Settings.from_env(env_file)
    except (FileNotFoundError, ValueError) as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)
    cfg = _alembic_config(env_file)
    alembic_cmd.revision(cfg, message=message, autogenerate=autogenerate)
    typer.echo("Revision created.")


@db_cli.command("current")
def db_current(
        env_file: str = typer.Option(".env", "--env-file", "-e",
                                     help="Path to .env"),
) -> None:
    try:
        Settings.from_env(env_file)
    except (FileNotFoundError, ValueError) as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)
    cfg = _alembic_config(env_file)
    alembic_cmd.current(cfg)


if __name__ == "__main__":
    db_cli()
