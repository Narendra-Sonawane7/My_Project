"""
TaskAutomation.py - SEEU AI Direct Task Automation
Place in: Backend/TaskAutomation.py

Handles without needing AI:
  - Timer / Reminders
  - Folder: create, delete, rename
  - Files: move, copy, find, zip, unzip, cleanup downloads
  - Apps: open, close
  - Screenshot
  - Time and Date
  - Internet Speed
  - RAM, CPU, Process info
"""

import os
import re
import time
import shutil
import zipfile
import glob
import threading
import subprocess
import psutil
from datetime import datetime
from typing import Optional, Callable

# ─────────────────────────────────────────────────────────────────────────────
# Common Windows path shortcuts
# ─────────────────────────────────────────────────────────────────────────────

COMMON_PATHS = {
    "desktop":   os.path.join(os.path.expanduser("~"), "Desktop"),
    "downloads": os.path.join(os.path.expanduser("~"), "Downloads"),
    "documents": os.path.join(os.path.expanduser("~"), "Documents"),
    "pictures":  os.path.join(os.path.expanduser("~"), "Pictures"),
    "music":     os.path.join(os.path.expanduser("~"), "Music"),
    "videos":    os.path.join(os.path.expanduser("~"), "Videos"),
    "home":      os.path.expanduser("~"),
}

def _resolve_path(path_str: str) -> str:
    """Convert shortcut names like desktop to full paths."""
    p = path_str.strip().lower().rstrip(".")
    for name, full in COMMON_PATHS.items():
        if p == name or p == f"the {name}":
            return full
    return os.path.expandvars(os.path.expanduser(path_str.strip()))


# ─────────────────────────────────────────────────────────────────────────────
# 1. TIMER / REMINDER
# ─────────────────────────────────────────────────────────────────────────────

_active_timers = {}

def set_timer(duration_seconds: int, message: str, speak_fn: Callable = None) -> str:
    timer_id = f"timer_{int(time.time())}"

    def _fire():
        alert = message or "Your timer is up!"
        print(f"\n TIMER: {alert}")
        if speak_fn:
            try:
                speak_fn(alert)
            except Exception:
                pass
        _active_timers.pop(timer_id, None)

    t = threading.Timer(duration_seconds, _fire)
    t.daemon = True
    t.start()
    _active_timers[timer_id] = t

    mins = duration_seconds // 60
    secs = duration_seconds % 60
    if mins and secs:
        human = f"{mins} minute{'s' if mins != 1 else ''} and {secs} second{'s' if secs != 1 else ''}"
    elif mins:
        human = f"{mins} minute{'s' if mins != 1 else ''}"
    else:
        human = f"{secs} second{'s' if secs != 1 else ''}"

    return f"Timer set for {human}. I will remind you: '{message}'"


def parse_timer_command(command: str, speak_fn: Callable = None) -> Optional[str]:
    """Parse natural timer commands like 'remind me in 30 minutes to drink water'."""
    c = command.lower()
    total_seconds = 0
    matched = False

    m = re.search(r'(\d+)\s*hour[s]?\s*(?:and\s*)?(\d+)\s*minute[s]?', c)
    if m:
        total_seconds = int(m.group(1)) * 3600 + int(m.group(2)) * 60
        matched = True

    if not matched:
        m = re.search(r'(\d+)\s*hour[s]?', c)
        if m:
            total_seconds = int(m.group(1)) * 3600
            matched = True

    if not matched:
        m = re.search(r'(\d+)\s*minute[s]?', c)
        if m:
            total_seconds = int(m.group(1)) * 60
            matched = True
            m2 = re.search(r'(\d+)\s*minute[s]?\s*and\s*(\d+)\s*second[s]?', c)
            if m2:
                total_seconds += int(m2.group(2))

    if not matched:
        m = re.search(r'(\d+)\s*second[s]?', c)
        if m:
            total_seconds = int(m.group(1))
            matched = True

    if not matched:
        return None

    message = "Your timer is up!"
    for pat in [
        r'remind(?:er)?\s+(?:me\s+)?(?:to|about|that)\s+(.+)',
        r'to\s+(.+?)\s+(?:in|after)',
    ]:
        m = re.search(pat, c)
        if m:
            message = f"Reminder: {m.group(1).strip().capitalize()}!"
            break

    return set_timer(total_seconds, message, speak_fn)


# ─────────────────────────────────────────────────────────────────────────────
# 2. FOLDER MANAGEMENT
# ─────────────────────────────────────────────────────────────────────────────

def create_folder(name: str, location: str = "desktop") -> str:
    base = _resolve_path(location)
    path = os.path.join(base, name.strip())
    try:
        os.makedirs(path, exist_ok=True)
        return f"Folder '{name}' created at {base}."
    except Exception as e:
        return f"Could not create folder: {e}"


def delete_folder(name: str, location: str = "desktop") -> str:
    base = _resolve_path(location)
    path = os.path.join(base, name.strip())
    if not os.path.exists(path):
        return f"Folder '{name}' not found in {location}."
    try:
        shutil.rmtree(path)
        return f"Folder '{name}' deleted."
    except Exception as e:
        return f"Could not delete folder: {e}"


def rename_folder(old_name: str, new_name: str, location: str = "desktop") -> str:
    base = _resolve_path(location)
    old  = os.path.join(base, old_name.strip())
    new  = os.path.join(base, new_name.strip())
    if not os.path.exists(old):
        return f"Folder '{old_name}' not found."
    try:
        os.rename(old, new)
        return f"Folder renamed from '{old_name}' to '{new_name}'."
    except Exception as e:
        return f"Could not rename: {e}"


# ─────────────────────────────────────────────────────────────────────────────
# 3. MOVE / COPY FILES
# ─────────────────────────────────────────────────────────────────────────────

def move_file(filename: str, source: str, destination: str) -> str:
    src     = os.path.join(_resolve_path(source), filename.strip())
    dst_dir = _resolve_path(destination)
    if not os.path.exists(src):
        return f"File '{filename}' not found in {source}."
    try:
        os.makedirs(dst_dir, exist_ok=True)
        shutil.move(src, os.path.join(dst_dir, filename.strip()))
        return f"Moved '{filename}' to {destination}."
    except Exception as e:
        return f"Could not move file: {e}"


def copy_file(filename: str, source: str, destination: str) -> str:
    src     = os.path.join(_resolve_path(source), filename.strip())
    dst_dir = _resolve_path(destination)
    if not os.path.exists(src):
        return f"File '{filename}' not found in {source}."
    try:
        os.makedirs(dst_dir, exist_ok=True)
        shutil.copy2(src, os.path.join(dst_dir, filename.strip()))
        return f"Copied '{filename}' to {destination}."
    except Exception as e:
        return f"Could not copy file: {e}"


# ─────────────────────────────────────────────────────────────────────────────
# 4. FIND FILES
# ─────────────────────────────────────────────────────────────────────────────

def find_files(query: str, location: str = "home") -> str:
    base    = _resolve_path(location)
    q       = query.strip()
    pattern = f"**/*{q}*" if "*" not in q else f"**/{q}"
    if q.startswith("."):
        pattern = f"**/*{q}"
    try:
        matches = glob.glob(os.path.join(base, pattern), recursive=True)[:15]
        if not matches:
            return f"No files matching '{query}' found in {location}."
        result = f"Found {len(matches)} file(s) matching '{query}':\n"
        for f in matches:
            result += f"  - {f}\n"
        return result.strip()
    except Exception as e:
        return f"Search error: {e}"


# ─────────────────────────────────────────────────────────────────────────────
# 5. ZIP / UNZIP
# ─────────────────────────────────────────────────────────────────────────────

def zip_folder(folder_name: str, location: str = "desktop") -> str:
    base        = _resolve_path(location)
    folder_path = os.path.join(base, folder_name.strip())
    zip_path    = os.path.join(base, folder_name.strip() + ".zip")
    if not os.path.exists(folder_path):
        return f"Folder '{folder_name}' not found."
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    fp = os.path.join(root, file)
                    zf.write(fp, os.path.relpath(fp, base))
        return f"Folder '{folder_name}' zipped successfully at {location}."
    except Exception as e:
        return f"Could not zip: {e}"


def unzip_file(zip_name: str, location: str = "desktop", destination: str = None) -> str:
    base     = _resolve_path(location)
    zip_path = os.path.join(base, zip_name.strip())
    dst      = _resolve_path(destination) if destination else base
    if not os.path.exists(zip_path):
        return f"Zip file '{zip_name}' not found."
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(dst)
        return f"Unzipped '{zip_name}' to {dst}."
    except Exception as e:
        return f"Could not unzip: {e}"


# ─────────────────────────────────────────────────────────────────────────────
# 6. CLEANUP DOWNLOADS
# ─────────────────────────────────────────────────────────────────────────────

def cleanup_downloads(days_old: int = 30) -> str:
    downloads = COMMON_PATHS["downloads"]
    cutoff    = time.time() - (days_old * 86400)
    deleted   = []
    try:
        for item in os.listdir(downloads):
            path = os.path.join(downloads, item)
            try:
                if os.path.getmtime(path) < cutoff:
                    if os.path.isfile(path):
                        os.remove(path)
                    else:
                        shutil.rmtree(path)
                    deleted.append(item)
            except Exception:
                continue
        if deleted:
            return f"Deleted {len(deleted)} item(s) older than {days_old} days from Downloads."
        return f"No files older than {days_old} days found in Downloads."
    except Exception as e:
        return f"Cleanup error: {e}"


# ─────────────────────────────────────────────────────────────────────────────
# 7. OPEN / CLOSE APPS
# ─────────────────────────────────────────────────────────────────────────────

_USER = os.environ.get("USERNAME", "")

APP_MAP = {
    "calculator":         "calc.exe",
    "notepad":            "notepad.exe",
    "paint":              "mspaint.exe",
    "wordpad":            "wordpad.exe",
    "explorer":           "explorer.exe",
    "file explorer":      "explorer.exe",
    "task manager":       "taskmgr.exe",
    "control panel":      "control.exe",
    "cmd":                "cmd.exe",
    "command prompt":     "cmd.exe",
    "terminal":           "wt.exe",
    "powershell":         "powershell.exe",
    "snipping tool":      "SnippingTool.exe",
    "chrome":             rf"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "google chrome":      rf"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "edge":               rf"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "firefox":            rf"C:\Program Files\Mozilla Firefox\firefox.exe",
    "brave":              rf"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
    "word":               rf"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
    "excel":              rf"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
    "powerpoint":         rf"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
    "outlook":            rf"C:\Program Files\Microsoft Office\root\Office16\OUTLOOK.EXE",
    "vlc":                rf"C:\Program Files\VideoLAN\VLC\vlc.exe",
    "spotify":            rf"C:\Users\{_USER}\AppData\Roaming\Spotify\Spotify.exe",
    "discord":            rf"C:\Users\{_USER}\AppData\Local\Discord\Update.exe",
    "whatsapp":           rf"C:\Users\{_USER}\AppData\Local\WhatsApp\WhatsApp.exe",
    "telegram":           rf"C:\Users\{_USER}\AppData\Roaming\Telegram Desktop\Telegram.exe",
    "zoom":               rf"C:\Users\{_USER}\AppData\Roaming\Zoom\bin\Zoom.exe",
    "vs code":            rf"C:\Users\{_USER}\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "vscode":             rf"C:\Users\{_USER}\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "visual studio code": rf"C:\Users\{_USER}\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "teams":              rf"C:\Users\{_USER}\AppData\Local\Microsoft\Teams\current\Teams.exe",
}

PROCESS_MAP = {
    "chrome":        "chrome.exe",
    "google chrome": "chrome.exe",
    "edge":          "msedge.exe",
    "firefox":       "firefox.exe",
    "brave":         "brave.exe",
    "notepad":       "notepad.exe",
    "calculator":    "CalculatorApp.exe",
    "vlc":           "vlc.exe",
    "spotify":       "Spotify.exe",
    "discord":       "Discord.exe",
    "teams":         "Teams.exe",
    "zoom":          "Zoom.exe",
    "whatsapp":      "WhatsApp.exe",
    "telegram":      "Telegram.exe",
    "vs code":       "Code.exe",
    "vscode":        "Code.exe",
    "word":          "WINWORD.EXE",
    "excel":         "EXCEL.EXE",
    "powerpoint":    "POWERPNT.EXE",
    "outlook":       "OUTLOOK.EXE",
    "paint":         "mspaint.exe",
}


def open_app(app_name: str) -> str:
    key = app_name.lower().strip()
    exe = APP_MAP.get(key)
    if exe and os.path.exists(exe):
        try:
            subprocess.Popen([exe])
            return f"Opening {app_name}."
        except Exception as e:
            return f"Could not open {app_name}: {e}"
    # Fallback: shell command (works for built-ins like calc.exe, notepad.exe)
    try:
        subprocess.Popen(exe or key, shell=True)
        return f"Opening {app_name}."
    except Exception as e:
        return f"Could not open '{app_name}': {e}"


def close_app(app_name: str) -> str:
    key       = app_name.lower().strip()
    proc_name = PROCESS_MAP.get(key, app_name)
    killed    = 0
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'].lower() == proc_name.lower():
                proc.kill()
                killed += 1
        except Exception:
            continue
    if killed:
        return f"Closed {app_name}."
    return f"'{app_name}' is not currently running."


# ─────────────────────────────────────────────────────────────────────────────
# 8. SCREENSHOT
# ─────────────────────────────────────────────────────────────────────────────

def take_screenshot(save_location: str = "desktop") -> str:
    try:
        import pyautogui
        save_dir  = _resolve_path(save_location)
        os.makedirs(save_dir, exist_ok=True)
        fname     = f"Screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        save_path = os.path.join(save_dir, fname)
        pyautogui.screenshot().save(save_path)
        return f"Screenshot saved as '{fname}' in {save_location}."
    except ImportError:
        return "Screenshot failed. Run: pip install pyautogui pillow"
    except Exception as e:
        return f"Screenshot error: {e}"


# ─────────────────────────────────────────────────────────────────────────────
# 9. TIME AND DATE
# ─────────────────────────────────────────────────────────────────────────────

def get_time() -> str:
    now  = datetime.now()
    hour = now.strftime("%I").lstrip("0") or "12"
    return f"The current time is {hour}:{now.strftime('%M')} {now.strftime('%p')}."


def get_date() -> str:
    return f"Today is {datetime.now().strftime('%A, %d %B %Y')}."


def get_datetime() -> str:
    now  = datetime.now()
    hour = now.strftime("%I").lstrip("0") or "12"
    return f"It is {hour}:{now.strftime('%M')} {now.strftime('%p')} on {now.strftime('%A, %d %B %Y')}."


# ─────────────────────────────────────────────────────────────────────────────
# 10. INTERNET SPEED
# ─────────────────────────────────────────────────────────────────────────────

def check_internet_speed_background(speak_fn: Callable = None) -> str:
    def _run():
        try:
            import speedtest
            st     = speedtest.Speedtest()
            st.get_best_server()
            dl     = st.download() / 1_000_000
            ul     = st.upload()   / 1_000_000
            ping   = st.results.ping
            result = f"Internet speed: Download {dl:.1f} Mbps, Upload {ul:.1f} Mbps, Ping {ping:.0f} ms."
        except ImportError:
            result = "Speed test not available. Run: pip install speedtest-cli"
        except Exception as e:
            result = f"Speed test error: {e}"
        print(f"[SpeedTest] {result}")
        if speak_fn:
            try:
                speak_fn(result)
            except Exception:
                pass
    threading.Thread(target=_run, daemon=True, name="SpeedTest").start()
    return "Running speed test in the background. I will tell you the result in about 10 seconds."


# ─────────────────────────────────────────────────────────────────────────────
# 11. SYSTEM INFO
# ─────────────────────────────────────────────────────────────────────────────

def get_ram_usage() -> str:
    mem = psutil.virtual_memory()
    return (f"RAM: {mem.used/(1024**3):.1f} GB used out of "
            f"{mem.total/(1024**3):.1f} GB. {mem.percent:.0f}% in use.")


def get_cpu_usage() -> str:
    return f"CPU usage is {psutil.cpu_percent(interval=1):.0f}% across {psutil.cpu_count()} cores."


def get_top_processes(limit: int = 5) -> str:
    try:
        procs = []
        for p in psutil.process_iter(['name', 'cpu_percent', 'memory_percent']):
            try:
                procs.append(p.info)
            except Exception:
                continue
        procs.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
        result = f"Top {limit} processes by CPU:\n"
        for i, p in enumerate(procs[:limit], 1):
            result += (f"  {i}. {p.get('name','?')} "
                       f"CPU: {p.get('cpu_percent',0):.1f}%  "
                       f"RAM: {p.get('memory_percent',0):.1f}%\n")
        return result.strip()
    except Exception as e:
        return f"Could not get processes: {e}"


def get_system_summary() -> str:
    try:
        ram  = psutil.virtual_memory()
        cpu  = psutil.cpu_percent(interval=1)
        disk = psutil.disk_usage('/')
        return (f"System: CPU {cpu:.0f}%, "
                f"RAM {ram.percent:.0f}% ({ram.used/(1024**3):.1f} GB used), "
                f"Disk {disk.percent:.0f}% ({disk.free/(1024**3):.1f} GB free).")
    except Exception as e:
        return f"System info error: {e}"



# ─────────────────────────────────────────────────────────────────────────────
# SYSTEM VOLUME CONTROL (Windows)
# ─────────────────────────────────────────────────────────────────────────────

def _get_volume_obj():
    """
    Get pycaw IAudioEndpointVolume object.
    Handles both old pycaw (devices.Activate) and
    new pycaw (devices._dev.Activate) APIs.
    """
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from comtypes import CLSCTX_ALL
    import ctypes

    devices = AudioUtilities.GetSpeakers()

    # New pycaw wraps MMDevice in AudioDevice — unwrap it
    dev = getattr(devices, '_dev', devices)
    interface = dev.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    return ctypes.cast(interface, ctypes.POINTER(IAudioEndpointVolume))


def _ps_set_volume(percent: int) -> bool:
    """PowerShell fallback for setting volume (no pycaw needed)."""
    import subprocess
    # Uses Windows Audio COM via PowerShell
    ps = (
        "$volume = (New-Object -ComObject WScript.Shell); "
        "Add-Type -TypeDefinition '"
        "using System; using System.Runtime.InteropServices; "
        "public class Audio { "
        "[DllImport(\"winmm.dll\")] public static extern int waveOutSetVolume(IntPtr h, uint v); }"
        "'; "
        f"$v = [uint32](([uint16]::MaxValue) * {percent / 100.0}); "
        "[Audio]::waveOutSetVolume([IntPtr]::Zero, $v -bor ($v -shl 16));"
    )
    r = subprocess.run(['powershell', '-WindowStyle', 'Hidden', '-Command', ps],
                       capture_output=True)
    return r.returncode == 0


def set_system_volume(percent: int) -> str:
    """Set Windows system volume to exact percentage (0-100)."""
    percent = max(0, min(100, percent))
    # Try pycaw first, PowerShell fallback
    try:
        vol = _get_volume_obj()
        vol.SetMasterVolumeLevelScalar(percent / 100.0, None)
        return f"System volume set to {percent} percent."
    except ImportError:
        pass
    except Exception:
        pass
    # PowerShell fallback
    if _ps_set_volume(percent):
        return f"System volume set to {percent} percent."
    return f"Could not set volume. Run: pip install pycaw"


def get_system_volume() -> str:
    """Get current Windows system volume percentage."""
    try:
        vol   = _get_volume_obj()
        level = round(vol.GetMasterVolumeLevelScalar() * 100)
        muted = vol.GetMute()
        if muted:
            return f"System volume is muted. Last level was {level} percent."
        return f"System volume is at {level} percent."
    except Exception as e:
        return f"Could not read volume: {e}"


def mute_system_volume() -> str:
    """Mute Windows system volume."""
    try:
        _get_volume_obj().SetMute(1, None)
        return "System volume muted."
    except Exception as e:
        return f"Mute error: {e}"


def unmute_system_volume() -> str:
    """Unmute Windows system volume."""
    try:
        _get_volume_obj().SetMute(0, None)
        return "System volume unmuted."
    except Exception as e:
        return f"Unmute error: {e}"


def volume_up_system(step: int = 10) -> str:
    """Increase system volume by step percent."""
    try:
        vol     = _get_volume_obj()
        current = round(vol.GetMasterVolumeLevelScalar() * 100)
        new_lvl = min(100, current + step)
        vol.SetMasterVolumeLevelScalar(new_lvl / 100.0, None)
        return f"Volume increased to {new_lvl} percent."
    except Exception as e:
        return f"Volume up error: {e}"


def volume_down_system(step: int = 10) -> str:
    """Decrease system volume by step percent."""
    try:
        vol     = _get_volume_obj()
        current = round(vol.GetMasterVolumeLevelScalar() * 100)
        new_lvl = max(0, current - step)
        vol.SetMasterVolumeLevelScalar(new_lvl / 100.0, None)
        return f"Volume decreased to {new_lvl} percent."
    except Exception as e:
        return f"Volume down error: {e}"


# ─────────────────────────────────────────────────────────────────────────────
# MAIN DISPATCHER
# ─────────────────────────────────────────────────────────────────────────────

class TaskAutomation:
    """
    Plug into Brain.py's process_message() before battery/AI checks.
    Returns response string if handled, None to let AI process it.
    """

    def __init__(self, speak_fn: Callable = None):
        self.speak_fn = speak_fn
        print("Task Automation initialized")

    def handle(self, command: str) -> Optional[str]:
        c = command.lower().strip()

        # ── System Volume ─────────────────────────────────────────────────────
        # Catch ALL volume commands that are NOT YouTube-specific

        if "youtube" not in c and "spotify" not in c:

            # "volume 50%" / "set volume 50" / "volume to 50" / "system volume 50"
            m = re.search(r'(?:set\s+)?(?:system\s+)?volume\s+(?:to\s+)?(\d+)\s*%?$', c)
            if m:
                return set_system_volume(int(m.group(1)))

            # "set volume to 50" / "make volume 80"
            m = re.search(r'(?:set|make|put|change)\s+(?:system\s+)?volume\s+(?:to\s+)?(\d+)\s*%?', c)
            if m:
                return set_system_volume(int(m.group(1)))

            # "volume up" / "increase volume" / "louder" / "volume up 20"
            if any(w in c for w in ["volume up", "increase volume", "turn up",
                                     "raise volume", "louder", "volume higher"]):
                m = re.search(r'(\d+)\s*%?', c)
                step = int(m.group(1)) if m else 10
                return volume_up_system(step)

            # "volume down" / "decrease volume" / "quieter"
            if any(w in c for w in ["volume down", "decrease volume", "turn down",
                                     "lower volume", "quieter", "volume lower"]):
                m = re.search(r'(\d+)\s*%?', c)
                step = int(m.group(1)) if m else 10
                return volume_down_system(step)

            # "mute"
            if any(w in c for w in ["mute volume", "mute system", "mute my pc",
                                     "mute computer", "mute"]):
                if "unmute" not in c:
                    return mute_system_volume()

            # "unmute"
            if any(w in c for w in ["unmute", "turn on sound", "unmute volume"]):
                return unmute_system_volume()

            # "what is the volume" / "check volume"
            if any(w in c for w in ["what is the volume", "check volume",
                                     "current volume", "volume level",
                                     "what's the volume", "volume status"]):
                return get_system_volume()

        # Timer / Reminder
        if any(w in c for w in ["timer", "remind me", "set a reminder", "alert me"]):
            result = parse_timer_command(c, self.speak_fn)
            if result:
                return result

        # Time
        if any(w in c for w in ["what time", "current time", "what's the time",
                                  "whats the time", "tell me the time"]):
            return get_time()

        # Date
        if any(w in c for w in ["what date", "today's date", "what day is",
                                  "which day", "what is today"]):
            return get_date()

        if any(w in c for w in ["date and time", "time and date"]):
            return get_datetime()

        # Screenshot
        if any(w in c for w in ["screenshot", "screen shot", "capture screen",
                                  "take a screenshot"]):
            loc = "desktop"
            for l in ["downloads", "pictures", "documents"]:
                if l in c:
                    loc = l
                    break
            return take_screenshot(loc)

        # Internet Speed
        if any(w in c for w in ["internet speed", "check speed", "speed test",
                                  "network speed", "wifi speed", "how fast is my"]):
            return check_internet_speed_background(self.speak_fn)

        # RAM
        if any(w in c for w in ["ram usage", "memory usage", "how much ram",
                                  "check ram", "check memory"]):
            return get_ram_usage()

        # CPU
        if any(w in c for w in ["cpu usage", "processor usage",
                                  "how much cpu", "check cpu"]):
            return get_cpu_usage()

        # Processes
        if any(w in c for w in ["running processes", "top processes",
                                  "whats running", "show processes"]):
            return get_top_processes()

        # System Summary
        if any(w in c for w in ["system summary", "system info",
                                  "system performance", "pc status"]):
            return get_system_summary()

        # Create Folder
        m = re.search(
            r'create\s+(?:a\s+)?folder\s+(?:named?|called)?\s*["\']?([^"\']+?)["\']?'
            r'(?:\s+(?:on|in|at)\s+(.+))?$', c)
        if m:
            return create_folder(m.group(1).strip(),
                                 (m.group(2) or "desktop").strip().rstrip("."))

        # Delete Folder
        m = re.search(
            r'delete\s+(?:the\s+)?folder\s+["\']?([^"\']+?)["\']?'
            r'(?:\s+(?:on|in|from)\s+(.+))?$', c)
        if m:
            return delete_folder(m.group(1).strip(),
                                  (m.group(2) or "desktop").strip().rstrip("."))

        # Rename Folder
        m = re.search(
            r'rename\s+folder\s+["\']?(.+?)["\']?\s+to\s+["\']?(.+?)["\']?'
            r'(?:\s+(?:on|in)\s+(.+))?$', c)
        if m:
            return rename_folder(m.group(1).strip(), m.group(2).strip(),
                                  (m.group(3) or "desktop").strip().rstrip("."))

        # Move File
        m = re.search(
            r'move\s+(?:file\s+)?["\']?(.+?)["\']?\s+from\s+(.+?)\s+to\s+(.+)$', c)
        if m:
            return move_file(m.group(1).strip(),
                             m.group(2).strip(), m.group(3).strip().rstrip("."))

        # Copy File
        m = re.search(
            r'copy\s+(?:file\s+)?["\']?(.+?)["\']?\s+from\s+(.+?)\s+to\s+(.+)$', c)
        if m:
            return copy_file(m.group(1).strip(),
                             m.group(2).strip(), m.group(3).strip().rstrip("."))

        # Find Files
        m = re.search(
            r'find\s+(?:all\s+)?["\']?(.+?)["\']?\s+(?:files?\s+)?'
            r'(?:in|on|from)\s+(.+)$', c)
        if m:
            return find_files(m.group(1).strip(),
                              m.group(2).strip().rstrip("."))

        m = re.search(r'find\s+(?:all\s+)?["\']?(.+?)["\']?\s+files?$', c)
        if m:
            return find_files(m.group(1).strip())

        # Zip
        m = re.search(
            r'zip\s+(?:the\s+)?folder\s+["\']?(.+?)["\']?'
            r'(?:\s+(?:on|in)\s+(.+))?$', c)
        if m:
            return zip_folder(m.group(1).strip(),
                              (m.group(2) or "desktop").strip().rstrip("."))

        # Unzip
        m = re.search(r'unzip\s+["\']?(.+?\.zip)["\']?'
                      r'(?:\s+(?:to|into)\s+(.+))?$', c)
        if m:
            dst = m.group(2).strip().rstrip(".") if m.group(2) else None
            return unzip_file(m.group(1).strip(), destination=dst)

        # Cleanup Downloads
        if any(w in c for w in ["clean downloads", "cleanup downloads",
                                  "clear downloads", "clean up downloads"]):
            m = re.search(r'(\d+)\s*day', c)
            return cleanup_downloads(int(m.group(1)) if m else 30)

        # Open App — skip web URLs (handled elsewhere)
        m = re.search(r'^open\s+(.+)$', c)
        if m:
            app = m.group(1).strip()
            web_keywords = ["youtube", "google", "facebook", "twitter",
                            "instagram", "http", "www", "website"]
            if not any(ex in app for ex in web_keywords):
                return open_app(app)

        # Close App — skip window/tab commands (handled by Automation.py)
        m = re.search(r'^close\s+(.+)$', c)
        if m:
            app = m.group(1).strip()
            if not any(ex in app for ex in ["tab", "window", "this", "current"]):
                return close_app(app)

        return None  # Not handled — let AI/Automation.py deal with it