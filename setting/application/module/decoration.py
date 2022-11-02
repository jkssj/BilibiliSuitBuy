from application.errors import GuiFileAskWarning

import tkinter.messagebox
import threading


def application_thread(func):
    """ 多线程 """
    def wrapper(*args, **kwargs):
        thread_kwargs = {
            "target": func,
            "args": args,
            "kwargs": kwargs
        }
        t = threading.Thread(**thread_kwargs)
        t.start()
        return t
    return wrapper


def application_error(func):
    """ 报错弹窗 """
    def wrapper(*args, **kwargs):
        try:
            results = func(*args, **kwargs)
        except Exception as e:
            if e.__class__ == GuiFileAskWarning:
                return None
            err = ("错误", str(e))
            tkinter.messagebox.showerror(*err)
        else:
            return results
    return wrapper
