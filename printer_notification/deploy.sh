cat deployment.yaml | sed -e "s/latest/${1:-latest}/g" | kubectl apply -f -
