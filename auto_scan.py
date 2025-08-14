import time
import smtplib
from email.mime.text import MIMEText
import detailed_scan
import datetime

# Configuration email
EMAIL = "candas.kuran@gmail.com"
PASSWORD = "zbht esqj xryv oazk"
TO_EMAIL = "candas.kuran@gmail.com"

def send_email(subject, message):
    try:
        msg = MIMEText(message, 'plain', 'utf-8')
        msg['Subject'] = subject
        msg['From'] = EMAIL
        msg['To'] = TO_EMAIL
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL, PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print(f"Email envoyé à: {TO_EMAIL}")
        return True
    except Exception as e:
        print(f"Erreur email: {e}")
        return False

def make_scan_report(network):
    # Faire le scan détaillé
    devices = detailed_scan.detailed_network_scan(network)
    alerts = detailed_scan.security_check(devices)
    
    # Afficher dans le terminal
    detailed_scan.show_detailed_results(devices)
    
    # Créer le texte pour l'email
    now = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
    report = f"Rapport de scan - {now}\n"
    report += f"Réseau: {network}\n"
    report += f"Appareils trouvés: {len(devices)}\n\n"
    
    for i, device in enumerate(devices, 1):
        report += f"{i}. IP: {device['ip']}\n"
        report += f"   MAC: {device['mac']}\n"
        report += f"   OS: {device['os']}\n"
        if device['ports']:
            report += f"   Ports: {', '.join(map(str, device['ports']))}\n"
        report += "\n"
    
    if alerts:
        report += f"ALERTES ({len(alerts)}):\n"
        for alert in alerts:
            report += f"- {alert}\n"
    else:
        report += "Sécurité: OK\n"
    
    return report



def main():
    print("Auto Scan - Scan automatique toutes les heures")
    
    network = input("Entrez le réseau (exemple: 192.168.1.1/24): ")
    if not network:
        print("Réseau requis!")
        return
    
    print(f"Réseau: {network}")
    print("Premier scan en cours...")
    
    # Faire le premier scan immédiatement
    report = make_scan_report(network)
    subject = f"Premier scan - {datetime.datetime.now().strftime('%H:%M')}"
    send_email(subject, report)
    
    print("\nScan automatique démarré...")
    print("Appuyez CTRL+C pour arrêter")
    print("Prochain scan dans 1 heure...")
    
    try:
        while True:
            time.sleep(3600)  # Attendre 1 heure
            print(f"\nScan démarré: {datetime.datetime.now().strftime('%H:%M:%S')}")
            
            # Faire le scan et envoyer l'email
            report = make_scan_report(network)
            subject = f"Rapport de scan - {datetime.datetime.now().strftime('%H:%M')}"
            send_email(subject, report)
            
            print("Prochain scan dans 1 heure...")
    except KeyboardInterrupt:
        print("\nScan automatique arrêté!")

if __name__ == "__main__":
    main()