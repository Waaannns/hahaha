from flask import Flask, render_template, request, jsonify
from spotify_scraper.auth.auth import Auth
from spotify_scraper import SpotifyClient
from spotify_scraper.download import DownlodTrack
import requests, time

app = Flask(__name__)
app.secret_key = "awan12345"

class Spotify:
    SPOTIFY_HOME_PAGE_URL = "https://open.spotify.com/"
    SPOTI_API_URL = "https://api-partner.spotify.com/pathfinder/v2/query"
    CLIENT_VERSION = "1.2.46.25.g7f189073"

    def __init__(self):
        self.download = DownlodTrack()
        self.client = SpotifyClient()
        self.api = requests.Session()
        self.client = SpotifyClient(browser_type="requests")
        self.api_spotify = "https://api-partner.spotify.com/pathfinder/v2/query"
        self.headers = {
            "accept": "application/json",
            "accept-language": "en-US",
            "content-type": "application/json",
            "origin": self.SPOTIFY_HOME_PAGE_URL,
            "priority": "u=1, i",
            "referer": self.SPOTIFY_HOME_PAGE_URL,
            "sec-ch-ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{self.CLIENT_VERSION} Safari/537.36",
            "spotify-app-version": self.CLIENT_VERSION,
            "app-platform": "WebPlayer",
        }
        self.auth = None
        self.client_token = None
        self.timestamp_session_expire = None
        self.sp_t = None
        self.get_cookies()
        self.get_client_token()
    
    def get_cookies(self):
        res = self.api.get(self.SPOTIFY_HOME_PAGE_URL)
        sp_t = res.cookies.get("sp_t")
        sp_landing = res.cookies.get("sp_landing")
        self.sp_t = sp_t
        return sp_t, sp_landing

    def set_session(self):
        auth = Auth()
        token = auth.generate_token()
        if 'error' in token:
            return token
        
        client_id = token.get("clientId", "")
        access_token = token.get("accessToken", "")
        timestamp_session_expire = int(token.get("accessTokenExpirationTimestampMs", 0))
        return client_id, access_token, timestamp_session_expire
    
    def get_client_token(self):
        client_id, access_token, timestamp_session_expire = self.set_session()
        data = {
            "client_data": {
                "client_version": self.CLIENT_VERSION,
                "client_id": client_id,
                "js_sdk_data": {
                "device_brand": "unknown",
                "device_model": "unknown",
                "os": "windows",
                "os_version": "NT 10.0",
                "device_id": "8337755e025190d5c2d906247d8664f7",
                "device_type": "computer"
                }
            }
        }
        res = self.api.post("https://clienttoken.spotify.com/v1/clienttoken", json=data, headers=self.headers)
        data = res.json()
        self.client_token = data['granted_token']['token']
        self.auth = f"Bearer {access_token}"
        self.timestamp_session_expire = timestamp_session_expire

    def check_session_auth(self):
        timestamp_now = time.time() * 1000
        if timestamp_now < self.timestamp_session_expire:
            return {"message": "Session is still valid"}
        else:
            self.get_client_token()
            return {"error": "Session expired, please re-authenticate"}
    
    def fetch_home(self):
        auth_check = self.check_session_auth()
        if "error" in auth_check:
            return auth_check

        headers = {
            "accept": "application/json",
            "accept-language": "en-US",
            "content-type": "application/json",
            "authorization": self.auth,
            "client-token": self.client_token,
            "origin": self.SPOTIFY_HOME_PAGE_URL,
            "priority": "u=1, i",
            "referer": self.SPOTIFY_HOME_PAGE_URL,
            "sec-ch-ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{self.CLIENT_VERSION} Safari/537.36",
            "spotify-app-version": self.CLIENT_VERSION,
            "app-platform": "WebPlayer",
        }

        data = {
            "variables": {
                "timeZone": "Asia/Makassar",
                "sp_t": self.sp_t,
                "facet": "",
                "sectionItemsLimit": 10
            },
            "operationName": "home",
            "extensions": {
                "persistedQuery": {
                "version": 1,
                "sha256Hash": "3357ffed7961629ba92b4e0a41514e4d5004a14355c964c23ce442205c9e44a1"
                }
            }
        }

        response = self.api.post(self.api_spotify, json=data, headers=headers)
        if response.status_code != 200:
            return {"error": f"Failed to fetch home data. Status code: {response.text}"}
        return response.json()
    
    def fetch_search(self, query):
        """Mencari track berdasarkan query"""
        auth_check = self.check_session_auth()
        if "error" in auth_check:
            return auth_check
        
        headers = {
            "accept": "application/json",
            "accept-language": "en-US",
            "content-type": "application/json",
            "authorization": self.auth,
            "client-token": self.client_token,
            "origin": self.SPOTIFY_HOME_PAGE_URL,
            "priority": "u=1, i",
            "referer": self.SPOTIFY_HOME_PAGE_URL,
            "sec-ch-ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{self.CLIENT_VERSION} Safari/537.36",
            "spotify-app-version": self.CLIENT_VERSION,
            "app-platform": "WebPlayer",
        }

        data = {
            "variables": {
                "searchTerm": query,
                "offset": 0,
                "limit": 50,
                "numberOfTopResults": 5,
                "includeAudiobooks": True,
                "includeArtistHasConcertsField": False,
                "includePreReleases": True,
                "includeLocalConcertsField": False,
                "includeAuthors": False
            },
            "operationName": "searchDesktop",
            "extensions": {
                "persistedQuery": {
                "version": 1,
                "sha256Hash": "d9f785900f0710b31c07818d617f4f7600c1e21217e80f5b043d1e78d74e6026"
                }
            }
        }

        response = self.api.post(self.api_spotify, json=data, headers=headers)
        if response.status_code != 200:
            return {"error": f"Failed to fetch search results. Status code: {response.text}"}
        
        return response.json()
    
    def fetch_track_by_id(self, track_id):
        """Fetches track information from Spotify.
        Args:
            track_url (str): The URL of the Spotify track.
        Returns:
            dict: A dictionary containing track information.
        """
        track = self.client.get_track_info(f"https://open.spotify.com/track/{track_id}")
        if not track:
            return {"error": "Track not found or invalid ID"}

        self.client.close()

        return track
    
    def play_track(self, track_id):
        """Plays a track by its ID."""
        play = self.download._main(track_id)
        if not play:
            return {"error": "Failed to play track or invalid ID"}
        return play
    
    def get_recomen(self, query):
        auth_check = self.check_session_auth()
        if "error" in auth_check:
            return auth_check
        
        headers = {
            "accept": "application/json",
            "accept-language": "en-US",
            "content-type": "application/json",
            "authorization": self.auth,
            "client-token": self.client_token,
            "origin": self.SPOTIFY_HOME_PAGE_URL,
            "priority": "u=1, i",
            "referer": self.SPOTIFY_HOME_PAGE_URL,
            "sec-ch-ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{self.CLIENT_VERSION} Safari/537.36",
            "spotify-app-version": self.CLIENT_VERSION,
            "app-platform": "WebPlayer",
        }

        data = {
            "variables": {
                "searchTerm": query,
                "offset": 5,
                "limit": 20,
                "numberOfTopResults": 5,
                "includeAudiobooks": False,
                "includeArtistHasConcertsField": False,
                "includePreReleases": False,
                "includeLocalConcertsField": False,
                "includeAuthors": False
            },
            "operationName": "searchDesktop",
            "extensions": {
                "persistedQuery": {
                "version": 1,
                "sha256Hash": "d9f785900f0710b31c07818d617f4f7600c1e21217e80f5b043d1e78d74e6026"
                }
            }
        }

        response = self.api.post(self.api_spotify, json=data, headers=headers)
        if response.status_code != 200:
            return {"error": f"Failed to fetch search results. Status code: {response.text}"}
        
        return response.json()

spotify = Spotify()

SAMPLE_TRACKS = [
    {
        'id': '4uLU6hMCjMI75M1A2tKUQC',
        'name': 'Blinding Lights',
        'artist': 'The Weeknd',
        'tipe': 'track',
        'image_300': 'https://i.scdn.co/image/ab67616d00001e028863bc11d2aa12b54f5aeb36',
        'image_64': 'https://i.scdn.co/image/ab67616d000048518863bc11d2aa12b54f5aeb36',
        'duration': 200040
    },
    {
        'id': '7qiZfU4dY1lWllzX7mPBI3',
        'name': 'Shape of You',
        'artist': 'Ed Sheeran',
        'tipe': 'track',
        'image_300': 'https://i.scdn.co/image/ab67616d00001e02ba5db46f4b838ef6027e6f96',
        'image_64': 'https://i.scdn.co/image/ab67616d00004851ba5db46f4b838ef6027e6f96',
        'duration': 233713
    },
    {
        'id': '0VjIjW4GlULA6LaGWNh4I7',
        'name': 'Watermelon Sugar',
        'artist': 'Harry Styles',
        'tipe': 'track',
        'image_300': 'https://i.scdn.co/image/ab67616d00001e02277b3fd1b9e54adae8b78828',
        'image_64': 'https://i.scdn.co/image/ab67616d00004851277b3fd1b9e54adae8b78828',
        'duration': 174000
    },
    {
        'id': '1r9xUipOqoNwggBpENDsvJ',
        'name': 'Someone Like You',
        'artist': 'Adele',
        'tipe': 'track',
        'image_300': 'https://i.scdn.co/image/ab67616d00001e02372eb33d0cd0618269fb6be1',
        'image_64': 'https://i.scdn.co/image/ab67616d00004851372eb33d0cd0618269fb6be1',
        'duration': 285000
    }
]

@app.route('/')
def home():
    """Halaman utama"""
    featured_tracks = spotify.fetch_home()
    
    # Jika gagal mendapatkan data dari Spotify, gunakan sample tracks
    if not featured_tracks or 'error' in featured_tracks:
        return render_template('index.html', tracks=SAMPLE_TRACKS)

    trending_songs = []
    try:
        ts_raw = featured_tracks['data']['home']['sectionContainer']['sections']['items'][0]
        for ts in ts_raw['sectionItems']['items']:
            try:
                name = ts['content']['data']['name']
                artist = ts['content']['data']['artists']['items']
                artist_names = ', '.join([artist['profile']['name'] for artist in artist])
                images = ts['content']['data']['albumOfTrack']['coverArt']['sources']
                image_300 = images[0]['url']
                image_64 = images[1]['url']
                uri = ts['uri']
                if uri.split(":"):
                    og, tp, id = uri.split(':')

                trending = {
                'id': id,
                'name': name,
                'tipe': tp,
                'artist': artist_names,
                "image_300": image_300,
                "image_64": image_64,
                }

                trending_songs.append(trending)
            except Exception as e:
                continue
    except Exception as e:
        print(f"Error parsing home data: {e}")
        trending_songs = SAMPLE_TRACKS
    
    # Jika tidak ada trending songs, gunakan sample tracks
    if not trending_songs:
        trending_songs = SAMPLE_TRACKS
    
    return render_template('index.html', tracks=trending_songs)

@app.route('/search')
def search():
    """Endpoint untuk pencarian musik"""
    query = request.args.get('q', '')
    if not query:
        render_template('index.html')
    
    tracks = spotify.fetch_search(query)
    
    if not tracks or 'error' in tracks:
        if query.lower() in ['sample', 'test', 'demo']:
            return jsonify(SAMPLE_TRACKS)
        return jsonify([])

    result_search = []
    try:
        sr_raw = tracks['data']['searchV2']['tracksV2']['items']
        for sr in sr_raw:
            id = sr['item']['data']['id']
            name = sr['item']['data']['name']
            tipe = sr['item']['data']['__typename'].lower()
            artist = ', '.join([artist['profile']['name'] for artist in sr['item']['data']['artists']['items']])
            image_300 = sr['item']['data']['albumOfTrack']['coverArt']['sources'][0]['url']
            image_64 = sr['item']['data']['albumOfTrack']['coverArt']['sources'][1]['url']
            duration = sr['item']['data']['duration']['totalMilliseconds']
        
            result = {
                'id': id,
                'name': name,
                'tipe': tipe,
                'artist': artist,
                'image_300': image_300,
                'image_64': image_64,
                'duration': duration
            }
            result_search.append(result)
    except (KeyError, TypeError) as e:
        print(f"Error parsing search results: {e}")
        return jsonify([])
    
    return jsonify(result_search)

@app.route('/recommendations/<name>')
def get_recommendations(name):
    """Endpoint untuk mendapatkan rekomendasi track"""
    if not name:
        return jsonify({'error': 'Name parameter is required'}), 400
    recommendations = spotify.get_recomen(name)
    if not recommendations or 'error' in recommendations:
        if name.lower() in ['sample', 'test', 'demo']:
            return jsonify(SAMPLE_TRACKS)
        return jsonify([])

    result_recommendations = []
    try:
        sr_raw = recommendations['data']['searchV2']['tracksV2']['items']
        for sr in sr_raw:
            id = sr['item']['data']['id']
            name = sr['item']['data']['name']
            tipe = sr['item']['data']['__typename'].lower()
            artist = ', '.join([artist['profile']['name'] for artist in sr['item']['data']['artists']['items']])
            image_300 = sr['item']['data']['albumOfTrack']['coverArt']['sources'][0]['url']
            image_64 = sr['item']['data']['albumOfTrack']['coverArt']['sources'][1]['url']
            duration = sr['item']['data']['duration']['totalMilliseconds']
        
            result = {
                'id': id,
                'name': name,
                'tipe': tipe,
                'artist': artist,
                'image_300': image_300,
                'image_64': image_64,
                'duration': duration
            }
            result_recommendations.append(result)
    except (KeyError, TypeError) as e:
        print(f"Error parsing search results: {e}")
        return jsonify([])
    
    return jsonify(result_recommendations)

@app.route('/track/<track_id>')
def get_track_info(track_id):
    """Endpoint untuk mendapatkan informasi track"""
    track_info = spotify.fetch_track_by_id(track_id)
    if 'error' in track_info:
        return jsonify({'error': track_info['error']}), 404
    return jsonify(track_info)

@app.route('/play/<track_id>')
def play_track_endpoint(track_id):
    """Endpoint untuk memutar track"""
    play_result = spotify.play_track(track_id)
    if 'false' in play_result:
        return jsonify({'error': play_result['error']}), 404
    return jsonify(play_result['url'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
