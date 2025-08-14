import subprocess
import os

# Fonction pour scanner le réseau et obtenir les détails complets
def detailed_network_scan(network_range):
    devices = []
    
    try:
        # Scan détaillé avec nmap - même commande que scan.py
        cmd = ["nmap", "-sV", "-p", "21,22,23,25,53,80,110,135,139,443,445,993,995,3389,4444,8080", "--open", "-T4", network_range]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            devices = parse_detailed_nmap_output(result.stdout)
        
        return devices
        
    except Exception as e:
        print(f"Erreur de scan: {e}")
        return []

# Parser pour la sortie nmap détaillée
def parse_detailed_nmap_output(output):
    devices = []
    lines = output.split('\n')
    current_device = None
    
    for line in lines:
        line = line.strip()
        
        # Nouveau périphérique trouvé
        if "Nmap scan report for" in line:
            if current_device:
                # OS avant d'ajouter
                if current_device["os"] == "Unknown":
                    current_device["os"] = guess_os_from_ports(current_device["ports"])
                devices.append(current_device)
            
            # Extraire l'adresse IP
            ip = extract_ip(line)
            current_device = {
                "ip": ip,
                "mac": "Unknown",
                "os": "Unknown", 
                "ports": []
            }
        
        # Adresse MAC
        elif "MAC Address:" in line and current_device:
            parts = line.split()
            if len(parts) >= 3:
                current_device["mac"] = parts[2]
        
        # Information des ports
        elif "/tcp" in line and "open" in line and current_device:
            port = line.split('/')[0]
            if port.isdigit():
                current_device["ports"].append(int(port))
        
        # OS Detection
        elif "Running:" in line and current_device:
            current_device["os"] = line.replace("Running:", "").strip()
    
    # Ajouter le dernier périphérique
    if current_device:
        # Si OS toujours Unknown, deviner à partir des ports
        if current_device["os"] == "Unknown":
            current_device["os"] = guess_os_from_ports(current_device["ports"])
        devices.append(current_device)
    
    return devices

# Deviner l'OS simple basé sur les ports
def guess_os_from_ports(ports):
    if not ports:
        return "Unknown"
    
    # Ports très spécifiques (priorité maximale)
    if 4444 in ports:
        if 22 in ports:  # SSH + Metasploit = Linux Metasploit
            return "Metasploit Linux"
        else:
            return "Metasploit"
    
    # SSH est très caractéristique de Linux (priorité haute)
    if 22 in ports:
        web_ports = [80, 443, 8080, 8443]
        if any(p in web_ports for p in ports):
            return "Linux Server"
        else:
            return "Linux/Unix"
    
    # Ports Windows spécifiques
    windows_ports = [135, 139, 445, 3389]  # RPC, NetBIOS, SMB, RDP
    found_windows = [p for p in ports if p in windows_ports]
    
    if found_windows:
        web_ports = [80, 443, 8080, 8443]
        if any(p in web_ports for p in ports):
            return "Windows Server"
        else:
            return "Windows"
    
    # Autres détections
    if 23 in ports:  # Telnet
        return "Network Device"
    elif any(p in [80, 443, 8080, 8443] for p in ports):
        return "Web Server"
    elif any(p in [21, 25, 53, 110, 143] for p in ports):
        return "Linux/Unix"
    else:
        return f"Unknown (ports: {ports[:3]})"

# Extraire l'IP de la ligne
def extract_ip(line):
    parts = line.split()
    for part in parts:
        if is_valid_ip(part.replace('(', '').replace(')', '')):
            return part.replace('(', '').replace(')', '')
    return "Unknown"

# Validation IP
def is_valid_ip(ip):
    try:
        parts = ip.split('.')
        return len(parts) == 4 and all(0 <= int(p) <= 255 for p in parts)
    except:
        return False

# Charger la whitelist des MACs
def load_mac_whitelist():
    mac_list = []
    try:
        with open('mac_whitelist.txt', 'r') as f:
            for line in f:
                mac = line.strip()
                if mac:
                    mac_list.append(mac)
    except FileNotFoundError:
        print("Fichier mac_whitelist.txt non trouvé")
    return mac_list

# Charger le mapping MAC-IP
def load_mac_ip_mapping():
    mapping = {}
    try:
        with open('mac_ip_mapping.txt', 'r') as f:
            for line in f:
                parts = line.strip().split(',')
                if len(parts) == 2:
                    mapping[parts[0]] = parts[1]
    except FileNotFoundError:
        print("Fichier mac_ip_mapping.txt non trouvé")
    return mapping

# Charger le mapping MAC-OS
def load_mac_os_mapping():
    mapping = {}
    try:
        with open('mac_os_mapping.txt', 'r') as f:
            for line in f:
                parts = line.strip().split(',')
                if len(parts) == 2:
                    mapping[parts[0]] = parts[1]
    except FileNotFoundError:
        print("Fichier mac_os_mapping.txt non trouvé")
    return mapping

# Charger le mapping MAC-Ports
def load_mac_ports_mapping():
    mapping = {}
    try:
        with open('mac_ports_mapping.txt', 'r') as f:
            for line in f:
                parts = line.strip().split(',')
                if len(parts) >= 2:
                    mac = parts[0]
                    ports = [int(p) for p in parts[1:] if p.isdigit()]
                    mapping[mac] = ports
    except FileNotFoundError:
        print("Fichier mac_ports_mapping.txt non trouvé")
    return mapping

# Fonction principale de vérification sécuritaire
def security_check(devices):
    print("\n--- VÉRIFICATION SÉCURITAIRE ---")
    
    # Charger toutes les listes de référence
    mac_whitelist = load_mac_whitelist()
    mac_ip_map = load_mac_ip_mapping()
    mac_os_map = load_mac_os_mapping()
    mac_ports_map = load_mac_ports_mapping()
    
    alerts = []
    
    for device in devices:
        mac = device['mac']
        ip = device['ip']
        os = device['os']
        ports = device['ports']
        
        # Vérifier si MAC est dans la whitelist
        if mac != "Unknown" and mac not in mac_whitelist:
            alerts.append(f"ALERTE: Nouveau MAC détecté: {mac} (IP: {ip})")
        
        # Vérifier le mapping MAC-IP
        if mac in mac_ip_map:
            expected_ip = mac_ip_map[mac]
            if ip != expected_ip:
                alerts.append(f"ALERTE: MAC {mac} sur IP différente (attendue: {expected_ip}, actuelle: {ip})")
        
        # Vérifier le mapping MAC-OS
        if mac in mac_os_map:
            expected_os = mac_os_map[mac]
            if os != "Unknown" and os != expected_os:
                alerts.append(f"ALERTE: MAC {mac} OS différent (attendu: {expected_os}, actuel: {os})")
        
        # Vérifier les ports
        if mac in mac_ports_map:
            expected_ports = mac_ports_map[mac]
            new_ports = [p for p in ports if p not in expected_ports]
            if new_ports:
                alerts.append(f"ALERTE: MAC {mac} nouveaux ports ouverts: {new_ports}")
    
    # Afficher les résultats
    if alerts:
        print(f"\n{len(alerts)} ALERTE(S) DÉTECTÉE(S):")
        for alert in alerts:
            print(f"⚠️  {alert}")
    else:
        print("\n✅ Aucune anomalie détectée - Réseau sécurisé")
    
    return alerts

# Afficher les résultats du scan détaillé
def show_detailed_results(devices):
    print(f"\n{len(devices)} appareil(s) trouvé(s) avec détails:")
    print("-" * 80)
    
    for i, device in enumerate(devices, 1):
        print(f"{i}. IP: {device['ip']}")
        print(f"   MAC: {device['mac']}")
        print(f"   OS: {device['os']}")
        if device['ports']:
            print(f"   Ports: {', '.join(map(str, device['ports']))}")
        else:
            print("   Ports: Aucun détecté")
        print("-" * 40)
