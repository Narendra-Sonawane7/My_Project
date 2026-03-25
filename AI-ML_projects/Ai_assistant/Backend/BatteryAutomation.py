"""
Battery Automation Module for SEEU AI
Monitors battery status, provides percentage info, and smart charging suggestions
"""

import psutil
import time
import threading
from datetime import datetime


class BatteryMonitor:
    """
    Advanced battery monitoring system for SEEU
    Tracks: Battery %, Charging status, Power events
    """

    def __init__(self):
        """Initialize Battery Monitor"""
        self.last_plugged_state = None
        self.last_battery_percent = None
        self.is_monitoring = False
        self.monitor_thread = None
        self.callbacks = {
            'on_charger_connected': None,
            'on_charger_disconnected': None,
            'on_battery_low': None,
            'on_battery_full': None,
            'on_battery_critical': None
        }

        # Thresholds
        self.LOW_BATTERY_THRESHOLD = 20
        self.CRITICAL_BATTERY_THRESHOLD = 10
        self.FULL_BATTERY_THRESHOLD = 95

        print("✅ Battery Monitor initialized")

    def debug_battery_object(self):
        """
        Debug function to see what attributes are available in battery object
        Useful for troubleshooting platform differences
        """
        try:
            battery = psutil.sensors_battery()
            if battery is None:
                print("❌ No battery object available")
                return

            print("\n🔍 Battery Object Debug Info:")
            print("=" * 60)
            print(f"Battery object type: {type(battery)}")
            print(f"\nAvailable attributes:")
            for attr in dir(battery):
                if not attr.startswith('_'):
                    try:
                        value = getattr(battery, attr)
                        print(f"  {attr}: {value} (type: {type(value).__name__})")
                    except:
                        print(f"  {attr}: <unable to read>")
            print("=" * 60)

        except Exception as e:
            print(f"❌ Error in debug: {e}")
            import traceback
            traceback.print_exc()

    def get_battery_info(self):
        """
        Get comprehensive battery information

        Returns:
            dict: Battery status information
        """
        try:
            battery = psutil.sensors_battery()

            if battery is None:
                return {
                    'available': False,
                    'message': 'No battery detected. Running on desktop PC.'
                }

            # Handle different attribute names across platforms
            # Some systems use 'power_plugged', others use 'plugged'
            percent = int(battery.percent)

            # Try different attribute names for plugged status
            plugged = None
            for attr in ['power_plugged', 'plugged', 'ac_line_status']:
                if hasattr(battery, attr):
                    plugged = getattr(battery, attr)
                    break

            # If still None, assume not plugged
            if plugged is None:
                plugged = False

            # Get time remaining (secsleft)
            time_left = None
            for attr in ['secsleft', 'secs_left', 'time_remaining']:
                if hasattr(battery, attr):
                    time_left = getattr(battery, attr)
                    break

            # Calculate time remaining
            if time_left is None:
                time_remaining = "Unknown"
            elif time_left == psutil.POWER_TIME_UNLIMITED or time_left == -1:
                time_remaining = "Charging"
            elif time_left == psutil.POWER_TIME_UNKNOWN or time_left == -2:
                time_remaining = "Unknown"
            elif time_left > 0:
                hours = time_left // 3600
                minutes = (time_left % 3600) // 60
                time_remaining = f"{hours}h {minutes}m"
            else:
                time_remaining = "Unknown"

            return {
                'available': True,
                'percent': percent,
                'plugged': plugged,
                'time_remaining': time_remaining,
                'status': 'Charging' if plugged else 'Discharging'
            }

        except Exception as e:
            print(f"❌ Error getting battery info: {e}")
            import traceback
            traceback.print_exc()
            return {
                'available': False,
                'message': f'Error: {e}'
            }

    def get_battery_percentage(self):
        """
        Get just the battery percentage

        Returns:
            int: Battery percentage (0-100) or None if unavailable
        """
        info = self.get_battery_info()
        if info['available']:
            return info['percent']
        return None

    def is_charging(self):
        """
        Check if device is currently charging

        Returns:
            bool: True if charging, False if not, None if unavailable
        """
        info = self.get_battery_info()
        if info['available']:
            return info['plugged']
        return None

    def get_battery_status_message(self):
        """
        Get a natural language battery status message

        Returns:
            str: Human-readable battery status
        """
        info = self.get_battery_info()

        if not info['available']:
            return info.get('message', 'Battery information unavailable.')

        percent = info['percent']
        plugged = info['plugged']
        time_remaining = info['time_remaining']

        # Build status message
        if plugged:
            if percent >= self.FULL_BATTERY_THRESHOLD:
                return f"Battery is at {percent}%. Fully charged. You can disconnect the charger."

            else:
                return f"Battery is at {percent}% and charging. Estimated time to full charge: {time_remaining}."
        else:
            if percent <= self.CRITICAL_BATTERY_THRESHOLD:
                return f"Critical! Battery is at {percent}%. Please connect the charger immediately!"
            elif percent <= self.LOW_BATTERY_THRESHOLD:
                return f"Battery is low at {percent}%. You should connect the charger soon. Estimated {time_remaining} remaining."
            else:
                return f"Battery is at {percent}%. Running on battery power. Estimated {time_remaining} remaining."

    def get_simple_percentage_message(self):
        """
        Get a simple battery percentage message

        Returns:
            str: Simple percentage message
        """
        percent = self.get_battery_percentage()

        if percent is None:
            return "Battery information is not available on this device."

        charging = self.is_charging()

        if charging:
            return f"Battery is at {percent}% and charging."
        else:
            return f"Battery is at {percent}%."

    def start_monitoring(self, check_interval=5):
        """
        Start background battery monitoring

        Args:
            check_interval: Seconds between battery checks (default: 5)
        """
        if self.is_monitoring:
            print("⚠️ Battery monitoring already running")
            return

        self.is_monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(check_interval,),
            daemon=True
        )
        self.monitor_thread.start()
        print(f"🔋 Battery monitoring started (checking every {check_interval}s)")

    def stop_monitoring(self):
        """Stop battery monitoring"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        print("⏹️ Battery monitoring stopped")

    def _monitor_loop(self, check_interval):
        """
        Internal monitoring loop

        Args:
            check_interval: Seconds between checks
        """
        while self.is_monitoring:
            try:
                info = self.get_battery_info()

                if not info['available']:
                    time.sleep(check_interval)
                    continue

                current_percent = info['percent']
                current_plugged = info['plugged']

                # Detect charger connection/disconnection
                if self.last_plugged_state is not None:
                    if current_plugged and not self.last_plugged_state:
                        # Charger connected
                        self._trigger_callback('on_charger_connected', current_percent)
                    elif not current_plugged and self.last_plugged_state:
                        # Charger disconnected
                        self._trigger_callback('on_charger_disconnected', current_percent)

                # Check battery levels when NOT charging
                if not current_plugged:
                    if current_percent <= self.CRITICAL_BATTERY_THRESHOLD:
                        if self.last_battery_percent is None or self.last_battery_percent > self.CRITICAL_BATTERY_THRESHOLD:
                            self._trigger_callback('on_battery_critical', current_percent)
                    elif current_percent <= self.LOW_BATTERY_THRESHOLD:
                        if self.last_battery_percent is None or self.last_battery_percent > self.LOW_BATTERY_THRESHOLD:
                            self._trigger_callback('on_battery_low', current_percent)

                # Check if battery full while charging
                if current_plugged and current_percent >= self.FULL_BATTERY_THRESHOLD:
                    if self.last_battery_percent is None or self.last_battery_percent < self.FULL_BATTERY_THRESHOLD:
                        self._trigger_callback('on_battery_full', current_percent)

                # Update state
                self.last_plugged_state = current_plugged
                self.last_battery_percent = current_percent

            except Exception as e:
                print(f"❌ Error in monitoring loop: {e}")

            time.sleep(check_interval)

    def _trigger_callback(self, event_name, battery_percent):
        """
        Trigger registered callback for battery events

        Args:
            event_name: Name of the event
            battery_percent: Current battery percentage
        """
        callback = self.callbacks.get(event_name)
        if callback:
            try:
                callback(battery_percent)
            except Exception as e:
                print(f"❌ Error in callback {event_name}: {e}")

    def register_callback(self, event_name, callback_function):
        """
        Register callback for battery events

        Args:
            event_name: 'on_charger_connected', 'on_charger_disconnected',
                       'on_battery_low', 'on_battery_full', 'on_battery_critical'
            callback_function: Function to call (receives battery_percent as argument)
        """
        if event_name in self.callbacks:
            self.callbacks[event_name] = callback_function
            print(f"✅ Registered callback for {event_name}")
        else:
            print(f"❌ Unknown event: {event_name}")


class BatteryVoiceCommands:
    """
    Process voice commands related to battery
    """

    def __init__(self, battery_monitor):
        """
        Initialize with a BatteryMonitor instance

        Args:
            battery_monitor: BatteryMonitor instance
        """
        self.monitor = battery_monitor

    def process_command(self, command_text):
        """
        Process battery-related voice commands

        Args:
            command_text: Voice command string

        Returns:
            str: Response message or None if command not recognized
        """
        command = command_text.lower().strip()

        # Battery percentage queries
        if any(phrase in command for phrase in [
            "battery", "battery percentage", "battery status",
            "how much battery", "battery level", "check battery",
            "what's the battery", "battery left"
        ]):
            # Full status if they say "status" or "check"
            if "status" in command or "check" in command:
                return self.monitor.get_battery_status_message()
            else:
                # Simple percentage otherwise
                return self.monitor.get_simple_percentage_message()

        # Charging status
        elif any(phrase in command for phrase in [
            "is charging", "am i charging", "charging status",
            "is it charging", "are we charging"
        ]):
            charging = self.monitor.is_charging()
            if charging is None:
                return "Battery information is not available."
            elif charging:
                percent = self.monitor.get_battery_percentage()
                return f"Yes, the system is charging. Battery is at {percent}%."
            else:
                return "No, the system is running on battery power."

        return None  # Command not recognized


# Event response messages for monitoring callbacks
class BatteryEventResponses:
    """
    Default response messages for battery events
    Use these with TTS to announce battery events
    """

    @staticmethod
    def charger_connected(percent):
        """Response when charger is connected"""
        return f"Charger connected. System is now charging. Battery at {percent}%."

    @staticmethod
    def charger_disconnected(percent):
        """Response when charger is disconnected"""
        return f"Charger disconnected. Running on battery power. Battery at {percent}%."

    @staticmethod
    def battery_low(percent):
        """Response when battery is low"""
        return f"Battery low warning! Battery at {percent}%. Please connect the charger soon."

    @staticmethod
    def battery_critical(percent):
        """Response when battery is critical"""
        return f"Critical battery warning! Only {percent}% remaining. Connect charger immediately!"

    @staticmethod
    def battery_full(percent):
        """Response when battery is full"""
        return f"Battery fully charged at {percent}%. You can disconnect the charger now."


# Quick access functions
def get_battery_percentage():
    """Quick function to get battery percentage"""
    monitor = BatteryMonitor()
    return monitor.get_simple_percentage_message()


def get_battery_status():
    """Quick function to get full battery status"""
    monitor = BatteryMonitor()
    return monitor.get_battery_status_message()


def is_charging():
    """Quick function to check if charging"""
    monitor = BatteryMonitor()
    return monitor.is_charging()


def handle_battery_command(command_text):
    """Quick function to process battery commands"""
    monitor = BatteryMonitor()
    voice_commands = BatteryVoiceCommands(monitor)
    return voice_commands.process_command(command_text)


# Example usage with monitoring and callbacks
if __name__ == "__main__":
    print("\n🔋 SEEU Battery Automation Test")
    print("=" * 60)

    # Create monitor
    monitor = BatteryMonitor()

    # Run debug to see available attributes
    print("\n🔍 Running battery debug...")
    monitor.debug_battery_object()

    # Test basic functions
    print("\n📊 Current Battery Status:")
    print(monitor.get_battery_status_message())
    print()

    info = monitor.get_battery_info()
    if info['available']:
        print(f"  Percentage: {info['percent']}%")
        print(f"  Status: {info['status']}")
        print(f"  Plugged: {'Yes' if info['plugged'] else 'No'}")
        print(f"  Time Remaining: {info['time_remaining']}")

    # Test voice commands
    print("\n\n🎤 Testing Voice Commands:")
    print("=" * 60)

    voice_processor = BatteryVoiceCommands(monitor)

    test_commands = [
        "battery percentage",
        "check battery",
        "is it charging",
        "battery status"
    ]

    for cmd in test_commands:
        response = voice_processor.process_command(cmd)
        print(f"\nCommand: '{cmd}'")
        print(f"Response: {response}")

    # Demonstrate monitoring setup
    print("\n\n🔍 Battery Monitoring Demo:")
    print("=" * 60)
    print("Monitoring can be enabled with callbacks:")
    print()
    print("Example setup:")
    print("""
    def on_charger_connected(percent):
        tts.SpeakSeeu(f"Charger connected. Battery at {percent}%")

    def on_battery_low(percent):
        tts.SpeakSeeu(f"Battery low at {percent}%. Please charge soon.")

    monitor.register_callback('on_charger_connected', on_charger_connected)
    monitor.register_callback('on_battery_low', on_battery_low)
    monitor.start_monitoring(check_interval=5)
    """)

    print("\n" + "=" * 60)
    print("✅ Battery Automation Module Ready!")
    print("=" * 60)

    # Interactive test
    print("\n🧪 Interactive Test Mode")
    print("Commands: 'status', 'percent', 'charging', 'monitor', 'stop', 'exit'")

    monitoring_active = False

    while True:
        try:
            cmd = input("\n> ").strip().lower()

            if cmd in ['exit', 'quit']:
                if monitoring_active:
                    monitor.stop_monitoring()
                break

            elif cmd == 'status':
                print(monitor.get_battery_status_message())

            elif cmd == 'percent':
                print(monitor.get_simple_percentage_message())

            elif cmd == 'charging':
                charging = monitor.is_charging()
                if charging is None:
                    print("Battery info unavailable")
                else:
                    print(f"Charging: {'Yes' if charging else 'No'}")

            elif cmd == 'monitor' and not monitoring_active:
                # Setup callbacks
                def on_charger_connected(p):
                    print(f"\n🔌 EVENT: {BatteryEventResponses.charger_connected(p)}")

                def on_charger_disconnected(p):
                    print(f"\n🔋 EVENT: {BatteryEventResponses.charger_disconnected(p)}")

                def on_battery_low(p):
                    print(f"\n⚠️ EVENT: {BatteryEventResponses.battery_low(p)}")

                def on_battery_critical(p):
                    print(f"\n🚨 EVENT: {BatteryEventResponses.battery_critical(p)}")

                def on_battery_full(p):
                    print(f"\n✅ EVENT: {BatteryEventResponses.battery_full(p)}")

                monitor.register_callback('on_charger_connected', on_charger_connected)
                monitor.register_callback('on_charger_disconnected', on_charger_disconnected)
                monitor.register_callback('on_battery_low', on_battery_low)
                monitor.register_callback('on_battery_critical', on_battery_critical)
                monitor.register_callback('on_battery_full', on_battery_full)

                monitor.start_monitoring(check_interval=3)
                monitoring_active = True
                print("✅ Monitoring started! Try connecting/disconnecting charger.")

            elif cmd == 'stop' and monitoring_active:
                monitor.stop_monitoring()
                monitoring_active = False

            else:
                print("Unknown command. Try: status, percent, charging, monitor, stop, exit")

        except KeyboardInterrupt:
            print("\n\nExiting...")
            if monitoring_active:
                monitor.stop_monitoring()
            break

    print("\n👋 Battery Automation Test Complete!")