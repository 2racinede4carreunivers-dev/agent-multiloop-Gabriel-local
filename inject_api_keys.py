#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'injection des clés API dans les fichiers .env
Les clés restent LOCALES - elles ne sont jamais transmises
"""

import os
import sys
from pathlib import Path
import subprocess
import time

def main():
    print("\n" + "="*80)
    print("INJECTION DES CLÉS API DANS LES FICHIERS .env")
    print("="*80)
    
    # Chemins
    root_env = Path(r"C:\agent-multiloop-Gabriel-local-final\.env")
    container_env = Path(r"C:\agent-multiloop-Gabriel-local-final\agent-multiloop-Gabriel-local\.env")
    
    print("\n📁 Fichiers à modifier:")
    print(f"   1. {root_env}")
    print(f"   2. {container_env}")
    
    # Demander les clés
    print("\n" + "="*80)
    print("ÉTAPE 1: ENTRE TA CLÉ CLAUDE")
    print("="*80)
    print("\nOù la trouver: https://console.anthropic.com/")
    print("Format: sk-ant-XXXXXXXXXXXXX...")
    print("\n⚠️  La clé sera cachée à l'écran pour la sécurité")
    
    import getpass
    claude_key = getpass.getpass("\nColle ta clé Claude ici: ").strip()
    
    # Valider Claude
    if not claude_key.startswith("sk-ant-"):
        print("\n❌ ERREUR: La clé Claude doit commencer par 'sk-ant-'")
        return False
    
    if len(claude_key) < 40:
        print("\n❌ ERREUR: La clé Claude est trop courte (doit faire 50+ caractères)")
        return False
    
    print(f"✅ Clé Claude valide ({len(claude_key)} caractères)")
    
    # Demander OpenAI
    print("\n" + "="*80)
    print("ÉTAPE 2: ENTRE TA CLÉ OPENAI")
    print("="*80)
    print("\nOù la trouver: https://platform.openai.com/api-keys")
    print("Format: sk-proj-XXXXXXXXXXXXX... ou sk-XXXXXXXXXXXXX...")
    print("\n⚠️  La clé sera cachée à l'écran pour la sécurité")
    
    openai_key = getpass.getpass("\nColle ta clé OpenAI ici: ").strip()
    
    # Valider OpenAI
    if not openai_key.startswith("sk-"):
        print("\n❌ ERREUR: La clé OpenAI doit commencer par 'sk-'")
        return False
    
    if len(openai_key) < 40:
        print("\n❌ ERREUR: La clé OpenAI est trop courte (doit faire 50+ caractères)")
        return False
    
    print(f"✅ Clé OpenAI valide ({len(openai_key)} caractères)")
    
    # Confirmation
    print("\n" + "="*80)
    print("CONFIRMATION")
    print("="*80)
    print(f"\n✅ Clé Claude: {claude_key[:10]}...{claude_key[-10:]}")
    print(f"✅ Clé OpenAI: {openai_key[:10]}...{openai_key[-10:]}")
    
    confirm = input("\n👉 Continuer et injecter les clés? (oui/non): ").strip().lower()
    if confirm not in ["oui", "yes", "o", "y"]:
        print("\n❌ Annulé par l'utilisateur")
        return False
    
    # Fonction pour remplacer dans un fichier
    def update_env_file(filepath, claude_key, openai_key):
        print(f"\n📝 Modification: {filepath}")
        
        if not filepath.exists():
            print(f"   ❌ Fichier non trouvé: {filepath}")
            return False
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remplacer Claude
            content = content.replace(
                "CLAUDE_API_KEY=[REDACTED]",
                f"CLAUDE_API_KEY={claude_key}"
            )
            content = content.replace(
                "CLAUDE_API_KEY=sk-ant-[REDACTED]",
                f"CLAUDE_API_KEY={claude_key}"
            )
            
            # Remplacer Anthropic (alias)
            content = content.replace(
                "ANTHROPIC_API_KEY=[REDACTED]",
                f"ANTHROPIC_API_KEY={claude_key}"
            )
            content = content.replace(
                "ANTHROPIC_API_KEY=sk-ant-[REDACTED]",
                f"ANTHROPIC_API_KEY={claude_key}"
            )
            
            # Remplacer OpenAI
            # Gérer les cas: sk-[REDACTED], sk-proj-[REDACTED], etc.
            lines = content.split('\n')
            new_lines = []
            for line in lines:
                if line.startswith("OPENAI_API_KEY="):
                    new_lines.append(f"OPENAI_API_KEY={openai_key}")
                else:
                    new_lines.append(line)
            
            content = '\n'.join(new_lines)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"   ✅ Fichier modifié avec succès")
            return True
        
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            return False
    
    # Appliquer les modifications
    print("\n" + "="*80)
    print("ÉTAPE 3: INJECTION DES CLÉS")
    print("="*80)
    
    success1 = update_env_file(root_env, claude_key, openai_key)
    success2 = update_env_file(container_env, claude_key, openai_key)
    
    if not (success1 and success2):
        print("\n❌ Injection échouée!")
        return False
    
    # Vérifier
    print("\n" + "="*80)
    print("ÉTAPE 4: VÉRIFICATION")
    print("="*80)
    
    try:
        with open(container_env, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if claude_key in content and openai_key in content:
            print("\n✅ Les clés sont correctement présentes dans les fichiers!")
        else:
            print("\n⚠️  Les clés n'ont pas été trouvées après injection")
            return False
    
    except Exception as e:
        print(f"\n❌ Erreur de vérification: {e}")
        return False
    
    # Redémarrer Docker
    print("\n" + "="*80)
    print("ÉTAPE 5: REDÉMARRAGE DOCKER")
    print("="*80)
    
    docker_path = Path(r"C:\agent-multiloop-Gabriel-local-final\agent-multiloop-Gabriel-local")
    
    try:
        print("\n🔄 Arrêt des conteneurs...")
        subprocess.run(
            ["docker-compose", "down"],
            cwd=str(docker_path),
            capture_output=True,
            timeout=30
        )
        
        time.sleep(2)
        
        print("🔄 Redémarrage des conteneurs...")
        subprocess.run(
            ["docker-compose", "up", "-d"],
            cwd=str(docker_path),
            capture_output=True,
            timeout=60
        )
        
        print("✅ Conteneurs redémarrés")
    
    except subprocess.TimeoutExpired:
        print("⚠️  Docker timeout (mais les conteneurs devraient redémarrer)")
    except Exception as e:
        print(f"⚠️  Erreur Docker: {e}")
        print("   👉 Redémarre manuellement: docker-compose down && docker-compose up")
    
    # Résumé final
    print("\n" + "="*80)
    print("✅ INJECTION COMPLÈTE!")
    print("="*80)
    
    print("""
✅ Les clés ont été injectées dans:
   - C:\\agent-multiloop-Gabriel-local-final\\.env
   - C:\\agent-multiloop-Gabriel-local-final\\agent-multiloop-Gabriel-local\\.env

✅ Docker a été redémarré

⏳ Attends 60 secondes que Gabriel démarre complètement

🚀 Puis teste une requête mathématique!

Les logs doivent montrer:
[INFO] 🔴 Tentative 2/3: Claude-3.5-Sonnet - timeout 60s
[INFO] ✅ Claude a répondu

Si Claude ne marche pas, rapporte les logs!
""")
    
    print("="*80 + "\n")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
