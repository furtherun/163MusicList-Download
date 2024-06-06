#!/usr/bin/python3
# -*- coding: utf-8 -*-
import requests
import threading
import os
import sys
import re
import wx
import wx.xrc
from bs4 import BeautifulSoup
from mutagen.easyid3 import EasyID3


class MyFrame1 (threading.Thread, wx.Frame):
    musicData = []
    # user_agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36'
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.62"

    def __init__(self, threadID, name, counter):
        wx.Frame.__init__(self, None, id=wx.ID_ANY, title=u"网易云音乐歌曲批量下载", pos=wx.DefaultPosition, size=wx.Size(
            540, 600), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        self.SetBackgroundColour(
            wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))

        bSizerBase = wx.BoxSizer(wx.VERTICAL)
        bSizerInfo = wx.BoxSizer(wx.VERTICAL)
        bSizerUrl = wx.BoxSizer(wx.HORIZONTAL)
        bSizerDir = wx.BoxSizer(wx.HORIZONTAL)
        # bSizerCheck = wx.BoxSizer(wx.HORIZONTAL)

        """
        url boxSizer
        """

        self.url_staticText = wx.StaticText(
            self, wx.ID_ANY, u"网址", wx.DefaultPosition, wx.DefaultSize, 0)
        self.url_staticText.Wrap(-1)

        self.url_staticText.SetFont(wx.Font(
            13, wx.FONTFAMILY_DECORATIVE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString))

        bSizerUrl.Add(self.url_staticText, 0, wx.ALL, 5)

        self.url_text = wx.TextCtrl(
            self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(300, -1), 0)
        bSizerUrl.Add(self.url_text, 0, wx.ALL, 5)

        self.down_button = wx.Button(
            self, wx.ID_ANY, u"下载歌单", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizerUrl.Add(self.down_button, 0, wx.ALL, 5)

        self.fast_button = wx.Button(
            self, wx.ID_ANY, u"快速下载", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizerUrl.Add(self.fast_button, 0, wx.ALL, 5)

        """
        dir boxSizer    
        """

        self.dir_staticText = wx.StaticText(
            self, wx.ID_ANY, u"目录", wx.DefaultPosition, wx.DefaultSize, 0)
        self.dir_staticText.Wrap(-1)

        self.dir_staticText.SetFont(wx.Font(
            13, wx.FONTFAMILY_DECORATIVE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString))

        bSizerDir.Add(self.dir_staticText, 0, wx.ALL, 5)

        self.dir_text = wx.TextCtrl(
            self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(300, -1), 0)
        bSizerDir.Add(self.dir_text, 0, wx.ALL, 5)

        self.dir_button = wx.Button(
            self, wx.ID_ANY, u"选择目录", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizerDir.Add(self.dir_button, 0, wx.ALL, 5)

        self.restart_button = wx.Button(
            self, wx.ID_ANY, u"重新启动", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizerDir.Add(self.restart_button, 0, wx.ALL, 5)

        bSizerInfo.Add(bSizerUrl, 1, wx.EXPAND, 4)
        bSizerInfo.Add(bSizerDir, 1, wx.EXPAND, 4)

        # 默认下载目录
        self.dir_text.SetValue('D:\\MusicBox\\')

        self.output_text = wx.TextCtrl(self, wx.ID_ANY,
                                       '''
        简 易 说 明

        网易云音乐歌单（专辑）下载，网页中复制URL， \n
        歌单的格式如下， \n
        https://music.163.com/#/playlist?id=xxxxxxxxxx \n
        专辑的格式如下， \n
        https://music.163.com/#/album?id=xxxxxxxxxxxxx \n

        “下载歌单”和“快速下载”的区别是写入信息不同，\n
        “下载歌单”命名格式：[歌名] - [歌手].mp3，\n
        并添加文件的标题、参与创作的艺术家和唱片集信息。 \n
        “快速下载”命名格式：[歌名].mp3， \n
        只添加文件的标题，解析信息时间少。 \n

        最终下载速度和需要的时间，取决于网速等因素。 \n

        默认保存目录： D:\MusicList，目录不存在时会自动创建， \n

        线程只能执行一次，下载后如需重新下载其他歌单、专辑， \n
        请点击“重新启动”按钮。 \n

        可多开下载同个歌单或者不同歌单。\n

        更多说明，请看说明文档。
        -------------------------------------------------------\n
        原作者 - ccphamy \n
        修改 - furtherun - 2023.10 \n
        -------------------------------------------------------\n
        ''', wx.DefaultPosition, wx.Size(500, 520), wx.TE_MULTILINE)

        bSizerBase.Add(bSizerInfo, 0, wx.EXPAND, 4)

        """
        把“重新启动”的按钮移动到“选择目录”的后面
        """
        # self.restart_button = wx.Button(
        #     self, wx.ID_ANY, u"重新启动", wx.DefaultPosition, wx.DefaultSize, 0)
        # bSizerBase.Add(self.restart_button, 0, wx.ALL, 5)

        """
        check box
        """
        self.use_trck = wx.CheckBox(self, label='命名添加音轨号前缀')
        bSizerBase.Add(self.use_trck, 0, wx.ALL, 5)
        self.auto_subdir = wx.CheckBox(self, label='自动创建子目录')
        bSizerBase.Add(self.auto_subdir, 0, wx.ALL, 5)

        bSizerBase.Add(self.output_text, 0, wx.ALL, 5)

        self.SetSizer(bSizerBase)
        self.Layout()

        self.Centre(wx.BOTH)

        # Connect Events
        self.down_button.Bind(
            wx.EVT_BUTTON, lambda event: self.downloadMusic(event, False))
        self.fast_button.Bind(
            wx.EVT_BUTTON, lambda event: self.downloadMusic(event, True))
        self.dir_button.Bind(wx.EVT_BUTTON, self.selectSaveDir)
        self.restart_button.Bind(wx.EVT_BUTTON, self.restart)
        self.use_trck.Bind(wx.EVT_CHECKBOX, self.use_trck_checked)
        self.auto_subdir.Bind(wx.EVT_CHECKBOX, self.auto_subdir_checked)

        # 多线程
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def __del__(self):
        pass

    def run(self):
        self.output_text.AppendText(u"\n 歌曲获取成功，任务线程开启 \n")
        # print("music data = ", self.musicData)
        self.get(self.musicData)

    def restart(self, event):
        self.output_text.AppendText(u"\n 任务线程重启 \n")
        python = sys.executable
        os.execl(python, python, * sys.argv)

    def downloadMusic(self, event, useFast=False):
        self.musicData = []
        if useFast:
            self.musicData = self.getMusicDataFast(
                self.url_text.GetValue().replace("#/", ""))
        else:
            self.musicData = self.getMusicData(
                self.url_text.GetValue().replace("#/", ""))

        if len(self.musicData) > 1:
            self.start()

    def get(self, musicData, useFast=False):
        """
        Downloads mp3 files from a list of songs.

        Args:
            musicData (list): A list of dictionaries containing song information.

        Returns:
            None
        """
        succ_num = 0
        fail_num = 0
        skip_num = 0
        trck_num = 0

        rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
        for x in musicData:
            x['title'] = re.sub(rstr, "_", x['title'])

            music_id = x['id']
            music_title = x['title']
            music_artist = x.get('artist', [])
            music_album = x.get('album', [])
            trck_num += 1

            save_dir = self.getSaveDir()

            if self.auto_subdir.GetValue():
                if len(music_artist) != 0:
                    save_dir = save_dir + '\\' + music_album[0] + '\\'
                else:
                    save_dir = save_dir + '\\' + music_id + '\\'

            if not os.path.exists(save_dir):
                try:
                    os.makedirs(save_dir)
                except:
                    wx.MessageBox('创建目录失败，请检查目录是否存在或是否有权限创建目录！',
                                  '错误', wx.OK | wx.ICON_ERROR)
                    exit(0)

            if not useFast and len(music_artist) != 0:
                music_file = save_dir + \
                    music_title + ' - ' + ', '.join(music_artist) + '.mp3'
            else:
                music_file = save_dir + music_title + '.mp3'

            if self.use_trck.GetValue():
                music_file = save_dir + str(trck_num) + ' ' + music_file

            # print(music_file)

            if not os.path.exists(music_file):
                # self.output_text.AppendText(
                #     '***** ' + music_title + ' ***** 正在下载...\n')

                url = 'http://music.163.com/song/media/outer/url?id=' + \
                    music_id + '.mp3'
                try:
                    self.saveFile(url, music_file)

                except:
                    fail_num += 1
                    self.output_text.SetDefaultStyle(wx.TextAttr(wx.RED))
                    self.output_text.AppendText(
                        music_title + '下载失败 ! \n')
                    self.output_text.SetDefaultStyle(wx.TextAttr(wx.BLACK))
                    continue

                succ_num += 1
                self.output_text.AppendText(
                    ' [ ' + str(succ_num) + ' ] ' + music_title + ' 下载成功 ~\n')

                try:
                    audio = EasyID3(music_file)
                    audio['title'] = music_title
                    audio['artist'] = music_artist
                    audio['album'] = music_album
                    audio['tracknumber'] = str(trck_num)
                    audio.save()
                except:
                    self.output_text.AppendText(
                        ' [ * ] ' + music_title + ' 歌曲信息写入失败 ~\n')
                    """
                    大概率是因为该歌曲是付费歌曲，因此把无效的下载删除
                    """
                    os.remove(music_file)
                    succ_num -= 1
                    fail_num += 1
            else:
                self.output_text.AppendText(
                    ' [ * ] ' + music_title + ' 已经存在，跳过下载 \n')
                skip_num += 1

        self.output_text.AppendText(
            '--------------------------------------------------\n')

        if succ_num > 0:
            self.output_text.AppendText(
                '成功下载 ' + str(succ_num) + ' 首新音乐! \n')

        if fail_num > 0:
            self.output_text.SetDefaultStyle(wx.TextAttr(wx.RED))
            self.output_text.AppendText(
                '失败下载 ' + str(fail_num) + ' 首音乐! \n')

        if skip_num > 0:
            self.output_text.AppendText(
                '跳过下载 ' + str(skip_num) + ' 首已存在的音乐! \n')

        self.output_text.AppendText(
            '--------------------------------------------------\n')
        pass

    def getMusicDataFast(self, url) -> list:
        """
        This method takes in a URL and only returns the music id & name.
        Each dictionary contains the following keys:
        - id: the ID of the music
        - name: the name of the music
        Args:
        - url (str): the URL of the music page

        Returns:
        - tempArr (list): a list of dictionaries containing information about the music
        """
        headers = {'User-Agent': self.user_agent}

        webData = requests.get(url, headers=headers).text
        soup = BeautifulSoup(webData, 'lxml')
        find_list = soup.find('ul', class_="f-hide").find_all('a')

        tempArr = []
        for a in find_list:
            music_id = a['href'].replace('/song?id=', '')
            music_title = a.text
            tempArr.append({'id': music_id, 'title': music_title})
        return tempArr

    def getMusicData(self, url) -> list:
        """
        This method takes in a URL and returns a list of dictionaries containing information about the music.
        Each dictionary contains the following keys:
        - id: the ID of the music
        - name: the name of the music
        - artist: the name of the artist
        - album: the name of the album

        Args:
        - url (str): the URL of the music page

        Returns:
        - tempArr (list): a list of dictionaries containing information about the music
        """
        headers = {'User-Agent': self.user_agent}

        webData = requests.get(url, headers=headers).text
        soup = BeautifulSoup(webData, 'lxml')
        find_list = soup.find('ul', class_="f-hide").find_all('a')

        tempArr = []
        for a in find_list:
            music_id = a['href'].replace('/song?id=', '')
            music_title = a.text
            # 访问音乐详情页面，解析出歌手、专辑信息
            detail_url = 'https://music.163.com/song?id=' + music_id
            detail_data = requests.get(detail_url, headers=headers).text
            detail_soup = BeautifulSoup(detail_data, 'lxml')

            """
            考虑可能有多名歌手、艺术家，其实不太可能有多张专辑，不过还是采用相同的处理方式
            """

            artist_tags = detail_soup.find_all(
                'a', {'href': lambda href: href and href.startswith('/artist?id='), 'class': 's-fc7'})
            artist_names = [artist_tag.text for artist_tag in artist_tags]

            album_tags = detail_soup.find_all(
                'a', {'href': lambda href: href and href.startswith('/album?id='), 'class': 's-fc7'})
            album_names = [album_tag.text for album_tag in album_tags]

            tempArr.append({'id': music_id, 'title': music_title,
                           'artist': artist_names, 'album': album_names})
            """
            single artist & album case
            """
            # artist_tag = detail_soup.find(
            #     'a', href=lambda href: href and href.startswith('/artist?id='))
            # album_tag = detail_soup.find(
            #     'a', href=lambda href: href and href.startswith('/album?id='))

            # artist_name = artist_tag.text if artist_tag else ''
            # album_name = album_tag.text if album_tag else ''

            # tempArr.append({'id': music_id, 'title': music_title,
            #                'artist': artist_name, 'album': album_name})

        return tempArr

    def selectSaveDir(self, event):
        """
        Opens a dialog box to allow the user to select a directory to save downloaded files to.
        Updates the download_dir attribute and the text in the dir_text control with the selected directory.
        """
        dlg = wx.DirDialog(self, "选择下载目录", style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            save_dir = dlg.GetPath()
            self.dir_text.SetValue(save_dir)
        dlg.Destroy()

    def getSaveDir(self) -> str:
        """
        Returns the save directory for downloaded files.

        Returns:
        str: The save directory for downloaded files.
        """
        save_dir = self.dir_text.GetValue()
        if not save_dir.endswith('/') or not save_dir.endswith('\\'):
            save_dir = save_dir + '\\'
        return save_dir

    def saveFile(self, url, path):
        """
        Downloads a file from the specified URL and saves it to the specified path.

        Args:
            url (str): The URL of the file to download.
            path (str): The path to save the downloaded file to.

        Returns:
            None
        """
        headers = {'User-Agent': self.user_agent,
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8', 'Upgrade-Insecure-Requests': '1'}
        response = requests.get(url, headers=headers)

        with open(path, 'wb') as f:
            f.write(response.content)
            f.flush()

    def use_trck_checked(self, event) -> bool:
        # if self.use_trck.GetValue():
        #     self.output_text.AppendText(u"\n 记录专辑中的音轨号 \n")
        # else:
        #     self.output_text.AppendText(u"\n 不记录专辑中的音轨号 \n")

        return self.use_trck.GetValue()

    def auto_subdir_checked(self, event) -> bool:
        return self.auto_subdir.GetValue()


def main():
    app = wx.App(False)
    frame = MyFrame1(1, "Thread-1", 1)
    frame.Show(True)
    # start the applications
    app.MainLoop()


if __name__ == '__main__':
    main()
