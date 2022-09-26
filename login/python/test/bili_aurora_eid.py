import base64


"""

//tv.danmaku.bili.aurora.api.ids.a

@AnyThread
private final String e(String str) {
    byte[] bArr = new byte[str.length()];
    int length = str.length() - 1;
    if (length >= 0) {
        int i = 0;
        while (true) {
            int i2 = i + 1;
            bArr[i] = (byte) (((byte) str.charAt(i)) ^ ((byte) "ad1va46a7lza".charAt(i % 12)));
            if (i2 > length) {
                break;
            }
            i = i2;
        }
    }
    return Base64.encodeToString(bArr, 10);
}

"""


def bili_aurora_eid_java(mid: str):
    """ 照搬java """
    length = mid.__len__() - 1
    barr = [int() for _ in range(mid.__len__())]
    if length >= 0:
        i = 0
        while True:
            i2 = i + 1
            a = ord(mid[i])
            b = ord("ad1va46a7lza"[i % 12])
            barr[i] = a ^ b
            if i2 > length:
                break
            i = i2
    base64_de = b"".join([chr(li).encode() for li in barr])
    base64_en = base64.b64encode(base64_de)
    return base64_en.decode()


def bili_aurora_eid_python(mid: str):
    length = mid.__len__()
    barr = [int() for _ in range(length)]
    if length - 1 < 0:
        return ""
    for i in range(length):
        a = ord(mid[i])
        b = ord("ad1va46a7lza"[i % 12])
        barr[i] = a ^ b
    base64_de = b"".join([chr(li).encode() for li in barr])
    base64_en = base64.b64encode(base64_de)
    return base64_en.decode()


if __name__ == '__main__':
    print(bili_aurora_eid_java("1701735549"))
    print(bili_aurora_eid_python("1701735549"))

    # UFMBR1YHA1QDVQ==
    # UFMBR1YHA1QDVQ==
