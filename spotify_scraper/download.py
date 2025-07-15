import requests
from bs4 import BeautifulSoup

class DownlodTrack:
    
    def __init__(self,):
        pass

    def get_cookies(self):
        url = "https://spotmate.online/en"
        response = requests.get(url)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            meta_token = soup.find('meta', attrs={'name': 'csrf-token'})
            token = meta_token['content'] if meta_token else None

            cookies = response.cookies
            xsrftoken = cookies['XSRF-TOKEN']
            spotmateonline_session = cookies['spotmateonline_session']

            return xsrftoken, spotmateonline_session, token
        else:
            print(f"Failed to get cookies. Status code: {response.status_code}")
            return None
        
    def get_data_by_id(self, track_id, xsrftoken, spotmateonline_session, token):
        headers = {
            "accept": "*/*",
            "Accept-Encoding": 'gzip, deflate, br, zstd',
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Type": "application/json",
            "cookie": f"XSRF-TOKEN={xsrftoken}; spotmateonline_session={spotmateonline_session}",
            "Host": "spotmate.online",
            "Origin": "https://spotmate.online",
            "Referer": "https://spotmate.online/en",
            "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "Windows",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "X-CSRF-TOKEN": token
        }

        data = {
            "spotify_url": f"https://open.spotify.com/track/{track_id}"
        }

        response = requests.post("https://spotmate.online/getTrackData", json=data, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            cookies = response.cookies
            xsrftoken = cookies['XSRF-TOKEN']
            spotmateonline_session = cookies['spotmateonline_session']
            return result, xsrftoken, spotmateonline_session
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}, Response: {response.text}")
            return None
        
    def download_track(self, track_id, xsrftoken, spotmateonline_session, token):
        headers = {
            "accept": "*/*",
            "Accept-Encoding": 'gzip, deflate, br, zstd',
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Type": "application/json",
            "cookie": f"XSRF-TOKEN={xsrftoken}; spotmateonline_session={spotmateonline_session}",
            "Host": "spotmate.online",
            "Origin": "https://spotmate.online",
            "Referer": "https://spotmate.online/en",
            "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "Windows",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "X-CSRF-TOKEN": token
        }

        data = {
            "urls": f"https://open.spotify.com/track/{track_id}"
        }

        response = requests.post("https://spotmate.online/convert", json=data, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}, Response: {response.text}")
            return None
        
    def _main(self, track_id):
        xsrftoken, spotmateonline_session, token = self.get_cookies()
        if not xsrftoken or not spotmateonline_session or not token:
            print("Failed to retrieve cookies.")
            return
        
        result, xsrftoken1, spotmateonline_session1 = self.get_data_by_id(track_id, xsrftoken, spotmateonline_session, token)
        if not result:
            print("Failed to retrieve track data.")
            return
        
        download_result = self.download_track(track_id, xsrftoken1, spotmateonline_session1, token)
        if not download_result:
            print("Failed to download track.")
            return
        
        return download_result