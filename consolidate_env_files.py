#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de consolidation des fichiers .env multiples
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

def consolidate_env_files():
    """Consolide tous les .env en un seul fichier master"""
    
    print("\n" + "="*80)
    print("CONSOLIDATION DES FICHIERS .env - GABRIEL MULTILOOP")
    print("="*80)
    
    # Chemins des fichiers .env
    env_files = {
        "root": Path("C:/agent-multiloop-Gabriel-local-final/.env"),
        "container": Path("C:/agent-multiloop-Gabriel-local-final/agent-multiloop-Gabriel-local/.env"),
        "example": Path("C:/agent-multiloop-Gabriel-local-final/.env.example"),
        "master": Path("C:/agent-multiloop-Gabriel-local-final/.env.master"),
    }
    
    print("\nFICHIERS DETECTES:")
    for name, path in env_files.items():
        exists = "[OK]" if path.exists() else "[X]"
        size = f"{path.stat().st_size} bytes" if path.exists() else "N/A"
        print(f"  {exists} {name:12} : {path}")
        print(f"       {size}")
    
    # Analyse des contenus
    print("\n" + "="*80)
    print("ANALYSE DES CONTENUS")
    print("="*80)
    
    env_data = {}
    for name, path in env_files.items():
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            env_data[name] = {
                'path': path,
                'content': content,
                'has_claude': 'CLAUDE_API_KEY' in content,
                'has_anthropic': 'ANTHROPIC_API_KEY' in content,
                'has_typo': 'ANTROPPIC_API_KEY' in content,
                'lines': len(content.split('\n')),
            }
    
    for name, data in env_data.items():
        print(f"\n{name.upper()}")
        print(f"   Lignes: {data['lines']}")
        print(f"   CLAUDE_API_KEY: {data['has_claude']} (OK={data['has_claude']})")
        print(f"   ANTHROPIC_API_KEY: {data['has_anthropic']} (OK={data['has_anthropic']})")
        print(f"   TYPO ANTROPPIC: {data['has_typo']} (PROBLEM={data['has_typo']})")
    
    # Problemes
    print("\n" + "="*80)
    print("PROBLEMES IDENTIFIES")
    print("="*80)
    
    issues = []
    
    if env_data.get('container', {}).get('has_typo'):
        issues.append("[CRITICAL] TYPO: ANTROPPIC_API_KEY in container .env (missing H)")
    
    if not env_data.get('root', {}).get('has_claude'):
        issues.append("[ERROR] CLAUDE_API_KEY missing in root .env")
    
    if not env_data.get('container', {}).get('has_claude'):
        issues.append("[ERROR] CLAUDE_API_KEY missing in container .env")
    
    if len(env_data) > 2:
        issues.append(f"[WARNING] {len(env_data)} .env files found (confusion risk)")
    
    if issues:
        for issue in issues:
            print(f"  {issue}")
    else:
        print("  All OK - No issues detected")
    
    # Recommandations
    print("\n" + "="*80)
    print("CONSOLIDATION STRATEGY")
    print("="*80)
    
    print("""
STEP 1: KEEP
  - .env.master (NEW - unified master file)
  - .env.example (template, do not modify)

STEP 2: BACKUP & DELETE
  - C:\\agent-multiloop-Gabriel-local-final\\.env
  - C:\\agent-multiloop-Gabriel-local-final\\agent-multiloop-Gabriel-local\\.env

STEP 3: COPY MASTER
  copy .env.master -> C:\\agent-multiloop-Gabriel-local-final\\.env
  copy .env.master -> C:\\agent-multiloop-Gabriel-local-final\\agent-multiloop-Gabriel-local\\.env

STEP 4: ADD YOUR KEYS
  Edit both files
  Replace: sk-ant-[VOTRE_CLE_CLAUDE_ICI]
  Replace: sk-[VOTRE_CLE_OPENAI_ICI]

STEP 5: RESTART DOCKER
  docker-compose down
  docker-compose up --build

STEP 6: VERIFY
  python test_claude_api_key_location.py
  
  Expected logs:
  [INFO] Claude-3.5-Sonnet - timeout 60s
  [INFO] Claude a repondu
""")
    
    # Rapport
    report = f"""
ENV FILES CONSOLIDATION REPORT
Generated: {datetime.now().isoformat()}

CURRENT STATUS:
  Root .env: {'Present' if env_data.get('root') else 'Missing'}
  Container .env: {'Present' if env_data.get('container') else 'Missing'}
  Example file: {'Present' if env_data.get('example') else 'Missing'}
  Master file: {'Present' if env_data.get('master') else 'Missing'}

ISSUES FOUND:
{chr(10).join(['  ' + issue for issue in issues]) if issues else '  NONE'}

SOLUTION:
  Use .env.master as single unified file
  Copy to both root and container locations
  Delete old files after backup

ACTION ITEMS:
  1. Read this report
  2. Backup old .env files
  3. Copy .env.master to both locations
  4. Add your real API keys
  5. Restart docker-compose
  6. Run test_claude_api_key_location.py
"""
    
    print(report)
    
    # Sauvegarder
    report_path = Path("C:/agent-multiloop-Gabriel-local-final/ENV_CONSOLIDATION_REPORT.txt")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\nReport saved: {report_path}")
    
    return len(issues) == 0


if __name__ == "__main__":
    success = consolidate_env_files()
    print("\n" + "="*80)
    if success:
        print("OK: All files are consistent")
    else:
        print("ISSUES DETECTED: See recommendations above")
    print("="*80 + "\n")
