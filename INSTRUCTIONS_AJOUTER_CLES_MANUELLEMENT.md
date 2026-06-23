# ============================================================
# INSTRUCTIONS POUR AJOUTER TA CLÉ CLAUDE MANUELLEMENT
# ============================================================

ÉTAPE 1: GÉNÉRER UNE CLÉ CLAUDE
=====================================
1. Va sur: https://console.anthropic.com/
2. Login avec ton compte Anthropic
3. Clique sur "API Keys" (à gauche)
4. Clique "Create Key" (en bleu)
5. COPIE la clé complète (elle commence par "sk-ant-" suivi de 50+ caractères)
   Format: sk-ant-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
6. Ne ferme PAS la fenêtre (tu ne pourras plus la voir après!)

ÉTAPE 2: GÉNÉRER UNE CLÉ OPENAI
=====================================
1. Va sur: https://platform.openai.com/api-keys
2. Login avec ton compte OpenAI
3. Clique "Create new secret key"
4. COPIE la clé complète (elle commence par "sk-" suivi de 40+ caractères)
   Format: sk-proj-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

ÉTAPE 3: ÉDITER LE FICHIER .env
=====================================
1. Ouvre VS Code
2. Ouvre le fichier:
   C:\agent-multiloop-Gabriel-local-final\agent-multiloop-Gabriel-local\.env

3. CHERCHE ces lignes:
   Line 17: CLAUDE_API_KEY=[REDACTED]
   Line 18: ANTHROPIC_API_KEY=[REDACTED]
   Line 27: OPENAI_API_KEY=sk-[REDACTED]

4. REMPLACE-LES EXACTEMENT PAR:

   CLAUDE_API_KEY=sk-ant-COLLE_TA_VRAIE_CLE_CLAUDE_ICI
   ANTHROPIC_API_KEY=sk-ant-COLLE_TA_VRAIE_CLE_CLAUDE_ICI
   OPENAI_API_KEY=sk-COLLE_TA_VRAIE_CLE_OPENAI_ICI

   EXEMPLE (PAS UNE VRAIE CLÉ):
   CLAUDE_API_KEY=sk-ant-abcd1234efgh5678ijkl9012mnopqrst
   ANTHROPIC_API_KEY=sk-ant-abcd1234efgh5678ijkl9012mnopqrst
   OPENAI_API_KEY=sk-proj-123456789abcdefghijklmnopqrstuvwxyz

5. SAUVEGARDE LE FICHIER (Ctrl+S)

ÉTAPE 4: FAIRE LA MÊME CHOSE DANS L'AUTRE FICHIER
=====================================
1. Ouvre aussi: C:\agent-multiloop-Gabriel-local-final\.env
2. REMPLACE les mêmes lignes par les mêmes clés
3. SAUVEGARDE (Ctrl+S)

ÉTAPE 5: REDÉMARRER DOCKER
=====================================
Ouvre PowerShell et tape:

cd "C:\agent-multiloop-Gabriel-local-final\agent-multiloop-Gabriel-local"
docker-compose restart

Attends 30-60 secondes.

ÉTAPE 6: TESTER
=====================================
Envoie une requête à Gabriel.

Si tu vois dans les logs:
[INFO] 🔴 Tentative 2/3: Claude-3.5-Sonnet - timeout 60s
[INFO] ✅ Claude a répondu

→ 🎉 ÇA MARCHE!

Si tu vois toujours:
[WARNING] ⚠️ Claude indisponible (CLAUDE_API_KEY manquante)

→ ⚠️ Les clés ne sont pas correctement placées, recommence

=====================================
IMPORTANT:
- Les clés ne doivent JAMAIS contenir [REDACTED] ou [...] ou <...>
- Les clés commencent TOUJOURS par "sk-ant-" (Claude) ou "sk-" (OpenAI)
- Les deux fichiers .env doivent avoir LES MÊMES clés
- Après modification, TOUJOURS redémarrer Docker
=====================================
