import os, io
from google.cloud import vision
from IPython.display import Image, display

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'ServiceAccountToken.json'

client = vision.ImageAnnotatorClient()


def text_recognition(storage_path, image_name):
    '../../ {0} / {1}'.format(storage_path, image_name)
    with io.open(image_name, 'rb') as image_file:
        content = image_file.read()
    image = vision.types.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations

    result = 'Texts:'

    for text in texts:
        result += '\n"{}"'.format(text.description)
        vertices = (['({},{})'.format(vertex.x, vertex.y)
                     for vertex in text.bounding_poly.vertices])
        print('bounds: {}'.format(','.join(vertices)))

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))
