from fastapi import FastAPI
import pickle
from fastapi.middleware.cors import CORSMiddleware
import requests
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")

app = FastAPI()

# CORS (keep this)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load data
movies = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('model.pkl', 'rb'))

movies['title'] = movies['title'].str.lower()


# Fetch poster from TMDB
def fetch_poster(movie_title):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={movie_title}"
    data = requests.get(url).json()

    if data["results"]:
        poster_path = data["results"][0].get("poster_path")
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"

    return ""


# Recommendation logic (upgraded)
def recommend(movie):
    movie = movie.lower()

    if movie not in movies['title'].values:
        return []

    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]

    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:11]

    results = []
    for i in movies_list:
        title = movies.iloc[i[0]].title
        poster = fetch_poster(title)

        results.append({
            "title": title,
            "poster": poster
        })

    return results


# Search dropdown
@app.get("/search")
def search_movies(query: str):
    query = query.lower()

    matches = movies[movies['title'].str.contains(query)]['title'].head(5)

    return {"results": matches.tolist()}


# Root
@app.get("/")
def root():
    return {"message": "API is running"}


# Recommend endpoint
@app.get("/recommend")
def get_recommendation(movie: str):
    return {"recommendations": recommend(movie)}