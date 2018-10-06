import requests
import os
import json
import bs4
import re
import time


class Song:
    """
    用于获取qq音乐单曲的类
    获得qq音乐单曲的songmid的方法，使用网页版qq音乐，进入一首歌的详情页面
    网址类似于"https://y.qq.com/n/yqq/song/00375L600p9sxv.html"
    该网址中的字符串"00375L600p9sxv"即为songmid
    """
    def __init__(self, songmid):
        self.song_mid = songmid
        self.song_data = None
        self.song_summary = None
        self.song_img_url = ""
        self.song_name = ""
        self.song_singer = ""
        self.get_song_data()

    def get_song_data(self):
        filename = "C400{0}.m4a".format(self.song_mid)
        headers = {
            "User-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
            "Referer": "https://y.qq.com/portal/playlist.html",
            "Host": "c.y.qq.com"
        }

        # 获取歌曲的简要信息，为了获得vkey
        song_summary_url = "https://c.y.qq.com/base/fcgi-bin/fcg_music_express_mobile3.fcg" \
                   "?g_tk=5381&jsonpCallback=MusicJsonCallback20480960151150063&loginUin=0&hostUin=0" \
                   "&format=json&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0" \
                   "&cid=205361747&callback=MusicJsonCallback20480960151150063&uin=0&songmid={0}&filename={1}" \
                   "&guid=9602668140".format(self.song_mid, filename)
        summary_html_text = requests.get(song_summary_url, headers=headers).text
        self.song_summary = json.loads(summary_html_text.strip("MusicJsonCallback20480960151150063()"))

        # 获取歌曲的详细信息
        song_url = "https://c.y.qq.com/v8/fcg-bin/fcg_play_single_song.fcg?songmid={0}&tpl=yqq_song_detail&" \
                   "format=jsonp&callback=getOneSongInfoCallback".format(self.song_mid)
        html_text = requests.get(song_url, headers=headers).text
        song_data = html_text.strip("getOneSongInfoCallback()")

        # 初始化歌曲的常用信息
        song_play_url = "https://y.qq.com/n/yqq/song/{0}.html".format(self.song_mid)
        song_play_bs = bs4.BeautifulSoup(requests.get(song_play_url).text, features="html5lib")
        self.song_img_url = "https:" + song_play_bs.find("img", {"class": "data__photo"}).attrs['src']
        self.song_name = song_play_bs.find("h1", {"class": "data__name_txt"}).get_text()
        self.song_singer = song_play_bs.find("div", {"class": "data__singer"}).attrs['title']
        self.song_data = json.loads(song_data)

    def download_song(self, filepath, songname=None):
        """
        下载歌曲源文件
        :param filepath: 保存文件的路径
        :param songname: 歌曲名
        :return:
        """
        filepath = self.__parse_path(filepath)
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        headers = {
            "User-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
            "Host": "dl.stream.qqmusic.qq.com"
        }
        filename = "C400{0}.m4a".format(self.song_mid)
        vkey = self.song_summary['data']['items'][0]['vkey']
        song_src_url = "http://dl.stream.qqmusic.qq.com/{0}?vkey={1}&guid=9602668140&uin=0&fromtag=66".format(filename, vkey)
        song_stream = requests.get(song_src_url, headers=headers, stream=True)
        if songname is not None:
            song_file = "{0}\\{1}.mp3".format(filepath, songname)
        else:
            song_file = "{0}\\{1}.mp3".format(filepath, self.song_name)
        song_file = self.__parse_path(song_file)
        with open(song_file, "wb") as f:
            f.write(song_stream.raw.read())
            print("Download the music of", self.song_name)
            f.close()

    def download_img(self, filepath, imgname=None):
        """
        下载歌曲的封面图片
        :param filepath: 文件保存路径
        :param imgname: 图片名
        :return:
        """
        filepath = self.__parse_path(filepath)
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        img = requests.get(self.song_img_url, stream=True)
        if imgname is not None:
            song_img_file = "{0}\\{1}.png".format(filepath, imgname)
        else:
            song_img_file = "{0}\\{1}.png".format(filepath, self.song_name)
        song_img_file = self.__parse_path(song_img_file)
        with open(song_img_file, "wb") as f:
            f.write(img.raw.read())
            print("Download the image of", self.song_name)
            f.close()

    def download_lyric(self, filepath, lyricname=None):
        headers = {
            "User-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
            "Referer": "https://y.qq.com/portal/playlist.html",
            "Host": "c.y.qq.com"
        }
        song_id = self.song_data['data'][0]['id']
        lyric_url = "http://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric.fcg?nobase64=1&musicid={0}&callback=jsonp1".format(
            song_id)
        # song_type = song['songtype']
        # if (song_type == 111) or (song_type == 112) or (song_type == 113):
        #     lyric_url += "&songtype={0}".format(song_type)
        lyric_html = requests.get(lyric_url, headers=headers)
        lyric_content = json.loads(lyric_html.text.strip("jsonp1()"))
        try:
            lyric = self.__parse_lyric(lyric_content['lyric'])
        except KeyError:
            lyric = "没有找到歌词"

        filepath = self.__parse_path(filepath)
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        if lyricname is not None:
            lyric_file = "{0}\\{1}.txt".format(filepath, lyricname)
        else:
            lyric_file = "{0}\\{1}.txt".format(filepath, self.song_name)
        lyric_file = self.__parse_path(lyric_file)
        with open(lyric_file, "w", encoding="utf-8") as f:
            f.write(lyric)
            print("Download the lyric of", self.song_name)
            f.close()

    def download_origin_lyric(self, filepath, lyricname=None):
        """
        下载有时间控制的歌词
        :param filepath:
        :param lyricname:
        :return:
        """
        headers = {
            "User-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
            "Referer": "https://y.qq.com/portal/playlist.html",
            "Host": "c.y.qq.com"
        }
        song_id = self.song_data['data'][0]['id']
        lyric_url = "http://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric.fcg?nobase64=1&musicid={0}&callback=jsonp1".format(
            song_id)
        lyric_html = requests.get(lyric_url, headers=headers)
        lyric_content = json.loads(lyric_html.text.strip("jsonp1()"))['lyric']
        # parsed_lrc = "\n".join(lyric_content.replace("&#32;", " ").split("&#10;"))
        parsed_lrc = lyric_content
        p = re.compile("\&#[0-9]{1,2};")
        ascii_list = set(re.findall(p, parsed_lrc))
        for a in ascii_list:
            parsed_lrc = parsed_lrc.replace(a, chr(int(a[2:4])))
        l = parsed_lrc.split("\n")
        o = []
        for i in l:
            if i.index("]") != len(i) - 1:
                o.append(i)
        parsed_lrc = "\n".join(o)

        filepath = self.__parse_path(filepath)
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        if lyricname is not None:
            lyric_file = "{0}\\{1}.txt".format(filepath, lyricname + "_o")
        else:
            lyric_file = "{0}\\{1}.txt".format(filepath, self.song_name + "_o")
        lyric_file = self.__parse_path(lyric_file)
        with open(lyric_file, "w", encoding="utf-8") as f:
            f.write(parsed_lrc)
            print("Download the origin lyric of", self.song_name)
            f.close()

    def get_song_info(self):
        """
        获取歌曲的关键信息，包括：
        song_mid  song_name  music_url
        :return: song_info -- JSON
        """
        song_info = dict()
        song_info['songmid'] = self.song_mid
        song_info['songname'] = self.song_name
        song_info['singername'] = self.song_singer
        song_info['songtime'] = self.song_data['data'][0]['interval']
        filename = "C400{0}.m4a".format(self.song_mid)
        vkey = self.song_summary['data']['items'][0]['vkey']
        song_info['musicurl'] = "http://dl.stream.qqmusic.qq.com/{0}?vkey={1}&guid=9602668140&uin=0&fromtag=66"\
            .format(filename, vkey)
        return song_info

    @staticmethod
    def __parse_lyric(lyric):
        """
        内部解析歌词的函数
        :param lyric: 歌词源件
        :return:
        """
        # parsed_lrc = lyric.replace("&#32;", " ").split("&#10;")
        # p = re.compile("\[(.*)\]")
        # parsed_lrc = [re.sub(p, "", a) for a in parsed_lrc]
        # parsed_lrc = "\n".join(parsed_lrc)
        #
        # # 替换歌词中的ascii字符
        # parsed_lrc = parsed_lrc.strip()
        # p = re.compile("\&#[0-9]{1,2};")
        # ascii_list = re.findall(p, parsed_lrc)
        # for a in ascii_list:
        #     parsed_lrc = parsed_lrc.replace(a, chr(int(a[2:4])))

        parsed_lrc = lyric
        p = re.compile("\&#[0-9]{1,2};")
        ascii_list = set(re.findall(p, parsed_lrc))
        for a in ascii_list:
            parsed_lrc = parsed_lrc.replace(a, chr(int(a[2:4])))
        p = re.compile("\[.*\]")
        parsed_lrc = re.sub(p, "", parsed_lrc)

        l = parsed_lrc.split("\n")
        k = []
        for i in l:
            if i != "":
                k.append(i)

        return "\n".join(k)

    @staticmethod
    def __parse_path(path):
        p = re.compile(r'[\/*?"<>|]+')
        parsed_path = re.sub(p, "", path)
        return parsed_path


class SongList:
    """
    用于获取qq音乐歌单的类
    获得qq音乐歌单的listid的方法，使用网页版qq音乐，进入一张歌单的详情页面
    网址类似于"https://y.qq.com/n/yqq/playsquare/3628032628.html#stat=y_new.playlist.dissname"
    该网址中的字符串"3628032628"即为listid
    """
    def __init__(self, listid):
        self.list_id = listid
        headers = {
            "User-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
            "Host": "c.y.qq.com"
        }
        url = "https://c.y.qq.com/qzone/fcg-bin/fcg_ucc_getcdinfo_byids_cp.fcg" \
              "?type=1&json=1&utf8=1&onlysong=0&disstid={0}&format=jsonp&g_tk=5381" \
              "&jsonpCallback=playlistinfoCallback&loginUin=0&hostUin=0&format=jsonp" \
              "&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0".format(listid)

        headers['Referer'] = "https://y.qq.com/n/yqq/playsquare/{0}.html".format(listid)
        html_content = requests.get(url, headers=headers).text
        data = html_content.strip("playlistinfoCallback()")
        self.song_list = json.loads(data)['cdlist'][0]['songlist']

    def download_songs_all(self,archive=True, filepath=None):
        """
        下载歌单中的所有歌曲的所有内容，包含歌曲、歌词、歌曲封面
        :param filepath: 保存文件的路径
        :param archive: 是否将一首歌曲的内容归档到一个文件夹中
        :return:
        """
        if filepath is not None:
            root_path = filepath
        else:
            root_path = "Songs"
        root_path = self.__parse_path(root_path)
        if not os.path.exists(root_path):
            os.makedirs(root_path)

        for song_data in self.song_list:
            song_mid = song_data['songmid']
            song = Song(song_mid)
            if archive:
                file_path = root_path + "\\" + song.song_name
            else:
                file_path = root_path
            song.download_song(file_path)
            song.download_img(file_path)
            song.download_lyric(file_path)

    def download_songs(self,archive=False, filepath=None):
        """
        下载歌单中的所有歌曲的音乐
        :param filepath: 文件保存的路径
        :param archive: 是否将一首歌曲的内容归档到一个文件夹中
        :return:
        """
        if filepath is not None:
            root_path = filepath
        else:
            root_path = "Songs"
        root_path = self.__parse_path(root_path)
        if not os.path.exists(root_path):
            os.makedirs(root_path)

        for song_data in self.song_list:
            song_mid = song_data['songmid']
            song = Song(song_mid)
            if archive:
                file_path = root_path + "\\" + song.song_name
            else:
                file_path = root_path
            song.download_song(file_path)
            time.sleep(1)

    def download_song_info(self, filepath=None):
        song_info = []
        for i in range(len(self.song_list)):
            song_mid = self.song_list[i]['songmid']
            song = Song(song_mid)
            si = song.get_song_info()
            si['serial'] = i
            song_info.append(si)
        if filepath is None:
            filepath = "songinfo"
        filepath = self.__parse_path(filepath)
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        filename = filepath + "\\" + "songs.json"
        with open(filename, "a+", encoding="utf-8") as f:
            json.dump(song_info, f, ensure_ascii=False, indent=4)
            f.close()

    @staticmethod
    def __parse_path(path):
        p = re.compile(r'[\/*?"<>|]+')
        parsed_path = re.sub(p, "", path)
        return parsed_path


# 测试
# if __name__ == "__main__":
#     album = SongList("4757081140")
#     album.download_songs_all()
