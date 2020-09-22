# This is a simple example of how to create a webapp showing data from a CSV
# The app is reading the CSV, doing some calculations (create new features) and then showing the user a simple BI tool (i.e. a table with some filters)
# Technology used: python, streamlit, docker and for Alternative B hosting by heroku

# In short: The streamlit package is very simple to use, check the code for the 'st.' lines and look at the dockerfile

# === Alternative A ===: run it locally with docker
# docker desktop needs to be installed and running

cd .\ch_o_finder
# Build:
docker build -f Dockerfile -t or_finder:latest .
# Run:
docker run -p 8501:8501 or_finder:latest
# access in webbrowser:
localhost:8501

# === Alternative B === : run it in the cloud (heroku, 5 apps are for free)
# install heroku CLI (command line interface)
# https://devcenter.heroku.com/articles/container-registry-and-runtime
# create a user on heroku.com

cd .\ch_o_finder
heroku login
heroku container:login
# create heroku app:
heroku create [your_app_name]
# build image and push to container registry
heroku container:push web --app [your_app_name]
heroku container:relaese web --app [your_app_name]

# Ressources for heroku:
# https://devcenter.heroku.com/articles/container-registry-and-runtime
# https://medium.com/travis-on-docker/how-to-run-dockerized-apps-on-heroku-and-its-pretty-great-76e07e610e22
# (second link: without downloading the heroku-container-registry (already installed))

# check out the finished webapp on: https://orfinder.herokuapp.com/
