from Quote2Image import convert
from PIL import Image

IMAGE_PATH = "background_images/PC_1.jpg"
# Font Size Default to 32, Height and Width by default is 612
def generate(IMAGE_PATH,author, quote,IMAGE_TEMP="temp.jpg", font="fonts/Precious.ttf"):
    image = Image.open(IMAGE_PATH)
    grayscale = image.convert("L")
    grayscale.save(IMAGE_TEMP)

    img=convert(
	quote=quote,
	author=author,
	fg="white",
	image=IMAGE_TEMP,
	border_color="black",
	font_size=50,
	font_file=font,
	width=400,
	height=400)

# Save The Image as a Png file
    img.save("quote.png")
