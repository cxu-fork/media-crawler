import time
import os
import requests
import re
import music_tag

# referer can be any site to get through verification.
headers = {
    'referer': 'https://kg.qq.com/index-pc.html',
}

def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)

class Karaoke(object):
    def __init__(self, uid: str) -> None:
        super().__init__()
        self.songs_id = []
        self.songs_name = []
        self.songs_date = []
        self.get_songs(uid)
    
    def get_songs(self, uid: str) -> list:
        url = 'https://node.kg.qq.com/cgi/fcgi-bin/kg_ugc_get_homepage?type=get_uinfo&start=%d&num=8&share_uid=%s&inCharset=utf-8&outCharset=utf-8'
        res = requests.get(url % (1, uid), headers=headers)
        if res.status_code != 200:
            print(res.status_code)
            return

        res = res.text
        self.artist = re.search(r'(?<="nickname": ").*?(?=",)', res).group()
        self.path = 'data/' + self.artist
        num = re.search(r'(?<="ugc_total_count":).+?(?=,)', res).group()
        total = (int(num)+ 7) // 8

        for start in range(1, total + 1):
            res = requests.get(url % (start, uid), headers=headers).text
            self.songs_id += re.findall(r'(?<="shareid": ").*?(?=",)', res)
            self.songs_name += re.findall(r'(?<="title": ").*?(?=",)', res)
            self.songs_date += re.findall(r'(?<="time": ).*?(?=,)', res)

        print(self.songs_name)
        if '' in self.songs_name:
            index = []
            for i in range(len(self.songs_name)):
                if self.songs_name[i] == '':
                   index.append(i+1) 
            for i in index:
                del self.songs_name[i]

        print(self.songs_name)
        print('found %d songs.' % len(self.songs_id))

    def scrawlMedia(self):
        mkdir(self.path)

        url = 'https://node.kg.qq.com/cgi/fcgi-bin/fcg_get_play_url?shareid=%s'
        for song_id, song_name, song_date in zip(self.songs_id, self.songs_name, self.songs_date):
#             epoch = song_date
#             song_date_ = time.strftime("%Y-%m-%d", time.localtime(int(song_date)))
            self.dlSong(url % song_id, song_name, time.strftime("%Y-%m-%d", time.localtime(int(song_date))), song_date)
        
    def dlSong(self, url, name, date, epoch):
        try:
            fname = f'{date}-{name}-{epoch}.m4a'
            fname = re.sub(r'[\/:*?"<>|]', '_', fname)
            fname = fname.strip().replace('\\','')
            fname = re.sub(r'\s+', ' ', fname)
            path_to_file = self.path + '/' + fname
            if os.path.exists(path_to_file): return

            song = requests.get(url)
            if song:
                print(fname)
                with open(path_to_file, 'wb') as f:
                    f.write(song.content)

                file = music_tag.load_file(path_to_file)
                file['title'] = name
                file['artist'] = self.artist
                file['year'] = date
                file.save()
        except:
            print('try download the song again...')
            self.dlSong(url, fname, date, epoch)

if __name__ == '__main__':
    uid = input('Please input the karaoke share uid of the user: ')
    karaoke = Karaoke(uid)

    start_time = time.time()
    karaoke.scrawlMedia()
    end_time = time.time()

    print("All finished in %ds!" % (end_time-start_time))
    os.system('pause')
