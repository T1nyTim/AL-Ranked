from typing import TypedDict

import csv
import requests
from requests.exceptions import HTTPError


BASE_API_URL = 'https://graphql.anilist.co'


class Media(TypedDict, total=False):
    id: int
    title: str
    rank: int


def post_graphql_request(url: str, json_data: dict) -> dict:
    try:
        response = requests.post(url, json=json_data)
        response.raise_for_status()
        return response.json()
    except HTTPError as error:
        print(f"Error: {error}")
        if hasattr(error.response, "request") and error.response.request:
            print(f"Request Headers: {error.response.request.headers}")

def get_top_media(media_type: str, media_status: None | str = None, country: None | str = None, genre: None | str = None) -> dict[int, Media]:
    variables = {"perPage": 50}
    ranked_media = {}
    sort_criteria = "POPULARITY_DESC" if media_status == "NOT_YET_RELEASED" else "SCORE_DESC"
    for page in [1, 2]:
        variables["page"] = page
        query_parts = [f"type: {media_type}"]
        if media_status:
            query_parts.append(f"status: {media_status}")
        if country:
            query_parts.append(f"countryOfOrigin: {country}")
        if genre:
            query_parts.append(f"genre: \"{genre}\"")
        query_filters = ", ".join(query_parts)
        query = f'''
        query ($page: Int, $perPage: Int) {{
          Page(page: $page, perPage: $perPage) {{
            media({query_filters}, sort: {sort_criteria}) {{
              id
              title {{
                romaji
              }}
              averageScore
            }}
          }}
        }}
        '''
        json_data = {"query": query, "variables": variables}
        data = post_graphql_request(BASE_API_URL, json_data)
        for item in data["data"]["Page"]["media"]:
            ranked_media[item["id"]] = {
                "id": item["id"],
                "title": item["title"]["romaji"],
                "rank": len(ranked_media) + 1
            }
    return ranked_media

def new_csv(rankings: dict[str, Media]) -> None:
    for rank_type in rankings:
        csv_name = rank_type + ".csv"
        with open(csv_name, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["id", "title", "rank"])
            for media in rankings[rank_type]:
                id = rankings[rank_type][media]["id"]
                title = rankings[rank_type][media]["title"]
                rank = rankings[rank_type][media]["rank"]
                writer.writerow([id, title, rank])

def main():
    rankings = {}
    rankings['All Anime'] = get_top_media(media_type='ANIME')
    rankings['All Manga'] = get_top_media(media_type='MANGA')
    rankings['Releasing Anime'] = get_top_media(media_type='ANIME', media_status='RELEASING')
    rankings['Unreleased Anime'] = get_top_media(media_type='ANIME', media_status='NOT_YET_RELEASED')
    rankings['Releasing Manga'] = get_top_media(media_type='MANGA', media_status='RELEASING')
    rankings['Unreleased Manga'] = get_top_media(media_type='MANGA', media_status='NOT_YET_RELEASED')
    rankings['All Manhwa'] = get_top_media(media_type='MANGA', country='KR')
    rankings['All Hentai'] = get_top_media(media_type='ANIME', genre='hentai')
    rankings['All Hentai Manga'] = get_top_media(media_type='MANGA', genre='hentai')
    new_csv(rankings)


if __name__ == '__main__':
    main()