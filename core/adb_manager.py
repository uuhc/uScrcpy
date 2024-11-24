from adbutils import adb


class ADBManager:
    def __init__(self):
        self.devices = []

    def refresh_devices(self):
        """刷新已连接的设备列表"""
        self.devices = [device.serial for device in adb.device_list()]
        return self.devices
