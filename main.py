import scan
import blockip
import detailed_scan
import auto_scan
import os
import sys

# Vérifier les permissions root et redémarrer avec sudo si nécessaire
def check_root():
    if os.geteuid() != 0:
        print("Permissions root requises. Redémarrage avec sudo...")
        try:
            # Redémarrer avec sudo
            os.execvp('sudo', ['sudo', 'python3'] + sys.argv)
        except:
            print("Échec du redémarrage avec sudo. Veuillez exécuter manuellement: sudo python3 main.py")
            sys.exit(1)

# Afficher le menu principal
def show_menu():
    print("\n" + "="*50)
    print("              SECNET - MENU PRINCIPAL")
    print("="*50)
    print("1. Scanner le réseau")
    print("2. Bloquer une IP")
    print("3. Débloquer une IP") 
    print("4. Voir les IPs bloquées")
    print("5. Scan de sécurité détaillé")
    print("6. Scan automatique avec email")
    print("7. Quitter")
    print("="*50)

# Fonction pour scanner le réseau
def menu_scan():
    print("\n--- SCANNER LE RÉSEAU ---")
    network = input("Entrez la plage réseau (ex: 10.10.10.1/24): ").strip()
    
    if not network:
        print("Erreur: Veuillez entrer une plage réseau")
        return
    
    print("Scanning...")
    devices = scan.scan_network(network)
    
    if not devices:
        print("Aucun appareil trouvé")
    else:
        print(f"\n{len(devices)} appareil(s) trouvé(s):")
        print("-" * 60)
        for i, device in enumerate(devices, 1):
            print(f"{i}. {device['ip']} - {device['os']}")     #********************************************************************************??????????
        
        # Demander les détails d'un appareil
        while True:
            choice = input("\nEntrez le numéro pour voir les détails (ou Enter pour continuer): ").strip()
            if not choice:
                break
            try:
                idx = int(choice) - 1      #********************************************************************************??????????
                if 0 <= idx < len(devices):
                    device = devices[idx]
                    print("\n" + "="*40)
                    print(scan.get_device_details_text(device))
                    print("="*40)
                else:
                    print("Numéro invalide")
            except ValueError:
                print("Veuillez entrer un numéro valide")

# Fonction pour bloquer une IP
def menu_block():
    print("\n--- BLOQUER UNE IP ---")
    ip = input("Entrez l'IP à bloquer (ex: 10.10.10.100): ").strip()
    
    if not ip:
        print("Erreur: Veuillez entrer une adresse IP")
        return
    
    if not blockip.is_valid_ip(ip):
        print("Erreur: Adresse IP invalide")
        return
    
    gateway = blockip.get_default_gateway()
    success = blockip.block_ip(ip, gateway)
    
    if success:
        print(f"IP {ip} bloquée avec succès")
    else:
        print(f"Échec du blocage de {ip}")

# Fonction pour débloquer une IP
def menu_unblock():
    print("\n--- DÉBLOQUER UNE IP ---")
    
    if not blockip.blocked_ips:
        print("Aucune IP bloquée")
        return
    
    print("IPs actuellement bloquées:")
    for i, ip in enumerate(blockip.blocked_ips, 1):
        print(f"{i}. {ip}")
    
    ip = input("Entrez l'IP à débloquer: ").strip()
    
    if not ip:
        print("Erreur: Veuillez entrer une adresse IP")
        return
    
    success = blockip.unblock_ip(ip)
    
    if success:
        print(f"IP {ip} débloquée avec succès")
    else:
        print(f"Échec du déblocage de {ip}")

# Fonction pour voir les IPs bloquées
def menu_show_blocked():
    print("\n--- IPS BLOQUÉES ---")
    
    if not blockip.blocked_ips:
        print("Aucune IP bloquée")
    else:
        print(f"{len(blockip.blocked_ips)} IP(s) bloquée(s):")
        for i, ip in enumerate(blockip.blocked_ips, 1):
            print(f"{i}. {ip}")

# Fonction pour le scan de sécurité détaillé
def menu_detailed_security_scan():
    print("\n--- SCAN DE SÉCURITÉ DÉTAILLÉ ---")
    network = input("Entrez la plage réseau (ex: 10.10.10.1/24): ").strip()
    
    if not network:
        print("Erreur: Veuillez entrer une plage réseau")
        return
    
    print("Scan détaillé en cours...")
    devices = detailed_scan.detailed_network_scan(network)
    
    if not devices:
        print("Aucun appareil trouvé")
        return
    
    # Afficher les résultats
    detailed_scan.show_detailed_results(devices)
    
    # Vérification sécuritaire
    detailed_scan.security_check(devices)

# Fonction pour le scan automatique
def menu_auto_scan():
    print("\n--- SCAN AUTOMATIQUE AVEC EMAIL ---")
    auto_scan.main()

# Fonction principale
def main():
    check_root()
    
    while True:
        show_menu()
        choice = input("Votre choix: ").strip()
        
        if choice == "1":
            menu_scan()
        elif choice == "2":
            menu_block()
        elif choice == "3":
            menu_unblock()
        elif choice == "4":
            menu_show_blocked()
        elif choice == "5":
            menu_detailed_security_scan()
        elif choice == "6":
            menu_auto_scan()
        elif choice == "7":
            print("Au revoir!")
            break
        else:
            print("Choix invalide. Veuillez entrer 1, 2, 3, 4, 5, 6 ou 7")

if __name__ == "__main__":
    main()