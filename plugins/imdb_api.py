from imdb import IMDb

imdb = IMDb()

async def get_poster(query, id=False):
    if not id:
        query = query.strip().lower()
        movie_list = imdb.search_movie(query)
        if not movie_list:
            return None
        movie = imdb.get_movie(movie_list[0].movieID)
    else:
        movie = imdb.get_movie(query)

    if not movie:
        return None

    return {
        'title': movie.get('title'),
        'year': movie.get('year'),
        'poster': movie.get('full-size cover url'),
        'plot': movie.get('plot outline', 'No description available.'),
        'url': f"https://www.imdb.com/title/tt{movie.movieID}/"
    }
