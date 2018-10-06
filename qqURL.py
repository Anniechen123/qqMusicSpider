import requests
import json

URL = {
        'song': "https://c.y.qq.com/soso/fcgi-bin/client_search_cp?ct=24&qqmusic_ver=1298&new_json=1&remoteplace=txt.yqq.top&searchid=1&t=0&aggr=1&cr=1&catZhida=1&lossless=0&flag_qc=0&p={0}&n={1}&w={2}",
        'album': "https://c.y.qq.com/soso/fcgi-bin/client_search_cp?ct=24&qqmusic_ver=1298&remoteplace=txt.yqq.top&searchid=1&aggr=0&catZhida=1&lossless=0&sem=10&t=8&p={0}&n=%{1}&w={2}",
        'mv': "https://c.y.qq.com/soso/fcgi-bin/client_search_cp?ct=24&qqmusic_ver=1298&remoteplace=txt.yqq.top&searchid=1&aggr=0&catZhida=1&lossless=0&sem=1&t=12&p={0}&n={1}&w={2}",
        'playlist': "https://c.y.qq.com/soso/fcgi-bin/client_music_search_songlist?remoteplace=txt.yqq.top&searchid=1&flag_qc=0&page_no={0}&num_per_page={1}&query={2}",
        'user': "https://c.y.qq.com/soso/fcgi-bin/client_search_user?ct=24&qqmusic_ver=1298&p={0}&n={1}&searchid=1&remoteplace=txt.yqq.top&w={2}",
        'lyric': "https://c.y.qq.com/soso/fcgi-bin/client_search_cp?ct=24&qqmusic_ver=1298&remoteplace=txt.yqq.top&searchid=1&aggr=0&catZhida=1&lossless=0&sem=1&t=7&p={0}&n={1}&w={2}"
}


def format_url(t, page, num, word):
    try:
        url = URL[t].format(page, num, word)
    except KeyError:
        print("The type is wrong. Type should be one of ['song', 'album', 'mv', 'playlist', 'user', 'lyric'].")
        url = ""
    return url


def get_json(url):
    html = requests.get(url)
    return json.loads(html.text.strip("callback()"))


def parse_song_json(j):
    songlist = []
    for i in j['data']['song']['list']:
        song = {}
        song['songmid'] = i['mid']
        song['songname'] = i['name']
        song['subtitle'] = i['subtitle']
        song['singername'] = []
        for k in i['singer']:
            song['singername'].append(k['name'])
        song['albumname'] = i['album']['name']
        songlist.append(song)
    return songlist


url = format_url('song', 1, 4, "不哭")
parse_song_json(get_json(url))