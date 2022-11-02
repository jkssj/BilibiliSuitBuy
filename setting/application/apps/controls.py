from functools import partial

from application.errors import GuiEntryError

from application.apps.windows import AppWindow

from application.utils import reader_setting

from application.module.module import func_list

from application.module.controls import (
    TkinterLabel,
    TkinterEntry,
    TkinterButton
)


class AppControl(AppWindow):
    def __init__(self):
        super(AppControl, self).__init__()

        label_settings = reader_setting("./settings/controls/label.json")
        entry_settings = reader_setting("./settings/controls/entry.json")
        button_settings = reader_setting("./settings/controls/button.json")

        # 生成标签
        for label_config in label_settings:
            TkinterLabel(self, label_config)

        # 生成输入框
        for key, entry_config in entry_settings.items():
            self[key] = TkinterEntry(self, entry_config)

        # 生成按钮
        for func, name in func_list:
            TkinterButton(self, button_settings[name], partial(func, self))

    def __setitem__(self, key, value):
        """ 设置 """
        return setattr(self, f"{key}_entry", value)

    def __getitem__(self, item):
        """ 取得 """
        value = self.__dict__.get(f"{item}_entry")
        if not value:
            raise GuiEntryError(f"不存在{item}输入框")
        return value
