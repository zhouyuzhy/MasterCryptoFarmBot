import traceback

from wxpusher import WxPusher

APP_TOKEN='AT_xqMuBHDHg03UKKaTJOuZGayC8oYgPgEr'
UID='UID_Rp9eNMIiRMcI9Fi3O6S4CtsRBwuC'

def send_wxpusher_message(content, content_type=2, uids=[UID], token=APP_TOKEN):
    '''
    https://wxpusher.zjiecode.com/admin/main/wxuser/list
    https://github.com/wxpusher/wxpusher-sdk-python
    :param content:
    :param uids:
    :param token:
    :return:
    '''
    try:
        res = WxPusher.send_message(content, content_type=content_type, uids=uids, token=token)
        return res
    except Exception:
        print(traceback.format_exc())
