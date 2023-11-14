# AniList Media Ranker

## Introduction
AniList Media Ranker is a Python application designed to fetch and rank media (anime and manga) from the AniList GraphQL API. The application ranks media based on various criteria, such as type, status, country of origin, and genre, and exports these rankings into CSV files for easy analysis and record-keeping.

## Features
- Fetch media information from AniList GraphQL API.
- Rank media based on scores, popularity, or other criteria.
- Export media rankings into CSV files.
- Handle different media categories like Anime, Manga, Manhwa.

## Installation
To set up AniList Media Ranker, you need to have Python installed on your system. Clone this repository to your local machine using:

`git clone https://github.com/T1nyTim/AL-Ranked.git`

Navigate to the project directory and install the required dependencies:

`cd [project-directory]`

`pip install -r requirements.txt`

## Usage
To run the application, use the following command in the project directory:

`python main.py`

This will execute the main script and generate CSV files for various media categories in the current directory.

## Configuration
You can configure the application by modifying the dictionary in the `main()` function to fetch different types of media or change the ranking criteria.
