from requests import get
from html import unescape
from bs4 import BeautifulSoup
import re

RATING_PAGE = "http://www.imdb.com/chart/toptv"

def get_top_shows(n):
    # text_page = get(RATING_PAGE).text
    with open("chart.html") as f:
        text_page = f.read()
        title_regex = r'(\d+)\.\n.*?<a href="/title/(?P<id>[\w\W\d]+?)/.*?"\n.*?>(?P<title>[\w\W\d]+?)</a>'
        title_regex = re.compile(title_regex)

        tv_shows = title_regex.findall(text_page)
        tv_shows = [(int(n), id_title, title) for n, id_title, title in tv_shows]
    return tv_shows[:n]

def get_chapters_rates(show):
    pos, id_title, title = show
    url_rating = "http://www.imdb.com/title/{id}/epdate".format(id=id_title)
    text_page = get(url_rating).text
    tables_regex = r"""<td align="right" bgcolor="#eeeeee">(?P<episode>[\d.]+).*?</td>[\n ]*?<td><a href="/title/.*?/">(?P<name_episode>[\w\W\d]+?)</a></td>[\n ]*?<td align="right">(?P<score>[\d.]+)</td>"""
    tables_regex = re.compile(tables_regex)

    chapters = tables_regex.findall(text_page)

    chapters = [(unescape(episode), unescape(title), unescape(score)) for episode, title, score in chapters]
    return chapters

def get_number_seasons(chapters_list):
    max = 0
    for n, name, score in chapters_list:
        season, chapter = n.strip().split(".")
        season = int(season)
        if season > max:
            max = season

    return max


def generate_dataset(list_shows, name):
    with open(name, "w") as dataset:
        dataset.write("show;chapter;name_chapter;score\n")
        for show in list_shows:

            chapters = get_chapters_rates(show)

            for chapter, name_chapter, score in chapters:

                metadata = {
                    "show": show[2],
                    "chapter": chapter,
                    "name_chapter": name_chapter,
                    "score": score
                }

                dataset.write("{show};{chapter};{name_chapter};{score}\n".format(**metadata))

if __name__ == "__main__":
    all_series = get_top_shows(25)

    # we filter the shows with only one season
    top_series = []
    TOTAL_SERIES = 5

    i = 0
    while len(top_series) < TOTAL_SERIES and i < len(all_series):

        chapters = get_chapters_rates(all_series[i])
        if get_number_seasons(chapters) > 1:
            print("Se agrego ", all_series[i][2])
            top_series.append(all_series[i])

        i += 1

    generate_dataset(top_series, "more_seasons.csv")
    


