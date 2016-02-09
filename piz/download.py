from os import devnull
from subprocess import call
import re
from urlparse import urlparse

from bs4 import BeautifulSoup
import requests

from .exceptions import *


class Downloader:
    def __init__(self, url, verbose=False):
        self.verbose = verbose
        if verbose:
            print 'Checking to see that wget dependency has been met...'
        self.check_wget_dependency()
        if verbose:
            print 'wget dependency satisfied!'

        # Get session cookie and set class attributes
        self.domain = '{uri.scheme}://{uri.netloc}'.format(uri=urlparse(url))
        self.user_agent = 'Mozilla/5.0 (Windows NT 6.0) Gecko/20100101 Firefox/14.0.1'
        headers = {'user-agent': self.user_agent}
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        self.referer = url
        self.jsessionid = r.cookies['JSESSIONID']

        if verbose:
            print 'user-agent set to {user_agent}'.format(user_agent=self.user_agent)
            print 'referer is {referer}'.format(referer=self.referer)
            print 'jsessionid cookie set to {jsessionid}'.format(jsessionid=self.jsessionid)

        # Parse html and build download url from js script tag
        referer_html = r.text
        self.soup = BeautifulSoup(referer_html, 'html.parser')
        js = self.soup(text=re.compile('var e = function\(\)'))[0].parent.text.split('\n')
        try:
            a = int(re.search('\.a = (\d+);', js[1]).group(1))
            b = int(re.search('b = (\d+);', js[3]).group(1))
            e = eval(re.search('var e = .+ else \{return (.+)\}\};', js[10]).group(1))
            r_href = re.search('\.href = \"(.+)\"\+e\(\)\+\"(.+)\";', js[11])
            href = r_href.group(1) + str(e) + r_href.group(2)
        except AttributeError:
            raise ParseError('Error parsing js for download link. Contact the developer for correction.')
        self.download_url = '{domain}{dl_path}'.format(domain=self.domain, dl_path=href)

        if verbose:
            print 'download link set to {dl_url}'.format(dl_url=self.download_url)

    def download(self, song_title='Unknown Track'):
        print 'Downloading {song_title}...'.format(song_title=song_title)

        cmd = [
            'wget',
            self.download_url,
            '--referer=\'{referer}\''.format(referer=self.referer),
            '--cookies=off',
            '--header=Cookie: JSESSIONID={jsessionid}'.format(jsessionid=self.jsessionid),
            '--user-agent=\'{user_agent}\''.format(user_agent=self.user_agent)
        ]
        if self.verbose:
            r = call(cmd)
        else:
            dev_null = open(devnull, 'w')
            r = call(cmd, stdout=dev_null, stderr=dev_null)
            dev_null.close()
        if r == 0:
            print 'Download complete!'
        else:
            raise DownloadSubprocessError('Error during download. wget returned non-zero exit status.')

    def get_file_size(self):
        return float(self.soup(text=re.compile('Size:'))[0].next.next.text[0:-3])

    @staticmethod
    def check_wget_dependency():
        dev_null = open(devnull, 'w')
        cmd = ['wget', '-h']
        r = call(cmd, stdout=dev_null, stderr=dev_null)
        dev_null.close()
        if r == 0:
            return
        elif r == 126:
            raise DependencyNotSatisfiedError('Denied access when attempting to run wget. Check permissions.')
        elif r == 127:
            raise DependencyNotSatisfiedError('wget command not found. Is the wget installed or on your path?')
        else:
            raise DownloadSubprocessError('wget returned non-zero exit status.')
