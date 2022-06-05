import os
import io
from pdf2image import convert_from_path
from google.cloud import vision
from PIL import Image

client = vision.ImageAnnotatorClient.from_service_account_json('jade-ocr-a6a21d754209.json')
contents = convert_from_path(os.path.abspath('./images/sample.pdf'), 500)

for i, content in enumerate(contents):
    page_cut_params = (1280, 200, 4134, 5650) if i else (1250, 3000, 4134, 5650)
    content = content.crop(page_cut_params)
    content.save(f'./images/sample.png', 'PNG', quality = 10, optimize=True) # chr(97 + i) maps numbers to alphabet
    file_name = os.path.abspath(f'./images/sample.png')
    # Loads the image into memory
    with io.open(file_name, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=file_name)

    # Performs label detection on the image file
    response =  client.text_detection(
            image=image,
            image_context={'language_hints': ['ja']}
        )

    # レスポンスからテキストデータを抽出
    output_text = ''
    for page in response.full_text_annotation.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                for word in paragraph.words:
                    output_text += ''.join([
                        symbol.text for symbol in word.symbols
                    ])
                output_text += '\n'
    print(output_text)




'''
file_name = os.path.abspath('./images/sample-two.png')
# Loads the image into memory
with io.open(file_name, 'rb') as image_file:
    content = image_file.read()

image = vision.Image(content=content)

# Performs label detection on the image file
response =  client.document_text_detection(
        image=image,
        image_context={'language_hints': ['ja']}
    )

# レスポンスからテキストデータを抽出
output_text = ''
for page in response.full_text_annotation.pages:
    for block in page.blocks:
        for paragraph in block.paragraphs:
            for word in paragraph.words:
                output_text += ''.join([
                    symbol.text for symbol in word.symbols
                ])
            output_text += '\n'
print(output_text)
'''


