# Documentation scan.py

## Vue d'ensemble
Ce module effectue le scan réseau basique en utilisant nmap. Il détecte les appareils connectés, leurs ports ouverts et devine leur système d'exploitation.

## Imports
```python
import subprocess
```
- `subprocess` : permet d'exécuter des commandes système (nmap) depuis Python

## Fonctions principales

### scan_network(network_range)
**Objectif** : Scanner une plage réseau et retourner la liste des appareils trouvés

**Paramètres nmap utilisés** :
- `-sV` : détection de version des services (Service Version detection)
- `-p` : spécifie les ports à scanner
- `21,22,23,25,53,80,110,135,139,443,445,993,995,3389,4444,8080` : liste des ports communs
- `--open` : affiche seulement les ports ouverts
- `-T4` : timing template 4 (scan rapide mais pas agressif)

**Fonctionnement** :
- `subprocess.run(cmd, capture_output=True, text=True, timeout=30)` 
  - `capture_output=True` : capture stdout et stderr
  - `text=True` : retourne du texte (pas des bytes)
  - `timeout=30` : arrête si le scan prend plus de 30 secondes
- `result.returncode == 0` : vérifie que nmap s'est exécuté sans erreur

**Logique** :
1. Construit la commande nmap
2. Exécute le scan avec subprocess
3. Si succès, parse la sortie avec `parse_nmap_output()`
4. Retourne la liste des appareils

### parse_nmap_output(output)
**Objectif** : Analyser la sortie texte de nmap et extraire les informations

**Paramètres utilisés** :
- `output.split('\n')` : divise la sortie en lignes
- `line.strip()` : enlève les espaces en début/fin de ligne

**Logique de parsing** :
1. **Détection d'appareil** : `"Nmap scan report for" in line`
   - Crée un nouvel objet device avec IP, MAC, OS, ports
   - Sauvegarde l'appareil précédent avant de commencer le nouveau

2. **Adresse MAC** : `"MAC Address:" in line`
   - `parts = line.split()` : divise la ligne en mots
   - `parts[2]` : récupère le 3ème élément qui est l'adresse MAC

3. **Ports ouverts** : `"/tcp" in line and "open" in line`
   - `line.split('/')[0]` : prend la partie avant '/' qui est le numéro de port
   - `port.isdigit()` : vérifie que c'est bien un nombre
   - `int(port)` : convertit en entier et ajoute à la liste

**Structure de données retournée** :
```python
{
    "ip": "192.168.1.100",
    "mac": "AA:BB:CC:DD:EE:FF", 
    "os": "Linux Server",
    "ports": [22, 80, 443]
}
```

### guess_os_from_ports(ports)
**Objectif** : Deviner le système d'exploitation basé sur les ports ouverts

**Logique de détection par priorité** :

1. **Metasploit** (priorité maximale) :
   - Port `4444` : port par défaut de Metasploit
   - Si `22` aussi présent : "Metasploit Linux"
   - Sinon : "Metasploit"

2. **Linux/Unix** (priorité haute) :
   - Port `22` (SSH) : très caractéristique de Linux
   - Si ports web (80,443,8080,8443) aussi : "Linux Server"
   - Sinon : "Linux/Unix"

3. **Windows** :
   - Ports `[135, 139, 445, 3389]` : RPC, NetBIOS, SMB, RDP
   - Si ports web aussi : "Windows Server"
   - Sinon : "Windows"

4. **Autres** :
   - Port `23` (Telnet) : "Network Device"
   - Ports web seulement : "Web Server"
   - Ports services (21,25,53,110,143) : "Linux/Unix"

**Paramètres utilisés** :
- `any(p in web_ports for p in ports)` : vérifie si au moins un port web est présent
- `[p for p in ports if p in windows_ports]` : filtre les ports Windows
- `ports[:3]` : prend les 3 premiers ports pour affichage

### extract_ip(line)
**Objectif** : Extraire l'adresse IP d'une ligne de sortie nmap

**Fonctionnement** :
- `line.split()` : divise la ligne en mots
- `part.replace('(', '').replace(')', '')` : enlève les parenthèses
- `is_valid_ip()` : valide chaque partie pour trouver l'IP

### is_valid_ip(ip)
**Objectif** : Valider qu'une chaîne est une adresse IP valide

**Logique** :
- `ip.split('.')` : divise par les points
- `len(parts) == 4` : doit avoir exactement 4 parties
- `all(0 <= int(p) <= 255 for p in parts)` : chaque partie entre 0-255

**Gestion d'erreur** :
- `try/except` : capture les erreurs de conversion `int()`

### get_device_details_text(device)
**Objectif** : Formater les détails d'un appareil pour affichage

**Paramètres utilisés** :
- `', '.join(map(str, device['ports']))` :
  - `map(str, ...)` : convertit chaque port en string
  - `', '.join()` : joint avec des virgules

**Logique** :
1. Construit une chaîne avec IP, MAC, OS
2. Si des ports existent, les affiche séparés par virgules
3. Sinon affiche "None detected"

## Flux d'exécution
1. **scan_network()** reçoit la plage réseau
2. Construit et exécute la commande nmap
3. **parse_nmap_output()** analyse la sortie ligne par ligne
4. Pour chaque appareil, **guess_os_from_ports()** devine l'OS
5. Retourne la liste des appareils avec toutes les infos
6. **get_device_details_text()** formate l'affichage si demandé

## Ports scannés et leur signification
- **21** : FTP (File Transfer Protocol)
- **22** : SSH (Secure Shell) - très Linux
- **23** : Telnet - équipements réseau
- **25** : SMTP (email)
- **53** : DNS
- **80** : HTTP (web)
- **110** : POP3 (email)
- **135** : RPC Windows
- **139** : NetBIOS Windows
- **443** : HTTPS (web sécurisé)
- **445** : SMB Windows
- **993/995** : IMAP/POP3 sécurisé
- **3389** : RDP Windows
- **4444** : Metasploit
- **8080** : HTTP alternatif
