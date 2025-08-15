#!/bin/bash
export MONGO_URL=mongodb://localhost:27018/prepaire-lab
export REDIS_HOST=localhost
export REDIS_PORT=6379
export REDIS_PASSWORD=
export ENV=LOCAL
export USE_LOCAL_STORAGE=true
export LOCAL_STORAGE_PATH=./data
python3 -m uvicorn index:app --host 0.0.0.0 --port 8001 --reload
