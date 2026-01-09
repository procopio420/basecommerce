"""Smoke tests for infrastructure validation."""

import sys
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
)
from basec.ssh import SSHClientWrapper

app = typer.Typer()


def test_container_running(docker: DockerCompose, service: str) -> tuple[bool, str]:
    """Test if a container is running."""
    try:
        containers = docker.ps()
        for container in containers:
            if container["service"] == service or container["name"] == service:
                if "Up" in container["status"] or "running" in container["status"].lower():
                    return True, "OK"
        return False, "Container not running"
    except Exception as e:
        return False, f"Error: {e}"


def test_http_endpoint(ssh: SSHClientWrapper, url: str) -> tuple[bool, str]:
    """Test HTTP endpoint accessibility."""
    try:
        exit_code, stdout, _ = ssh.execute(
            f"curl -sf {url}",
            check=False,
            capture_output=True,
        )
        if exit_code == 0 and stdout:
            return True, "OK"
        return False, "Endpoint not accessible"
    except Exception as e:
        return False, f"Error: {e}"


def smoke_edge(droplet_name: str, config) -> int:
    """Run smoke tests for Edge droplet."""
    print_section(f"Edge Smoke Tests: {droplet_name}")
    
    ssh = SSHClientWrapper(host=config.ip, user=config.user)
    ssh.connect()
    
    docker = DockerCompose(config)
    failed = 0
    
    # Test nginx container
    ok, msg = test_container_running(docker, "nginx")
    if ok:
        print_success("Nginx running")
    else:
        print_error(f"Nginx running: {msg}")
        failed = 1
    
    # Test auth container
    ok, msg = test_container_running(docker, "auth")
    if ok:
        print_success("Auth service running")
    else:
        print_error(f"Auth service running: {msg}")
        failed = 1
    
    # Test nginx config
    try:
        output = docker.exec("nginx", "nginx -t", capture_output=True)
        if "successful" in output.lower():
            print_success("Nginx config valid")
        else:
            print_error("Nginx config invalid")
            failed = 1
    except Exception as e:
        print_error(f"Nginx config: {e}")
        failed = 1
    
    # Test health endpoint
    ok, msg = test_http_endpoint(ssh, "http://localhost/health")
    if ok:
        print_success("Health endpoint")
    else:
        print_error(f"Health endpoint: {msg}")
        failed = 1
    
    # Test auth health
    ok, msg = test_http_endpoint(ssh, "http://localhost/auth/health")
    if ok:
        print_success("Auth health")
    else:
        print_error(f"Auth health: {msg}")
        failed = 1
    
    # Test tenant.json
    ok, msg = test_http_endpoint(ssh, "http://localhost/tenant.json")
    if ok:
        print_success("Tenant JSON (default)")
    else:
        print_error(f"Tenant JSON: {msg}")
        failed = 1
    
    ssh.disconnect()
    return failed


def smoke_platform(droplet_name: str, config) -> int:
    """Run smoke tests for Platform droplet."""
    print_section(f"Platform Smoke Tests: {droplet_name}")
    
    ssh = SSHClientWrapper(host=config.ip, user=config.user)
    ssh.connect()
    
    docker = DockerCompose(config)
    failed = 0
    
    # Test PostgreSQL
    try:
        output = docker.exec(
            "postgres",
            "pg_isready -U basecommerce",
            capture_output=True,
        )
        if "accepting connections" in output.lower():
            # Get version
            version_output = docker.exec(
                "postgres",
                "psql -U basecommerce -t -c 'SELECT version();'",
                capture_output=True,
            )
            version = version_output.strip().split()[0] if version_output else "unknown"
            print_success(f"PostgreSQL: OK ({version})")
        else:
            print_error("PostgreSQL: Not ready")
            failed = 1
    except Exception as e:
        print_error(f"PostgreSQL: {e}")
        failed = 1
    
    # Test PostgreSQL queries
    try:
        docker.exec("postgres", "psql -U basecommerce -c 'SELECT 1;'", capture_output=True)
        print_success("PostgreSQL queries")
    except Exception as e:
        print_error(f"PostgreSQL queries: {e}")
        failed = 1
    
    # Test Redis
    try:
        output = docker.exec("redis", "redis-cli ping", capture_output=True)
        if "PONG" in output.upper():
            # Get version
            version_output = docker.exec(
                "redis",
                "redis-cli INFO server | grep redis_version",
                capture_output=True,
            )
            version = "unknown"
            if version_output:
                for line in version_output.split("\n"):
                    if "redis_version" in line:
                        version = line.split(":")[1].strip()
            print_success(f"Redis: OK (v{version})")
        else:
            print_error("Redis: Not responding")
            failed = 1
    except Exception as e:
        print_error(f"Redis: {e}")
        failed = 1
    
    # Test Redis Streams
    try:
        docker.exec("redis", "redis-cli XINFO HELP", capture_output=True)
        print_success("Redis Streams")
    except Exception as e:
        print_error(f"Redis Streams: {e}")
        failed = 1
    
    # Test Outbox Relay
    ok, msg = test_container_running(docker, "outbox-relay")
    if ok:
        print_success("Outbox Relay: Running")
    else:
        print_error(f"Outbox Relay: {msg}")
        failed = 1
    
    # Test Engines Worker
    ok, msg = test_container_running(docker, "engines-worker")
    if ok:
        print_success("Engines Worker: Running")
    else:
        print_error(f"Engines Worker: {msg}")
        failed = 1
    
    ssh.disconnect()
    return failed


def smoke_vertical(droplet_name: str, config) -> int:
    """Run smoke tests for Vertical droplet."""
    print_section(f"Vertical Smoke Tests: {droplet_name}")
    
    ssh = SSHClientWrapper(host=config.ip, user=config.user)
    ssh.connect()
    
    docker = DockerCompose(config)
    failed = 0
    
    # Determine service name (usually matches vertical name or "construction")
    service_name = config.vertical or "construction"
    
    # Test container running
    ok, msg = test_container_running(docker, service_name)
    if ok:
        print_success("Container running")
    else:
        print_error(f"Container running: {msg}")
        failed = 1
    
    # Test health endpoint
    ok, msg = test_http_endpoint(ssh, f"http://localhost:8000/health")
    if ok:
        print_success("Health endpoint")
    else:
        print_error(f"Health endpoint: {msg}")
        failed = 1
    
    # Test OpenAPI docs
    ok, msg = test_http_endpoint(ssh, "http://localhost:8000/docs")
    if ok:
        print_success("OpenAPI docs")
    else:
        print_error(f"OpenAPI docs: {msg}")
        failed = 1
    
    # Test database connectivity
    try:
        # Use single quotes to avoid shell escaping issues
        db_test = docker.exec(
            service_name,
            "python -c 'from sqlalchemy import create_engine, text; import os; e = create_engine(os.environ.get(\"DATABASE_URL\", \"\")); c = e.connect(); c.execute(text(\"SELECT 1\")); print(\"OK\")'",
            capture_output=True,
        )
        if "OK" in db_test:
            print_success("Database connection")
        else:
            print_error(f"Database connection: {db_test}")
            failed = 1
    except Exception as e:
        print_error(f"Database connection: {e}")
        failed = 1
    
    # Test Redis connectivity
    try:
        redis_test = docker.exec(
            service_name,
            "python -c 'import redis; import os; r = redis.from_url(os.environ.get(\"REDIS_URL\", \"redis://localhost:6379\")); r.ping(); print(\"OK\")'",
            capture_output=True,
        )
        if "OK" in redis_test:
            print_success("Redis connection")
        else:
            print_error(f"Redis connection: {redis_test}")
            failed = 1
    except Exception as e:
        print_error(f"Redis connection: {e}")
        failed = 1
    
    ssh.disconnect()
    return failed


@app.command()
def smoke(
    target: Optional[str] = typer.Argument(
        None,
        help="Target to test: 'edge', 'platform', 'vertical <name>', or 'all' (default: all)",
    ),
    vertical_name: Optional[str] = typer.Option(
        None,
        "--vertical",
        "-v",
        help="Vertical name (required if target is 'vertical')",
    ),
    env: str = typer.Option("production", "--env", "-e", help="Environment name"),
) -> None:
    """Run smoke tests on infrastructure."""
    print_header(f"BaseCommerce Smoke Tests (env: {env})")
    
    total_failed = 0
    
    if target is None or target == "all":
        # Test all droplets
        droplets = list_droplets(env)
        for name, config in droplets.items():
            if config.role == "edge":
                total_failed += smoke_edge(name, config)
            elif config.role == "platform":
                total_failed += smoke_platform(name, config)
            elif config.role == "vertical":
                total_failed += smoke_vertical(name, config)
    elif target == "edge":
        edge_droplets = get_droplets_by_role("edge", env)
        if not edge_droplets:
            print_error("No edge droplets found")
            sys.exit(1)
        for name, config in edge_droplets.items():
            total_failed += smoke_edge(name, config)
    elif target == "platform":
        platform_droplets = get_droplets_by_role("platform", env)
        if not platform_droplets:
            print_error("No platform droplets found")
            sys.exit(1)
        for name, config in platform_droplets.items():
            total_failed += smoke_platform(name, config)
    elif target == "vertical":
        if not vertical_name:
            print_error("Vertical name required when testing vertical (use --vertical <name>)")
            sys.exit(1)
        droplet = get_droplet(f"vertical_{vertical_name}", env)
        if not droplet:
            print_error(f"Vertical droplet 'vertical_{vertical_name}' not found")
            sys.exit(1)
        total_failed += smoke_vertical(f"vertical_{vertical_name}", droplet)
    else:
        # Try to find droplet by name
        droplet = get_droplet(target, env)
        if not droplet:
            print_error(f"Droplet '{target}' not found")
            sys.exit(1)
        
        if droplet.role == "edge":
            total_failed += smoke_edge(target, droplet)
        elif droplet.role == "platform":
            total_failed += smoke_platform(target, droplet)
        elif droplet.role == "vertical":
            total_failed += smoke_vertical(target, droplet)
    
    print()
    if total_failed == 0:
        print_success("All Tests Passed ✓")
        sys.exit(0)
    else:
        print_error("Some Tests Failed ✗")
        sys.exit(1)

