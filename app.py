import pickle
import streamlit as st
import requests
import numpy as np
from scipy.sparse import csr_matrix

# Fetch poster based on movie_id
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
        data = requests.get(url).json()
        poster_path = data.get('poster_path', '')
        if poster_path:
            full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
            return full_path
        return ""
    except Exception as e:
        st.error(f"Error fetching poster: {str(e)}")
        return ""

# Lazy load similarity row only
def recommend(movie):
    try:
        index = movies[movies['title'] == movie].index[0]
        similarity_row = similarity[index].toarray().flatten()  # Get dense row from sparse matrix
        distances = sorted(list(enumerate(similarity_row)), reverse=True, key=lambda x: x[1])
        recommended_movie_names = []
        recommended_movie_posters = []

        for i in distances[1:6]:  # Fetch top 5 movies excluding the selected one
            movie_id = movies.iloc[i[0]].movie_id
            recommended_movie_posters.append(fetch_poster(movie_id))
            recommended_movie_names.append(movies.iloc[i[0]].title)

        return recommended_movie_names, recommended_movie_posters
    except IndexError:
        st.error("Movie not found in the list!")
        return [], []
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return [], []

# Streamlit UI
st.header('Movie Recommender System')

# Load movies data
movies = pickle.load(open('movie_list.pkl', 'rb'))

# Load the similarity matrix as sparse for memory efficiency
similarity_dense = pickle.load(open('similarity.pkl', 'rb'))
similarity = csr_matrix(similarity_dense)  # Convert to sparse matrix

# Select movie
movie_list = movies['title'].values
selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movie_list
)

# Show recommendation when button is pressed
if st.button('Show Recommendation'):
    recommended_movie_names, recommended_movie_posters = recommend(selected_movie)
    
    if recommended_movie_names:
        cols = st.columns(len(recommended_movie_names))
        for idx, col in enumerate(cols):
            with col:
                st.text(recommended_movie_names[idx])
                st.image(recommended_movie_posters[idx])
