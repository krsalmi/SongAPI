#!/bin/bash
docker-machine create -d virtualbox --virtualbox-memory 4096 SongAPI
docker-machine stop SongAPI
VBoxManage modifyvm SongAPI --cpus 2
docker-machine start SongAPI
IP=$(docker-machine ip SongAPI)
eval $(docker-machine env SongAPI)
docker-compose up -d
ADDR="http://${IP}:5000"
open ${ADDR}