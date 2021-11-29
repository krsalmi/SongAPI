#!/bin/bash
ID=$(docker ps -aqf "name=flask")
docker exec -it $ID py.test tests/
