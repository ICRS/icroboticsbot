# icroboticsbot

Discord bot for the Imperial College Robotics Society discord server


Discord Bot has been split into 5 microservices:

* File Handler: copy files from the discord to the slicing computer
* Meme: all the meme functionalities - in particular quote bot
* Registration: code to register users to the discord
* Printer handler: webhooks to handle printer status and camera feed
* Printer features: 3D Printer misc commands
* Discord Printing: Uploading and slicing files for automatic 3D printing

See relevant directories for instructions to build containers and deployment

## Build Instructions

BUILDX Create Builder:
docker buildx create --config ~/.docker/buildx/config.toml --name builder --driver-opt network=host

The config.toml file should look like this:
```
[registry."REGISTRY_IP:REGISTRY_PORT"]
http = true
insecure = true
```

Run the build_docker.sh script file in each respective folder
