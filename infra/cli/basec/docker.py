"""Docker Compose helpers for remote execution."""

import json
import shlex
import tempfile
import time
from pathlib import Path
from typing import Optional, Union

import yaml

from basec.inventory import DropletConfig
from basec.ssh import SSHClientWrapper


class DockerComposeError(Exception):
    """Exception raised for Docker Compose errors."""
    
    def __init__(self, message: str, command: str, exit_code: int, stdout: str = "", stderr: str = ""):
        super().__init__(message)
        self.command = command
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr


class DockerCompose:
    """Helper class for docker compose operations via SSH."""
    
    def __init__(self, droplet: DropletConfig):
        """Initialize with droplet configuration.
        
        Args:
            droplet: Droplet configuration
        """
        self.droplet = droplet
        self.ssh = SSHClientWrapper(host=droplet.ip, user=droplet.user)
        # Use remote_dir from droplet config (will be resolved on first use)
        self._remote_dir: Optional[str] = None
    
    @property
    def remote_dir(self) -> str:
        """Get the remote directory, with automatic fallback to legacy path.
        
        Returns:
            Remote directory path (new structure or legacy fallback)
        """
        if self._remote_dir is not None:
            return self._remote_dir
        
        # If remote_dir is explicitly set in droplet config, use it directly (no fallback)
        if self.droplet.remote_dir:
            self._remote_dir = self.droplet.remote_dir
            return self._remote_dir
        
        # Ensure SSH connection is established
        if self.ssh.client is None:
            self.ssh.connect()
        
        # Get preferred directory from droplet config
        preferred_dir = self.droplet.get_remote_dir()
        
        # Check if preferred directory exists and has docker-compose.yml
        exit_code, _, _ = self.ssh.execute(
            f"test -f {shlex.quote(preferred_dir)}/docker-compose.yml",
            check=False,
            capture_output=True,
        )
        
        if exit_code == 0:
            self._remote_dir = preferred_dir
            return self._remote_dir
        
        # Fallback to legacy directory
        legacy_dir = "/opt/basecommerce"
        exit_code, _, _ = self.ssh.execute(
            f"test -f {shlex.quote(legacy_dir)}/docker-compose.yml",
            check=False,
            capture_output=True,
        )
        
        if exit_code == 0:
            # Legacy directory exists, use it
            self._remote_dir = legacy_dir
            return self._remote_dir
        
        # Neither exists - raise informative error
        raise RuntimeError(
            f"Neither new directory ({preferred_dir}) nor legacy directory ({legacy_dir}) "
            f"exists on droplet {self.droplet.ip}. "
            f"Please ensure docker-compose.yml exists in one of these locations."
        )
    
    def _run_compose(
        self,
        command: str,
        capture_output: bool = True,
        timeout: Optional[int] = None,
    ) -> tuple[int, str, str]:
        """Run docker compose command on remote host.
        
        Args:
            command: Docker compose command (e.g., "ps --format json")
            capture_output: Capture stdout/stderr instead of printing
            timeout: Command timeout in seconds (default: SSH default)
        
        Returns:
            Tuple of (exit_code, stdout, stderr)
        
        Raises:
            RuntimeError: If command fails (always raises, never returns non-zero silently)
        """
        full_command = f"cd {shlex.quote(self.remote_dir)} && docker compose {command}"
        
        exit_code, stdout, stderr = self.ssh.execute(
            full_command,
            check=False,
            capture_output=capture_output,
            timeout=timeout,
        )
        
        # Always raise error if exit_code != 0
        if exit_code != 0:
            # Get last 500 chars of stderr for error message
            stderr_tail = stderr[-500:] if stderr else ""
            
            error_msg = (
                f"Docker compose command failed (exit code {exit_code}):\n"
                f"Command: {command}\n"
                f"Directory: {self.remote_dir}\n"
            )
            
            if stderr_tail:
                error_msg += f"Stderr (last 500 chars):\n{stderr_tail}\n"
            
            raise RuntimeError(error_msg)
        
        return exit_code, stdout, stderr
    
    def ps(self) -> list[dict[str, str]]:
        """Get status of all containers.
        
        Returns:
            List of dicts with container info (name, status, service, etc.)
        """
        exit_code, stdout, stderr = self._run_compose("ps --format '{{json .}}'")
        
        containers = []
        for line in stdout.strip().split("\n"):
            if not line.strip():
                continue
            try:
                container = json.loads(line)
                containers.append({
                    "name": container.get("Name", ""),
                    "status": container.get("Status", ""),
                    "service": container.get("Service", ""),
                    "ports": container.get("Ports", ""),
                })
            except json.JSONDecodeError:
                # Skip invalid JSON lines
                continue
        
        return containers
    
    def logs(
        self,
        service: Optional[str] = None,
        follow: bool = False,
        tail: int = 100,
    ) -> None:
        """Get logs from containers.
        
        Args:
            service: Service name to filter (optional)
            follow: Follow log output (streaming)
            tail: Number of lines to show (default: 100)
        """
        command_parts = ["logs", f"--tail={tail}"]
        
        if follow:
            command_parts.append("--follow")
        
        if service:
            command_parts.append(shlex.quote(service))
        
        command = " ".join(command_parts)
        full_command = f"cd {shlex.quote(self.remote_dir)} && docker compose {command}"
        
        if follow:
            # Use execute_stream with pty=True for better compatibility
            try:
                exit_code = self.ssh.execute_stream(full_command, pty=True)
                if exit_code != 0:
                    # Non-zero exit is OK for follow (user might interrupt)
                    pass
            except KeyboardInterrupt:
                # User interrupted, that's OK for follow mode
                pass
            except Exception as e:
                # Fallback to polling if streaming fails (e.g., CI environments)
                self._logs_follow_polling(service, tail)
        else:
            # For non-follow mode, capture and print
            exit_code, stdout, stderr = self._run_compose(command, capture_output=True)
            if stdout:
                print(stdout, end="")
            if stderr:
                print(stderr, end="", file=__import__("sys").stderr)
    
    def _logs_follow_polling(
        self,
        service: Optional[str] = None,
        tail: int = 100,
    ) -> None:
        """Fallback polling implementation for logs follow.
        
        Used when execute_stream fails (e.g., CI environments without PTY).
        """
        last_timestamp = time.time()
        command_parts = ["logs", f"--tail={tail}"]
        
        if service:
            command_parts.append(shlex.quote(service))
        
        try:
            while True:
                # Get logs since last timestamp
                since_command = " ".join(command_parts + [f"--since={int(last_timestamp)}"])
                exit_code, stdout, stderr = self._run_compose(since_command, capture_output=True)
                
                if stdout:
                    print(stdout, end="", flush=True)
                
                last_timestamp = time.time()
                time.sleep(1)  # Poll every 1 second
        except KeyboardInterrupt:
            pass
    
    def pull(self) -> None:
        """Pull latest images."""
        self._run_compose("pull", capture_output=False)
    
    def up(self, detach: bool = True, pull: bool = False, remove_orphans: bool = True) -> None:
        """Start services.
        
        Args:
            detach: Run in detached mode (default: True)
            pull: Pull latest images before starting (default: False)
            remove_orphans: Remove orphaned containers (default: True)
        """
        if pull:
            self.pull()
        
        command_parts = ["up"]
        
        if detach:
            command_parts.append("-d")
        
        if remove_orphans:
            command_parts.append("--remove-orphans")
        
        command = " ".join(command_parts)
        self._run_compose(command, capture_output=False)
    
    def down(self) -> None:
        """Stop and remove containers."""
        self._run_compose("down", capture_output=False)
    
    def restart(self, service: Optional[str] = None) -> None:
        """Restart services.
        
        Args:
            service: Service name to restart (optional, restarts all if not specified)
        """
        command_parts = ["restart"]
        
        if service:
            command_parts.append(shlex.quote(service))
        
        command = " ".join(command_parts)
        self._run_compose(command, capture_output=False)
    
    def exec(
        self,
        service: str,
        command: Union[str, list[str]],
        capture_output: bool = True,
    ) -> str:
        """Execute command in a container.
        
        Args:
            service: Service name
            command: Command to execute (string or list of strings)
            capture_output: Capture output (default: True)
        
        Returns:
            Command output (if capture_output is True)
        
        Raises:
            RuntimeError: If command fails
        """
        # Convert command to list if string
        if isinstance(command, str):
            # Parse string command into list (respects quoting)
            command_list = shlex.split(command)
        else:
            command_list = command
        
        # Join command list with proper quoting using shlex.join (Python 3.8+)
        try:
            command_str = shlex.join(command_list)
        except AttributeError:
            # Fallback for Python < 3.8
            command_str = " ".join(shlex.quote(arg) for arg in command_list)
        
        compose_command = f"exec -T {shlex.quote(service)} {command_str}"
        exit_code, stdout, stderr = self._run_compose(compose_command, capture_output=capture_output)
        
        return stdout
    
    def stats(self) -> list[dict[str, str]]:
        """Get container resource usage statistics.
        
        Returns:
            List of dicts with stats (name, cpu, memory, etc.)
        """
        # Use docker stats instead of compose
        full_command = f"cd {shlex.quote(self.remote_dir)} && docker stats --no-stream --format '{{{{json .}}}}'"
        
        exit_code, stdout, stderr = self.ssh.execute(
            full_command,
            check=False,
            capture_output=True,
        )
        
        if exit_code != 0:
            return []
        
        stats = []
        for line in stdout.strip().split("\n"):
            if not line.strip():
                continue
            try:
                stat = json.loads(line)
                stats.append({
                    "name": stat.get("Name", ""),
                    "cpu": stat.get("CPUPerc", ""),
                    "memory": stat.get("MemUsage", ""),
                    "memory_percent": stat.get("MemPerc", ""),
                    "net_io": stat.get("NetIO", ""),
                    "block_io": stat.get("BlockIO", ""),
                })
            except json.JSONDecodeError:
                continue
        
        return stats
    
    def set_image_tags(self, tag: str, registry: str = "ghcr.io/procopio420/basecommerce") -> None:
        """Set image tags for services via docker-compose.override.yml.
        
        This method generates a docker-compose.override.yml file that overrides
        image tags for services that have build context (auth, outbox-relay, 
        engines-worker, construction). Official images (nginx, postgres, redis) 
        are not modified.
        
        Args:
            tag: Image tag to use (e.g., 'sha-abc123' or 'latest-staging')
            registry: Docker registry prefix (default: ghcr.io/procopio420/basecommerce)
        """
        role = self.droplet.role
        
        # Build override structure
        override = {"services": {}}
        
        if role == "edge":
            override["services"]["auth"] = {"image": f"{registry}/auth:{tag}"}
        elif role == "platform":
            override["services"]["outbox-relay"] = {"image": f"{registry}/outbox-relay:{tag}"}
            override["services"]["engines-worker"] = {"image": f"{registry}/engines-worker:{tag}"}
        elif role == "vertical":
            # For verticals, use the vertical name from droplet config
            vertical_name = self.droplet.vertical
            if not vertical_name:
                raise ValueError("Vertical name is required for vertical role droplets")
            override["services"][vertical_name] = {"image": f"{registry}/{vertical_name}:{tag}"}
        else:
            raise ValueError(f"Unknown role for image tag mapping: {role}")
        
        # Convert to YAML
        override_yaml = yaml.dump(override, default_flow_style=False, sort_keys=False)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(override_yaml)
            temp_path = Path(f.name)
        
        try:
            # Upload to remote
            remote_path = f"{self.remote_dir}/docker-compose.override.yml"
            self.ssh.upload_file(temp_path, remote_path)
            
            # Set permissions
            self.ssh.execute(f"chmod 644 {shlex.quote(remote_path)}", check=True)
        finally:
            # Clean up temp file
            temp_path.unlink(missing_ok=True)
    
    def get_current_tag(self) -> Optional[str]:
        """Get the current image tag being used from docker-compose.override.yml.
        
        Returns:
            Current tag if override exists, None otherwise
        """
        remote_path = f"{self.remote_dir}/docker-compose.override.yml"
        
        # Check if override file exists
        exit_code, stdout, stderr = self.ssh.execute(
            f"test -f {shlex.quote(remote_path)} && cat {shlex.quote(remote_path)} || echo ''",
            check=False,
            capture_output=True,
        )
        
        if exit_code != 0 or not stdout.strip():
            return None
        
        try:
            override_data = yaml.safe_load(stdout)
            if not override_data or "services" not in override_data:
                return None
            
            # Extract tag from first service image
            for service_name, service_config in override_data["services"].items():
                if "image" in service_config:
                    image = service_config["image"]
                    # Extract tag (format: registry/service:tag)
                    if ":" in image:
                        tag = image.split(":")[-1]
                        return tag
        except (yaml.YAMLError, KeyError, AttributeError):
            pass
        
        return None
