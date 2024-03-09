# docker build -t localhost:32000/icrsbot-reduced .
# docker push localhost:32000/icrsbot-reduced
docker buildx build --builder=builder --push --platform linux/arm64,linux/amd64 -t localhost:32000/icrsbot-reduced .
