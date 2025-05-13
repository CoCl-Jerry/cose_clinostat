import subprocess

def get_current_ssid():
    try:
        result = subprocess.run(["iwgetid", "-r"], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error getting current SSID: {e}")
        return None

def handle_handshake_response(response_data):
    try:
        response_parts = response_data.split(',')
        ssid = response_parts[1].split('=')[1]
        password = response_parts[2].split('=')[1]
        print(f"Received SSID: {ssid}, PASSWORD: {password}")

        current_ssid = get_current_ssid()
        print(f"Current SSID: {current_ssid}, Received SSID: {ssid}")

        if current_ssid == ssid:
            print(f"Already connected to SSID: {ssid}")
            return

        print(f"Connecting to new Wi-Fi SSID: {ssid}, PASSWORD: {password}")

        # Create a WPA supplicant configuration file
        wpa_supplicant_conf = f"""
        ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
        update_config=1
        country=US

        network={{
            ssid="{ssid}"
            psk="{password}"
            key_mgmt=WPA-PSK
        }}
        """
        with open("/etc/wpa_supplicant/wpa_supplicant.conf", "w") as file:
            file.write(wpa_supplicant_conf)

        # Restart wpa_supplicant service
        subprocess.run(["sudo", "wpa_cli", "-i", "wlan0", "reconfigure"], check=True)

        # Obtain an IP address using dhclient
        subprocess.run(["sudo", "dhclient", "wlan0"], check=True)

        print("Connected to Wi-Fi network successfully.")
    except Exception as e:
        print(f"Error connecting to Wi-Fi: {e}")