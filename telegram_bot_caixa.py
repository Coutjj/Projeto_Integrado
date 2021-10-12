from re import S
from gpiozero import DigitalInputDevice, SmoothedInputDevice
from time import sleep
from statistics import mean
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from dotenv import load_dotenv
from pathlib import Path
import os
from threading import Thread


water_in_pipe = False
sentinel_mode = False

dotenvPath = str(Path(__file__).resolve().parent) + '/.env'
load_dotenv(dotenv_path=dotenvPath)

telegram_token = os.getenv('TELEGRAM_TOKEN_ENV')
group_id = os.getenv('GROUP_ID_ENV')

sensor1 = DigitalInputDevice(21, pull_up=False)
sensor2 = DigitalInputDevice(20, pull_up=False)
sensor3 = DigitalInputDevice(16, pull_up=False)
sensor4 = SmoothedInputDevice(26, pull_up=False, threshold=0.2, sample_wait=0.4, queue_len=5, average=mean)
sensor4._queue.start()


def help(update: Update, context: CallbackContext) -> None:
    message = ( 'Objetivo:\n'
                'O objetivo deste bot eh auxiliar no processo de monitoramento de uma cisterna.\n'
                'Comandos principais:\n'
                '/status: estado atual da cisterna.\n'
                '/start: inicia o processo de monitoramento.\n'
                '/stop: encerra o processo de monitoramento.'
            )
    sendMessage(message)

def status(update: Update, context: CallbackContext) -> None:
    
    message = ''
    if sensor1.is_active:
        message = 'Cisterna em 100%'
    elif sensor2.is_active:
        message = 'Cisterna em 50%'
    elif sensor3.is_active:
        message = 'Cisterna em 20%'
    else:
        message = 'Cisterna vazia'

    if sensor4.is_active:
        message += '\nEntrando agua: Sim.'
    else:
        message += '\nEntrando agua: Nao.'

    if sentinel_mode == False:
        message += '\nStatus do monitoramento: desativado.'
    else:
        message += '\nStatus do monitoramento: ativado.'


    sendMessage(message)


def checkPipeStatus():

    global water_in_pipe
    sleep(5)  
    while (True):
        water_in_pipe = sensor4.is_active
        print('Thread de monitoramento rodando.')
        
        global sentinel_mode
        if sentinel_mode == False:
            break

        if not water_in_pipe:
            sendMessage('Desligue a bomba!')
        elif sensor1.is_active:
            sendMessage('Cisterna cheia, desligue a bomba!')
        
        sleep(5)
        


def start(update: Update, context: CallbackContext) -> None:
    global sentinel
    global sentinel_mode
    sentinel_mode = True
    sentinel = Thread(target=checkPipeStatus)
    sendMessage("Processo de monitoramento iniciado.")
    status(Update, CallbackContext)
    sentinel.start()


def stop(update: Update, context: CallbackContext) -> None:
    global sentinel_mode
    global sentinel

    if sentinel_mode == True:

        sendMessage("Processo de monitoramento encerrado.")
        
        sentinel_mode = False
        sentinel.join()
        print('Thread de monitoramento encerrada')
    else:
        sendMessage('O processo de monitoramento nao foi iniciado previamente.')


 

def sendMessage(message):
    id = int(group_id)
    updater.bot.send_message(id, message)


updater = Updater(telegram_token)

updater.dispatcher.add_handler(CommandHandler('help', help))
updater.dispatcher.add_handler(CommandHandler('status', status))
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('stop', stop))


sensor1.when_activated = lambda : status(Update, CallbackContext)
sensor1.when_deactivated = lambda: status(Update, CallbackContext)

sensor2.when_activated = lambda : status(Update, CallbackContext)
sensor2.when_deactivated = lambda : status(Update, CallbackContext)

sensor3.when_activated = lambda : status(Update, CallbackContext)
sensor3.when_deactivated = lambda : status(Update, CallbackContext)

sensor4.when_activated = lambda : sendMessage("Entrada de agua detectada.")
sensor4.when_deactivated = lambda : sendMessage("Entrada de agua nao detectada.")

updater.start_polling()
updater.idle()

