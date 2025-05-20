import requests
from bs4 import BeautifulSoup

async def get_imdb_details(title):
    try:
        url = f"https://www.imdb.com/find?q={title.replace(' ', '+')}"
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        link = soup.select_one(".result_text a")
        if not link:
            return {"title": title, "year": "None", "poster": "", "plot": "None", "rating": "N/A"}

        movie_url = f"https://www.imdb.com{link['href']}"
        r = requests.get(movie_url)
        soup = BeautifulSoup(r.text, "html.parser")

        title = soup.find("h1").text.strip()
        year = soup.select_one("#titleYear a").text
        plot = soup.select_one(".plot-summary .summary_text").text.strip()
        poster = soup.select_one(".poster img")["src"]
        rating = soup.select_one("span[itemprop='ratingValue']").text

        return {
            "title": title,
            "year": year,
            "plot": plot,
            "poster": poster,
            "rating": rating
        }
    except:
        return {"title": title, "year": "None", "poster": "", "plot": "None", "rating": "N/A"}
