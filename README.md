# Door-Bot

Using telegram bot to control a relay connect to a Raspberry Pi for opening a door. Implemented with python2 and `telebot`

![door-bot-interface](https://user-images.githubusercontent.com/1984426/54068163-a271e400-4284-11e9-948f-0be37a0a2659.jpeg)

## Install

```
pip install -r requirements.txt
cp config.example.py config.py
```

Edit `config.py` and input your telegram bot API Key, administrator telegram ID, and the telegram ID which are allowed to open the door

```
pm2 start door-bot.py --name=door-bot 
```

## Raspberry Pi Install

![photo_2019-03-09 16 00 16](https://user-images.githubusercontent.com/1984426/54068157-7a828080-4284-11e9-8a43-d6e483e13921.jpeg)

The relay is connect to Raspberry Pi 3 GPIO04 (Pin 7), Ground (Pin 6) and DC power 5V (Pin 2)

![photo_2019-03-09 15 59 55](https://user-images.githubusercontent.com/1984426/54068156-78202680-4284-11e9-9216-3b44730ac36a.jpeg)

The two thin white cable is connected to the button of the original controller installed in the apartment. Once the black button is pressed, the front door of the apartment will be unlocked. Which is now triggered by the relay.
