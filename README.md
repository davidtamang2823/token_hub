# Setup
## Docker create network and volumes
- sudo docker network create token_hub_network
- sudo docker volume create token_hub_postgres_data
- sudo docker volume create token_hub_redis_data
## Build image and run container using docker compose
- sudo docker compose up -d --build