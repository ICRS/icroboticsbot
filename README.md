# icroboticsbot

Discord bot for the Imperial College Robotics Society discord server


Discord Bot has been split into 3 microservices:

* File Handler: copy files from the discord to the slicing computer
* Meme: all the meme functionalities - in particular quote bot
* Registration: code to register users to the discord
* Printer handler: webhooks to handle printer status and camera feed

See relevant directories for instructions to build containers and deployment


BUILDX Create Builder:
docker buildx create --config ~/.docker/buildx/config.toml --name builder --driver-opt network=host
