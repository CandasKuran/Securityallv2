# Documentation blockip.py

## Vue d'ensemble
Ce module gère le blocage et déblocage d'adresses IP en utilisant l'ARP spoofing. Il maintient une liste des IP bloquées et utilise l'outil `arpspoof` pour interrompre les communications.

## Imports
```python
import subprocess
import os
```
- `subprocess` : exécution de commandes système (arpspoof)
- `os` : commandes système pour tuer des processus

## Variables globales
```python
blocked_ips = []
unblocked_ips = []
```
- `blocked_ips` : liste des IP actuellement bloquées
- `unblocked_ips` : historique des IP qui ont été débloquées

## Fonctions principales

### block_ip(target_ip, gateway_ip="10.10.10.2")
**Objectif** : Bloquer une IP cible en utilisant l'ARP spoofing bidirectionnel

**Paramètres** :
- `target_ip` : IP à bloquer
- `gateway_ip` : passerelle réseau (par défaut "10.10.10.2")

**Technique ARP spoofing** :
L'ARP spoofing consiste à envoyer de fausses réponses ARP pour rediriger le trafic.

**Commandes arpspoof** :
1. `arpspoof -i eth0 -t target_ip gateway_ip` :
   - `-i eth0` : utilise l'interface réseau eth0
   - `-t target_ip` : cible l'IP à bloquer
   - `gateway_ip` : se fait passer pour la passerelle

2. `arpspoof -i eth0 -t gateway_ip target_ip` :
   - Sens inverse : se fait passer pour la cible vers la passerelle

**Paramètres subprocess** :
- `subprocess.Popen()` : lance en arrière-plan (non bloquant)
- `stdout=subprocess.DEVNULL` : ignore la sortie standard
- `stderr=subprocess.DEVNULL` : ignore les erreurs
- `start_new_session=True` : crée un nouveau groupe de processus

**Logique** :
1. Lance deux processus arpspoof en parallèle
2. Ajoute l'IP à `blocked_ips`
3. Retourne `True` si succès, `False` si erreur

**Pourquoi bidirectionnel** :
- Bloque target → gateway (sortie Internet)
- Bloque gateway → target (entrée Internet)
- Coupe complètement la communication

### unblock_ip(target_ip)
**Objectif** : Débloquer une IP en arrêtant les processus arpspoof correspondants

**Fonctionnement** :
- `os.system(f"pkill -f 'arpspoof.*{target_ip}'")` :
  - `pkill` : tue des processus par nom/motif
  - `-f` : recherche dans la ligne de commande complète
  - `'arpspoof.*{target_ip}'` : motif regex pour trouver les processus arpspoof concernant cette IP

**Gestion des listes** :
- `if target_ip in blocked_ips:` vérifie si l'IP était bloquée
- `blocked_ips.remove(target_ip)` : enlève de la liste des bloquées
- `unblocked_ips.append(target_ip)` : ajoute à l'historique

**Gestion d'erreur** :
- `try/except` : capture les erreurs système
- Retourne `True/False` selon le succès

### unblock_all()
**Objectif** : Débloquer toutes les IP en arrêtant tous les processus arpspoof

**Fonctionnement** :
- `os.system("pkill -f arpspoof")` : tue TOUS les processus arpspoof
- `for ip in blocked_ips:` : parcourt toutes les IP bloquées
- `unblocked_ips.append(ip)` : ajoute chacune à l'historique
- `blocked_ips.clear()` : vide la liste des bloquées

**Cas d'usage** :
- Arrêt d'urgence de tout blocage
- Nettoyage en fin de session

## Fonctions utilitaires

### is_valid_ip(ip)
**Objectif** : Valider qu'une chaîne est une adresse IP valide

**Logique identique à scan.py** :
- `ip.split('.')` : divise par les points
- `len(parts) == 4` : exactement 4 parties
- `all(0 <= int(p) <= 255 for p in parts)` : chaque partie entre 0-255

**Gestion d'erreur** :
- `try/except` : capture les erreurs de conversion

### get_default_gateway()
**Objectif** : Obtenir automatiquement la passerelle par défaut du système

**Commande système** :
- `ip route show default` : affiche les routes par défaut

**Parsing** :
- `result.stdout.split('\n')` : divise la sortie en lignes
- `if 'default via' in line:` : trouve la ligne avec la passerelle
- `line.split()[2]` : prend le 3ème mot qui est l'IP de la passerelle

**Fallback** :
- Si échec, retourne `"10.10.10.2"` par défaut

## Principe de l'ARP spoofing

### Table ARP normale
```
IP Gateway    → MAC Gateway
IP Target     → MAC Target
```

### Après ARP spoofing
```
IP Gateway    → MAC Attaquant  (sur la machine cible)
IP Target     → MAC Attaquant  (sur la passerelle)
```

### Résultat
- La cible envoie ses paquets à l'attaquant au lieu de la passerelle
- La passerelle envoie les paquets pour la cible à l'attaquant
- L'attaquant peut choisir de ne pas relayer → blocage

## Flux d'exécution

### Blocage
1. **Validation** : `is_valid_ip()` vérifie l'IP
2. **Passerelle** : `get_default_gateway()` trouve la gateway
3. **ARP spoofing** : `block_ip()` lance les deux arpspoof
4. **Tracking** : ajoute à `blocked_ips`

### Déblocage
1. **Arrêt processus** : `pkill` tue les arpspoof concernés
2. **Mise à jour listes** : enlève de `blocked_ips`, ajoute à `unblocked_ips`
3. **Récupération ARP** : les tables ARP se reconstituent naturellement

## Sécurité et considérations

### Permissions nécessaires
- Privilèges root requis pour arpspoof
- Accès à l'interface réseau

### Effet sur le réseau
- Bloque complètement l'accès Internet de la cible
- Peut affecter les communications locales
- Détectable par monitoring réseau

### Nettoyage
- Important de débloquer avant d'arrêter le programme
- Les processus arpspoof continuent en arrière-plan si non tués

### Détection
- Outils comme arpwatch peuvent détecter l'ARP spoofing
- Logs réseau montrent des anomalies ARP

## Interface avec main.py

- `blocked_ips` : accessible depuis main.py pour affichage
- `is_valid_ip()` : utilisé pour valider les saisies utilisateur
- `get_default_gateway()` : obtient automatiquement la passerelle
- `block_ip()` et `unblock_ip()` : fonctions principales appelées par l'interface
