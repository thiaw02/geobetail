import meshtastic.serial_interface
import serial.tools.list_ports


def test_com6_connection():
    print("=== TEST DE CONNEXION COM6 ===")
    
    # 1. Vérification des ports disponibles
    print("1. Scan des ports COM...")
    ports = serial.tools.list_ports.comports()
    
    for port in ports:
        status = "✅" if port.device == "COM6" else "  "
        print(f"   {status} {port.device} - {port.description}")
    
    # 2. Test de connexion Meshtastic
    print("\n2. Test de connexion Meshtastic sur COM6...")
    try:
        interface = meshtastic.serial_interface.SerialInterface("COM6")
        print("   ✅ Connexion Meshtastic réussie!")
        
        # 3. Infos du device
        print("\n3. Informations du T-Beam:")
        node_info = interface.getMyNodeInfo()
        print(f"   Numéro de node: {node_info.get('num', 'N/A')}")
        print(f"   Utilisateur: {node_info.get('user', {}).get('longName', 'N/A')}")
        
        # 4. Statut GPS
        print("\n4. Statut GPS:")
        position = interface.getMyNodeInfo().get('position', {})
        if position:
            print(f"   Latitude: {position.get('latitude', 'N/A')}")
            print(f"   Longitude: {position.get('longitude', 'N/A')}")
            print(f"   Altitude: {position.get('altitude', 'N/A')}")
        else:
            print("   ❌ Aucune position GPS disponible")
            print("   Assurez-vous d'être en extérieur avec une vue dégagée du ciel")
        
        interface.close()
        
    except Exception as e:
        print(f"   ❌ Erreur de connexion: {e}")
        print("\nSolutions possibles:")
        print("   - Vérifiez que le câble USB est bien connecté")
        print("   - Essayez de redémarrer le T-Beam")
        print("   - Vérifiez dans le Gestionnaire de périphériques que COM6 est bien actif")

if __name__ == "__main__":
    test_com6_connection()