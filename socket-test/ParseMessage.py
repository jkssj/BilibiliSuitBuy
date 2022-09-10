from urllib.parse import urlsplit


def ParseHttpMessage(content: bytes):
    body_byte_array, value_dict = content.split(b"\r\n"), dict()

    body_split = [tuple(i.split(b": ")) for i in body_byte_array[1:]]
    body_dict = dict()
    for body_key in body_split:
        key = body_key[0].decode().lower()
        if 1 < len(body_key) < 3:
            value = body_key[1].decode()
            body_dict[key] = value
        else:
            body_dict[key] = None

    # url—path
    message_url = body_byte_array[0].split(b" ")[1]
    urlsplit_text = urlsplit(message_url.decode("utf-8"))
    verify_path = urlsplit_text.path == "/x/garb/v2/mall/suit/detail"
    assert verify_path, "/x/garb/v2/mall/suit/detail not in HttpMessage"
    url_params = urlsplit_text.query
    params_split = [i.split("=") for i in url_params.split("&")]
    params_dict = {key: value for key, value in params_split}

    access_key = params_dict.get("access_key", None)
    assert access_key, "access_key not in HttpMessage"
    value_dict.update({"access_key": access_key})

    app_key = params_dict.get("appkey", None)
    assert app_key, "app_key not in HttpMessage"
    value_dict.update({"app_key": app_key})

    csrf = params_dict.get("csrf", None)
    assert csrf, "csrf not in HttpMessage"
    value_dict.update({"csrf": csrf})

    item_id = params_dict.get("item_id", None)
    assert item_id, "item_id not in HttpMessage"
    value_dict.update({"item_id": item_id})

    statistics = params_dict.get("statistics", None)
    assert statistics, "statistics not in HttpMessage"
    value_dict.update({"statistics": statistics})

    # cookie
    cookie_message = body_dict.get("cookie", None)
    assert cookie_message, "cookie not in HttpMessage"
    value_dict.update({"cookie": cookie_message})

    user_agent = body_dict.get("user-agent", None)
    assert user_agent, "User-Agent not in HttpMessage"
    value_dict.update({"user-agent": user_agent})

    # x-bili-aurora-eid
    aurora_eid = body_dict.get("x-bili-aurora-eid", None)
    assert aurora_eid, "x-bili-aurora-eid not in HttpMessage"
    value_dict.update({"x-bili-aurora-eid": aurora_eid})

    # x-bili-mid
    bili_mid = body_dict.get("x-bili-mid", None)
    assert bili_mid, "x-bili-mid not in HttpMessage"
    value_dict.update({"x-bili-mid": bili_mid})

    return value_dict


def main():
    with open("./message.txt", "rb") as f:
        data_byte = f.read()
    f.close()
    value = ParseHttpMessage(data_byte)
    print(value)


if __name__ == '__main__':
    main()
