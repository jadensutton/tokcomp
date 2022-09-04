import requests
from bs4 import BeautifulSoup

r = requests.get('https://www.tiktok.com/@andcarli/video/7122199535459306758',  headers={'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'})

soup = BeautifulSoup(r.text, 'lxml')

thumbnail_url = soup.find('div', {'class': 'tiktok-1nmqpes-DivBlurBackground eqrezik1'}).get('style').split('(')[1]
print(thumbnail_url)
