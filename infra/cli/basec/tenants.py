"""Tenants command - manage tenants."""

import sys
import uuid
from datetime import datetime

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


@app.command()
def list() -> None:
    """List all tenants."""
    print_header("Tenants")
    
    try:
        platform = get_platform_droplet()
        docker = DockerCompose(platform)
        
        # Query tenants
        sql = """
        SELECT 
            id::text,
            nome,
            slug,
            email,
            CASE WHEN ativo THEN 'Active' ELSE 'Inactive' END as status,
            created_at::text
        FROM tenants
        ORDER BY created_at DESC;
        """
        
        output = execute_sql(docker, sql)
        
        if not output.strip():
            print_error("No tenants found")
            return
        
        # Parse output (psql -t outputs pipe-separated values)
        rows = []
        for line in output.strip().split("\n"):
            if not line.strip():
                continue
            parts = [p.strip() for p in line.split("|")]
            # psql -t outputs: id|nome|slug|email|status|created_at
            if len(parts) >= 6:
                rows.append([
                    parts[1] if len(parts) > 1 else "",  # nome
                    parts[2] if len(parts) > 2 else "",  # slug
                    parts[3] if len(parts) > 3 else "",  # email
                    parts[4] if len(parts) > 4 else "",  # status
                    parts[5][:19] if len(parts) > 5 and len(parts[5]) > 19 else (parts[5] if len(parts) > 5 else ""),  # created_at
                ])
        
        if rows:
            print_table(
                "Tenants",
                ["Name", "Slug", "Email", "Status", "Created"],
                rows,
            )
        else:
            print_error("No tenants found")
    
    except Exception as e:
        print_error(f"Failed to list tenants: {e}")
        sys.exit(1)


@app.command()
def create(
    slug: str = typer.Argument(..., help="Tenant slug (subdomain identifier)"),
    nome: str = typer.Option(..., "--nome", "-n", help="Tenant name"),
    email: str = typer.Option(..., "--email", "-e", help="Tenant email"),
    cnpj: str = typer.Option(None, "--cnpj", "-c", help="CNPJ (optional)"),
    telefone: str = typer.Option(None, "--telefone", "-t", help="Phone number (optional)"),
    vertical: str = typer.Option(
        "construction",
        "--vertical",
        "-v",
        help="Vertical name (default: construction)",
    ),
) -> None:
    """Create a new tenant."""
    print_header(f"Creating Tenant: {slug}")
    
    try:
        platform = get_platform_droplet()
        docker = DockerCompose(platform)
        
        # Generate UUID
        tenant_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        # Build SQL
        cnpj_part = f"'{cnpj}'" if cnpj else "NULL"
        telefone_part = f"'{telefone}'" if telefone else "NULL"
        
        # Escape single quotes in SQL strings
        nome_escaped = nome.replace("'", "''")
        email_escaped = email.replace("'", "''")
        slug_escaped = slug.replace("'", "''")
        
        sql = f"""
        INSERT INTO tenants (id, nome, slug, email, cnpj, telefone, ativo, created_at, updated_at)
        VALUES (
            '{tenant_id}',
            '{nome_escaped}',
            '{slug_escaped}',
            '{email_escaped}',
            {cnpj_part},
            {telefone_part},
            true,
            '{now}',
            '{now}'
        );
        """
        
        execute_sql(docker, sql)
        
        # Create default branding (optional)
        try:
            branding_sql = f"""
            INSERT INTO tenant_branding (tenant_id, primary_color, secondary_color, created_at, updated_at)
            VALUES (
                '{tenant_id}',
                '#1a73e8',
                '#ea4335',
                '{now}',
                '{now}'
            )
            ON CONFLICT (tenant_id) DO NOTHING;
            """
            execute_sql(docker, branding_sql)
        except Exception:
            # Branding is optional, continue if it fails
            pass
        
        print_success(f"Tenant '{slug}' created successfully")
        print_success(f"Tenant ID: {tenant_id}")
        print_success(f"Access via: https://{slug}.basecommerce.com.br")
    
    except Exception as e:
        print_error(f"Failed to create tenant: {e}")
        sys.exit(1)


@app.command()
def disable(
    slug: str = typer.Argument(..., help="Tenant slug to disable"),
) -> None:
    """Disable a tenant."""
    print_header(f"Disabling Tenant: {slug}")
    
    try:
        platform = get_platform_droplet()
        docker = DockerCompose(platform)
        
        sql = f"UPDATE tenants SET ativo = false, updated_at = '{datetime.utcnow().isoformat()}' WHERE slug = '{slug}';"
        
        output = execute_sql(docker, sql)
        
        # Check if tenant was found
        check_sql = f"SELECT COUNT(*) FROM tenants WHERE slug = '{slug}';"
        count_output = execute_sql(docker, check_sql)
        count = int(count_output.strip()) if count_output.strip() else 0
        
        if count == 0:
            print_error(f"Tenant '{slug}' not found")
            sys.exit(1)
        
        print_success(f"Tenant '{slug}' disabled successfully")
    
    except Exception as e:
        print_error(f"Failed to disable tenant: {e}")
        sys.exit(1)


@app.command()
def enable(
    slug: str = typer.Argument(..., help="Tenant slug to enable"),
) -> None:
    """Enable a tenant."""
    print_header(f"Enabling Tenant: {slug}")
    
    try:
        platform = get_platform_droplet()
        docker = DockerCompose(platform)
        
        sql = f"UPDATE tenants SET ativo = true, updated_at = '{datetime.utcnow().isoformat()}' WHERE slug = '{slug}';"
        
        execute_sql(docker, sql)
        
        # Check if tenant was found
        check_sql = f"SELECT COUNT(*) FROM tenants WHERE slug = '{slug}';"
        count_output = execute_sql(docker, check_sql)
        count = int(count_output.strip()) if count_output.strip() else 0
        
        if count == 0:
            print_error(f"Tenant '{slug}' not found")
            sys.exit(1)
        
        print_success(f"Tenant '{slug}' enabled successfully")
    
    except Exception as e:
        print_error(f"Failed to enable tenant: {e}")
        sys.exit(1)

