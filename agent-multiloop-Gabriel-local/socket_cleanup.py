#!/usr/bin/env python3
"""
SOCKET CLEANUP UTILITY - Ferme complètement les sockets sans fermer Docker Desktop

Cette librairie gère la fermeture des sockets au niveau du système d'exploitation
pour garantir que le port se libère quand Gabriel s'arrête.
"""

import os
import sys
import socket
import logging
import subprocess
import time
from typing import Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class SocketCleanup:
    """Gère la fermeture complète des sockets au niveau système."""
    
    def __init__(self, port: int):
        self.port = port
        self.listener_socket: Optional[socket.socket] = None
        self.original_sigint = None
        
    def close_socket(self):
        """Ferme la socket directement."""
        if self.listener_socket:
            try:
                self.listener_socket.close()
                logger.info(f"Socket fermée proprement (port {self.port})")
            except Exception as e:
                logger.warning(f"Erreur fermeture socket: {e}")
    
    def force_close_port_listeners(self):
        """Force la fermeture de tous les listeners sur le port (au niveau OS)."""
        try:
            if sys.platform == "win32":
                self._close_port_windows()
            elif sys.platform in ["linux", "linux2"]:
                self._close_port_linux()
            elif sys.platform == "darwin":
                self._close_port_macos()
        except Exception as e:
            logger.warning(f"Erreur force close: {e}")
    
    def _close_port_windows(self):
        """Windows: Utilise netstat + taskkill pour fermer le port."""
        try:
            # Trouver les PIDs qui écouten sur le port
            result = subprocess.run(
                f'netstat -ano | findstr :{self.port}',
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                pids = set()
                
                for line in lines:
                    parts = line.split()
                    if len(parts) > 0:
                        try:
                            pid = int(parts[-1])
                            pids.add(pid)
                        except (ValueError, IndexError):
                            pass
                
                # TUE SEULEMENT LE LISTENER, PAS LE PARENT
                for pid in pids:
                    try:
                        proc_info = subprocess.run(
                            f'tasklist /fi "PID eq {pid}"',
                            shell=True,
                            capture_output=True,
                            text=True
                        )
                        
                        # Vérifier que c'est pas docker daemon lui-même
                        if "docker" not in proc_info.stdout.lower() or "wsl" in proc_info.stdout.lower():
                            subprocess.run(
                                f'taskkill /PID {pid} /F',
                                shell=True,
                                timeout=3
                            )
                            logger.info(f"Listener PID {pid} fermé (port {self.port})")
                    except Exception as e:
                        logger.warning(f"Erreur fermeture PID {pid}: {e}")
        
        except subprocess.TimeoutExpired:
            logger.warning("Timeout lors de la fermeture du port")
        except Exception as e:
            logger.warning(f"Erreur Windows close: {e}")
    
    def _close_port_linux(self):
        """Linux: Utilise lsof + kill."""
        try:
            result = subprocess.run(
                f'lsof -i :{self.port} -t',
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            for pid_str in result.stdout.strip().split():
                try:
                    pid = int(pid_str)
                    os.kill(pid, 15)  # SIGTERM
                    time.sleep(0.5)
                    try:
                        os.kill(pid, 9)  # SIGKILL si encore actif
                    except ProcessLookupError:
                        pass
                    logger.info(f"Listener PID {pid} tué (port {self.port})")
                except (ValueError, ProcessLookupError):
                    pass
        except Exception as e:
            logger.warning(f"Erreur Linux close: {e}")
    
    def _close_port_macos(self):
        """macOS: Utilise lsof + kill (similaire à Linux)."""
        self._close_port_linux()
    
    def reset_port(self):
        """Remet le port en état utilisable."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, b'\x01\x00\x00\x00\x00\x00\x00\x00')
            sock.bind(('0.0.0.0', self.port))
            sock.close()
            logger.info(f"Port {self.port} réinitialisé (SO_REUSEADDR)")
            return True
        except OSError as e:
            logger.warning(f"Port {self.port} pas complètement libéré: {e}")
            return False
    
    def cleanup(self):
        """Nettoyage complet."""
        logger.info(f"=== SOCKET CLEANUP: Port {self.port} ===")
        
        # Étape 1: Fermer la socket Python
        self.close_socket()
        
        # Étape 2: Forcer la fermeture des listeners
        self.force_close_port_listeners()
        
        # Étape 3: Réinitialiser le port
        time.sleep(1)
        self.reset_port()
        
        logger.info(f"=== SOCKET CLEANUP COMPLÈTE ===")


@contextmanager
def socket_context(port: int):
    """Context manager pour socket cleanup automatique."""
    cleanup = SocketCleanup(port)
    try:
        yield cleanup
    finally:
        cleanup.cleanup()


def force_port_cleanup(port: int, force_kill_listener: bool = True):
    """Force le cleanup du port (fonction standalone)."""
    cleanup = SocketCleanup(port)
    if force_kill_listener:
        cleanup.force_close_port_listeners()
    time.sleep(1)
    cleanup.reset_port()
    logger.info(f"Port {port} forcément nettoyé")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    print(f"Nettoyage port {port}...")
    force_port_cleanup(port)
    print(f"Port {port} nettoyé!")
