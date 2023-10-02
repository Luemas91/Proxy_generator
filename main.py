import pandas as pd
import scrython
import time
import requests
from PIL import Image as PILImage
from io import BytesIO
from tqdm import tqdm
from dataclasses import dataclass
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

"""
Imports Cards from a txt file (preferably from mtggoldfish), then gathers the images from scryfall.
Stores the images in an A4 for printing... somehow
TODO: Print multiple basics, or any amount per .
"""

@dataclass
class CardInfo:
    card_count: int
    card_name: str
    card: scrython.Named
    image_url: str = "Unknown"
    image: PILImage = "Unknown"

file_path = 'Deck - Rock the Dinosore.txt' # input path
output_path = f"{file_path[0:len(file_path)-4]}.pdf"
columns = ['Magic Card']
card_list = pd.read_csv(file_path, delimiter='\t', names=columns)

print(card_list[columns])

cards = []
image_urls = []
card_counts = []

# Initial Scryfall query to get the image url data
for card in tqdm(card_list[columns].values):
    space_index = card[0].index(" ")
    cards.append(CardInfo(
        card_count=card[0][0:space_index],
        card_name=card[0][space_index+1:],
        card=scrython.Named(exact=card[0][space_index+1:])
    ))    

    # cards.append(scrython.Named(exact=card[0][2:])) # trims the numbers from MTG gold fish, shouldn't be a problem with csvs, breaks with more than 1 integer
    # card_counts.append(card[0][0:2])
    time.sleep(0.1)
    cards[-1].image_url = cards[-1].card.image_uris()['large']
    # image_urls.append(cards[-1].card.image_uris()['large'])

# Second scryfall query to get the images
images = []
image_width = int(A4[0] / 3) - 10
image_height = int(A4[1] / 3) - 10
for card in tqdm(cards):
    time.sleep(0.1)
    response = requests.get(card.image_url)
    if response.status_code == 200:
        image_contnt = PILImage.open(BytesIO(response.content))
        image_contnt = image_contnt.resize((image_width, image_height))
        card.image = image_contnt
        # img = PILImage.open(BytesIO(image_contnt))
        # image = Image(image_contnt, width=image_width, height=image_height)
        # images.append(image_contnt)
    else:
        print('Failed to grab image')

# render the pdf
c = canvas.Canvas(output_path, pagesize=A4)

cell_width = 2.25 * inch
cell_height = 3.25 * inch
x_start = 0.5 * inch
y_start = A4[1] - 0.5 * inch - cell_height  # Start from the top of the page

# Loop through image paths and add images to the grid

card_sum = sum([i.card_count for i in cards])
render_images = [card.image * card.card_count for card in cards]
row_number = int(card_sum / 3) +1

for row in tqdm(range(row_number)):
    for col in range(3):
        image_index = row * 3 + col
        if image_index < len(images):
            image_path = render_images[image_index]
            c.drawInlineImage(image_path, x_start + col * cell_width, y_start - (row % 3 ) * cell_height, 
                              width=cell_width, height=cell_height)

            # Draw a border around the image cell
            c.rect(x_start + col * cell_width, y_start - (row % 3) * cell_height, cell_width, cell_height)
    
    if row % 3 == 0 and row > 0:
        c.showPage()
        x_start = 0.5 * inch
        y_start = A4[1] - 0.5 * inch - cell_height



# Save the PDF
c.save()

print("PDF with image grid on A4 created successfully.")
