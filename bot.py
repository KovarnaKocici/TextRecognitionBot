import telebot
import urllib.request
import os
from os import environ

from vision import text_recognition

global bot
global result_storage_path

# setup bot with Telegram token from .env
bot = telebot.TeleBot(environ['TELEGRAM_TOKEN'])

# store files in /tmp so storage does not get complete
result_storage_path = 'tmp'

# welcome message
bot_text = """
       Welcome to the TextRecognition bot! It uses the VisionAPI service to recognize text based on the image you send.
       """


def get_image_id_from_message(message):
    # there are multiple array of images, check the biggest
    return message.photo[len(message.photo) - 1].file_id


def save_image_from_message(message):
    cid = message.chat.id

    image_id = get_image_id_from_message(message)

    bot.send_message(cid, '🔥 Analyzing image, be patient ! 🔥')

    # prepare image for downlading
    file_path = bot.get_file(image_id).file_path

    # generate image download url
    image_url = "https://api.telegram.org/file/bot{0}/{1}".format(environ['TELEGRAM_TOKEN'], file_path)
    print(image_url)

    # create folder to store pic temporary, if it doesnt exist
    if not os.path.exists(result_storage_path):
        os.makedirs(result_storage_path)

    # retrieve and save image
    image_name = "{0}.jpg".format(image_id)
    urllib.request.urlretrieve(image_url, "{0}/{1}".format(result_storage_path, image_name))

    return image_name;


def cleanup_remove_image(image_name):
  os.remove('{0}/{1}'.format(result_storage_path, image_name))


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, bot_text)


@bot.message_handler(content_types=['photo'])
def handle(message):
        try:
            # extract the image name for further operations
            image_name = save_image_from_message(message)

            # use VisionAPI to execute image classification
            output = text_recognition(result_storage_path, image_name)

            # reply with a text to the photo the user sent
            bot.reply_to(message, output)

            cleanup_remove_image(image_name);

        except Exception:
            # if things went wrong
            bot.reply_to(message, "There was a problem, please try again")


# configure the webhook for the bot, with the url of the Glitch project
bot.set_webhook("https://{}.glitch.me/{}".format(environ['PROJECT_NAME'], environ['TELEGRAM_TOKEN']))


if __name__ == '__main__':
    bot.run(threaded=True)
