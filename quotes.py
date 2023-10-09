from Quote2Image import convert
from PIL import Image

# Font Size Default to 32, Height and Width by default is 612
def generate(IMAGE_PATH,author, quote,IMAGE_TEMP="/home/pi/code/icroboticsbot/temp.jpg", font="/home/pi/code/icroboticsbot/fonts/Precious.ttf"):
	image = Image.open(IMAGE_PATH)
	grayscale = image.convert("L")
	width, height = grayscale.size
	ratio = 400/width
	grayscale = grayscale.resize((int(width*ratio),int(height*ratio)))
	grayscale.save(IMAGE_TEMP)

	img=convert(
	quote=quote,
	author=author,
	fg="white",
	image=IMAGE_TEMP,
	border_color="black",
	font_size=40,
	font_file=font,
	width=400,
	height=400)

# Save The Image as a Png file
	img.save("/home/pi/code/icroboticsbot/quote.png")
