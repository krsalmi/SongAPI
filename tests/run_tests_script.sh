#!/bin/bash
IP=$(docker-machine ip SongAPI)
eval $(docker-machine env SongAPI)
ID=$(docker ps -aqf "name=flask")
docker exec -it $ID py.test tests/