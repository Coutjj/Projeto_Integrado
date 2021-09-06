from gpiozero import DigitalInputDevice, SmoothedInputDevice
from time import sleep
from statistics import mean
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from dotenv import load_dotenv
from pathlib import Path
import os


dotenvPath = str(Path(__file__).resolve().parent) + '/.env'
load_dotenv(dotenv_path=dotenvPath)

telegram_token = os.getenv('TELEGRAM_TOKEN_ENV')
group_id = os.getenv('GROUP_ID_ENV')

sensor1 = DigitalInputDevice(21, pull_up=False)
sensor2 = DigitalInputDevice(20, pull_up=False)
sensor3 = DigitalInputDevice(16, pull_up=False)
sensor4 = SmoothedInputDevice(26, pull_up=False, threshold=0.2, sample_wait=0.4, queue_len=5, average=mean)
sensor4._queue.start()


def hello(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(f'Hello {update.effective_user.first_name}')


def status(update: Update, context: CallbackContext) -> None:
    message = ''
    if sensor1.is_active:
        message = "Cisterna em 100%"
    elif sensor2.is_active:
        message = "Cisterna em 50%"
    elif sensor3.is_active:
        message = "Cisterna em 20%"
    else:
        message = "Cisterna vazia"

    if sensor4.is_active:
        message += "\nBomba ativada e funcionando."

    update.message.reply_text(message)
    

def sendMessage(message):
    id = int(group_id)
    updater.bot.send_message(id, message)


updater = Updater(telegram_token)

updater.dispatcher.add_handler(CommandHandler('hello', hello))
updater.dispatcher.add_handler(CommandHandler('status', status))


sensor1.when_activated = lambda : sendMessage("Sensor 1 ativado")
sensor2.when_activated = lambda : sendMessage("Sensor 2 ativado")
sensor3.when_activated = lambda : sendMessage("Sensor 3 ativado")
sensor4.when_activated = lambda : sendMessage("Sensor de presenca de agua ativado")
sensor4.when_deactivated = lambda : sendMessage("Sensor de presenca de agua desativado")

updater.start_polling()
updater.idle()

