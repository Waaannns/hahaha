import base64, requests, pyotp, time
from random import randrange

class Auth:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'Referer': 'https://open.spotify.com/',
            'Origin': 'https://open.spotify.com'
        }
    
    def get_random_user_agent(self):
        return f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_{randrange(11, 15)}_{randrange(4, 9)}) AppleWebKit/{randrange(530, 537)}.{randrange(30, 37)} (KHTML, like Gecko) Chrome/{randrange(80, 105)}.0.{randrange(3000, 4500)}.{randrange(60, 125)} Safari/{randrange(530, 537)}.{randrange(30, 36)}"

    def generate_totp(self):
        url = "https://raw.githubusercontent.com/Thereallo1026/spotify-secrets/refs/heads/main/secrets/secretBytes.json"
        
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code != 200:
                raise Exception(f"Failed to fetch TOTP secrets from GitHub. Status: {resp.status_code}")
            secrets_list = resp.json()
            
            latest_entry = max(secrets_list, key=lambda x: x["version"])
            version = latest_entry["version"]
            secret_cipher = latest_entry["secret"]
        except Exception as e:
            raise Exception(f"Failed to fetch secrets from GitHub: {str(e)}")

        processed = [byte ^ ((i % 33) + 9) for i, byte in enumerate(secret_cipher)]
        processed_str = "".join(map(str, processed))
        utf8_bytes = processed_str.encode('utf-8')
        hex_str = utf8_bytes.hex()
        secret_bytes = bytes.fromhex(hex_str)
        b32_secret = base64.b32encode(secret_bytes).decode('utf-8')
        totp = pyotp.TOTP(b32_secret)

        headers = {
            "Host": "open.spotify.com",
            "User-Agent": self.get_random_user_agent(),
            "Accept": "*/*",
        }

        try:
            resp = requests.get("https://open.spotify.com/api/server-time", headers=headers, timeout=10)
            if resp.status_code != 200:
                raise Exception(f"Failed to get server time. Status code: {resp.status_code}")
            data = resp.json()
            server_time = data.get("serverTime")
            if server_time is None:
                raise Exception("Failed to fetch server time from Spotify")
            return totp, server_time, version
        except Exception as e:
            raise Exception(f"Error getting server time: {str(e)}")
        
    def generate_token(self):
        try:
            totp, server_time, totp_version = self.generate_totp()
            otp_code = totp.at(int(server_time))
            timestamp_ms = int(time.time() * 1000)
            
            params = {
                'reason': 'transport',
                'productType': 'web-player',
                'totp': otp_code,
                'totpServerTime': server_time,
                'totpVer': str(totp_version),
                'sTime': server_time,
                'cTime': timestamp_ms,
                'buildVer': 'web-player_2025-06-11_1749636522102_27bd7d1',
                'buildDate': '2025-06-11'
            }
            
            req = requests.get("https://open.spotify.com/api/token", headers=self.headers, params=params)
            if req.status_code != 200:
                return {"error": f"Failed to get access token. Status code: {req.status_code}"}
            token = req.json()
            return token
        except Exception as e:
            return {"error": f"Failed to get access token: {str(e)}"}