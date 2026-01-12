import datetime
import random

import tmdb_client
from dotenv import dotenv_values, find_dotenv
from flask import Flask, redirect, render_template, request, url_for, session

env_file = find_dotenv(".env")
config_env = dotenv_values(env_file)

app = Flask(__name__)
app.config["TMDB_TOKEN"] = config_env["FLASK_MOVIEDB_API_KEYv4"]
app.config["SECRET_KEY"] = config_env["FLASK_MOVIEDB_SECRET_KEY"]

LIST_TYPES = ["top_rated", "upcoming", "popular", "now_playing"]

FAVORITES = set()  # later to be changed into a database entry for logged-in user


@app.route("/")
def homepage():
    selected_list = request.args.get("list_type", "popular")
    if selected_list not in LIST_TYPES:
        selected_list = "popular"
    session["selected_list"] = selected_list
    movies = tmdb_client.get_movies(8, list_type=selected_list)
    return render_template(
        "homepage.html",
        movies=movies,
        list_types=LIST_TYPES,
        current_list=selected_list,
        favorites=FAVORITES,
    )


@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("q", "").strip()
    if not query:
        return redirect(request.referrer or url_for("homepage"))

    results = tmdb_client.search(query)
    movies = results.get("results", [])
    if not movies:
        return render_template(
            "search_results.html", movies=[], search_query=query, no_results=True
        )

    movies_sorted = sorted(movies, key=lambda m: m.get("popularity", 0), reverse=True)

    if len(movies) == 1:
        return redirect(url_for("movie_details", movie_id=movies[0]["id"]))

    return render_template(
        "search_results.html",
        movies=movies_sorted,
        search_query=query,
        no_results=False,
    )


@app.route("/movie/<movie_id>")
def movie_details(movie_id):
    movie = tmdb_client.get_movie_details(movie_id)
    cast = tmdb_client.get_single_movie_cast(movie_id)
    images = tmdb_client.get_movie_images(movie_id)
    selected_backdrop = random.choice(images) if images else None
    return render_template(
        "movie_details.html",
        movie=movie,
        cast=cast,
        selected_backdrop=selected_backdrop,
    )


@app.route("/today")
def today():
    movies = tmdb_client.get_airing_today()
    today = datetime.date.today()
    return render_template("today.html", movies=movies, today=today)


@app.route("/favorites/toggle", methods=["POST"])
def toggle_favorite():
    data = request.json
    movie_id = int(data.get("movie_id"))
    movie_title = data.get("movie_title", "")

    if movie_id in FAVORITES:
        FAVORITES.remove(movie_id)
        return {
            "status": "removed",
            "message": f'Removed "{movie_title}" from favorites.',
        }
    else:
        FAVORITES.add(movie_id)
        return {"status": "added", "message": f'Added "{movie_title}" to favorites!'}


@app.route("/favorites")
def show_favorites():
    if FAVORITES:
        movies = []
        for movie_id in FAVORITES:
            movie_details = tmdb_client.get_movie_details(movie_id)
            movies.append(movie_details)
    else:
        movies = []
    return render_template("homepage.html", movies=movies, favorites=FAVORITES)


@app.context_processor
def utility_processor():
    def tmdb_image_url(path, size):
        return tmdb_client.get_poster_url(path, size)

    return {"tmdb_image_url": tmdb_image_url}


@app.template_filter("number_sep")
def number_sep(value):
    try:
        # set separator as comma and then replace
        return f"{value:,.2f}".replace(
            ",", ","
        )  # the second parameter is the target ones
    except (ValueError, TypeError):
        return value


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run(debug=True)
