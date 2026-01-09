"""Rollback command - rollback deployments to previous versions."""

import shlex
import sys
import tempfile
from pathlib import Path
from typing import Optional

import typer

from basec.docker import DockerCompose
from basec.inventory import (
    get_droplet,
    get_droplets_by_role,
    list_droplets,
)
from basec.output import (
    print_error,
    print_header,
    print_section,
    print_success,
    spinner,
)

app = typer.Typer()


def get_deploy_history(docker: DockerCompose) -> list[str]:
    """Get deployment history from remote .deploy-history file.
    
    Returns:
        List of tags in reverse chronological order (newest first)
    """
    history_file = f"{docker.remote_dir}/.deploy-history"
    
    try:
        exit_code, stdout, stderr = docker.ssh.execute(
            f"test -f {history_file} && cat {history_file} || echo ''",
            check=False,
            capture_output=True,
        )
        
        if exit_code != 0 or not stdout.strip():
            return []
        
        # Read history (one tag per line, newest first)
        tags = [line.strip() for line in stdout.strip().split("\n") if line.strip()]
        return tags
    except Exception:
        return []


def save_deploy_history(docker: DockerCompose, tag: str) -> None:
    """Save tag to deployment history."""
    history_file = f"{docker.remote_dir}/.deploy-history"
    
    # Get existing history
    existing_tags = get_deploy_history(docker)
    
    # Add new tag at the beginning (if not already there)
    if tag not in existing_tags:
        new_history = [tag] + existing_tags
        # Keep only last 10 deployments
        new_history = new_history[:10]
    else:
        # Move existing tag to front
        existing_tags.remove(tag)
        new_history = [tag] + existing_tags
    
    # Write history file
    history_content = "\n".join(new_history) + "\n"
    
    # Create temporary file and upload
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(history_content)
        temp_path = Path(f.name)
    
    try:
        docker.ssh.upload_file(temp_path, history_file)
        docker.ssh.execute(f"chmod 644 {shlex.quote(history_file)}", check=True)
    finally:
        temp_path.unlink(missing_ok=True)


def rollback_droplet(name: str, config, env: str, target_tag: str) -> int:
    """Rollback a single droplet to a specific tag.
    
    Args:
        name: Droplet name
        config: Droplet configuration
        env: Environment name
        target_tag: Tag to rollback to (e.g., 'sha-abc123' or 'previous')
    
    Returns:
        0 on success, 1 on failure
    """
    print_section(f"Rolling back: {name} ({config.ip})")
    
    try:
        docker = DockerCompose(config)
        
        # If target_tag is 'previous', get from history
        if target_tag == "previous":
            history = get_deploy_history(docker)
            if not history or len(history) < 2:
                print_error(f"No previous deployment found for {name}")
                return 1
            
            target_tag = history[1]  # Second item (first is current)
            print_section(f"Rolling back to previous tag: {target_tag}")
        
        # Deploy with target tag
        with spinner(f"Setting image tag: {target_tag}..."):
            docker.set_image_tags(target_tag)
        
        with spinner("Restarting services..."):
            docker.up(detach=True, pull=True, remove_orphans=True)
        
        # Save to history
        save_deploy_history(docker, target_tag)
        
        print_success(f"Rollback complete for {name} (tag: {target_tag})")
        return 0
    except Exception as e:
        print_error(f"Rollback failed for {name}: {e}")
        return 1


@app.command()
def rollback(
    target: str = typer.Argument(
        ...,
        help="Target to rollback: 'edge', 'platform', 'vertical <name>', or 'all'",
    ),
    vertical_name: Optional[str] = typer.Option(
        None,
        "--vertical",
        "-v",
        help="Vertical name (required if target is 'vertical')",
    ),
    env: str = typer.Option(
        "production",
        "--env",
        "-e",
        help="Environment name (default: production)",
    ),
    to: str = typer.Option(
        "previous",
        "--to",
        "-t",
        help="Tag to rollback to: 'previous' (default) or specific tag (e.g., 'sha-abc123')",
    ),
) -> None:
    """Rollback deployments to a previous version."""
    # Validate environment path exists
    from basec.envs import validate_env_path
    
    if not validate_env_path(env):
        print_error(f"Environment '{env}' not found. Available environments: production, development")
        sys.exit(1)
    
    print_header(f"BaseCommerce Rollback (env: {env}, to: {to})")
    
    total_failed = 0
    
    if target == "all":
        # Rollback all droplets in order: platform, edge, verticals
        droplets = list_droplets(env)
        
        # Platform first
        platform_droplets = {k: v for k, v in droplets.items() if v.role == "platform"}
        for name, config in platform_droplets.items():
            total_failed += rollback_droplet(name, config, env, to)
        
        # Edge second
        edge_droplets = {k: v for k, v in droplets.items() if v.role == "edge"}
        for name, config in edge_droplets.items():
            total_failed += rollback_droplet(name, config, env, to)
        
        # Verticals last
        vertical_droplets = {k: v for k, v in droplets.items() if v.role == "vertical"}
        for name, config in vertical_droplets.items():
            total_failed += rollback_droplet(name, config, env, to)
    
    elif target == "edge":
        edge_droplets = get_droplets_by_role("edge", env)
        if not edge_droplets:
            print_error("No edge droplets found")
            sys.exit(1)
        for name, config in edge_droplets.items():
            total_failed += rollback_droplet(name, config, env, to)
    
    elif target == "platform":
        platform_droplets = get_droplets_by_role("platform", env)
        if not platform_droplets:
            print_error("No platform droplets found")
            sys.exit(1)
        for name, config in platform_droplets.items():
            total_failed += rollback_droplet(name, config, env, to)
    
    elif target == "vertical":
        if not vertical_name:
            print_error("Vertical name required (use --vertical <name>)")
            sys.exit(1)
        droplet = get_droplet(f"vertical_{vertical_name}", env)
        if not droplet:
            print_error(f"Vertical droplet 'vertical_{vertical_name}' not found")
            sys.exit(1)
        total_failed += rollback_droplet(f"vertical_{vertical_name}", droplet, env, to)
    
    else:
        # Try to find droplet by name
        droplet = get_droplet(target, env)
        if not droplet:
            print_error(f"Droplet '{target}' not found")
            sys.exit(1)
        total_failed += rollback_droplet(target, droplet, env, to)
    
    print()
    if total_failed == 0:
        print_success("All rollbacks completed successfully")
        sys.exit(0)
    else:
        print_error("Some rollbacks failed")
        sys.exit(1)

