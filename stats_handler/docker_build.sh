#docker buildx create --use --name builder
#docker buildx build --platform linux/amd64,linux/arm64 --push -t 127.0.0.1:32000/icrsbot-stats-handler .
docker buildx build --builder=builder --push --platform linux/arm64,linux/amd64 -t localhost:32000/icrsbot-stats-handler .

