# Documentation detailed_scan.py

## Vue d'ensemble
Ce module effectue des scans réseau avancés avec vérification sécuritaire. Il compare les résultats avec des fichiers de référence pour détecter les anomalies et intrusions.

## Imports
```python
import subprocess
import os
```
- `subprocess` : exécution de commandes nmap
- `os` : opérations sur les fichiers

## Fonctions de scan

### detailed_network_scan(network_range)
**Objectif** : Scanner le réseau avec la même logique que scan.py mais pour usage sécuritaire

**Fonctionnement** :
- Utilise exactement la même commande nmap que scan.py
- `cmd = ["nmap", "-sV", "-p", "21,22,23,25,53,80,110,135,139,443,445,993,995,3389,4444,8080", "--open", "-T4", network_range]`
- Parse avec `parse_detailed_nmap_output()` qui est identique à scan.py

**Différence avec scan.py** :
- Même logique, mais utilisé dans un contexte sécuritaire
- Les résultats servent pour les vérifications de sécurité

### parse_detailed_nmap_output(output)
**Objectif** : Parser la sortie nmap (identique à scan.py)

**Logique identique** :
1. Détecte les appareils avec `"Nmap scan report for"`
2. Extrait MAC avec `"MAC Address:"`
3. Récupère les ports avec `"/tcp" in line and "open"`
4. Détecte OS avec `"Running:"`
5. Devine l'OS avec `guess_os_from_ports()` si non trouvé

### guess_os_from_ports(ports)
**Objectif** : Même logique que scan.py pour deviner l'OS

**Priorités identiques** :
1. Metasploit (port 4444)
2. Linux (port 22 SSH)
3. Windows (ports 135,139,445,3389)
4. Autres services

## Fonctions de chargement des fichiers

### load_mac_whitelist()
**Objectif** : Charger la liste des adresses MAC autorisées

**Fonctionnement** :
- `open('mac_whitelist.txt', 'r')` : ouvre le fichier en lecture
- `for line in f:` : lit ligne par ligne
- `line.strip()` : enlève espaces/retours à la ligne
- `if mac:` : vérifie que la ligne n'est pas vide

**Gestion d'erreur** :
- `except FileNotFoundError` : si le fichier n'existe pas
- Retourne liste vide si erreur

**Format du fichier** :
```
AA:BB:CC:DD:EE:FF
11:22:33:44:55:66
```

### load_mac_ip_mapping()
**Objectif** : Charger les associations MAC ↔ IP connues

**Format attendu** :
```
AA:BB:CC:DD:EE:FF,192.168.1.100
11:22:33:44:55:66,192.168.1.101
```

**Parsing** :
- `parts = line.strip().split(',')` : divise par virgule
- `if len(parts) == 2` : vérifie exactement 2 éléments
- `mapping[parts[0]] = parts[1]` : MAC → IP

### load_mac_os_mapping()
**Objectif** : Charger les associations MAC ↔ OS connues

**Format attendu** :
```
AA:BB:CC:DD:EE:FF,Linux Server
11:22:33:44:55:66,Windows 10
```

**Logique identique** à load_mac_ip_mapping()

### load_mac_ports_mapping()
**Objectif** : Charger les ports normaux pour chaque MAC

**Format attendu** :
```
AA:BB:CC:DD:EE:FF,22,80,443
11:22:33:44:55:66,135,139,445
```

**Parsing spécial** :
- `parts = line.strip().split(',')` : divise par virgule
- `if len(parts) >= 2` : au moins MAC + 1 port
- `ports = [int(p) for p in parts[1:] if p.isdigit()]` :
  - `parts[1:]` : tous sauf le premier (MAC)
  - `p.isdigit()` : vérifie que c'est un nombre
  - `int(p)` : convertit en entier

## Fonctions de vérification sécuritaire

### security_check(devices)
**Objectif** : Détecter les anomalies en comparant avec les fichiers de référence

**Étapes de vérification** :

1. **Chargement des références** :
   - `mac_whitelist = load_mac_whitelist()`
   - `mac_ip_map = load_mac_ip_mapping()`
   - `mac_os_map = load_mac_os_mapping()`
   - `mac_ports_map = load_mac_ports_mapping()`

2. **Vérification MAC non autorisée** :
   - `if mac != "Unknown" and mac not in mac_whitelist`
   - Alerte si nouveau MAC détecté

3. **Vérification changement d'IP** :
   - `if mac in mac_ip_map:` si MAC connu
   - `if ip != expected_ip:` si IP différente
   - Alerte de possible usurpation d'identité

4. **Vérification changement d'OS** :
   - Compare l'OS détecté avec l'OS attendu
   - Alerte si différence (possible changement d'appareil)

5. **Vérification nouveaux ports** :
   - `new_ports = [p for p in ports if p not in expected_ports]`
   - Détecte les ports qui n'étaient pas ouverts avant
   - Alerte de possible compromission

**Gestion des alertes** :
- `alerts.append(f"ALERTE: ...")` : ajoute à la liste
- Format standardisé des messages d'alerte
- Retourne la liste pour usage externe

### show_detailed_results(devices)
**Objectif** : Afficher les résultats du scan de façon détaillée

**Formatage** :
- `print("-" * 80)` : ligne de séparation
- `enumerate(devices, 1)` : numérote à partir de 1
- Affiche IP, MAC, OS, ports pour chaque appareil
- `', '.join(map(str, device['ports']))` : ports séparés par virgules

## Fonctions utilitaires

### extract_ip(line) et is_valid_ip(ip)
**Objectif** : Identiques à scan.py pour extraire et valider les IP

## Flux d'exécution sécuritaire

1. **Scan initial** : `detailed_network_scan()` découvre les appareils
2. **Affichage** : `show_detailed_results()` montre les détails
3. **Vérification** : `security_check()` compare avec les références
4. **Alertes** : affiche les anomalies détectées

## Types d'anomalies détectées

1. **Nouveau MAC** : appareil inconnu sur le réseau
2. **Changement d'IP** : MAC connu sur une IP différente
3. **Changement d'OS** : même MAC mais OS différent
4. **Nouveaux ports** : ports supplémentaires ouverts

## Fichiers de référence nécessaires

- `mac_whitelist.txt` : MAC autorisées
- `mac_ip_mapping.txt` : associations MAC-IP
- `mac_os_mapping.txt` : associations MAC-OS  
- `mac_ports_mapping.txt` : ports normaux par MAC

## Cas d'usage sécuritaire

- **Détection d'intrusion** : nouveaux appareils
- **Détection d'usurpation** : changement d'IP
- **Détection de compromission** : nouveaux ports ouverts
- **Monitoring continu** : surveillance des changements

## Différence avec scan.py

- **scan.py** : découverte et inventaire basique
- **detailed_scan.py** : surveillance sécuritaire avec comparaison de références
- Même logique de scan, but différent
