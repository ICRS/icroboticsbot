# docker build -t localhost:32000/icrsbot-file-handler .
# docker push localhost:32000/icrsbot-file-handler
docker buildx build --builder=builder --push --platform linux/arm64,linux/amd64 -t localhost:32000/icrsbot-printer-handler:${1:-latest} .
