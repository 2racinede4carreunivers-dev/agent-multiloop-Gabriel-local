#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'unification des .env files
1. Backup les anciens
2. Copie .env.master vers les deux emplacements
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

def backup_and_copy():
    """Unifie les fichiers .env"""
    
    print("\n" + "="*80)
    print("UNIFICATION DES .env FILES")
    print("="*80)
    
    # Chemins
    root_env = Path("C:/agent-multiloop-Gabriel-local-final/.env")
    container_env = Path("C:/agent-multiloop-Gabriel-local-final/agent-multiloop-Gabriel-local/.env")
    master_env = Path("C:/agent-multiloop-Gabriel-local-final/.env.master")
    backup_dir = Path("C:/agent-multiloop-Gabriel-local-final/.env_backup")
    
    # Créer dossier backup
    backup_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print(f"\nCreating backup directory: {backup_dir}")
    
    # Backup root .env
    if root_env.exists():
        backup_path = backup_dir / f".env.backup_{timestamp}"
        shutil.copy2(root_env, backup_path)
        print(f"[BACKUP] {root_env} -> {backup_path}")
    
    # Backup container .env
    if container_env.exists():
        backup_path = backup_dir / f".env_container.backup_{timestamp}"
        shutil.copy2(container_env, backup_path)
        print(f"[BACKUP] {container_env} -> {backup_path}")
    
    # Copier master vers root
    print(f"\n[COPY] {master_env} -> {root_env}")
    shutil.copy2(master_env, root_env)
    
    # Copier master vers container
    print(f"[COPY] {master_env} -> {container_env}")
    shutil.copy2(master_env, container_env)
    
    # Verifier
    print("\n[VERIFICATION]")
    print(f"  Root .env exists: {root_env.exists()} ({root_env.stat().st_size} bytes)")
    print(f"  Container .env exists: {container_env.exists()} ({container_env.stat().st_size} bytes)")
    
    # Check Claude keys
    with open(root_env, 'r') as f:
        root_content = f.read()
    
    has_claude = 'CLAUDE_API_KEY' in root_content and 'sk-ant-' in root_content
    
    print(f"\n[STATUS]")
    if has_claude:
        print("  [OK] CLAUDE_API_KEY found with sk-ant- prefix")
    else:
        print("  [WARNING] CLAUDE_API_KEY not properly set (placeholder present)")
        print("  -> You must replace sk-ant-[VOTRE_CLE_CLAUDE_ICI] with real key")
    
    print("\n" + "="*80)
    print("NEXT STEPS:")
    print("="*80)
    print("""
1. BACKUP CREATED:
   Folder: C:\\agent-multiloop-Gabriel-local-final\\.env_backup
   Your old .env files are safe there

2. FILES UNIFIED:
   Both root and container .env now use .env.master template

3. MUST DO:
   Edit BOTH files and replace:
   - sk-ant-[VOTRE_CLE_CLAUDE_ICI] with your real Claude key
   - sk-[VOTRE_CLE_OPENAI_ICI] with your real OpenAI key
   
   Files to edit:
   - C:\\agent-multiloop-Gabriel-local-final\\.env
   - C:\\agent-multiloop-Gabriel-local-final\\agent-multiloop-Gabriel-local\\.env

4. RESTART DOCKER:
   docker-compose down
   docker-compose up --build

5. VERIFY:
   python test_claude_api_key_location.py
""")
    
    print("="*80 + "\n")

if __name__ == "__main__":
    backup_and_copy()
