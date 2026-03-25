"""
YouTube Automation Module for SEEU AI
Provides comprehensive YouTube control via browser automation
"""

import webbrowser
import time
import pyautogui
import pywhatkit
import urllib.parse
from typing import Optional


class YouTubeController:
    """
    Advanced YouTube automation controller
    Supports: Play, Pause, Volume, Navigate, Search, Close

    IMPORTANT: YouTube volume cannot be read/retrieved via browser automation.
    You can only increase/decrease volume, never check the current level.
    This is a YouTube/browser limitation, not a code limitation.
    """

    def __init__(self):
        """Initialize YouTube Controller"""
        self.youtube_base_url = "https://www.youtube.com"
        print("✅ YouTube Controller initialized")

    @staticmethod
    def _wait_for_page_load(seconds=3):
        """Wait for page to load"""
        time.sleep(seconds)

    @staticmethod
    def _focus_browser():
        """Ensure browser window is focused without clicking video"""
        time.sleep(0.5)
        # Just press a neutral key to focus, don't click (clicking pauses video!)
        # Using Shift key which doesn't affect playback
        pyautogui.press('shift')
        time.sleep(0.3)

    def play_video(self, query: str, wait_time: int = 5) -> bool:
        """
        Play a video on YouTube by search query

        Args:
            query: Search term for video
            wait_time: Time to wait for page load

        Returns:
            bool: Success status
        """
        try:
            print(f"🎬 Playing '{query}' on YouTube...")
            pywhatkit.playonyt(query)
            self._wait_for_page_load(wait_time)
            print(f"✅ Playing: {query}")
            return True
        except Exception as e:
            print(f"❌ Error playing video: {e}")
            return False

    def search_youtube(self, query: str) -> bool:
        """
        Open YouTube search results for a query

        Args:
            query: Search term

        Returns:
            bool: Success status
        """
        try:
            encoded_query = urllib.parse.quote(query)
            search_url = f"{self.youtube_base_url}/results?search_query={encoded_query}"
            webbrowser.open(search_url)
            self._wait_for_page_load(3)
            print(f"✅ Searched YouTube for: {query}")
            return True
        except Exception as e:
            print(f"❌ Error searching YouTube: {e}")
            return False

    def open_channel(self, channel_name: str) -> bool:
        """
        Open a YouTube channel

        Args:
            channel_name: Name of the channel

        Returns:
            bool: Success status
        """
        try:
            encoded_name = urllib.parse.quote(channel_name)
            search_url = f"{self.youtube_base_url}/results?search_query={encoded_name}"
            webbrowser.open(search_url)
            self._wait_for_page_load(3)
            print(f"✅ Opened channel search: {channel_name}")
            return True
        except Exception as e:
            print(f"❌ Error opening channel: {e}")
            return False

    def pause_play_toggle(self) -> bool:
        """
        Toggle pause/play on YouTube (using K key or Space)

        Returns:
            bool: Success status
        """
        try:
            self._focus_browser()
            pyautogui.press('k')  # K key pauses/plays YouTube
            print("✅ Toggled pause/play")
            return True
        except Exception as e:
            print(f"❌ Error toggling pause/play: {e}")
            return False

    def play(self) -> bool:
        """Resume playback"""
        return self.pause_play_toggle()

    def pause(self) -> bool:
        """Pause playback"""
        return self.pause_play_toggle()

    def mute_unmute_toggle(self) -> bool:
        """
        Toggle mute/unmute (using M key)

        Returns:
            bool: Success status
        """
        try:
            time.sleep(0.3)
            # Focus without clicking
            pyautogui.press('shift')
            time.sleep(0.2)

            pyautogui.press('m')
            print("✅ Toggled mute/unmute")
            return True
        except Exception as e:
            print(f"❌ Error toggling mute: {e}")
            return False

    def volume_up(self, steps: int = 1) -> bool:
        """
        Increase volume

        Args:
            steps: Number of volume steps (each step = ~5%)

        Returns:
            bool: Success status
        """
        try:
            # Small delay to ensure browser is ready
            time.sleep(0.3)
            # Focus without clicking
            pyautogui.press('shift')
            time.sleep(0.2)

            # Send volume up keys
            for _ in range(steps):
                pyautogui.press('up')
                time.sleep(0.15)

            print(f"✅ Volume increased by {steps} steps")
            return True
        except Exception as e:
            print(f"❌ Error increasing volume: {e}")
            return False

    def volume_down(self, steps: int = 1) -> bool:
        """
        Decrease volume

        Args:
            steps: Number of volume steps (each step = ~5%)

        Returns:
            bool: Success status
        """
        try:
            # Small delay to ensure browser is ready
            time.sleep(0.3)
            # Focus without clicking
            pyautogui.press('shift')
            time.sleep(0.2)

            # Send volume down keys
            for _ in range(steps):
                pyautogui.press('down')
                time.sleep(0.15)

            print(f"✅ Volume decreased by {steps} steps")
            return True
        except Exception as e:
            print(f"❌ Error decreasing volume: {e}")
            return False

    def fullscreen_toggle(self) -> bool:
        """
        Toggle fullscreen mode (F key)

        Returns:
            bool: Success status
        """
        try:
            self._focus_browser()
            pyautogui.press('f')
            print("✅ Toggled fullscreen")
            return True
        except Exception as e:
            print(f"❌ Error toggling fullscreen: {e}")
            return False

    def next_video(self) -> bool:
        """
        Skip to next video (Shift+N)

        Returns:
            bool: Success status
        """
        try:
            self._focus_browser()
            pyautogui.hotkey('shift', 'n')
            print("✅ Skipped to next video")
            return True
        except Exception as e:
            print(f"❌ Error skipping to next: {e}")
            return False

    def previous_video(self) -> bool:
        """
        Go to previous video (Shift+P)

        Returns:
            bool: Success status
        """
        try:
            self._focus_browser()
            pyautogui.hotkey('shift', 'p')
            print("✅ Returned to previous video")
            return True
        except Exception as e:
            print(f"❌ Error going to previous: {e}")
            return False

    def seek_forward(self, seconds: int = 10) -> bool:
        """
        Seek forward in video

        Args:
            seconds: Seconds to skip (default 10, use L key or right arrow)

        Returns:
            bool: Success status
        """
        try:
            self._focus_browser()
            if seconds == 10:
                pyautogui.press('l')  # Skip 10 seconds
            else:
                # Use right arrow for 5 second skips
                presses = seconds // 5
                for _ in range(presses):
                    pyautogui.press('right')
                    time.sleep(0.1)
            print(f"✅ Seeked forward {seconds} seconds")
            return True
        except Exception as e:
            print(f"❌ Error seeking forward: {e}")
            return False

    def seek_backward(self, seconds: int = 10) -> bool:
        """
        Seek backward in video

        Args:
            seconds: Seconds to rewind (default 10, use J key or left arrow)

        Returns:
            bool: Success status
        """
        try:
            self._focus_browser()
            if seconds == 10:
                pyautogui.press('j')  # Rewind 10 seconds
            else:
                # Use left arrow for 5 second rewinds
                presses = seconds // 5
                for _ in range(presses):
                    pyautogui.press('left')
                    time.sleep(0.1)
            print(f"✅ Seeked backward {seconds} seconds")
            return True
        except Exception as e:
            print(f"❌ Error seeking backward: {e}")
            return False

    def close_youtube_tab(self) -> bool:
        """
        Close current browser tab (Ctrl+W)

        Returns:
            bool: Success status
        """
        try:
            self._focus_browser()
            pyautogui.hotkey('ctrl', 'w')
            print("✅ Closed YouTube tab")
            return True
        except Exception as e:
            print(f"❌ Error closing tab: {e}")
            return False

    def theater_mode_toggle(self) -> bool:
        """
        Toggle theater mode (T key)

        Returns:
            bool: Success status
        """
        try:
            self._focus_browser()
            pyautogui.press('t')
            print("✅ Toggled theater mode")
            return True
        except Exception as e:
            print(f"❌ Error toggling theater mode: {e}")
            return False

    def toggle_captions(self) -> bool:
        """
        Toggle closed captions/subtitles (C key)

        Returns:
            bool: Success status
        """
        try:
            self._focus_browser()
            pyautogui.press('c')
            print("✅ Toggled captions")
            return True
        except Exception as e:
            print(f"❌ Error toggling captions: {e}")
            return False

    def increase_speed(self) -> bool:
        """
        Increase playback speed (Shift+>)

        Returns:
            bool: Success status
        """
        try:
            self._focus_browser()
            pyautogui.hotkey('shift', '.')
            print("✅ Increased playback speed")
            return True
        except Exception as e:
            print(f"❌ Error increasing speed: {e}")
            return False

    def decrease_speed(self) -> bool:
        """
        Decrease playback speed (Shift+<)

        Returns:
            bool: Success status
        """
        try:
            self._focus_browser()
            pyautogui.hotkey('shift', ',')
            print("✅ Decreased playback speed")
            return True
        except Exception as e:
            print(f"❌ Error decreasing speed: {e}")
            return False


# Convenience functions for easy access
def play_on_youtube(query: str) -> bool:
    """Quick function to play a video"""
    controller = YouTubeController()
    return controller.play_video(query)


def pause_youtube() -> bool:
    """Quick function to pause"""
    controller = YouTubeController()
    return controller.pause_play_toggle()


def close_youtube() -> bool:
    """Quick function to close YouTube tab"""
    controller = YouTubeController()
    return controller.close_youtube_tab()


def volume_up_youtube(steps: int = 1) -> bool:
    """Quick function to increase volume"""
    controller = YouTubeController()
    return controller.volume_up(steps)


def volume_down_youtube(steps: int = 1) -> bool:
    """Quick function to decrease volume"""
    controller = YouTubeController()
    return controller.volume_down(steps)


def next_video_youtube() -> bool:
    """Quick function to skip to next video"""
    controller = YouTubeController()
    return controller.next_video()


# Test function
if __name__ == "__main__":
    print("\n🎵 SEEU YouTube Automation Test")
    print("=" * 60)

    yt = YouTubeController()

    print("\nAvailable YouTube Controls:")
    print("  ▶️  Play video: yt.play_video('song name')")
    print("  ⏸️  Pause/Play: yt.pause_play_toggle()")
    print("  🔇 Mute/Unmute: yt.mute_unmute_toggle()")
    print("  🔊 Volume Up: yt.volume_up()")
    print("  🔉 Volume Down: yt.volume_down()")
    print("  ⏭️  Next Video: yt.next_video()")
    print("  ⏮️  Previous Video: yt.previous_video()")
    print("  ⏩ Seek Forward: yt.seek_forward(10)")
    print("  ⏪ Seek Backward: yt.seek_backward(10)")
    print("  🔍 Search: yt.search_youtube('query')")
    print("  ❌ Close Tab: yt.close_youtube_tab()")
    print("  🎭 Theater Mode: yt.theater_mode_toggle()")
    print("  📺 Fullscreen: yt.fullscreen_toggle()")
    print("  ⚡ Speed Up: yt.increase_speed()")
    print("  🐌 Speed Down: yt.decrease_speed()")
    print("  💬 Captions: yt.toggle_captions()")
    print("=" * 60)

    # Interactive test
    while True:
        command = input("\n🎤 Enter test command (or 'exit'): ").strip().lower()

        if command in ['exit', 'quit']:
            break
        elif command.startswith('play '):
            query = command[5:]
            yt.play_video(query)
        elif command == 'pause':
            yt.pause_play_toggle()
        elif command == 'next':
            yt.next_video()
        elif command == 'previous':
            yt.previous_video()
        elif command == 'volume up':
            yt.volume_up()
        elif command == 'volume down':
            yt.volume_down()
        elif command == 'mute':
            yt.mute_unmute_toggle()
        elif command == 'close':
            yt.close_youtube_tab()
        elif command == 'fullscreen':
            yt.fullscreen_toggle()
        else:
            print("❓ Unknown command. Try: play [song], pause, next, volume up, etc.")

    print("\n👋 YouTube Automation Test Complete!")