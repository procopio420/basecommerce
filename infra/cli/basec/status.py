"""Status command - shows infrastructure status."""

import sys

from basec.docker import DockerCompose
from basec.inventory import list_droplets
from basec.output import (
    print_error,
    print_header,
    print_info,
    print_section,
    print_success,
    print_table,
)
from basec.ssh import SSHClientWrapper


def get_disk_usage(ssh: SSHClientWrapper) -> dict[str, str]:
    """Get disk usage information."""
    try:
        exit_code, stdout, _ = ssh.execute(
            "df -h / | tail -1",
            check=False,
            capture_output=True,
        )
        if exit_code == 0 and stdout:
            parts = stdout.strip().split()
            if len(parts) >= 5:
                return {
                    "total": parts[1],
                    "used": parts[2],
                    "available": parts[3],
                    "percent": parts[4],
                }
    except Exception:
        pass
    return {}


def check_droplet(name: str, droplet_config) -> dict:
    """Check status of a single droplet."""
    result = {
        "name": name.upper(),
        "ip": droplet_config.ip,
        "ssh_connected": False,
        "docker_running": False,
        "containers": [],
        "stats": [],
        "disk": {},
    }
    
    ssh = SSHClientWrapper(host=droplet_config.ip, user=droplet_config.user)
    
    # Check SSH connection
    try:
        if ssh.check_connection(timeout=5):
            result["ssh_connected"] = True
            ssh.connect()
            
            # Check Docker
            exit_code, _, _ = ssh.execute(
                "docker ps -q",
                check=False,
                capture_output=True,
            )
            result["docker_running"] = exit_code == 0
            
            if result["docker_running"]:
                # Get container status
                try:
                    docker = DockerCompose(droplet_config)
                    result["containers"] = docker.ps()
                    result["stats"] = docker.stats()
                except Exception as e:
                    print_error(f"Failed to get container info: {e}")
            
            # Get disk usage
            result["disk"] = get_disk_usage(ssh)
            
            ssh.disconnect()
        else:
            result["ssh_connected"] = False
    except Exception as e:
        result["ssh_connected"] = False
        result["error"] = str(e)
    
    return result


def status_command(env: str = "production") -> int:
    """Show status of all droplets.
    
    Args:
        env: Environment name (production, staging, development)
    """
    print_header(f"BaseCommerce Infrastructure Status (env: {env})")
    
    droplets = list_droplets(env)
    results = []
    
    for name, config in droplets.items():
        print_section(f"{name.upper()} ({config.ip})")
        result = check_droplet(name, config)
        results.append(result)
        
        # Print SSH status
        if result["ssh_connected"]:
            print_success("SSH: Connected")
        else:
            print_error("SSH: Cannot connect")
            if "error" in result:
                print_error(f"  Error: {result['error']}")
            continue
        
        # Print Docker status
        if result["docker_running"]:
            print_success("Docker: Running")
        else:
            print_error("Docker: Not running")
            continue
        
        # Print containers
        if result["containers"]:
            print_info("Containers:")
            container_rows = [
                [
                    container["name"],
                    container["service"],
                    container["status"],
                ]
                for container in result["containers"]
            ]
            print_table(
                "",
                ["Name", "Service", "Status"],
                container_rows,
                show_header=False,
            )
        
        # Print resource usage
        if result["stats"]:
            print_info("Resource Usage:")
            stats_rows = [
                [
                    stat["name"],
                    stat["cpu"],
                    stat["memory"],
                ]
                for stat in result["stats"]
            ]
            print_table(
                "",
                ["Container", "CPU", "Memory"],
                stats_rows,
                show_header=False,
            )
        
        # Print disk usage
        if result["disk"]:
            disk = result["disk"]
            print_info(
                f"Disk: {disk.get('used', 'N/A')} / {disk.get('total', 'N/A')} "
                f"({disk.get('percent', 'N/A')} used)"
            )
    
    # Summary
    print()
    all_connected = all(r["ssh_connected"] for r in results)
    all_docker_running = all(r.get("docker_running", False) for r in results if r["ssh_connected"])
    
    if all_connected and all_docker_running:
        print_success("All droplets are healthy")
        return 0
    else:
        print_error("Some droplets have issues")
        return 1

