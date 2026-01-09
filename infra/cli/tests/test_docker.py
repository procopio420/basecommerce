"""Unit tests for DockerCompose helper."""

import json
import unittest
from unittest.mock import MagicMock, patch

from basec.docker import DockerCompose, DockerComposeError
from basec.inventory import DropletConfig


class TestDockerCompose(unittest.TestCase):
    """Test cases for DockerCompose helper."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.droplet = DropletConfig(
            ip="192.168.1.1",
            role="edge",
            user="root",
        )
        self.docker = DockerCompose(self.droplet)
    
    @patch('basec.docker.SSHClientWrapper')
    def test_ps_parses_json_lines(self, mock_ssh_class):
        """Test that ps() correctly parses JSON lines."""
        # Mock SSH execute
        mock_ssh = MagicMock()
        mock_ssh_class.return_value = mock_ssh
        mock_ssh.client = None
        
        # Sample JSON output (one container per line)
        json_output = '\n'.join([
            json.dumps({
                "Name": "basecommerce-nginx",
                "Status": "Up 2 hours",
                "Service": "nginx",
                "Ports": "0.0.0.0:80->80/tcp"
            }),
            json.dumps({
                "Name": "basecommerce-auth",
                "Status": "Up 2 hours",
                "Service": "auth",
                "Ports": ""
            }),
        ])
        
        def mock_execute(command, check=False, capture_output=True, timeout=None):
            if "test -f" in command and "docker-compose.yml" in command:
                if "/opt/basecommerce/docker-compose.yml" in command:
                    return (0, "", "")  # Legacy exists
                return (1, "", "")  # New doesn't exist
            # Return JSON output for ps command
            return (0, json_output, "")
        
        mock_ssh.execute.side_effect = mock_execute
        
        # Create new instance to use mocked SSH
        docker = DockerCompose(self.droplet)
        docker.ssh = mock_ssh
        
        containers = docker.ps()
        
        self.assertEqual(len(containers), 2)
        self.assertEqual(containers[0]["name"], "basecommerce-nginx")
        self.assertEqual(containers[0]["service"], "nginx")
        self.assertEqual(containers[1]["name"], "basecommerce-auth")
        self.assertEqual(containers[1]["service"], "auth")
    
    @patch('basec.docker.SSHClientWrapper')
    def test_ps_skips_invalid_json(self, mock_ssh_class):
        """Test that ps() skips invalid JSON lines."""
        mock_ssh = MagicMock()
        mock_ssh_class.return_value = mock_ssh
        mock_ssh.client = None
        
        # Mix of valid and invalid JSON
        json_output = '\n'.join([
            json.dumps({"Name": "valid", "Status": "Up", "Service": "test"}),
            "invalid json line",
            json.dumps({"Name": "valid2", "Status": "Up", "Service": "test2"}),
            "",  # Empty line
        ])
        
        def mock_execute(command, check=False, capture_output=True, timeout=None):
            if "test -f" in command and "docker-compose.yml" in command:
                if "/opt/basecommerce/docker-compose.yml" in command:
                    return (0, "", "")  # Legacy exists
                return (1, "", "")  # New doesn't exist
            return (0, json_output, "")
        
        mock_ssh.execute.side_effect = mock_execute
        
        docker = DockerCompose(self.droplet)
        docker.ssh = mock_ssh
        
        containers = docker.ps()
        
        # Should only have 2 valid containers
        self.assertEqual(len(containers), 2)
        self.assertEqual(containers[0]["name"], "valid")
        self.assertEqual(containers[1]["name"], "valid2")
    
    @patch('basec.docker.SSHClientWrapper')
    def test_stats_parses_json_lines(self, mock_ssh_class):
        """Test that stats() correctly parses JSON lines."""
        mock_ssh = MagicMock()
        mock_ssh_class.return_value = mock_ssh
        mock_ssh.client = None
        
        json_output = '\n'.join([
            json.dumps({
                "Name": "basecommerce-nginx",
                "CPUPerc": "0.50%",
                "MemUsage": "15MiB / 1GiB",
                "MemPerc": "1.50%",
                "NetIO": "1.2kB / 856B",
                "BlockIO": "0B / 0B"
            }),
            json.dumps({
                "Name": "basecommerce-auth",
                "CPUPerc": "0.25%",
                "MemUsage": "10MiB / 1GiB",
                "MemPerc": "1.00%",
                "NetIO": "500B / 200B",
                "BlockIO": "0B / 0B"
            }),
        ])
        
        def mock_execute(command, check=False, capture_output=True, timeout=None):
            if "test -f" in command and "docker-compose.yml" in command:
                if "/opt/basecommerce/docker-compose.yml" in command:
                    return (0, "", "")  # Legacy exists
                return (1, "", "")  # New doesn't exist
            # Return JSON output for stats command
            return (0, json_output, "")
        
        mock_ssh.execute.side_effect = mock_execute
        
        docker = DockerCompose(self.droplet)
        docker.ssh = mock_ssh
        
        stats = docker.stats()
        
        self.assertEqual(len(stats), 2)
        self.assertEqual(stats[0]["name"], "basecommerce-nginx")
        self.assertEqual(stats[0]["cpu"], "0.50%")
        self.assertEqual(stats[1]["name"], "basecommerce-auth")
        self.assertEqual(stats[1]["cpu"], "0.25%")
    
    @patch('basec.docker.SSHClientWrapper')
    def test_run_compose_raises_error_on_failure(self, mock_ssh_class):
        """Test that _run_compose raises RuntimeError on failure."""
        mock_ssh = MagicMock()
        mock_ssh_class.return_value = mock_ssh
        mock_ssh.client = None
        
        # Mock directory check to return legacy directory exists
        def mock_execute(command, check=False, capture_output=True, timeout=None):
            if "test -f" in command and "docker-compose.yml" in command:
                if "/opt/basecommerce/docker-compose.yml" in command:
                    return (0, "", "")  # Legacy exists
                return (1, "", "")  # New doesn't exist
            # Simulate command failure for actual compose command
            return (1, "", "Error: command failed")
        
        mock_ssh.execute.side_effect = mock_execute
        
        docker = DockerCompose(self.droplet)
        docker.ssh = mock_ssh
        docker._remote_dir = "/opt/basecommerce"  # Set directly to avoid directory check
        
        with self.assertRaises(RuntimeError) as context:
            docker._run_compose("test command")
        
        error_msg = str(context.exception)
        self.assertIn("exit code 1", error_msg)
        self.assertIn("test command", error_msg)
        self.assertIn("Error: command failed", error_msg)
    
    @patch('basec.docker.SSHClientWrapper')
    def test_run_compose_includes_stderr_tail(self, mock_ssh_class):
        """Test that _run_compose includes stderr tail in error."""
        mock_ssh = MagicMock()
        mock_ssh_class.return_value = mock_ssh
        mock_ssh.client = None
        
        # Long stderr (should be truncated to last 500 chars)
        long_stderr = "A" * 1000
        
        def mock_execute(command, check=False, capture_output=True, timeout=None):
            if "test -f" in command and "docker-compose.yml" in command:
                if "/opt/basecommerce/docker-compose.yml" in command:
                    return (0, "", "")  # Legacy exists
                return (1, "", "")  # New doesn't exist
            # Simulate command failure
            return (1, "", long_stderr)
        
        mock_ssh.execute.side_effect = mock_execute
        
        docker = DockerCompose(self.droplet)
        docker.ssh = mock_ssh
        docker._remote_dir = "/opt/basecommerce"  # Set directly to avoid directory check
        
        with self.assertRaises(RuntimeError) as context:
            docker._run_compose("test")
        
        error_msg = str(context.exception)
        # Should contain last 500 chars
        self.assertIn("A" * 500, error_msg)
        # Should not contain first 500 chars
        self.assertNotIn("A" * 500 + "B", error_msg)
    
    @patch('basec.docker.SSHClientWrapper')
    def test_remote_dir_from_droplet(self, mock_ssh_class):
        """Test that remote_dir is correctly derived from droplet."""
        # Mock SSH to return legacy directory exists
        mock_ssh = MagicMock()
        mock_ssh_class.return_value = mock_ssh
        mock_ssh.client = None  # Simulate not connected initially
        
        # Mock execute to simulate legacy directory exists
        def mock_execute(command, check=False, capture_output=True, timeout=None):
            # Simulate legacy directory check succeeds
            if "/opt/basecommerce/docker-compose.yml" in command:
                return (0, "", "")
            # Simulate new directory doesn't exist
            return (1, "", "")
        
        mock_ssh.execute.side_effect = mock_execute
        
        edge_droplet = DropletConfig(ip="1.1.1.1", role="edge")
        docker = DockerCompose(edge_droplet)
        # Should fallback to legacy
        self.assertEqual(docker.remote_dir, "/opt/basecommerce")
        
        # Test with new directory existing
        def mock_execute_new(command, check=False, capture_output=True, timeout=None):
            if "/opt/basecommerce/edge/docker-compose.yml" in command:
                return (0, "", "")
            return (1, "", "")
        
        mock_ssh.execute.side_effect = mock_execute_new
        docker._remote_dir = None  # Reset cache
        self.assertEqual(docker.remote_dir, "/opt/basecommerce/edge")
    
    @patch('basec.docker.SSHClientWrapper')
    def test_remote_dir_custom(self, mock_ssh_class):
        """Test that custom remote_dir is respected."""
        # When remote_dir is custom, no SSH check should be made
        mock_ssh = MagicMock()
        mock_ssh_class.return_value = mock_ssh
        
        droplet = DropletConfig(
            ip="1.1.1.1",
            role="edge",
            remote_dir="/custom/path"
        )
        docker = DockerCompose(droplet)
        docker.ssh = mock_ssh
        
        # Should use custom path directly without SSH check
        self.assertEqual(docker.remote_dir, "/custom/path")
        
        # Verify no SSH execute was called for directory check
        mock_ssh.execute.assert_not_called()


if __name__ == "__main__":
    unittest.main()

