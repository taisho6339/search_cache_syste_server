# coding: UTF-8
import json

import requests

GOOGLE_SEARCH_API = "https://www.googleapis.com/customsearch/v1"


def retrieve_snippet(query):
    list = []
    print('search_query:' + query)
    for i in range(2):
        params = {
            'key': '',
            'cx': '',
            'alt': 'json',
            'q': query,
            'start': str(1 + i * 10)
        }

        r = requests.get(GOOGLE_SEARCH_API, params=params)
        data = json.loads(r.content.decode(r.encoding))

        if 'error' in data or not r.ok:
            return []

        if 'items' not in data:
            return [query]

        items = data['items']
        for item in items:
            snippet = item['snippet']
            snippet.encode(r.encoding)
            list.append(snippet)

    return list

