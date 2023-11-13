"""Fetches and ranks media from AniList API, exporting the data to CSV files.

This module provides functionality to interact with the AniList GraphQL API to retrieve and rank
media based on various criteria such as type, status, country of origin, and genre. The media data
is then written to CSV files for each category.

Classes:
    Media(TypedDict): A type definition for media items including attributes like id, title, and
        rank.

Functions:
    post_graphql_request(url: str, json_data: dict) -> dict:
        Sends a POST request to the specified GraphQL API URL with provided JSON data.
    get_top_media(
        media_type: str, media_status: None | str, country: None | str, genre: None | str
    )-> dict[int, Media]):
        Fetches and ranks top media from AniList API based on the specified media type, status,
        country of origin, or genre.
    new_csv(rankings: dict[str, Media]) -> None:
        Writes the ranked media data into CSV files, one for each category in the rankings
        dictionary.
    main() -> None:
        Main function to orchestrate fetching and ranking media data and then writing it to CSV
        files.

The script interacts with AniList's GraphQL API to retrieve media data, which includes anime and
manga titles, and ranks them based on their scores, popularity, or other criteria. The results are
then exported to CSV files for various categories like All Anime, All Manga, Releasing Anime, etc.

Usage:
    Run the script to fetch media data from AniList and write the ranked lists to CSV files in the
    current directory.
"""
import csv
from pathlib import Path
from typing import TypedDict

import requests
from requests.exceptions import HTTPError

BASE_API_URL = "https://graphql.anilist.co"


class Media(TypedDict):
    """Represents a media item.

    Fields:
    - id: An integer field that represents the unique identifier of the media item.
    - title: A string field that represents the title of the media item.
    - rank: An integer field that represents the rank of the media item.
    """

    id: int
    title: str
    rank: int


def post_graphql_request(url: str, json_data: dict) -> dict:
    """Sends a GraphQL request to a specified URL.

    Sends a GraphQL request to a specified URL with the given JSON data and returns the response as
    a dictionary.

    Args:
        url (str): The URL to which the GraphQL request will be sent.
        json_data (dict): The JSON data that will be included in the request body.

    Returns:
        dict: The response from the GraphQL request as a dictionary.
    """
    try:
        response = requests.post(url, json=json_data, timeout=10)
        response.raise_for_status()
        return response.json()
    except HTTPError as error:
        print(f"Error: {error}")
        if hasattr(error.response, "request") and error.response.request:
            print(f"Request Headers: {error.response.request.headers}")


def get_top_media(
    media_type: str,
    media_status: None | str = None,
    country: None | str = None,
    genre: None | str = None,
) -> dict[int, Media]:
    """Retrieves and ranks media based on various criteria such as media type, status, etc.

    Args:
        media_type (str): The type of media to retrieve and rank.
        media_status (None | str, optional): The status of the media. Defaults to None.
        country (None | str, optional): The country of origin of the media. Defaults to None.
        genre (None | str, optional): The genre of the media. Defaults to None.

    Returns:
        dict[int, Media]: A dictionary containing the ranked media items, where the keys are the
            media IDs and the values are dictionaries containing the media ID, title, and rank.
    """
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
            query_parts.append(f'genre: "{genre}"')
        query_filters = ", ".join(query_parts)
        query = f"""
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
        """
        json_data = {"query": query, "variables": variables}
        data = post_graphql_request(BASE_API_URL, json_data)
        for item in data["data"]["Page"]["media"]:
            ranked_media[item["id"]] = {
                "id": item["id"],
                "title": item["title"]["romaji"],
                "rank": len(ranked_media) + 1,
            }
    return ranked_media


def new_csv(rankings: dict[str, Media]) -> None:
    """Create a CSV file with the rankings data.

    Args:
        rankings (dict): A dictionary containing the rankings data. The keys represent the different
            rankings categories, and the values are the results of the 'get_top_media' function.

    Returns:
        dict: A dictionary containing the rankings data with the 'id', 'title', and 'rank'
            information for each item.
    """
    for rank_type in rankings:
        csv_name = rank_type + ".csv"
        with Path(csv_name).open("w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["id", "title", "rank"])
            for media in rankings[rank_type]:
                media_id = rankings[rank_type][media]["id"]
                title = rankings[rank_type][media]["title"]
                rank = rankings[rank_type][media]["rank"]
                writer.writerow([media_id, title, rank])


def main() -> None:
    """Orchestrates the fetching, ranking, and CSV export of media data from the AniList API.

    This function serves as the entry point for the script. It calls the 'get_top_media' function
    with different parameters to fetch various categories of media, including anime and manga, based
    on type, status, country of origin, and genre. The retrieved media data is then ranked and
    stored in a dictionary. Finally, it calls 'new_csv' to export these rankings into separate CSV
    files for each category.

    Usage:
        Called when the script is executed directly. It requires no arguments and returns nothing.
        Generates CSV files in the current directory with ranked media data.
    """
    rankings = {}
    rankings["All Anime"] = get_top_media(media_type="ANIME")
    rankings["All Manga"] = get_top_media(media_type="MANGA")
    rankings["Releasing Anime"] = get_top_media(media_type="ANIME", media_status="RELEASING")
    rankings["Unreleased Anime"] = get_top_media(
        media_type="ANIME",
        media_status="NOT_YET_RELEASED",
    )
    rankings["Releasing Manga"] = get_top_media(media_type="MANGA", media_status="RELEASING")
    rankings["Unreleased Manga"] = get_top_media(
        media_type="MANGA",
        media_status="NOT_YET_RELEASED",
    )
    rankings["All Manhwa"] = get_top_media(media_type="MANGA", country="KR")
    rankings["All Hentai"] = get_top_media(media_type="ANIME", genre="hentai")
    rankings["All Hentai Manga"] = get_top_media(media_type="MANGA", genre="hentai")
    new_csv(rankings)


if __name__ == "__main__":
    main()
