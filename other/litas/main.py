import asyncio
import logging
import random
from typing import List, Dict, Any
import aiohttp
import requests
import pytz

from wechat import send_wxpusher_message

beijing_timezone = pytz.timezone('Asia/Shanghai')

# 模拟从文件读取数据的函数
async def read_accounts_from_file(file_path: str) -> List[Dict[str, str]]:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = file.read().strip()
            lines = data.split('\n')
            accounts = []
            for line in lines:
                parts = line.split('|')
                if len(parts) == 3 and parts[0] and parts[1] and parts[2]:
                    accounts.append({
                        'token': parts[0].strip(),
                        'reToken': parts[1].strip(),
                        'nickname': parts[2].strip()
                    })
            return accounts
    except Exception as e:
        logging.error(f'Error reading accounts file: {str(e)}')
        return []

# 模拟从文件读取代理信息的函数
async def read_file(file_path: str) -> List[str]:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = file.read().strip()
            lines = data.split('\n')
            proxies = [line.strip() for line in lines if line.strip()]
            return proxies
    except Exception as e:
        logging.error(f'Error reading file: {str(e)}')
        return []

# 模拟写入文件的函数
async def write_accounts_to_file(file_name: str, accounts: List[Dict[str, str]]):
    data = '\n'.join([f"{account['token']}|{account['reToken']}|{account['nickname']}" for account in accounts])
    with open(file_name, 'w', encoding='utf-8') as file:
        file.write(data)

# 模拟延迟函数
async def delay(seconds: int):
    await asyncio.sleep(seconds)

# 模拟获取新token的函数
async def get_new_token(token: str, refresh_token: str, proxy: str = None) -> Dict[str, Any]:
    url = 'https://wallet.litas.io/api/v1/auth/refresh'
    xtoken, xtoken_cookie = get_antiforgery_token(token)

    headers = {
        'Content-Type': 'application/json',
        'referer': 'https://wallet.litas.io/miner',
        'X-CSRF-TOKEN': f'{xtoken}',
        'cookie': f'X-CSRF-TOKEN={xtoken_cookie}',
        'Authorization': f'Bearer {token}'
    }
    payload = {'refreshToken': refresh_token}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    send_wxpusher_message(f'litas Error: {await response.text()}')
                    logging.error(f'Error: {await response.text()}')
                    raise Exception(f'Error: {await response.text()}')
    except Exception as e:
        logging.error(f'Error: {str(e)}')
        return None

# 模拟获取用户农场信息的函数
async def get_user_farm(token: str, proxy: str = None) -> Dict[str, Any]:
    url = 'https://wallet.litas.io/api/v1/miner/current-user'
    headers = {
        'Authorization': f'Bearer {token}',
        'referer': 'https://wallet.litas.io/miner',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
        'sec-ch-ua-platform': '"macOS"',
        'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
        'Accept': 'application/json',
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    logging.info(f'getUserFarm response: {data}')
                    return data
                elif response.status == 401:
                    return None
                else:
                    logging.error(f'Error: {await response.text()}')
                    return None
    except Exception as e:
        logging.error(f'Error: {str(e)}')
        return None

def upgrade_mining_speed(token, nickname):
    url = 'https://wallet.litas.io/api/v1/miner/upgrade/speed'
    xtoken, xtoken_cookie = get_antiforgery_token(token)
    headers = {
        'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
        'X-CSRF-TOKEN': f'{xtoken}',
        'cookie': f'X-CSRF-TOKEN={xtoken_cookie}',
        'sec-ch-ua-mobile': '?0',
        'Authorization': f'Bearer {token}',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Referer': 'https://wallet.litas.io/miner',
        'sec-ch-ua-platform': '"macOS"'
    }

    try:
        response = requests.patch(url, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        return response.json()
    except requests.RequestException as e:
        print(f"请求发生错误: {e}")
        return None

# 模拟激活挖矿的函数
async def activate_mining(token: str,nickname: str, proxy: str = None) -> Dict[str, Any]:
    url = 'https://wallet.litas.io/api/v1/miner/activate'
    xtoken, xtoken_cookie = get_antiforgery_token(token)
    headers = {
        'authorization': f'Bearer {token}',
        'referer': 'https://wallet.litas.io/miner',
        'X-CSRF-TOKEN': f'{xtoken}',
        'cookie': f'X-CSRF-TOKEN={xtoken_cookie}',
        'IDEMPOTENCY-KEY': f'{nickname}',
        'referer': 'https://wallet.litas.io/miner',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
        'sec-ch-ua-platform': '"macOS"',
        'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
        'Accept': 'application/json',
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.patch(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 401:
                    return "unauth"
                elif response.status == 409:
                    return "success farm already activated"
                else:
                    logging.error(f'Error: {await response.text()}')
                    return None
    except Exception as e:
        logging.error(f'Error: {str(e)}')
        return None

# 模拟领取挖矿奖励的函数
async def claim_mining(token: str, nickname: str, proxy: str = None) -> Dict[str, Any]:
    url = 'https://wallet.litas.io/api/v1/miner/claim'
    xtoken, xtoken_cookie = get_antiforgery_token(token)
    headers = {
        'Authorization': f'Bearer {token}',
        'X-CSRF-TOKEN': f'{xtoken}',
        'cookie': f'X-CSRF-TOKEN={xtoken_cookie}',
        'Referer': 'https://wallet.litas.io/miner',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'sec-ch-ua-platform': '"macOS"',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'Accept': 'application/json',
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.patch(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 401:
                    return "unauth"
                elif response.status == 409:
                    return "success farm already claimed"
                else:
                    logging.error(f'Error: {await response.text()}')
                    return None
    except Exception as e:
        logging.error(f'Error: {str(e)}')
        return None

def get_antiforgery_token(token):
    """
    发送请求获取 antiforgery token 的函数
    参数:
    token (str): 认证所需的 Bearer token
    返回:
    dict or None: 如果请求成功，返回响应的 JSON 数据；否则返回 None
    """
    url = 'https://wallet.litas.io/api/v1/antiforgery/token'
    headers = {
        'Authorization': f'Bearer {token}',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'sec-ch-ua-platform': '"macOS"',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'Accept': 'application/json',
        'Referer': 'https://wallet.litas.io/miner',

    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        return response.json()['token'], response.cookies.get('X-CSRF-TOKEN')
    except requests.RequestException as e:
        print(f"Error: {e}")
        return None


# 刷新访问令牌的函数
async def refresh_access_token(token: str, refresh_token: str, proxy: str = None) -> Dict[str, Any]:
    refresh = None
    while not refresh:
        refresh = await get_new_token(token, refresh_token, proxy)
        if not refresh:
            logging.info('Token refresh failed, retrying...')
            await delay(3)
    logging.info('Token refreshed succesfully', refresh)
    return refresh
#
# # 激活挖矿流程的函数
# async def activate_mining_process(token: str,nickname: str, refresh_token: str, proxy: str = None) -> str:
#     activate = None
#     while not activate or activate == "unauth":
#         activate = await activate_mining(token, nickname, proxy)
#         if activate == "unauth":
#             logging.warn('Unauthorized, refreshing token...')
#             refreshed_tokens = await refresh_access_token(token, refresh_token, proxy)
#             token = refreshed_tokens.get('accessToken')
#             refresh_token = refreshed_tokens.get('refreshToken')
#         elif not activate:
#             logging.info('Activation failed, retrying...')
#             await delay(3)
#     logging.info('Mining activated response:', activate)
#     return token

# 获取用户农场信息的函数
async def get_user_farm_info(access_token: str, refresh_token: str, nick_name: str, proxy: str = None, index: int = 1) -> Dict[str, Any]:
    user_farm_info = None
    while not user_farm_info:
        logging.warn(f'Account {index}, refreshing token...')

        user_farm_info = await get_user_farm(access_token)
        if not user_farm_info:
            logging.warn(f'Account {index} get farm info failed, retrying...')
            refreshed_tokens = await refresh_access_token(access_token, refresh_token, proxy)
            access_token = refreshed_tokens.get('accessToken')
            refresh_token = refreshed_tokens.get('refreshToken')
            await delay(3)
    status = user_farm_info.get('status')
    total_mined = user_farm_info.get('totalMined')
    logging.info(f'Account {index} {nick_name} farm info: status: {status}, totalMined: {total_mined}')
    return {
        'userFarmInfo': user_farm_info,
        'accessToken': access_token,
        'refreshToken': refresh_token
    }

# 处理挖矿的函数
async def handle_farming(user_farm_info: Dict[str, Any], token: str,  refresh_token: str,nick_name:str, proxy: str = None):
    can_be_claimed_at = datetime.datetime.fromisoformat(user_farm_info.get('canBeClaimedAt','').replace('Z', '+00:00'))
    time_now = int(time.time())
    if can_be_claimed_at.timestamp() < time_now:
        logging.info('Farming rewards are claimable. Attempting to claim farming rewards...')
        claim_response = None
        while not claim_response:
            claim_response = await claim_mining(token,nick_name,proxy)
            if not claim_response:
                logging.info('Failed to claim farming rewards, retrying...')
                await delay(3)
        logging.info('Farming rewards claimed response:', claim_response)
        # await activate_mining_process(token, refresh_token,nick_name,  proxy)
        upgrade_mining_speed(token, nick_name)
    else:
        logging.info('Farming rewards can be claimed at:' + can_be_claimed_at.astimezone(beijing_timezone).strftime('%Y-%m-%d %H:%M:%S'))

# 主函数
async def main():
    logging.basicConfig(level=logging.INFO)
    accounts = await read_accounts_from_file("tokens.txt")
    proxies = await read_file("proxy.txt")

    if len(accounts) == 0:
        logging.warn('No tokens found, exiting...')
        return
    else:
        logging.info(f'Running with total Accounts: {len(accounts)}')

    if len(proxies) == 0:
        logging.warn('No proxy found, running without proxy...')
    while True:
        for i in range(len(accounts)):
            proxy = proxies[i % len(proxies)] if proxies else None
            account = accounts[i]
            try:
                token = account.get('token')
                re_token = account.get('reToken')
                nickname = account.get('nickname')
                logging.info(f'Processing run account {i + 1} of {len(accounts)} with: {proxy or "No proxy"}')
                user_farm_info_data = await get_user_farm_info(token, re_token, nickname, proxy, i + 1)
                user_farm_info = user_farm_info_data.get('userFarmInfo')
                access_token = user_farm_info_data.get('accessToken')
                refresh_token = user_farm_info_data.get('refreshToken')
                # await activate_mining_process(access_token, user_farm_info.get('nickName'), refresh_token, proxy)
                await handle_farming(user_farm_info, access_token, refresh_token, nickname, proxy)
                account['token'] = access_token
                account['reToken'] = refresh_token
            except Exception as e:
                logging.error(f'Error: {str(e)}')
            await delay(3)

        await write_accounts_to_file("tokens.txt", accounts)
        logging.info('All accounts processed, waiting 1 hour before next run...')
        await delay(random.randint(20, 40) * 60)

if __name__ == "__main__":
    import time
    import datetime
    asyncio.run(main())
