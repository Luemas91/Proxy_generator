import pandas as pd
import scrython
import time
import requests
from PIL import Image as PILImage
from io import BytesIO
from tqdm import tqdm
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Image
from reportlab.lib import colors
from fpdf import FPDF

"""
Imports Cards from a txt file (preferably from mtggoldfish), then gathers the images from scryfall.
Stores the images in an A4 for printing... somehow
"""

file_path = 'Deck - Rock the Dinosore.txt' # input path
output_path = f"{file_path[0:len(file_path)-4]}.pdf"
columns = ['Magic Card']
card_list = pd.read_csv(file_path, delimiter='\t', names=columns)

print(card_list[columns])

cards = []
image_urls = []

# Initial Scryfall query to get the image url data
for card in tqdm(card_list[columns].values):
    cards.append(scrython.Named(exact=card[0][2:])) # trims the numbers from MTG gold fish, shouldn't be a problem with csvs
    time.sleep(0.1)
    image_urls.append(cards[-1].image_uris()['normal'])

# Second scryfall query to get the images
images = []
image_width = A4[0] / 3 - 10
image_height =A4[1] / 3 - 10
for url in tqdm(image_urls):
    time.sleep(0.1)
    response = requests.get(url)
    if response.status_code == 200:
        image_contnt = BytesIO(response.content)
        # img = PILImage.open(BytesIO(image_contnt))
        image = Image(image_contnt, width=image_width, height=image_height)
        images.append(image)
    else:
        print('Failed to grab image')

# A list of rows for the images
doc = SimpleDocTemplate(output_path, pagesize=A4)

image_rows = []
for i in range(0, len(image_urls), 3):
    image_row = images[i:i+3]
    image_rows.append(image_row)
    doc.build(image_row)

# create of list of rows for each page
rows_per_page = 3
page_numbers = int(len(image_rows) / rows_per_page) + 1
# for i in range(page_numbers):

# rows_to_render = image_rows[:rows_per_page]

# render the pdf


# pdf = FPDF()
# pdf.set_auto_page_break(auto=True, margin=15)
# pdf.add_page()
# for i, row in tqdm(enumerate(image_rows)):
#     for j, url in enumerate(row):
#         time.sleep(0.1)
#         position = url.find('jpg')
#         lookup = url[:position+len('jpg')]
#         pdf.image(name=lookup, x=i % 3, y=j, w=image_width, h=image_height, type='JPG')

    

# save the PDF
# pdf.output(output_path)