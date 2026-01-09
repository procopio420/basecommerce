"""Inventory management - reads and validates infrastructure configuration."""

from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field, field_validator

# Import output only when needed to avoid circular imports


class DropletConfig(BaseModel):
    """Configuration for a single droplet."""
    
    ip: str = Field(..., description="IP address of the droplet")
    user: str = Field(default="root", description="SSH user")
    role: str = Field(..., description="Role: edge, platform, or vertical")
    hostname: Optional[str] = Field(None, description="Hostname")
    description: Optional[str] = Field(None, description="Description")
    vertical: Optional[str] = Field(None, description="Vertical name (if role is vertical)")
    remote_dir: Optional[str] = Field(None, description="Remote directory path (auto-computed if not set)")
    
    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        """Validate role is one of the allowed values."""
        allowed = {"edge", "platform", "vertical"}
        if v not in allowed:
            raise ValueError(f"Role must be one of {allowed}")
        return v
    
    @field_validator("vertical")
    @classmethod
    def validate_vertical(cls, v: Optional[str], info) -> Optional[str]:
        """Validate vertical is set when role is vertical."""
        if info.data.get("role") == "vertical" and not v:
            raise ValueError("Vertical name is required when role is 'vertical'")
        return v
    
    def get_remote_dir(self) -> str:
        """Get the remote directory path for this droplet.
        
        Returns:
            Remote directory path based on role and vertical name.
        """
        if self.remote_dir:
            return self.remote_dir
        
        if self.role == "edge":
            return "/opt/basecommerce/edge"
        elif self.role == "platform":
            return "/opt/basecommerce/platform"
        elif self.role == "vertical":
            if not self.vertical:
                raise ValueError("Vertical name is required for vertical droplets")
            return f"/opt/basecommerce/verticals/{self.vertical}"
        else:
            raise ValueError(f"Unknown role: {self.role}")


class Inventory(BaseModel):
    """Infrastructure inventory."""
    
    droplets: dict[str, DropletConfig] = Field(..., description="Droplet configurations")


_inventory_cache: dict[str, Inventory] = {}


def get_inventory_path() -> Path:
    """Get the path to inventory.yaml relative to the CLI."""
    # CLI is in infra/cli/, inventory.yaml is in infra/
    cli_dir = Path(__file__).parent.parent.parent
    return cli_dir / "inventory.yaml"


def load_inventory(env: str = "production") -> Inventory:
    """Load and validate inventory from YAML file for a specific environment.
    
    Args:
        env: Environment name (production, staging, etc.)
    
    Returns:
        Inventory for the specified environment
    """
    global _inventory_cache
    
    # Check cache
    cache_key = env
    if cache_key in _inventory_cache:
        return _inventory_cache[cache_key]
    
    inventory_path = get_inventory_path()
    
    if not inventory_path.exists():
        from basec.output import print_error
        print_error(f"Inventory file not found: {inventory_path}")
        raise FileNotFoundError(f"Inventory file not found: {inventory_path}")
    
    try:
        with open(inventory_path, "r") as f:
            data = yaml.safe_load(f)
        
        # Support new structure: {production: {...}, staging: {...}, droplets: {...}}
        if env in data:
            # New structure: environment-specific
            droplets_data = data[env]
        elif "droplets" in data:
            # Old structure: backward compatibility (defaults to production)
            droplets_data = data["droplets"]
        else:
            # Fallback: assume top-level is droplets
            droplets_data = data
        
        # Filter out empty IPs (placeholders)
        filtered_droplets = {}
        for name, config in droplets_data.items():
            if isinstance(config, dict) and config.get("ip"):
                filtered_droplets[name] = config
        
        if not filtered_droplets:
            from basec.output import print_error
            print_error(f"No droplets configured for environment '{env}'. Check inventory.yaml")
            raise ValueError(f"No droplets configured for environment '{env}'")
        
        inventory = Inventory(droplets=filtered_droplets)
        _inventory_cache[cache_key] = inventory
        return inventory
    except Exception as e:
        from basec.output import print_error
        print_error(f"Failed to load inventory for '{env}': {e}")
        raise


def get_droplet(name: str, env: str = "production") -> Optional[DropletConfig]:
    """Get a specific droplet by name.
    
    Args:
        name: Droplet name
        env: Environment name
    """
    inventory = load_inventory(env)
    return inventory.droplets.get(name)


def get_droplets_by_role(role: str, env: str = "production") -> dict[str, DropletConfig]:
    """Get all droplets with a specific role.
    
    Args:
        role: Role (edge, platform, vertical)
        env: Environment name
    """
    inventory = load_inventory(env)
    return {name: droplet for name, droplet in inventory.droplets.items() if droplet.role == role}


def list_droplets(env: str = "production") -> dict[str, DropletConfig]:
    """List all droplets.
    
    Args:
        env: Environment name
    """
    inventory = load_inventory(env)
    return inventory.droplets

