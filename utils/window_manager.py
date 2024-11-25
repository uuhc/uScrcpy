import os
import platform
import subprocess
import re
from loguru import logger


class WindowManager:
    @staticmethod
    def get_window_id(window_title):
        """获取窗口句柄，跨平台实现"""
        current_os = platform.system()

        if current_os == "Windows":
            return WindowManager._get_window_id_windows(window_title)
        elif current_os == "Linux":
            return WindowManager._get_window_id_linux(window_title)
        elif current_os == "Darwin":  # macOS
            return WindowManager._get_window_id_macos(window_title)
        else:
            raise NotImplementedError(f"Unsupported platform: {current_os}")

    @staticmethod
    def bring_window_to_front(window_id):
        """将窗口置于前台，跨平台实现"""
        current_os = platform.system()

        if current_os == "Windows":
            return WindowManager._bring_window_to_front_windows(window_id)
        elif current_os == "Linux":
            return WindowManager._bring_window_to_front_linux(window_id)
        elif current_os == "Darwin":  # macOS
            return WindowManager._bring_window_to_front_macos(window_id)
        else:
            raise NotImplementedError(f"Unsupported platform: {current_os}")

    # --- Windows 平台 ---
    @staticmethod
    def _get_window_id_windows(window_title):
        try:
            import pygetwindow as gw

            windows = gw.getWindowsWithTitle(window_title)
            return windows[0]._hWnd if windows else None
        except ImportError:
            raise ImportError(
                "Please install 'pygetwindow' to use this feature on Windows."
            )

    @staticmethod
    def _bring_window_to_front_windows(window_id):
        try:
            import win32gui

            win32gui.ShowWindow(window_id, 5)  # SW_SHOW
            win32gui.SetForegroundWindow(window_id)
        except ImportError:
            raise ImportError(
                "Please install 'pywin32' to use this feature on Windows."
            )
        except Exception as e:
            print(f"Error bringing window to front on Windows: {e}")

    # --- Linux 平台 ---
    @staticmethod
    def _get_window_id_linux(window_title):
        try:
            output = subprocess.check_output(
                ["xdotool", "search", "--name", window_title], text=True
            )
            return int(output.splitlines()[0]) if output else None
        except FileNotFoundError:
            raise FileNotFoundError(
                "xdotool is not installed. Please install it via your package manager."
            )
        except Exception as e:
            print(f"Error fetching window ID on Linux: {e}")
            return None

    @staticmethod
    def _bring_window_to_front_linux(window_id):
        try:
            subprocess.call(["xdotool", "windowactivate", str(window_id)])
        except FileNotFoundError:
            raise FileNotFoundError(
                "xdotool is not installed. Please install it via your package manager."
            )
        except Exception as e:
            print(f"Error bringing window to front on Linux: {e}")

    # --- macOS 平台 ---
    @staticmethod
    def _get_window_id_macos(window_title):
        try:
            from Quartz import (
                CGWindowListCopyWindowInfo,
                kCGWindowListOptionAll,
                kCGNullWindowID,
            )

            window_list = CGWindowListCopyWindowInfo(
                kCGWindowListOptionAll, kCGNullWindowID
            )
            for window in window_list:
                owner_name = window.get("kCGWindowOwnerName", "")
                name = window.get("kCGWindowName", "")
                window_id = window.get("kCGWindowNumber", None)
                logger.info(
                    f"owner_name: {owner_name}, name: {name}, window_id: {window_id}"
                )

                if window_title in name or window_title in owner_name:
                    return window_id
            return None
        except ImportError:
            raise ImportError("Please install 'pyobjc' to use this feature on macOS.")
        except Exception as e:
            print(f"Error fetching window ID on macOS: {e}")
            return None

    @staticmethod
    def _bring_window_to_front_macos(window_id):
        try:
            script = f"""
            tell application "System Events"
                set frontmost of the first window whose id is {window_id} to true
            end tell
            """
            subprocess.call(["osascript", "-e", script])
        except Exception as e:
            print(f"Error bringing window to front on macOS: {e}")

    @staticmethod
    def is_window_active(window_id):
        current_os = platform.system()

        if current_os == "Windows":
            return WindowManager._is_window_active_windows(window_id)
        elif current_os == "Linux":
            return WindowManager._is_window_active_linux(window_id)
        elif current_os == "Darwin":
            return WindowManager._is_window_active_macos(window_id)
        else:
            raise NotImplementedError(f"Unsupported platform: {current_os}")

    @staticmethod
    def _is_window_active_windows(window_id):
        import ctypes
        from pygetwindow import getActiveWindow

        active_window = getActiveWindow()
        return active_window and active_window._hWnd == window_id

    @staticmethod
    def _is_window_active_linux(window_id):
        import subprocess

        try:
            active_window = subprocess.check_output(
                ["xdotool", "getactivewindow"], text=True
            ).strip()
            return active_window == str(window_id)
        except Exception as e:
            print(f"Error checking active window on Linux: {e}")
            return False

    @staticmethod
    def _is_window_active_macos(window_id):
        from Quartz import (
            CGWindowListCopyWindowInfo,
            kCGWindowListOptionOnScreenOnly,
            kCGNullWindowID,
        )

        window_list = CGWindowListCopyWindowInfo(
            kCGWindowListOptionOnScreenOnly, kCGNullWindowID
        )
        for window in window_list:
            if window.get("kCGWindowNumber") == window_id:
                return True
        return False
