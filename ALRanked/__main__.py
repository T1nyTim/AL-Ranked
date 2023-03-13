from typing import TypedDict

import requests
from requests.exceptions import HTTPError


BASE_API_URL = 'https://graphql.anilist.co'


class Media(TypedDict, total=False):
    id: int
    title: str
    rank: int


def get_html_request(url: str, params: dict) -> dict:
    try:
        response = requests.get(url, params)
        response.raise_for_status()
        return response.json()
    except HTTPError:
        print(f"Error: {HTTPError}")
        print(f"Request Headers: {HTTPError.request.headers}")

def get_top_media(media_type: str) -> dict[int, Media]:
    variables = {}
    ranked_media: Media = {}
    variables['page'] = 1
    variables['perPage'] = 100
    query = '''
        query ($page: Int, $perPage: Int) {
            Page(page: $page, perPage: $perPage) {
                media(type: ''' + media_type + ''', sort: SCORE_DESC) {
                    id
                    title {
                        romaji
                    }
                    averageScore
                }
            }
        }
    '''
    params = {'query': query, 'variables': variables}
    data = get_html_request({BASE_API_URL}, params)

def get_top_media_by_status():
    pass

def get_top_media_by_country():
    pass

def get_top_media_by_genre():
    pass

def new_csv():
    pass

def main():
    rankings = {}
    rankings['All Anime'] = get_top_media('ANIME')
    rankings['All Manga'] = get_top_media('MANGA')
    rankings['Releasing Anime'] = get_top_media_by_status('ANIME', 'RELEASING')
    rankings['Unreleased Anime'] = get_top_media_by_status('ANIME', 'NOT_YET_RELEASED')
    rankings['Releasing Manga'] = get_top_media_by_status('MANGA', 'RELEASING')
    rankings['Unreleased Manga'] = get_top_media_by_status('MANGA', 'NOT_YET_RELEASED')
    rankings['All Manhwa'] = get_top_media_by_country('MANGA', 'KR')
    rankings['All Hentai'] = get_top_media_by_genre('ANIME', 'hentai')
    rankings['All Hentai Manga'] = get_top_media_by_genre('MANGA', 'hentai')
    new_csv(rankings)


if __name__ == '__main__':
    main()