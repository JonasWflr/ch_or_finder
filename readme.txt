# This is a simple example of how to create a webapp showing data from a CSV
# The app is reading the CSV, doing some calculations (feature engineering) and then showing a table with filters to the user
# Technology used: python, streamlit, docker and for the hosting heroku (can be changed or done locally)

# Alternative A: run it locally with docker
# docker desktop needs to be installed and running
cd .\ch_o_finder

# Build:
docker build -f Dockerfile -t or_finder:latest .

# Run:
docker run -p 8501:8501 or_finder:latest

# access in webbrowser:
localhost:8501

# ===================================================
# Alternative B: run it in the cloud (heroku, 5 apps are for free)
# install heroku CLI (command line interface)
# https://devcenter.heroku.com/articles/container-registry-and-runtime

