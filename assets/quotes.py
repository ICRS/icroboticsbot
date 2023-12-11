"""
Generate a Quote Image from a given Image and Quote
"""

from PIL import Image  # type: ignore

from assets.Quote2Image import convert


# Font Size Default to 32, Height and Width by default is 612
def generate(IMAGE_PATH, author, quote,
			 IMAGE_TEMP="./temp.jpg", # noqa
			 font="/home/pi/code/icroboticsbot/assets/fonts/Precious.ttf") -> tuple: # noqa
	"""
	generate a quote image from a given image and quote

	Parameters
	----------
	IMAGE_PATH : String
		Path to the Image
	author : String
		Author of quote
	quote : String
		Quote
	IMAGE_TEMP : str, optional
		Path to temp image, by default "./temp.jpg"

	Returns
	-------
	tuple
		Path to the generated png image and PIL Image Object
	"""
	image = Image.open(IMAGE_PATH)
	grayscale = image.convert("L")
	width, height = grayscale.size
	ratio = 400/width
	grayscale = grayscale.resize((int(width*ratio), int(height*ratio)))
	grayscale.save(IMAGE_TEMP)

	img = convert(
		quote=quote,
		author=author,
		fg="white",
		image=IMAGE_TEMP,
		border_color="black",
		font_size=40,
		font_file=font,
		width=400,
		height=400)

	PNG_PATH = "./quote.png"

	# Save The Image as a Png file
	img.save(PNG_PATH)
	return PNG_PATH, img
