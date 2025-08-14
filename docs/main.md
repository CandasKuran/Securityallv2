# Documentation main.py

## Vue d'ensemble
Ce fichier est le point d'entrée principal de l'application SECNET. Il gère l'interface utilisateur et orchestre tous les modules de scan et de sécurité.

## Imports
```python
import scan
import blockip
import detailed_scan
import auto_scan
import os
import sys
```
- `scan` : module pour scanner le réseau basique
- `blockip` : module pour bloquer/débloquer des IP
- `detailed_scan` : module pour scan de sécurité avancé
- `auto_scan` : module pour scan automatique avec email
- `os` : fonctions système (vérifier permissions root)
- `sys` : contrôle du programme (arguments, exit)

## Fonctions

### check_root()
**Objectif** : Vérifier que le programme a les permissions root nécessaires

**Fonctionnement** :
- `os.geteuid() != 0` : vérifie si l'utilisateur actuel n'est pas root (UID 0)
- `os.execvp('sudo', ['sudo', 'python3'] + sys.argv)` : redémarre le programme avec sudo
- `sys.argv` : liste des arguments passés au programme
- `sys.exit(1)` : quitte le programme avec code d'erreur 1

**Pourquoi** : Les outils réseau comme nmap et arpspoof nécessitent des privilèges root

### show_menu()
**Objectif** : Afficher le menu principal avec les options disponibles

**Fonctionnement** :
- `print("\n" + "="*50)` : crée une ligne de séparation avec 50 caractères "="
- Affiche 7 options numérotées pour l'utilisateur

**Pourquoi** : Interface utilisateur claire et organisée

### menu_scan()
**Objectif** : Gérer le scan réseau basique via l'interface

**Paramètres utilisés** :
- `input().strip()` : `.strip()` enlève les espaces avant/après la saisie utilisateur
- `if not network` : vérifie si la chaîne est vide
- `scan.scan_network(network)` : appelle la fonction de scan du module scan.py
- `enumerate(devices, 1)` : crée une liste numérotée à partir de 1

**Logique** :
1. Demande la plage réseau à l'utilisateur
2. Valide que ce n'est pas vide
3. Lance le scan via scan.py
4. Affiche les résultats
5. Permet de voir les détails d'un appareil spécifique

### menu_block()
**Objectif** : Interface pour bloquer une adresse IP

**Paramètres utilisés** :
- `blockip.is_valid_ip(ip)` : valide le format de l'IP
- `blockip.get_default_gateway()` : obtient la passerelle par défaut
- `blockip.block_ip(ip, gateway)` : lance le blocage ARP

**Logique** :
1. Demande l'IP à bloquer
2. Valide le format IP
3. Obtient la passerelle réseau
4. Lance le blocage via blockip.py

### menu_unblock()
**Objectif** : Interface pour débloquer une adresse IP

**Paramètres utilisés** :
- `blockip.blocked_ips` : liste globale des IP bloquées
- `enumerate(blockip.blocked_ips, 1)` : numérote la liste à partir de 1

**Logique** :
1. Vérifie s'il y a des IP bloquées
2. Affiche la liste
3. Demande quelle IP débloquer
4. Lance le déblocage via blockip.py

### menu_show_blocked()
**Objectif** : Afficher toutes les IP actuellement bloquées

**Fonctionnement** :
- Accède à `blockip.blocked_ips` (liste globale)
- `len(blockip.blocked_ips)` : compte le nombre d'IP bloquées

### menu_detailed_security_scan()
**Objectif** : Interface pour le scan de sécurité avancé

**Logique** :
1. Demande la plage réseau
2. Lance `detailed_scan.detailed_network_scan(network)`
3. Affiche les résultats avec `detailed_scan.show_detailed_results(devices)`
4. Vérifie la sécurité avec `detailed_scan.security_check(devices)`

### menu_auto_scan()
**Objectif** : Lancer le mode scan automatique avec emails

**Fonctionnement** :
- Appelle directement `auto_scan.main()` qui gère tout le processus

### main()
**Objectif** : Fonction principale qui orchestre tout le programme

**Logique** :
1. Vérifie les permissions root avec `check_root()`
2. Boucle infinie `while True:` pour le menu
3. `input("Votre choix: ").strip()` : récupère le choix utilisateur
4. Structure if/elif/else pour router vers la bonne fonction
5. `break` : sort de la boucle pour quitter le programme

**Bloc final** :
```python
if __name__ == "__main__":
    main()
```
Ce bloc assure que `main()` ne s'exécute que si le fichier est lancé directement (pas importé comme module).

## Flux d'exécution
1. Vérification des permissions root
2. Affichage du menu en boucle
3. Traitement du choix utilisateur
4. Appel du module approprié
5. Retour au menu (sauf pour quitter)
