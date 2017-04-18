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
    # print(text_page)
    tables_regex = r"""<td align="right" bgcolor="#eeeeee">(?P<episode>[\d.]+).*?</td>[\n ]*?<td><a href="/title/.*?/">(?P<name_episode>[\w\W\d]+?)</a></td>[\n ]*?<td align="right">(?P<score>[\d.]+)</td>"""
    tables_regex = re.compile(tables_regex)

    chapters = tables_regex.findall(text_page)

    chapters = [(unescape(episode), unescape(title), unescape(score)) for episode, title, score in chapters]
    return chapters

def generate_dataset(list_shows):
    with open("data.csv", "w") as dataset:
        dataset.write("show;chapter;name_chapter;score\n")
        for show in list_shows:
            for chapter, name_chapter, score in get_chapters_rates(show):

                metadata = {
                    "show": show[2],
                    "chapter": chapter,
                    "name_chapter": name_chapter,
                    "score": score
                }

                dataset.write("{show};{chapter};{name_chapter};{score}\n".format(**metadata))

if __name__ == "__main__":
    top_10 = get_top_shows(10)
    generate_dataset(top_10)
