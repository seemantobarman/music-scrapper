from bs4 import BeautifulSoup as soup
import urllib.request
import os.path
import re
import ssl
import progressbar
import os

#Progressbar Class
class MyProgressBar():
    def __init__(self):
        self.pbar = None

    def __call__(self, block_num, block_size, total_size):
        if not self.pbar:
            self.pbar=progressbar.ProgressBar(maxval=total_size,widgets=[progressbar.Bar('#', '[', ']'), ' ',progressbar.Percentage(), ' ',progressbar.ETA(), ' ',progressbar.FileTransferSpeed()])
            self.pbar.start()
        
        downloaded = block_num * block_size
        if downloaded < total_size:
            self.pbar.update(downloaded)
        else:
            self.pbar.finish()
            print("\n")

def force_download(filelink,filename):
    try:
        urllib.request.urlretrieve(filelink, filename+".mp3", MyProgressBar())
    except urllib.error.ContentTooShortError:
        print("__DOWNLOAD FAILED__")
        print("___Retrying___\n")
        force_download(filelink,filename)

webpagelink = "https://www.music.com.bd/download/browse/I/"
ssl._create_default_https_context = ssl._create_unverified_context
wp = urllib.request.urlopen(webpagelink)
pw = wp.read()
page_soup = soup(pw, "html.parser")

allAncorTags = page_soup.select("div[class=panel-body] > div[class=list-group] > a[class=list-group-item]")

def RecursivelyGetDownloadLinks(page_soup):
    allAncorTags = page_soup.select("div[class=panel-body] > div[class=list-group] > a[class=list-group-item]")

    for element in allAncorTags[1:]:
        if ".mp3" in element.get('href'):
            SongLink = "http://"+element.get('href')[2:].replace(" ","%20")

            wp = urllib.request.urlopen(SongLink)
            pw = wp.read()
            download_soup = soup(pw, "html.parser")

            DownloadLink = download_soup.find("a",{"class":"btn btn-default btn-lg btn-block btn-dl"}).get('href').replace(" ","%20")
            FileName = download_soup.find_all("h3", {"class": "panel-title"})[1].text.strip()
            FileName = re.sub(r"[\"#/@;:<>{}`+=~|!?,]", "", FileName)
            
            print("Downloading-> "+FileName)

            Path = page_soup.find_all("h3", {"class": "panel-title"})[1]
            Path = Path.text.strip().split(" >")[:-1]
            Path = r"".join(["/"+str(item).strip() for item in Path])
            Path = Path[1:]

            if not os.path.exists(Path):
                os.makedirs(Path)
            
            force_download(DownloadLink,Path+"/"+FileName)

        elif ".zip" in element.get('href'):
            print("ZIP FILE FOUND")
        else:
            Link = element.get('href')
            wp = urllib.request.urlopen(Link)
            pw = wp.read()
            page_soup = soup(pw, "html.parser")

            RecursivelyGetDownloadLinks(page_soup)


RecursivelyGetDownloadLinks(page_soup);