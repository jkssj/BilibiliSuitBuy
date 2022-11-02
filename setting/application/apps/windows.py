from PIL import ImageTk
import tkinter
import qrcode

from application.utils import (
    reader_setting,
    rgb_to_tkinter
)

from application.net.login import LoginQrcode


class AppWindow(tkinter.Tk):
    def __init__(self):
        """ 主窗口 """
        super(AppWindow, self).__init__()
        config = reader_setting("./settings/windows.json")["main"]

        self.title(config.get("title", "github.com/lllk140/BilibiliSuitBuy"))
        self.configure(background=rgb_to_tkinter(config["background"]))
        self.resizable(config['resizable'], config['resizable'])
        self.geometry(f"{config['width']}x{config['height']}")


class QrWindow(tkinter.Toplevel):
    def __init__(self, model: str, os_ver: str, buvid: str):
        """ 二维码登录窗口 """
        super(QrWindow, self).__init__()
        config = reader_setting("./settings/windows.json")["qrcode"]

        self.login = LoginQrcode(model, os_ver, buvid)
        self.update_time = float(config["update_time"])

        self.resizable(config['resizable'], config['resizable'])
        self.geometry(f"{config['width']}x{config['height']}")
        login_url, self.auth_code = self.login.GetUrlAndAuthCode()
        self.title(config.get("title", str(login_url)))

        image = qrcode.make(login_url).get_image()
        shape = (config['height'], config['width'])
        self._photo = ImageTk.PhotoImage(image.resize(shape))
        tkinter.Label(self, image=self._photo).pack()
