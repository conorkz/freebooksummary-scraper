from bs4 import BeautifulSoup
import re
import requests
import paramiko
from datetime import datetime
import pytz
dir = r'your_sftp_directory'
roi = 'no info on the website'
x = 1
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('host', username='', password='')
sftp = ssh.open_sftp()
def sftp_exists(sftp, path):
    try:
        sftp.stat(path)
        return True
    except:
        return False
while True:
    if x == 66:
        break
    url = f'https://freebooksummary.com/our-library/page/{x}'
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(response.content, "html.parser")
    print(f'PAGE: {url}')
    x+=1
    for s in soup.find_all('a', class_='layout-content__inner-item'):
        link = s['href']
        if s.find('img'):
            img = s.find('img')['src']
        else:
            img = roi
        title = s.find(class_='layout-content__inner-item-name').text.strip()
        if s.find(class_='layout-content__inner-item-author'):
            author = s.find(class_='layout-content__inner-item-author').text.strip()
        else:
            author = roi
        respons = requests.get(link, headers={'User-Agent': 'Mozilla/5.0'})
        sorpa = BeautifulSoup(respons.content, "html.parser")
        print(link)
        if sorpa.find(class_='rghfcx', string='Original title'):
            orgtitle = sorpa.find(class_='rghfcx', string='Original title').find_next_sibling().text.strip()
        else:
            orgtitle = roi
        if sorpa.find(class_='rghfcx', string='Year'):
            year = sorpa.find(class_='rghfcx', string='Year').find_next_sibling().text.strip()
        else:
            year = roi
        if sorpa.find(class_='rghfcx', string='Genre'):
            genre = sorpa.find(class_='rghfcx', string='Genre').find_next_sibling().text.strip()
        else:
            genre = roi
        if sorpa.find(class_='rghfcx', string='Language'):
            lang = sorpa.find(class_='rghfcx', string='Language').find_next_sibling().text.strip()
        else:
            lang = roi
        if sorpa.find(class_='rghfcx', string='Characters'):
            char = sorpa.find(class_='rghfcx', string='Characters').find_next_sibling().text.strip()
        else:
            char = roi
        if sorpa.find(class_='rghfcx', string='Setting'):
            setting = sorpa.find(class_='rghfcx', string='Setting').find_next_sibling().text.strip()
        else:
            setting = roi
        if sorpa.find(class_='rghfcx', string='Published'):
            publ = sorpa.find(class_='rghfcx', string='Published').find_next_sibling().text.strip()
        else:
            publ = roi
        if sorpa.find(class_='rghfcx', string='ISBN'):
            isbn = sorpa.find(class_='rghfcx', string='ISBN').find_next_sibling().text.strip()
        else:
            isbn = roi
        if sorpa.find(class_='text show-more-height'):
            desc = sorpa.find(class_='text show-more-height').text.strip()
        else:
            desc = roi
        current_time = datetime.now(pytz.timezone('Europe/Berlin'))
        berlin = current_time.strftime('%Y-%m-%d %H:%M:%S %Z')
        adas = re.sub(r"[^\w\s]", "", title)
        folder_path = f'{dir}/{adas}'
        suffix = 1
        while sftp_exists(sftp, folder_path):
            folder_path = f'{dir}/{adas}({suffix})'
            suffix += 1
        sftp.mkdir(folder_path)
        if sorpa.select_one('.audiobook source'):
            mp3 = sorpa.select_one('.audiobook source')['src']
            respo = requests.get(mp3)
            with sftp.open(f'{folder_path}/{adas}.mp3', "wb") as fil:
                fil.write(respo.content)
        else:
            mp3 = roi
        with sftp.open(f'{folder_path}/{adas}.txt', "w") as file:
            file.write(f"Link: {link}\n")
            file.write(f"Book cover: {img}\n")
            file.write(f"Title: {title}\n")
            file.write(f"Original title: {orgtitle}\n")
            file.write(f"Author: {author}\n")
            file.write(f"Year: {year}\n")
            file.write(f"Genre: {genre}\n")
            file.write(f"Language: {lang}\n")
            file.write(f"Characters: {char}\n")
            file.write(f"Setting: {setting}\n")
            file.write(f"Published: {publ}\n")
            file.write(f"ISBN: {isbn}\n")
            file.write(f"Audiobook: {mp3}\n")
            file.write(f"Berlin time: {berlin}\n")
            file.write(f"Description: {desc}\n\n")
            if sorpa.select_one('.tax-content__post-title a'):
                nlink = sorpa.select_one('.tax-content__post-title a')['href']
                ntitle = sorpa.select_one('.tax-content__post-title a').text.strip()
                respon = requests.get(nlink, headers={'User-Agent': 'Mozilla/5.0'})
                sorp = BeautifulSoup(respon.content, "html.parser")
                if sorp.find(class_='sample-post__meta-views'):
                    views = sorp.find(class_='sample-post__meta-views').text
                else:
                    views = roi
                if sorp.find(class_='sample-post__meta-pages'):
                    pages = sorp.find(class_='sample-post__meta-pages').text
                else:
                    pages = roi
                if sorp.find(class_='sample-post__meta-words'):
                    words = sorp.find(class_='sample-post__meta-words').text
                else:
                    words = roi
                if sorp.find(class_='sample-post__meta-category sample-post__meta-category_mt'):
                    topics = sorp.find(class_='sample-post__meta-category sample-post__meta-category_mt').text
                else:
                    topics = roi
                file.write(f"Title: {ntitle}\n")
                file.write(f"{views}\n")
                file.write(f"{pages}\n")
                file.write(f"{words}\n")
                file.write(f"{topics}\n\n")
                if sorp.find(class_='sample-post__content-inner'):
                    for h in sorp.find(class_='sample-post__content-inner').find_all(['p']):
                        file.write(f"{h.text.strip()}\n\n")
sftp.close()
ssh.close()

    