import subprocess
import commands
import telebot
import time
import os
import config
import random
from telebot import types

# Init env
env = config.Config

# Init Bot
bot = telebot.TeleBot(env.API_TOKEN)

# Save OTP in memory
OTP_IN_MEM = {}

# -------------------------------
# Check if user id is in the list
# -------------------------------
def check_user(uid):
    return str(uid) in env.ALLOW_ID_LIST

def check_otp_user(uid):
     return str(uid) in env.ALLOW_ID_CREATE_OTP

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

# -------------------------------
# Send logs to admin
# -------------------------------
def log_to_admin(message):
    print message
    bot.send_message(env.ADMIN_ID, message)


# -------------------------------
# Open door
# -------------------------------
def open_door_wrapper(user_id, via):
    bash_cmd('bash ' + os.getcwd()  + '/gpio-toggle.sh')

    if via != 'otp':
        msg = 'DOOR OPENED BY: ' + env.ALLOW_ID_LIST[user_id] + ' via ' + via
        log_to_admin(msg)

    if user_id in env.NOTIFY_LIST:
        for receiver in env.NOTIFY_LIST[user_id]:
            print 'Sending friendly notify to {} because of {}'.format(env.ALLOW_ID_LIST[receiver], env.ALLOW_ID_LIST[user_id])
            bot.send_message(receiver, "<Friendly Notification> {}".format(msg))    


def create_new_otp(user_name):
    new_otp = random.randint(100000, 999999)
    OTP_IN_MEM[str(new_otp)] = user_name
    return new_otp

# Init GPIO
bash_cmd('bash ' + os.getcwd()  +'/gpio-init.sh')

# Init msg to admin
def init_msg():
    uptime = bash_cmd('uptime')
    date = bash_cmd('date')
    temp = bash_cmd('vcgencmd measure_temp')
    msg = "Door Bot Initialized\nUptime: {}Date: {}{}".format(uptime, date, temp)
    log_to_admin(msg)

init_msg()

# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('/otp', '/wait3', '/wait', '/song', '/myid', '/check', '/open')
    bot.reply_to(message, "Hello! This is Jeremy Home Door Bot, open the door with /open or /otp [code]", reply_markup=markup)

@bot.message_handler(commands=['song'])
def song_open_door(message):
    if check_user(message.from_user.id):
        bot.reply_to(message, 'Playing door open song')
        log_to_admin('DOOR OPENED BY: ' + env.ALLOW_ID_LIST[str(message.from_user.id)] + ' via song')
        bash_cmd('bash ' + os.getcwd() + '/gpio-song.sh')
    else:
        log_to_admin('DENIED: {} (@{})'.format(str(message.from_user.id), message.from_user.username))
        bot.reply_to(message, 'User ID not allowd')

@bot.message_handler(commands=['wait'])
def wait_n_open_door(message):
    args = message.text.split(' ')
    if len(args) < 2:
        bot.reply_to(message, 'Usage: /wait [seconds] (max 300)')
    elif not args[1].isdigit():
        bot.reply_to(message, 'Usage: /wait [seconds] (max 300)')
    elif int(args[1]) > 300:
        bot.reply_to(message, 'Usage: /wait [seconds] (max 300)')
    else:
        if check_user(message.from_user.id):
            bot.reply_to(message, 'Wait {} sec to open'.format(args[1]))
            time.sleep(int(args[1]))
            open_door_wrapper(str(message.from_user.id), 'wait {}'.format(args[1]))
            bot.reply_to(message, 'Door opened')
        else:
            log_to_admin('DENIED: {} (@{})'.format(str(message.from_user.id), message.from_user.username))
            bot.reply_to(message, 'User ID not allowd')

@bot.message_handler(commands=['wait3'])
def wait_open_door(message):
    if check_user(message.from_user.id):
        bot.reply_to(message, 'Wait 3 sec to open')
        time.sleep(3)
        open_door_wrapper(str(message.from_user.id), 'wait3')
        bot.reply_to(message, 'Door opened')
    else:
        log_to_admin('DENIED: {} (@{})'.format(str(message.from_user.id), message.from_user.username))
        bot.reply_to(message, 'User ID not allowd')

@bot.message_handler(commands=['ip'])
def send_ip(message):
    ip = get_lan_ip()
    bot.reply_to(message, ip)

@bot.message_handler(commands=['myid'])
def send_my_id(message):
    bot.reply_to(message, 'My telegram user id: ' + str(message.from_user.id))
    uid = message.from_user.username
    log_to_admin('@{} send ID query: '.format(uid) + str(message.from_user.id))

@bot.message_handler(commands=['open'])
def open_door(message):
    if check_user(message.from_user.id):
        bot.reply_to(message, 'Door opened')
        open_door_wrapper(str(message.from_user.id), 'open')
    else:
        log_to_admin('DENIED: {} (@{})'.format(str(message.from_user.id), message.from_user.username))
        bot.reply_to(message, 'User ID not allowd')

@bot.message_handler(commands=['check'])
def check_priv(message):
    if check_user(message.from_user.id):
        log_to_admin('Check granted: {} (@{})'.format(str(message.from_user.id), message.from_user.username))
        bot.reply_to(message, 'Access Granted')
    else:
        log_to_admin('Check denied: {} (@{})'.format(str(message.from_user.id), message.from_user.username))
        bot.reply_to(message, 'Access Denied')

@bot.message_handler(commands=['env'])
def get_tmp_and_hum(message):
    output = bash_cmd('/home/pi/Adafruit_Python_DHT/examples/AdafruitDHT.py 11 3')
    bot.reply_to(message, output);

@bot.message_handler(commands=['init'])
def send_init_msg(message):
    init_msg()
    bot.reply_to(message, "Sent")

@bot.message_handler(commands=['otp'])
def gen_otp_or_open_with(message):
    args = message.text.split(' ')
    if len(args) < 2:
        bot.reply_to(message, 'Usage: /otp [code], list, create, revoke');
    elif args[1] == 'list':
        if check_otp_user(message.from_user.id):
            strr = "\n"
            for otp in OTP_IN_MEM:
                strr += otp + ' by ' + OTP_IN_MEM[otp] + "\n"
            if strr == "\n":
                strr = 'None'
            bot.reply_to(message, 'Available OTP: ' + strr)
        else:
            bot.reply_to(message, 'Access Denied')
    elif args[1] == 'create':
        if check_otp_user(message.from_user.id):
            by_user = env.ALLOW_ID_CREATE_OTP[str(message.from_user.id)]
            new_otp = create_new_otp(by_user)
            log_to_admin('[OTP] ' + by_user + ' created OTP: ' + str(new_otp))
            bot.reply_to(message, 'Created new otp: ' + str(new_otp))
        else:
            bot.reply_to(message, 'Access Denied')
    elif len(args) > 2 and args[1] == 'revoke':
        if check_otp_user(message.from_user.id):
            otp = args[2]
            if otp in OTP_IN_MEM:
                by_user = OTP_IN_MEM.pop(otp, None)
                log_to_admin('[OTP] ' + by_user + ' revoked OTP: ' + otp)
                bot.reply_to(message, 'Revoked otp ' + str(otp) + ' by ' + by_user)
            else:
                bot.reply_to(message, 'OTP not found: ' + otp)
        else:
            bot.reply_to(message, 'Access Denied')
    else:
        # Open with otp
        otp = args[1]
        if otp in OTP_IN_MEM:
            by_user = OTP_IN_MEM.pop(otp, None)
            msg = '[OTP] Door opened by user: ' + str(message.from_user.id) + ' with OTP: ' + otp + ' granted by ' + by_user
            log_to_admin(msg)
            open_door_wrapper(None, 'otp')
            bot.reply_to(message, 'Door opened')
        else:
            log_to_admin('[OTP] User: ' + str(message.from_user.id) + ' failed attempt to use OTP: ' + otp)
            bot.reply_to(message, 'Access Denied')

# Loop
bot.polling()
