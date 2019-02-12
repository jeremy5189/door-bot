import subprocess
import commands
import telebot
import time
import os
import config
from telebot import types

# Init env
env = config.Config

# Init Bot
bot = telebot.TeleBot(env.API_TOKEN)

# -------------------------------
# Check if user id is in the list
# -------------------------------
def check_user(uid):

    allow = False

    for user_id in env.ALLOW_ID_LIST:
        if user_id == str(uid):
            allow = True
            break

    return allow

# -------------------------------
# Get LAN IP
# -------------------------------
def get_lan_ip():
    return commands.getoutput("/sbin/ifenv").split("\n")[1].split()[1][5:]

# -------------------------------
# Call bash command
# -------------------------------
def bash_cmd(bashCommand):
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    return output

def log_to_admin(message):
    print message
    bot.send_message(env.ADMIN_ID, message)

# -------------------------------
# Open door
# -------------------------------
def open_door_wrapper(user_id, via):
    bash_cmd('bash ' + os.getcwd()  + '/gpio-toggle.sh')
    log_to_admin('DOOR OPENED BY: ' + env.ALLOW_ID_LIST[user_id] + ' via ' + via)

# Init GPIO
bash_cmd('bash ' + os.getcwd()  +'/gpio-init.sh')

# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('/ip', '/wait3', '/song', '/myid', '/check', '/env', '/open')
    bot.reply_to(message, "Hello! This is Jeremy Home Door Bot", reply_markup=markup)

@bot.message_handler(commands=['song'])
def song_open_door(message):
    if check_user(message.from_user.id):
        bot.reply_to(message, 'Playing door open song')
        log_to_admin('DOOR OPENED BY: ' + env.ALLOW_ID_LIST[str(message.from_user.id)] + ' via song')
        bash_cmd('bash ' + os.getcwd() + '/gpio-song.sh')
    else:
        log_to_admin('DENIED: ' + str(message.from_user.id))
        bot.reply_to(message, 'User ID not allowd')

@bot.message_handler(commands=['wait3'])
def wait_open_door(message):
    if check_user(message.from_user.id):
        bot.reply_to(message, 'Wait 3 sec to open')
        time.sleep(3)
        open_door_wrapper(str(message.from_user.id), 'wait3')
        bot.reply_to(message, 'Door opened')
    else:
        bot.reply_to(message, 'User ID not allowd')

@bot.message_handler(commands=['ip'])
def send_ip(message):
    ip = get_lan_ip()
    bot.reply_to(message, ip)

@bot.message_handler(commands=['myid'])
def send_my_id(message):
    bot.reply_to(message, 'My telegram user id: ' + str(message.from_user.id))
    log_to_admin('Someone send ID query: ' + str(message.from_user.id))

@bot.message_handler(commands=['open'])
def open_door(message):
    if check_user(message.from_user.id):
        bot.reply_to(message, 'Door opened')
        open_door_wrapper(str(message.from_user.id), 'open')
    else:
        bot.reply_to(message, 'User ID not allowd')

@bot.message_handler(commands=['check'])
def check_priv(message):
    if check_user(message.from_user.id):
        bot.reply_to(message, 'Access Granted')
    else:
        bot.reply_to(message, 'Access Denied')

@bot.message_handler(commands=['env'])
def get_tmp_and_hum(message):
    output = bash_cmd('/home/pi/Adafruit_Python_DHT/examples/AdafruitDHT.py 11 3')
    bot.reply_to(message, output);

# Loop
bot.polling()
