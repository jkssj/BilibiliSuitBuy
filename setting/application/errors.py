class GuiNetError(Exception):
    def __init__(self, *args):
        """ gui网络请求错误 """
        super(GuiNetError, self).__init__(*args)


class GuiEntryIndexWarning(Exception):
    def __init__(self, *args):
        """ gui输入框获取值异常 """
        super(GuiEntryIndexWarning, self).__init__(*args)


class SdkIntIndexError(Exception):
    def __init__(self, *args):
        """ sdk_int索引异常 """
        super(SdkIntIndexError, self).__init__(*args)


class GuiEntryError(Exception):
    def __init__(self, *args):
        """ gui输入框异常 """
        super(GuiEntryError, self).__init__(*args)


class GuiFileAskWarning(Exception):
    def __init__(self, *args):
        """ 文件会话窗口异常 """
        super(GuiFileAskWarning, self).__init__(*args)
