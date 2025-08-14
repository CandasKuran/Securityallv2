# Documentation auto_scan.py

## Vue d'ensemble
Ce module gère le scan automatique périodique du réseau avec envoi de rapports par email. Il combine les fonctionnalités de detailed_scan.py avec un système d'email automatisé.

## Imports
```python
import time
import smtplib
from email.mime.text import MIMEText
import detailed_scan
import datetime
```
- `time` : pour les pauses temporelles (`sleep`)
- `smtplib` : client SMTP pour envoyer des emails
- `MIMEText` : pour formater les emails en texte
- `detailed_scan` : module de scan sécuritaire
- `datetime` : gestion des dates et heures

## Configuration
```python
EMAIL = "candas.kuran@gmail.com"
PASSWORD = "zbht esqj xryv oazk"
TO_EMAIL = "candas.kuran@gmail.com"
```
- `EMAIL` : adresse email d'envoi (Gmail)
- `PASSWORD` : mot de passe d'application Gmail (pas le mot de passe normal)
- `TO_EMAIL` : destinataire des rapports

**Note** : `zbht esqj xryv oazk` est un mot de passe d'application Gmail (App Password) nécessaire pour l'authentification à deux facteurs.

## Fonctions

### send_email(subject, message)
**Objectif** : Envoyer un email avec le rapport de scan

**Paramètres SMTP utilisés** :
- `MIMEText(message, 'plain', 'utf-8')` :
  - `'plain'` : texte brut (pas HTML)
  - `'utf-8'` : encodage pour les caractères français
- `smtplib.SMTP('smtp.gmail.com', 587)` :
  - `smtp.gmail.com` : serveur SMTP de Gmail
  - `587` : port SMTP avec STARTTLS

**Fonctionnement** :
1. `msg['Subject'] = subject` : définit l'objet de l'email
2. `msg['From'] = EMAIL` : expéditeur
3. `msg['To'] = TO_EMAIL` : destinataire
4. `server.starttls()` : active le chiffrement TLS
5. `server.login(EMAIL, PASSWORD)` : authentification
6. `server.send_message(msg)` : envoi du message
7. `server.quit()` : ferme la connexion

**Gestion d'erreur** :
- `try/except` : capture les erreurs de connexion SMTP
- Retourne `True` si succès, `False` si échec

### make_scan_report(network)
**Objectif** : Créer un rapport de scan formaté pour l'email

**Fonctionnement** :
1. `detailed_scan.detailed_network_scan(network)` : lance le scan
2. `detailed_scan.security_check(devices)` : vérifie la sécurité
3. `detailed_scan.show_detailed_results(devices)` : affiche dans le terminal

**Formatage du rapport** :
- `datetime.now().strftime('%d/%m/%Y %H:%M')` : date/heure française
- `len(devices)` : compte les appareils trouvés
- Boucle `for i, device in enumerate(devices, 1)` : numérote à partir de 1

**Structure du rapport** :
```
Rapport de scan - 15/01/2024 14:30
Réseau: 192.168.1.1/24
Appareils trouvés: 5

1. IP: 192.168.1.1
   MAC: AA:BB:CC:DD:EE:FF
   OS: Linux Server
   Ports: 22, 80, 443


[...]


ALERTES (2):
- ALERTE: Nouveau MAC détecté: XX:XX:XX
- ALERTE: MAC YY:YY:YY nouveaux ports ouverts: [4444]
```

**Paramètres utilisés** :
- `', '.join(map(str, device['ports']))` : joint les ports avec virgules
- `map(str, ...)` : convertit les ports en chaînes

### main()
**Objectif** : Fonction principale qui gère le scan automatique périodique

**Logique d'exécution** :

1. **Configuration initiale** :
   - Demande la plage réseau à scanner
   - Valide que ce n'est pas vide

2. **Premier scan immédiat** :
   - `make_scan_report(network)` : génère le rapport
   - `datetime.now().strftime('%H:%M')` : heure pour l'objet email
   - `send_email(subject, report)` : envoie le premier rapport

3. **Boucle automatique** :
   - `while True:` : boucle infinie
   - `time.sleep(3600)` : attend 3600 secondes = 1 heure
   - Répète le scan et l'envoi d'email

**Gestion d'interruption** :
- `try/except KeyboardInterrupt` : capture Ctrl+C
- Permet d'arrêter proprement le scan automatique

**Paramètres temporels** :
- `3600` secondes = 1 heure entre chaque scan
- Peut être modifié pour changer la fréquence

## Flux d'exécution
1. **main()** demande la configuration réseau
2. Lance le premier scan immédiatement
3. **make_scan_report()** :
   - Fait le scan avec detailed_scan
   - Vérifie la sécurité  
   - Formate le rapport texte
4. **send_email()** envoie le rapport par Gmail
5. Boucle toutes les heures :
   - Nouveau scan
   - Nouveau rapport
   - Nouvel email
6. Continue jusqu'à Ctrl+C

## Intégration avec detailed_scan
Ce module utilise entièrement detailed_scan.py pour :
- `detailed_network_scan()` : le scan réseau complet
- `security_check()` : détection d'anomalies sécuritaires
- `show_detailed_results()` : affichage terminal

L'avantage est la réutilisation du code et la cohérence des rapports.

## Sécurité email
- Utilise TLS pour chiffrer la connexion
- Mot de passe d'application Gmail (plus sécurisé)
- Gestion des erreurs de connexion
- Fermeture propre des connexions SMTP

## Cas d'usage
- Monitoring continu d'un réseau
- Détection automatique d'intrusions
- Rapports périodiques pour administrateurs
- Surveillance de changements réseau
