# 실행 위치 기준 app 디렉토리에서 실행시 ./docker_compose.yaml 입력
# app/script 디렉토리에서 실행시 ../docker_compose.yaml 입력
docker compose -f ./docker_compose.yaml -p reservation up