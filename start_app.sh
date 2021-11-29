#!/bin/bash
IP="localhost"
docker-compose up -d
ADDR="http://${IP}:5000"
open ${ADDR}
