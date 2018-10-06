from qqMusicScrapy import *
import json
import os
import re

# 4454496076
# 3628032628
# sl = SongList("4454496076")
#sl.download_songs_all(True, "E:\大三课程\数字媒体资源管理\Songs")
# sl.download_song_info()
# s = Song("001Q3Rlo428b8g")
# s.download_origin_lyric("E:\PingendoPro\MusicManagement\static\songs")
# print(s.get_song_info())
# f = open("song/l_o.txt", "r", encoding="utf-8")
# for line in f:
#     p = re.compile("\[.*\]")
#     time = re.match(p, line)
#     print(time.group(0))

f = open("songinfo/songs_data.json", "r", encoding="utf-8")
data = json.load(f)
for l in data['like']:
    s = Song(l['songmid'])
    s.download_origin_lyric("E:\PingendoPro\MusicManagement\static\songs\Like\\" + l['songname'])
    s.download_lyric("E:\PingendoPro\MusicManagement\static\songs\Like\\" + l['songname'])

for dl in data['dislike']:
    s = Song(dl['songmid'])
    s.download_origin_lyric("E:\PingendoPro\MusicManagement\static\songs\Dislike\\" + dl['songname'])
    s.download_lyric("E:\PingendoPro\MusicManagement\static\songs\Dislike\\" + dl['songname'])
f.close()

