from typing import Union
import httpx

from application.utils import reader_setting
from application.errors import GuiNetError


class Connect(httpx.Client):
    def __init__(self):
        net_config = reader_setting("./settings/net/setting.json")
        super(Connect, self).__init__(
            trust_env=net_config.get("trust_env", False),
            proxies=net_config.get("proxies", None),
            timeout=float(net_config["timeout"])
        )
        self.headers.update(net_config.get("headers", dict()))

    def request_X(self, method, url, **kwargs) -> Union[httpx.Response, str]:
        if "timeout" not in kwargs:
            kwargs.update({"timeout": self.timeout})
        try:
            res = self.request(method, url, **kwargs)
        except Exception as e:
            raise GuiNetError(e)
        else:
            return res
