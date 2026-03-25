"""
Handles WiFi and Bluetooth control for SEEU
"""

import subprocess
import ctypes
import sys
import time
import os

class SystemController:
    """
    Fluent system controller for WiFi and Bluetooth
    Works on Windows 10/11
    """

    @staticmethod
    def is_admin():
        """Check if running as administrator"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    @staticmethod
    def run_as_admin():
        """Restart script as administrator"""
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit()

    @staticmethod
    def wifi_status():
        """Check WiFi status"""
        try:
            result = subprocess.run(
                'netsh interface show interface "Wi-Fi"',
                shell=True,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return "Enabled" in result.stdout
        except:
            return None

    @staticmethod
    def wifi_on():
        """Turn WiFi ON"""
        try:
            subprocess.run(
                'netsh interface set interface "Wi-Fi" enabled',
                shell=True,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            subprocess.run(
                'net start WlanSvc',
                shell=True,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            time.sleep(2)
            return True
        except Exception as e:
            print(f"WiFi ON error: {e}")
            return False

    @staticmethod
    def wifi_off():
        """Turn WiFi OFF"""
        try:
            subprocess.run(
                'netsh interface set interface "Wi-Fi" disabled',
                shell=True,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            subprocess.run(
                'net stop WlanSvc',
                shell=True,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            return True
        except Exception as e:
            print(f"WiFi OFF error: {e}")
            return False

    @staticmethod
    def toggle_wifi():
        """Toggle WiFi state"""
        if SystemController.wifi_status():
            return SystemController.wifi_off()
        else:
            return SystemController.wifi_on()

    @staticmethod
    def bluetooth_status():
        """Check Bluetooth status"""
        try:
            result = subprocess.run(
                'powershell Get-PnpDevice -Class Bluetooth | Where-Object {$_.FriendlyName -like "*Bluetooth*"} | Select-Object Status',
                shell=True,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return "OK" in result.stdout or "Enabled" in result.stdout
        except:
            return None

    @staticmethod
    def bluetooth_on():
        """Turn Bluetooth ON"""
        try:
            commands = [
                'powershell Get-PnpDevice -Class Bluetooth | Enable-PnpDevice -Confirm:$false',
                'sc config bthserv start= auto',
                'net start bthserv',
                'timeout /t 2 /nobreak > nul'
            ]

            for cmd in commands:
                subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )

            time.sleep(3)
            return True
        except Exception as e:
            print(f"Bluetooth ON error: {e}")
            return False

    @staticmethod
    def bluetooth_off():
        """Turn Bluetooth OFF"""
        try:
            commands = [
                'powershell Get-PnpDevice -Class Bluetooth | Disable-PnpDevice -Confirm:$false',
                'net stop bthserv',
                'sc config bthserv start= disabled'
            ]

            for cmd in commands:
                subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )

            return True
        except Exception as e:
            print(f"Bluetooth OFF error: {e}")
            return False

    @staticmethod
    def toggle_bluetooth():
        """Toggle Bluetooth state"""
        if SystemController.bluetooth_status():
            return SystemController.bluetooth_off()
        else:
            return SystemController.bluetooth_on()


class VoiceCommandProcessor:
    """
    Process voice commands for SEEU
    """

    @staticmethod
    def process_command(command_text):
        """Process voice command and execute appropriate action"""
        command = command_text.lower().strip()

        # WiFi commands
        if any(phrase in command for phrase in [
            "wifi on", "turn on wifi", "enable wifi",
            "start wifi", "connect wifi", "wi-fi on"
        ]):
            if SystemController.wifi_on():
                return "WiFi has been turned on successfully."
            else:
                return "Failed to turn WiFi on. Please try again."

        elif any(phrase in command for phrase in [
            "wifi off", "turn off wifi", "disable wifi",
            "stop wifi", "disconnect wifi", "wi-fi off"
        ]):
            if SystemController.wifi_off():
                return "WiFi has been turned off successfully."
            else:
                return "Failed to turn WiFi off. Please try again."

        elif "toggle wifi" in command or "switch wifi" in command:
            if SystemController.toggle_wifi():
                status = "on" if SystemController.wifi_status() else "off"
                return f"WiFi toggled. Now WiFi is {status}."
            else:
                return "Failed to toggle WiFi."

        # Bluetooth commands
        elif any(phrase in command for phrase in [
            "bluetooth on", "turn on bluetooth", "enable bluetooth",
            "start bluetooth", "bluetooth enable", "bt on"
        ]):
            if SystemController.bluetooth_on():
                return "Bluetooth has been turned on successfully."
            else:
                return "Failed to turn Bluetooth on. Please try again."

        elif any(phrase in command for phrase in [
            "bluetooth off", "turn off bluetooth", "disable bluetooth",
            "stop bluetooth", "bluetooth disable", "bt off"
        ]):
            if SystemController.bluetooth_off():
                return "Bluetooth has been turned off successfully."
            else:
                return "Failed to turn Bluetooth off. Please try again."

        elif "toggle bluetooth" in command or "switch bluetooth" in command:
            if SystemController.toggle_bluetooth():
                status = "on" if SystemController.bluetooth_status() else "off"
                return f"Bluetooth toggled. Now Bluetooth is {status}."
            else:
                return "Failed to toggle Bluetooth."

        # Status commands
        elif "wifi status" in command or "is wifi on" in command:
            status = SystemController.wifi_status()
            if status is None:
                return "Could not determine WiFi status."
            return f"WiFi is {'ON' if status else 'OFF'}."

        elif "bluetooth status" in command or "is bluetooth on" in command:
            status = SystemController.bluetooth_status()
            if status is None:
                return "Could not determine Bluetooth status."
            return f"Bluetooth is {'ON' if status else 'OFF'}."

        elif "system status" in command or "check connections" in command:
            wifi = "ON" if SystemController.wifi_status() else "OFF"
            bluetooth = "ON" if SystemController.bluetooth_status() else "OFF"
            return f"WiFi: {wifi}, Bluetooth: {bluetooth}."

        # Combined commands
        elif "all wireless off" in command or "turn off all connections" in command:
            wifi_result = SystemController.wifi_off()
            bt_result = SystemController.bluetooth_off()
            return "All wireless connections turned off." if wifi_result and bt_result else "Partially completed."

        elif "all wireless on" in command or "turn on all connections" in command:
            wifi_result = SystemController.wifi_on()
            bt_result = SystemController.bluetooth_on()
            return "All wireless connections turned on." if wifi_result and bt_result else "Partially completed."

        return None  # Return None if command not recognized


# Quick access function
def handle_wireless_command(command_text):
    """Quick function to process wireless commands"""
    return VoiceCommandProcessor.process_command(command_text)


if __name__ == "__main__":
    # Test the module
    print("Testing SystemControl module...")
    test_commands = ["wifi status", "bluetooth on", "system status"]
    for cmd in test_commands:
        response = handle_wireless_command(cmd)
        print(f"{cmd}: {response}")