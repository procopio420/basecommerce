"""Logs command - view container logs."""

import sys

import typer

from basec.docker import DockerCompose
from basec.inventory import get_droplet
from basec.output import print_error, print_header


def logs_command(
    droplet: str = typer.Argument(..., help="Droplet name (e.g., 'edge', 'platform', 'vertical_construction')"),
    service: str = typer.Argument(None, help="Service name to filter logs (optional)"),
    follow: bool = typer.Option(False, "--follow", "-f", help="Follow log output"),
    tail: int = typer.Option(100, "--tail", "-n", help="Number of lines to show from the end"),
    env: str = typer.Option("production", "--env", "-e", help="Environment name"),
) -> None:
    """View container logs from a droplet."""
    droplet_config = get_droplet(droplet, env)
    
    if not droplet_config:
        print_error(f"Droplet '{droplet}' not found in inventory")
        sys.exit(1)
    
    print_header(f"Logs: {droplet} ({droplet_config.ip})")
    
    try:
        docker = DockerCompose(droplet_config)
        docker.logs(service=service, follow=follow, tail=tail)
    except KeyboardInterrupt:
        print("\n")
        sys.exit(0)
    except Exception as e:
        print_error(f"Failed to get logs: {e}")
        sys.exit(1)

