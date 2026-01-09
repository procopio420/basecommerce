"""Users command - manage users for tenants."""

import secrets
import string
import sys
import uuid
from datetime import datetime
from typing import Optional

import bcrypt
import typer

from basec.docker import DockerCompose
from basec.inventory import get_droplets_by_role
from basec.output import (
    print_error,
    print_header,
    print_success,
    print_table,
)

app = typer.Typer()


def get_platform_droplet():
    """Get the platform droplet (where PostgreSQL runs)."""
    platform_droplets = get_droplets_by_role("platform")
    if not platform_droplets:
        raise RuntimeError("No platform droplet found in inventory")
    # Return first platform droplet
    return next(iter(platform_droplets.values()))


def execute_sql(docker: DockerCompose, sql: str) -> str:
    """Execute SQL query on PostgreSQL."""
    # Escape quotes in SQL for shell
    escaped_sql = sql.replace('"', '\\"')
    command = f"psql -U basecommerce -d basecommerce -t -c \"{escaped_sql}\""
    return docker.exec("postgres", command, capture_output=True)


def generate_random_password(length: int = 12) -> str:
    """Generate a secure random password."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def get_password_hash(password: str) -> str:
    """Get password hash using bcrypt locally."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


@app.command()
def create(
    tenant_slug: str = typer.Argument(..., help="Tenant slug"),
    nome: str = typer.Option(..., "--nome", "-n", help="User name"),
    email: str = typer.Option(..., "--email", "-e", help="User email"),
    role: str = typer.Option("vendedor", "--role", "-r", help="User role (admin or vendedor)"),
    password: Optional[str] = typer.Option(None, "--password", "-p", help="User password (optional, generates if not provided)"),
) -> None:
    """Create a new user for a tenant."""
    print_header(f"Creating User: {email} for tenant: {tenant_slug}")

    # Validate role
    if role not in ["admin", "vendedor"]:
        print_error("Invalid role. Must be 'admin' or 'vendedor'")
        sys.exit(1)

    try:
        platform = get_platform_droplet()
        docker = DockerCompose(platform)

        # Check if tenant exists and is active (escape tenant_slug for SQL safety)
        tenant_slug_escaped = tenant_slug.replace("'", "''")
        tenant_check_sql = f"SELECT id FROM tenants WHERE slug = '{tenant_slug_escaped}' AND ativo = true;"
        tenant_result = execute_sql(docker, tenant_check_sql).strip()
        
        if not tenant_result:
            print_error(f"Tenant '{tenant_slug}' not found or inactive")
            sys.exit(1)

        tenant_id = tenant_result

        # Check if email already exists in this tenant
        email_check_sql = f"""
        SELECT COUNT(*) FROM users 
        WHERE email = '{email}' AND tenant_id = '{tenant_id}';
        """
        email_count = int(execute_sql(docker, email_check_sql).strip() or 0)
        
        if email_count > 0:
            print_error(f"User with email '{email}' already exists in tenant '{tenant_slug}'")
            sys.exit(1)

        # Generate password if not provided
        actual_password = password or generate_random_password()

        # Get password hash using bcrypt locally
        password_hash = get_password_hash(actual_password)

        # Generate user ID and timestamp
        user_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        # Escape single quotes in SQL strings
        nome_escaped = nome.replace("'", "''")
        email_escaped = email.replace("'", "''")
        password_hash_escaped = password_hash.replace("'", "''")

        # Insert user
        sql = f"""
        INSERT INTO users (id, tenant_id, nome, email, password_hash, role, ativo, created_at, updated_at)
        VALUES (
            '{user_id}',
            '{tenant_id}',
            '{nome_escaped}',
            '{email_escaped}',
            '{password_hash_escaped}',
            '{role}',
            true,
            '{now}',
            '{now}'
        );
        """

        execute_sql(docker, sql)

        print_success(f"User '{email}' created successfully")
        print_success(f"User ID: {user_id}")
        print_success(f"Role: {role}")
        if not password:
            print_success(f"Generated password: {actual_password}")
            print_success("⚠️  Save this password securely - it won't be shown again!")

    except Exception as e:
        print_error(f"Failed to create user: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


@app.command()
def list(
    tenant_slug: str = typer.Argument(..., help="Tenant slug"),
) -> None:
    """List all users for a tenant."""
    print_header(f"Users for tenant: {tenant_slug}")

    try:
        platform = get_platform_droplet()
        docker = DockerCompose(platform)

        # Get tenant ID (escape tenant_slug for SQL safety)
        tenant_slug_escaped = tenant_slug.replace("'", "''")
        tenant_check_sql = f"SELECT id FROM tenants WHERE slug = '{tenant_slug_escaped}';"
        tenant_id = execute_sql(docker, tenant_check_sql).strip()

        if not tenant_id:
            print_error(f"Tenant '{tenant_slug}' not found")
            sys.exit(1)

        # Query users
        sql = f"""
        SELECT 
            id::text,
            nome,
            email,
            role,
            CASE WHEN ativo THEN 'Active' ELSE 'Inactive' END as status,
            created_at::text
        FROM users
        WHERE tenant_id = '{tenant_id}'
        ORDER BY created_at DESC;
        """

        output = execute_sql(docker, sql)

        if not output.strip():
            print_error(f"No users found for tenant '{tenant_slug}'")
            return

        # Parse output (psql -t outputs pipe-separated values)
        rows = []
        for line in output.strip().split("\n"):
            if not line.strip():
                continue
            parts = [p.strip() for p in line.split("|")]
            # psql -t outputs: id|nome|email|role|status|created_at
            if len(parts) >= 6:
                rows.append([
                    parts[1] if len(parts) > 1 else "",  # nome
                    parts[2] if len(parts) > 2 else "",  # email
                    parts[3] if len(parts) > 3 else "",  # role
                    parts[4] if len(parts) > 4 else "",  # status
                    parts[5][:19] if len(parts) > 5 and len(parts[5]) > 19 else (parts[5] if len(parts) > 5 else ""),  # created_at
                ])

        if rows:
            print_table(
                f"Users for {tenant_slug}",
                ["Name", "Email", "Role", "Status", "Created"],
                rows,
            )
        else:
            print_error(f"No users found for tenant '{tenant_slug}'")

    except Exception as e:
        print_error(f"Failed to list users: {e}")
        sys.exit(1)


@app.command()
def disable(
    tenant_slug: str = typer.Argument(..., help="Tenant slug"),
    email: str = typer.Argument(..., help="User email"),
) -> None:
    """Disable a user."""
    print_header(f"Disabling User: {email} in tenant: {tenant_slug}")

    try:
        platform = get_platform_droplet()
        docker = DockerCompose(platform)

        # Get tenant ID (escape tenant_slug for SQL safety)
        tenant_slug_escaped = tenant_slug.replace("'", "''")
        tenant_check_sql = f"SELECT id FROM tenants WHERE slug = '{tenant_slug_escaped}';"
        tenant_id = execute_sql(docker, tenant_check_sql).strip()

        if not tenant_id:
            print_error(f"Tenant '{tenant_slug}' not found")
            sys.exit(1)

        # Update user (escape email for SQL safety)
        email_escaped = email.replace("'", "''")
        sql = f"""
        UPDATE users 
        SET ativo = false, updated_at = '{datetime.utcnow().isoformat()}' 
        WHERE email = '{email_escaped}' AND tenant_id = '{tenant_id}';
        """

        execute_sql(docker, sql)

        # Check if user was found
        check_sql = f"""
        SELECT COUNT(*) FROM users 
        WHERE email = '{email_escaped}' AND tenant_id = '{tenant_id}';
        """
        count_output = execute_sql(docker, check_sql)
        count = int(count_output.strip()) if count_output.strip() else 0

        if count == 0:
            print_error(f"User '{email}' not found in tenant '{tenant_slug}'")
            sys.exit(1)

        print_success(f"User '{email}' disabled successfully")

    except Exception as e:
        print_error(f"Failed to disable user: {e}")
        sys.exit(1)


@app.command()
def enable(
    tenant_slug: str = typer.Argument(..., help="Tenant slug"),
    email: str = typer.Argument(..., help="User email"),
) -> None:
    """Enable a user."""
    print_header(f"Enabling User: {email} in tenant: {tenant_slug}")

    try:
        platform = get_platform_droplet()
        docker = DockerCompose(platform)

        # Get tenant ID (escape tenant_slug for SQL safety)
        tenant_slug_escaped = tenant_slug.replace("'", "''")
        tenant_check_sql = f"SELECT id FROM tenants WHERE slug = '{tenant_slug_escaped}';"
        tenant_id = execute_sql(docker, tenant_check_sql).strip()

        if not tenant_id:
            print_error(f"Tenant '{tenant_slug}' not found")
            sys.exit(1)

        # Update user (escape email for SQL safety)
        email_escaped = email.replace("'", "''")
        sql = f"""
        UPDATE users 
        SET ativo = true, updated_at = '{datetime.utcnow().isoformat()}' 
        WHERE email = '{email_escaped}' AND tenant_id = '{tenant_id}';
        """

        execute_sql(docker, sql)

        # Check if user was found
        check_sql = f"""
        SELECT COUNT(*) FROM users 
        WHERE email = '{email_escaped}' AND tenant_id = '{tenant_id}';
        """
        count_output = execute_sql(docker, check_sql)
        count = int(count_output.strip()) if count_output.strip() else 0

        if count == 0:
            print_error(f"User '{email}' not found in tenant '{tenant_slug}'")
            sys.exit(1)

        print_success(f"User '{email}' enabled successfully")

    except Exception as e:
        print_error(f"Failed to enable user: {e}")
        sys.exit(1)

