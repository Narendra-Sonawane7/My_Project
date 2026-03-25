"""
Notification Monitor Module for SEEU AI

SETUP REQUIRED:
    1. pip install winsdk
    2. Settings > Privacy & Security > Notifications
       Turn ON "Allow apps to access your notifications"

Uses WinRT get_notifications_async() polling (event listener is broken in winsdk).
Falls back to SQLite polling if winsdk is not installed.
"""

import os
import threading
import time
import shutil
import sqlite3
import tempfile
import xml.etree.ElementTree as ET
from typing import Optional, Callable, Set

# ─────────────────────────────────────────────────────────────────────────────
# winsdk import
# ─────────────────────────────────────────────────────────────────────────────
WINSDK_AVAILABLE = False
try:
    import asyncio
    import winsdk.windows.ui.notifications.management as _wnm
    import winsdk.windows.ui.notifications as _wn
    WINSDK_AVAILABLE = True
    print("[NotifMonitor] winsdk found - WinRT polling mode active")
except ImportError:
    print("[NotifMonitor] winsdk NOT found - using SQLite fallback")
    print("[NotifMonitor] Chrome/WhatsApp Web won't work. Fix: pip install winsdk")


# ─────────────────────────────────────────────────────────────────────────────
# Apps to silently skip
# ─────────────────────────────────────────────────────────────────────────────
_SKIP_APPS = [
    "windows.immersivecontrolpanel",
    "microsoft.windows.actioncenter",
    "windows.ui.notifications",
    "shellexperiencehost",
    "microsoft.windowsstore",
    "widgets",
    "xbox",
    "netflix",
    "hpsupport",
    "microsoftedgedevtools",
]

def _should_skip(app: str) -> bool:
    a = (app or "").lower()
    return any(s in a for s in _SKIP_APPS)


def _parse_xml_text(xml_str: str):
    """Parse toast XML string and return (title, body)."""
    title, body = "", ""
    try:
        if isinstance(xml_str, (bytes, bytearray)):
            xml_str = xml_str.decode("utf-8", errors="replace")
        root  = ET.fromstring(xml_str)
        texts = root.findall(".//text")
        if texts:
            title = (texts[0].text or "").strip()
        if len(texts) > 1:
            body = " ".join(
                (t.text or "").strip() for t in texts[1:] if t.text
            )
    except Exception as e:
        print(f"[XML] Parse error: {e}")
    return title, body


# ─────────────────────────────────────────────────────────────────────────────
# Message builder  (fixed: Chrome must not match Gmail)
# ─────────────────────────────────────────────────────────────────────────────

def _build_message(app_name: str, title: str, body: str) -> str:
    a = (app_name or "").lower()
    t = (title    or "").strip()
    b = (body     or "").strip()

    # ── WhatsApp (Desktop app) ────────────────────────────────────────────────
    if "whatsapp" in a:
        if t and b:
            return f"You have a WhatsApp message from {t}. {b}"
        elif t:
            return f"You have a WhatsApp message from {t}."
        return "You have a new WhatsApp message."

    # ── Chrome / Edge / Firefox (browser) ────────────────────────────────────
    # IMPORTANT: check browser BEFORE gmail/google so "Google Chrome" doesn't
    # accidentally match the gmail rule.
    if any(x in a for x in ["chrome", "msedge", "firefox"]):
        # WhatsApp Web comes through browser
        if "whatsapp" in t.lower() or "whatsapp" in b.lower():
            sender = t.replace("WhatsApp", "").strip(" -|:")
            if sender and b:
                return f"You have a WhatsApp message from {sender}. {b}"
            elif sender:
                return f"You have a WhatsApp message from {sender}."
            return f"You have a new WhatsApp message. {b}".strip()
        # Generic browser notification
        if t and b:
            return f"Browser notification: {t}. {b}"
        elif t:
            return f"Browser notification: {t}."
        return "You have a new browser notification."

    # ── Gmail (Gmail desktop app, not Chrome) ─────────────────────────────────
    if "gmail" in a:
        return f"You have a new Gmail. {t}." if t else "You have a new Gmail."

    # ── Google (other Google apps, not Chrome) ────────────────────────────────
    if "google" in a:
        if t:
            return f"Google notification: {t}."
        return "You have a new Google notification."

    # ── Outlook / Windows Mail ────────────────────────────────────────────────
    if any(x in a for x in ["outlook", "mail", "windowscommunications"]):
        return f"New email: {t}." if t else "You have a new email."

    # ── Telegram ──────────────────────────────────────────────────────────────
    if "telegram" in a:
        if t and b:
            return f"Telegram message from {t}. {b}"
        return f"Telegram message from {t}." if t else "New Telegram message."

    # ── Slack ─────────────────────────────────────────────────────────────────
    if "slack" in a:
        return f"Slack notification. {t}." if t else "New Slack message."

    # ── Teams ─────────────────────────────────────────────────────────────────
    if "teams" in a:
        return f"Microsoft Teams message from {t}." if t else "New Teams notification."

    # ── Instagram / Facebook ──────────────────────────────────────────────────
    if any(x in a for x in ["instagram", "facebook"]):
        return f"{t}: {b}".strip(": ") if (t or b) else "New social media notification."

    # ── Windows Defender ──────────────────────────────────────────────────────
    if any(x in a for x in ["defender", "securitycenter"]):
        return f"Windows Security alert. {t}." if t else "Windows Security alert."

    # ── Generic fallback ──────────────────────────────────────────────────────
    if t and b:
        return f"You have a notification. {t}. {b}"
    elif t:
        return f"You have a notification: {t}."
    return "You have a new notification."


# ─────────────────────────────────────────────────────────────────────────────
# WinRT backend  — polls get_notifications_async() every N seconds
# (add_notification_changed is broken in winsdk, polling works fine)
# ─────────────────────────────────────────────────────────────────────────────

class _WinRTBackend:

    def __init__(self, on_notification: Callable, poll_interval: float = 3.0):
        self._on_notification = on_notification
        # WinRT polls much faster than SQLite because Chrome notifications
        # can appear and disappear in under 1 second.
        self._poll_interval   = 0.5
        self._seen_ids: Set[int] = set()
        self._stop = threading.Event()
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def start(self) -> bool:
        t = threading.Thread(target=self._run, daemon=True,
                             name="WinRT-NotifMonitor")
        t.start()
        return True

    def stop(self):
        self._stop.set()
        if self._loop:
            self._loop.call_soon_threadsafe(self._loop.stop)

    def _run(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_until_complete(self._main())
        except Exception as e:
            print(f"[WinRT] Fatal: {e}")
        finally:
            self._loop.close()

    async def _main(self):
        try:
            listener = _wnm.UserNotificationListener.current
            status   = await listener.request_access_async()
            allowed  = _wnm.UserNotificationListenerAccessStatus.ALLOWED

            print(f"[WinRT] Access status: {status}")

            if status != allowed:
                print("[WinRT] ACCESS DENIED.")
                print("[WinRT] Fix: Settings > Privacy & Security > Notifications")
                print("[WinRT]      Enable 'Allow apps to access your notifications'")
                return

            # Seed existing IDs so old notifications are not announced
            notifs = await listener.get_notifications_async(
                _wn.NotificationKinds.TOAST
            )
            for n in notifs:
                self._seen_ids.add(n.id)
            print(f"[WinRT] Ready. Seeded {len(self._seen_ids)} existing IDs.")
            print(f"[WinRT] Polling every {self._poll_interval}s for new notifications...")
            print(f"[WinRT] Fast polling active - will catch Chrome/WhatsApp Web notifications.")

            # Poll loop  (event listener is broken in winsdk — polling works)
            while not self._stop.is_set():
                await asyncio.sleep(self._poll_interval)
                try:
                    await self._poll(listener)
                except Exception as e:
                    print(f"[WinRT] Poll error: {e}")

        except Exception as e:
            print(f"[WinRT] Error: {e}")
            import traceback
            traceback.print_exc()

    async def _poll(self, listener):
        """Fetch all current notifications and announce any new ones."""
        notifs = await listener.get_notifications_async(
            _wn.NotificationKinds.TOAST
        )
        for n in notifs:
            if n.id not in self._seen_ids:
                self._seen_ids.add(n.id)
                self._extract_and_fire(n)

    def _extract_and_fire(self, user_notif):
        try:
            # App name
            app_name = ""
            try:
                app_name = user_notif.app_info.display_info.display_name
            except Exception:
                try:
                    app_name = str(user_notif.app_info.app_user_model_id)
                except Exception:
                    pass

            title, body = "", ""

            # ── Method 1: iterate bindings directly ───────────────────────
            try:
                visual   = user_notif.notification.visual
                bindings = visual.bindings
                for binding in bindings:
                    try:
                        elems = list(binding.get_text_elements())
                        if elems:
                            title = (elems[0].text or "").strip()
                        if len(elems) > 1:
                            body = " ".join(
                                (e.text or "").strip()
                                for e in elems[1:] if e.text
                            )
                        if title or body:
                            break
                    except Exception:
                        continue
            except Exception as e1:
                print(f"[WinRT] Method1 error: {e1}")

            # ── Method 2: try get_binding with known template names ────────
            if not title and not body:
                try:
                    visual = user_notif.notification.visual
                    # Try common template strings directly
                    for template in ["ToastGeneric", "ToastText01",
                                     "ToastText02", "ToastText04"]:
                        try:
                            binding = visual.get_binding(template)
                            if binding:
                                elems = list(binding.get_text_elements())
                                if elems:
                                    title = (elems[0].text or "").strip()
                                if len(elems) > 1:
                                    body = " ".join(
                                        (e.text or "").strip()
                                        for e in elems[1:] if e.text
                                    )
                                if title or body:
                                    break
                        except Exception:
                            continue
                except Exception as e2:
                    print(f"[WinRT] Method2 error: {e2}")

            # ── Method 3: read raw XML payload and parse it ────────────────
            if not title and not body:
                try:
                    xml_str = user_notif.notification.content.get_xml()
                    title, body = _parse_xml_text(xml_str)
                except Exception as e3:
                    print(f"[WinRT] Method3 error: {e3}")

            print(f"[WinRT] App='{app_name}'  Title='{title}'  Body='{body}'")

            if _should_skip(app_name):
                print(f"[WinRT] Skipping: {app_name}")
                return

            if title or body:
                self._on_notification(app_name, title, body)
            else:
                print(f"[WinRT] No text extracted for '{app_name}' - skipping")

        except Exception as e:
            print(f"[WinRT] Extract error: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# SQLite fallback (only Desktop app toasts, NOT Chrome/browser)
# ─────────────────────────────────────────────────────────────────────────────

class _SQLiteFallbackBackend:

    def __init__(self, on_notification: Callable, interval: float = 3.0):
        self._on_notification = on_notification
        self._interval = interval
        self._seen: Set = set()
        self._stop  = threading.Event()
        self._query = None
        self._db    = None

    def start(self) -> bool:
        loc = os.environ.get("LOCALAPPDATA", "")
        p   = os.path.join(loc, "Microsoft", "Windows",
                           "Notifications", "wpndatabase.db")
        if not os.path.exists(p):
            print("[SQLite] wpndatabase.db not found")
            return False
        self._db = p
        t = threading.Thread(target=self._loop, daemon=True,
                             name="SQLite-NotifMonitor")
        t.start()
        return True

    def stop(self):
        self._stop.set()

    def _copy(self):
        try:
            tmp = tempfile.NamedTemporaryFile(suffix="_seeu.db", delete=False)
            tmp.close()
            shutil.copy2(self._db, tmp.name)
            return tmp.name
        except Exception as e:
            print(f"[SQLite] Copy error: {e}")
            return None

    def _make_query(self, conn):
        if self._query:
            return self._query
        nc = [r[1] for r in conn.execute(
            "PRAGMA table_info(Notification)").fetchall()]
        hc = [r[1] for r in conn.execute(
            "PRAGMA table_info(NotificationHandler)").fetchall()]
        n_id  = "Id"        if "Id"        in nc else nc[0]
        n_pay = "Payload"   if "Payload"   in nc else "NULL"
        n_fk  = "HandlerId" if "HandlerId" in nc else None
        h_pk  = "RecordId"  if "RecordId"  in hc else (
                "Id"         if "Id"         in hc else hc[0])
        h_app = "PrimaryId" if "PrimaryId" in hc else (
                "AppId"      if "AppId"      in hc else hc[1])
        if n_fk:
            self._query = (
                f"SELECT n.{n_id}, h.{h_app}, n.{n_pay} "
                f"FROM Notification n "
                f"JOIN NotificationHandler h ON n.{n_fk}=h.{h_pk} "
                f"WHERE n.{n_pay} LIKE '%<toast%' "
                f"ORDER BY n.{n_id} DESC LIMIT 60"
            )
        else:
            self._query = (
                f"SELECT {n_id},'unknown',{n_pay} FROM Notification "
                f"WHERE {n_pay} LIKE '%<toast%' "
                f"ORDER BY {n_id} DESC LIMIT 60"
            )
        print(f"[SQLite] Query built: {self._query}")
        return self._query

    def _parse(self, payload):
        title, body = "", ""
        if not payload:
            return title, body
        if isinstance(payload, (bytes, bytearray)):
            payload = payload.decode("utf-8", errors="replace")
        try:
            root  = ET.fromstring(payload)
            texts = root.findall(".//text")
            if texts:
                title = (texts[0].text or "").strip()
            if len(texts) > 1:
                body  = " ".join(
                    (x.text or "").strip() for x in texts[1:] if x.text
                )
        except Exception:
            pass
        return title, body

    def _read(self):
        tmp = self._copy()
        if not tmp:
            return
        new = []
        try:
            conn  = sqlite3.connect(tmp, timeout=5)
            q     = self._make_query(conn)
            rows  = conn.execute(q).fetchall()
            conn.close()
            for row in rows:
                nid, app_id, payload = row
                if nid in self._seen:
                    continue
                self._seen.add(nid)
                app_id = str(app_id or "unknown")
                if _should_skip(app_id):
                    continue
                title, body = self._parse(payload)
                if title or body:
                    new.append((app_id, title, body))
        except Exception as e:
            print(f"[SQLite] Read error: {e}")
        finally:
            try:
                os.remove(tmp)
            except Exception:
                pass
        for item in new:
            self._on_notification(*item)

    def _loop(self):
        print("[SQLite] Seeding existing IDs...")
        self._read()
        print(f"[SQLite] Seeded {len(self._seen)} IDs. Polling every {self._interval}s...")
        print("[SQLite] NOTE: Chrome/WhatsApp Web NOT covered — install winsdk.")
        while not self._stop.is_set():
            try:
                self._read()
            except Exception as e:
                print(f"[SQLite] Loop error: {e}")
            self._stop.wait(self._interval)


# ─────────────────────────────────────────────────────────────────────────────
# Public class
# ─────────────────────────────────────────────────────────────────────────────

class NotificationMonitor:
    """
    Unified notification monitor for SEEU.

    Usage:
        monitor = NotificationMonitor(speak_callback=tts_manager.speak)
        monitor.set_speaking_check(tts_manager.is_currently_speaking)
        monitor.start()
    """

    def __init__(
        self,
        speak_callback: Callable[[str], None],
        poll_interval: float = 3.0,
    ):
        self._speak         = speak_callback
        self._poll_interval = poll_interval
        self._is_running    = False
        self._is_speaking_fn: Optional[Callable[[], bool]] = None
        self._backend       = None

    def set_speaking_check(self, fn: Callable[[], bool]):
        self._is_speaking_fn = fn

    def is_running(self) -> bool:
        return self._is_running

    def start(self):
        if self._is_running:
            return
        if WINSDK_AVAILABLE:
            self._backend = _WinRTBackend(
                on_notification=self._announce,
                poll_interval=self._poll_interval,
            )
        else:
            self._backend = _SQLiteFallbackBackend(
                on_notification=self._announce,
                interval=self._poll_interval,
            )
        ok = self._backend.start()
        if ok is not False:
            self._is_running = True
            method = "WinRT-polling" if WINSDK_AVAILABLE else "SQLite-fallback"
            print(f"[NotifMonitor] Started ({method})")

    def stop(self):
        if self._backend:
            self._backend.stop()
        self._is_running = False
        print("[NotifMonitor] Stopped")

    def _announce(self, app_name: str, title: str, body: str):
        msg = _build_message(app_name, title, body)
        print(f"[NotifMonitor] Speaking: '{msg}'")
        # Wait if SEEU is already speaking (max 12s)
        waited = 0
        while (self._is_speaking_fn and
               self._is_speaking_fn() and
               waited < 12):
            time.sleep(0.4)
            waited += 0.4
        try:
            self._speak(msg)
        except Exception as e:
            print(f"[NotifMonitor] Speak error: {e}")

    def get_stats(self) -> dict:
        return {
            "running": self._is_running,
            "method":  "WinRT-polling" if WINSDK_AVAILABLE else "SQLite-fallback",
            "winsdk":  WINSDK_AVAILABLE,
        }


def create_notification_monitor(
    speak_callback: Callable[[str], None],
    poll_interval: float = 3.0,
) -> NotificationMonitor:
    return NotificationMonitor(
        speak_callback=speak_callback,
        poll_interval=poll_interval,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Standalone test
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\nSEEU NotificationMonitor - Standalone Test")
    print("=" * 60)
    print(f"winsdk: {WINSDK_AVAILABLE}")
    print("Waiting for notifications... Press Ctrl+C to stop.\n")

    def test_speak(msg):
        print(f"\n>>> SEEU WOULD SAY: {msg}\n")

    m = NotificationMonitor(speak_callback=test_speak, poll_interval=3.0)
    m.start()
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        m.stop()