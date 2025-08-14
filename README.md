# Diagramme d'Activité - SECNET

```mermaid
flowchart TD
    A([Démarrage de l'application]) --> B[Vérification des permissions root]
    B --> C{Root OK ?}
    C -->|Non| D([Redémarrage avec sudo])
    C -->|Oui| E[Afficher le menu principal]

    E --> F{Choix de l'utilisateur}
    F -->|1: Scanner le réseau| G[Entrer plage réseau]
    G --> H[Scan réseau avec scan.py]
    H --> I{Appareils trouvés ?}
    I -->|Oui| J[Afficher appareils]
    J --> K[Voir détails d'un appareil choisi]
    I -->|Non| L([Message: Aucun appareil trouvé])

    F -->|2: Bloquer une IP| M[Entrer IP à bloquer]
    M --> N[Validation IP]
    N --> O{IP valide ?}
    O -->|Oui| P[Blocage via blockip.py]
    O -->|Non| Q([Message: IP invalide])

    F -->|3: Débloquer une IP| R[Afficher IPs bloquées]
    R --> S[Entrer IP à débloquer]
    S --> T[Déblocage via blockip.py]

    F -->|4: Voir IPs bloquées| U[Afficher toutes les IPs bloquées]

    F -->|5: Scan de sécurité détaillé| V[Entrer plage réseau]
    V --> W[Scan détaillé avec detailed_scan.py]
    W --> X[Contrôle sécurité via whitelist et mappings]
    X --> Y{Alertes détectées ?}
    Y -->|Oui| Z[Afficher alertes]
    Y -->|Non| AA([Message: Réseau sécurisé])
    W --> AB[Afficher résultats détaillés]

    F -->|6: Scan automatique avec email| AC[Entrer plage réseau]
    AC --> AD[Premier scan avec detailed_scan.py]
    AD --> AE[Envoyer rapport par email]
    AE --> AF[Boucle: scan automatique chaque heure]

    F -->|7: Quitter| AG([Fin de l'application])
