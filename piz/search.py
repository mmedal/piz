from os import environ

from googleapiclient.discovery import build

from .exceptions import *


class Searcher:
    def __init__(self, api_key=environ.get('PIZ_GOOGLE_API_KEY'), cx=environ.get('PIZ_GOOGLE_SEARCH_CX')):
        if api_key is None or cx is None:
            raise UserMisconfigurationError('You must have both PIZ_GOOGLE_API_KEY and PIZ_GOOGLE_SEARCH_CX set as '
                                            'environment variables in your shell.')
        self.api_key = api_key
        self.cx = cx
        self.service = build('customsearch', 'v1', developerKey=api_key)

    def search(self, query):
        r = self.service.cse().list(
            q=query,
            cx=self.cx
        ).execute()
        if r['queries']['request'][0]['totalResults'] == '0':
            raise NoResultsFound('No download options found for "{query}"'.format(query=query))
        else:
            return [{
                        'track_title': x['pagemap']['metatags'][0]['og:title'],
                        'referer': x['pagemap']['metatags'][0]['og:url']
                    } for x in r['items']]
