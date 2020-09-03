# Hello World example

cd C:\Users\Waj\'OneDrive - AWK Group AG'\80_prog\test\ch_o_finder

# Build:
docker build -f Dockerfile -t or_finder:latest .

# Run:
docker run -p 8501:8501 or_finder:latest

# access:
localhost:8501



# ===================================================
# for azure:
# create image
#docker build -t <dockerhubusername>/myfirstapp:v1 .
docker build -t jonasdockerdocker/or_finder:v1 .

# push image to dockerhub
#docker push <dockerhubusername>/myfirstapp:v1
docker login
docker push jonasdockerdocker/or_finder:v1


# check
# for whole workflow with dockerhub and azure web app:
# https://www.codemotion.com/magazine/dev-hub/cloud-manager/run-docker-image-on-microsoft-azure/
# and for azure container instance:
# https://docs.microsoft.com/en-us/azure/container-instances/container-instances-quickstart-portal