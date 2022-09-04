import requests

from flask import session

class ThumbnailService:
    def __init__(self, beautiful_soup):
        self.beautiful_soup = beautiful_soup

    def get_one(self, share_url: str) -> dict:
        if not self.validate_tiktok_url(share_url):
            print('backend.thumbnails.service.py - get_one() - Input validation failed.')
            return {'error': 'Invalid input'}, 400

        try:
            r = requests.get(share_url, headers={'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'})
            soup = self.beautiful_soup(r.text, 'lxml')
            thumbnail_url = soup.find('div', {'class': 'tiktok-1nmqpes-DivBlurBackground eqrezik1'}).get('style').split('(')[1][:-1]
        except Exception as e:
            print('backend.thumbnails.service.py - get_one() - {}'.format(e))
            raise RuntimeError('Internal server error.')

        return thumbnail_url, 200

    def validate_tiktok_url(self, url: str):
        url_sections = url.split('/')
        if len(url_sections) != 6:
            return False

        if url_sections[0] != 'https:' or url_sections[2] != 'www.tiktok.com' or url_sections[3][0] != '@' or url_sections[4] != 'video':
            return False

        return True
