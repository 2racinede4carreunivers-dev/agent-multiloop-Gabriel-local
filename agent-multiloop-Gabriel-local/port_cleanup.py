#!/usr/bin/env python3
"""
PORT CLEANUP UTILITY FOR GABRIEL
Ensures proper socket cleanup on exit and port release.

Usage:
  from port_cleanup import CleanPortManager
  
  with CleanPortManager(9000) as manager:
      # Launch Flask or other service
      pass
  # Port is guaranteed to be released
"""

import os
import socket
import signal
import sys
import logging
import time
from contextlib import contextmanager
from pathlib import Path

logger = logging.getLogger(__name__)


class CleanPortManager:
    """Manages proper cleanup of TCP ports on exit."""
    
    def __init__(self, port: int, timeout: int = 10):
        self.port = port
        self.timeout = timeout
        self.original_sigint = None
        self.original_sigterm = None
        
    def __enter__(self):
        """Setup signal handlers for clean exit."""
        self.original_sigint = signal.signal(signal.SIGINT, self._handle_signal)
        self.original_sigterm = signal.signal(signal.SIGTERM, self._handle_signal)
        logger.info(f"Port manager active for port {self.port}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Restore signal handlers and cleanup port."""
        # Restore original handlers
        if self.original_sigint is not None:
            signal.signal(signal.SIGINT, self.original_sigint)
        if self.original_sigterm is not None:
            signal.signal(signal.SIGTERM, self.original_sigterm)
        
        # Close the port
        self.release_port()
        logger.info(f"Port {self.port} cleaned up and released")
        return False
    
    def _handle_signal(self, signum, frame):
        """Handle termination signals."""
        logger.info(f"Received signal {signum}, shutting down cleanly...")
        self.release_port()
        sys.exit(0)
    
    def release_port(self):
        """Force release of the port."""
        # Try to close any listening sockets
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, b'\x01\x00\x00\x00\x00\x00\x00\x00')
            sock.bind(('0.0.0.0', self.port))
            sock.close()
            logger.info(f"Port {self.port} successfully released")
        except OSError as e:
            logger.warning(f"Could not bind to port {self.port}: {e}")
            # Try using lsof/netstat to kill processes
            self._force_kill_port_processes()
    
    def _force_kill_port_processes(self):
        """Kill processes using the port (platform-specific)."""
        try:
            if sys.platform == "win32":
                # Windows: use netstat and taskkill
                import subprocess
                result = subprocess.run(
                    f'netstat -ano | findstr :{self.port}',
                    shell=True,
                    capture_output=True,
                    text=True
                )
                for line in result.stdout.split('\n'):
                    if line.strip():
                        parts = line.split()
                        if len(parts) > 0:
                            try:
                                pid = int(parts[-1])
                                subprocess.run(f'taskkill /PID {pid} /F', shell=True, timeout=2)
                                logger.info(f"Killed process {pid} using port {self.port}")
                            except (ValueError, subprocess.TimeoutExpired):
                                pass
            else:
                # Linux/macOS: use lsof
                import subprocess
                result = subprocess.run(
                    f'lsof -i :{self.port} -t',
                    shell=True,
                    capture_output=True,
                    text=True
                )
                for pid_str in result.stdout.strip().split():
                    try:
                        pid = int(pid_str)
                        os.kill(pid, signal.SIGTERM)
                        time.sleep(0.5)
                        try:
                            os.kill(pid, signal.SIGKILL)
                        except ProcessLookupError:
                            pass
                        logger.info(f"Killed process {pid} using port {self.port}")
                    except (ValueError, ProcessLookupError):
                        pass
        except Exception as e:
            logger.warning(f"Could not force kill port processes: {e}")


def check_port_available(port: int) -> bool:
    """Check if a port is available."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        return result != 0  # 0 means connected (port in use), != 0 means available
    except Exception:
        return True


def wait_for_port_available(port: int, timeout: int = 30) -> bool:
    """Wait for a port to become available."""
    start = time.time()
    while time.time() - start < timeout:
        if check_port_available(port):
            logger.info(f"Port {port} is now available")
            return True
        time.sleep(1)
    logger.warning(f"Port {port} not available after {timeout}s")
    return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 9000
    
    print(f"Checking port {port}...")
    if check_port_available(port):
        print(f"✓ Port {port} is available")
    else:
        print(f"✗ Port {port} is in use, attempting to free it...")
        manager = CleanPortManager(port)
        manager.release_port()
        if wait_for_port_available(port):
            print(f"✓ Port {port} is now available")
        else:
            print(f"✗ Could not free port {port}")
            sys.exit(1)
