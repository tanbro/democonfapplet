# -*- encoding: utf-8 -*-

from io import BytesIO, StringIO
from hashlib import md5
from base64 import b64encode
from datetime import datetime
import xml.etree.ElementTree as ETree

import aiohttp

from . import conf


class RestApiError(Exception):
    def __init__(self, code, message=''):
        super(Exception, self).__init__('{}: {}'.format(code, message))
        self._code = int(code)
        self._message = str(message)

    @property
    def code(self):
        return self._code

    @property
    def message(self):
        return self._message


def raise_if_error(obj):
    code = 0
    if isinstance(obj, ETree.ElementTree):
        root = obj.getroot()
        code = int(root.find('./statusCode').text)
        ele_msg = root.find('./statusMsg')
        if ele_msg is None:
            message = ''
        else:
            message = ele_msg.text
    elif isinstance(obj, dict):
        code = int(obj['statusCode'])
        message = str(obj.get('statusMsg', ''))
    else:
        raise TypeError('Unknown object type')
    if code:
        raise RestApiError(code, message)


def build_auth(sid, token):
    """帐号鉴权

    * `URL` 后必须带有 `sig `参数，例如： ``sig=AAABBBCCCDDDEEEFFFGGG`` 。
    * 使用 MD5 加密（主帐号Id + 主帐号授权令牌 +时间戳）。其中主帐号Id和主帐号授权令牌分别对应管理控制台中的 `ACCOUNT` `SID`和 `AUTH TOKEN` 。
    * 时间戳是当前系统时间，格式 `yyyyMMddHHmmss` 。时间戳有效时间为24小时，如：20140416142030
    * `SigParameter` 参数需要大写
    """
    ts = '{:%Y%m%d%H%M%S}'.format(datetime.now())
    sig = md5(
        '{}{}{}'.format(sid, token, ts).encode()
    ).hexdigest().upper()
    auth = b64encode('{}:{}'.format(sid, ts).encode()).decode()
    return auth, sig, ts


def ivr_resp_to_dict(et):
    if ETree.iselement(et):
        root = et
    else:
        root = et.getroot()
    result = {}
    for child in root:
        result[child.tag] = child.text
    return result


async def ivr_invoke(func_des, command, func='ivr', app_id=None, account_sid=None, auth_type=None, auth_token=None,
                     params=None,
                     **kwargs):
    app_id = app_id or conf.YTX_APP_ID
    account_sid = account_sid or conf.YTX_ACCOUNT_SID
    auth_type = auth_type or 'Accounts'
    auth_token = auth_token or conf.YTX_AUTH_TOKEN
    params = params or {}
    auth, sig, ts = build_auth(account_sid, auth_token)
    url = '{url}/{authType}/{account}/{func}/{funcdes}'.format(
        url=conf.YTX_URL_PREFIX,
        authType=auth_type,
        account=account_sid,
        func=func,
        funcdes=func_des,
    )
    headers = {
        'Authorization': auth,
        'Accept': 'application/xml',
        'Content-Type': 'application/xml;charset=utf-8',
    }
    params['sig'] = sig
    req = ETree.Element('Request')
    t = ETree.ElementTree(req)
    p = ETree.SubElement(req, 'Appid')
    p.text = str(app_id)
    p = ETree.SubElement(req, command)
    for k, v in kwargs.items():
        p.set(str(k), str(v))
    fs = BytesIO()
    try:
        t.write(fs, encoding='utf-8', xml_declaration=True)
        data = fs.getvalue()
    finally:
        fs.close()
    with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, params=params, data=data) as resp:
            s = await resp.text()
            fs = StringIO(s)
            try:
                tree = ETree.parse(StringIO(s))
            finally:
                fs.close()
            raise_if_error(tree)
            return ivr_resp_to_dict(tree)
