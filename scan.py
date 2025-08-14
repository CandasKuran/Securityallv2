import subprocess

# Fonction principale pour scanner le réseau
def scan_network(network_range):
    devices = []
    
    try:
        # Scan avec plus de ports pour détecter plus de services
        cmd = ["nmap", "-sV", "-p", "21,22,23,25,53,80,110,135,139,443,445,993,995,3389,4444,8080", "--open", "-T4", network_range]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            devices = parse_nmap_output(result.stdout)
        return devices
        
    except Exception as e:
        print(f"Scan error: {e}")
        return []

# Parser simple pour la sortie nmap
def parse_nmap_output(output):     #********************************************************************************??????????
    devices = []
    lines = output.split('\n')
    current_device = None
    
    for line in lines:
        line = line.strip()
        
        # Nouveau périphérique trouvé
        if "Nmap scan report for" in line:
            if current_device:
                # Traiter l'appareil précédent avant de passer au suivant
                if current_device["os"] == "Unknown":
                    current_device["os"] = guess_os_from_ports(current_device["ports"])
                devices.append(current_device)
            
            # Extraire l'adresse IP
            ip = extract_ip(line)
            current_device = {
                "ip": ip,
                "mac": "Unknown",           #********************************************************************************??????????
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
    
    # Ajouter le dernier périphérique
    if current_device:
        # Deviner l'OS basé sur les ports si pas trouvé
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
def extract_ip(line):     #********************************************************************************??????????
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

# Format des détails d'un périphérique
def get_device_details_text(device):
    details = f"IP Address: {device['ip']}\n"
    details += f"MAC Address: {device['mac']}\n"
    details += f"Operating System: {device['os']}\n"
    
    if device['ports']:
        details += f"Open Ports: {', '.join(map(str, device['ports']))}\n"
    else:
        details += "Open Ports: None detected\n"
    
    return details