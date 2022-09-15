import telebot
from telebot import types
import re
import os
import shutil
from datetime import datetime

#для отправки оповещений и монитора
import threading
import time
from time import sleep
import requests

#переменные
from params import my_token, bot_id, limit, path

#монитор
import subprocess
import sys
subprocess.Popen(["python.exe", f"{path}/monitor.py"])
subprocess.Popen(["python.exe", f"{path}/monitor4new_publick.py"])

token = my_token
bot = telebot.TeleBot(bot_id)

#разные переменные
publos_id = [] #хранилище id сообщений, в которых содержатся монитор (далее будет, где показывается список из пабликов)
stealed_posts = [] #хранилище id сообщений, в которых выведены монитор, в которых готовы посты
helper = [] #хранилище id сообщений, в которых содержатся сообщения-помощники
what_deleting = 0 #id сообщения, которое удаляем
pub_limit = limit #лимит пабликов в мониторе

def print_time_now():
    time = datetime.now()
    time = time.strftime('%m-%d %H:%M:%S')
    print(f'--{time}--')

while True:#бесконечный 4loop. чтобы, если какая-то ошибка, то бот перезапускался
    try:

        #рассылка уведомлений
        def notifes():
            while True:
                try:
                    if os.path.getsize('groups_processors/notifications.txt') != 0:
                        f = open("publicks/publicks.txt", "r", encoding='utf-8')
                        lines = f.readlines()
                        f.close()
                        f = open("groups_processors/chat__id.txt", "r", encoding='utf-8')
                        chat__id = f.readline()
                        f.close()

                        if chat__id == '0' or len(os.listdir('./publicks')) == 2:
                            sleep(300) 
                        else:
                            posts_count = 0

                            for publick in lines:

                                #найти кол-во постов
                                publick_number = publick.partition(':')[0]
                                strin = f'{publick_number}: https://vk.com/' #строчка, которую нужно будет отсечь от строки файла со списком пабликов
                                group_name = publick.replace(strin, '')
                                group_name = group_name.replace("\n", '') #название паблика
                                f = open(f"publicks/{group_name}.txt", "r", encoding='utf-8') #убираем строку из файла
                                posts_text = f.readlines()
                                f.close()
                                for text in posts_text:
                                    if text == '----------\n':
                                        posts_count += 1
                            #sleep(3)
                            f = open('groups_processors/notifications_count.txt', 'r')
                            message_count_4_noties = f.readline()
                            f.close()
                            if posts_count >= int(message_count_4_noties):

                                markup = types.InlineKeyboardMarkup(row_width=1) #добаление кнопок под сообщением
                                ok = types.InlineKeyboardButton(f'{message_count_4_noties} постов ✅', callback_data='ok') #чтобы уведомления снова включились
                                markup.add(ok)
                                f = open("groups_processors/chat__id.txt", "r", encoding='utf-8')
                                chat__id = f.readline()
                                f.close()
                                bot.send_message(chat_id=chat__id, text=f'💡', parse_mode='html', reply_markup=markup, disable_notification=True)

                                sleep(36000)
                except Exception as e:
                    print(e)
                    print_time_now()
                    print('уведомления ругаются\n')
                    sleep(1800)


        t = threading.Thread(target=notifes, args=[])
        t.start()

        def send_group_img(text): #функция по отправке нескольких фото
            f = open("groups_processors/chat__id.txt", "r", encoding='utf-8')
            chat__id = f.readline()
            f.close()
            temp_files_list = list()
            media = list()
            files = dict()
            for filename in os.listdir("./images"):                               # для каждого файла в папке images
                temp_files_list.append(f'{os.getcwd()}\\images\\{filename}')      # добавить его в temp_files_list()
            for f in enumerate(temp_files_list):                                  # для <f> в temp_files_list()
                files[f"name-{f[0]}"] = open(f[1], "rb")                          # files() с названием name-{f[0]} ##f[0] - номер картинки в папке; f[1] - ссылка на картинку
                if f[0] == 0:                                                     # если самое первое фото
                    media.append({"type": "photo",                                # добавление в media фотку
                                "media": f"attach://name-{f[0]}",                 # присвоить медиа имя-ключ, который в files()
                                "caption": text,
                                "parse_mode": 'html'}                                  # то добавить текст в медиа
                                )
                else:                                                             # для остальных фото
                    media.append({"type": "photo",                                # добавление в media фотку
                                "media": f"attach://name-{f[0]}"})                # присвоить медиа имя-ключ, который в files()
            params = {                                                            # параметры, которые будут передаваться в ссылке
                "chat_id": chat__id, "media": str(media).replace("'", '"')}       # chat_id, 'media'-все фотки, что добавили, добавить. заменить везде ' на "
            request_url = "https://api.telegram.org/bot" + bot_id + "/sendMediaGroup"
            result = requests.post(request_url, params=params, files=files)
            if result.status_code == 200:
                return True
            else:
                return False

        def pub_checker(publick_url):

            try:
                nedo_id = publick_url.replace('https://vk.com/', '')
                url = f'https://api.vk.com/method/groups.getById?group_id={nedo_id}&access_token={token}&v=5.131'
                r = requests.get(url)
                src = r.json()
                real_publick = src['response'][0]['id']
            except:
                return 100

        def id_checker(message): #проверка, чей это id чат
            chat_id = message.chat.id
            f = open("groups_processors/chat__id.txt", "r", encoding='utf-8')
            chat__id = f.readline()
            f.close()
            if chat__id == str(chat_id):
                return True
            else:
                return False
        def warning_message(message):
            print_time_now()
            print(f'{message.from_user.username}({message.chat.id}) пытался отправить команду')
            bot.send_message(message.chat.id, '🚫Похоже, это не твой бот!🚫\n\n(если хочешь приобрести себе такой, напиши @UnicChan)', parse_mode='html')

        @bot.message_handler(commands=['start']) #старт
        def start(message):
            chat_id = message.chat.id #id чата
            f = open("groups_processors/chat__id.txt", "r", encoding='utf-8')
            chat__id = f.readline()
            f.close()

            if chat__id == '0': #впервые записываем chat__id
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                menu = types.KeyboardButton('меню✨')

                markup.add(menu)
                print_time_now()
                print(f'{message.from_user.username}({message.chat.id}) впервые запустил бота!')
                start = bot.send_message(message.chat.id, '🦾', parse_mode='html', reply_markup=markup)
                start = bot.send_message(message.chat.id, '<b>Начнём работу!</b>', parse_mode='html', reply_markup=markup)

                f = open("groups_processors/chat__id.txt", "w", encoding='utf-8')
                chat__id = start.chat.id
                f.write(str(chat__id))
                f.close()

            elif chat__id == str(chat_id):
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                menu = types.KeyboardButton('меню✨')

                markup.add(menu)
                print_time_now()
                print(f'{message.from_user.username}({message.chat.id}) запустил бота!')
                start = bot.send_message(message.chat.id, '🦾', parse_mode='html', reply_markup=markup)
                start = bot.send_message(message.chat.id, '<b>Начнём работу!</b>', parse_mode='html', reply_markup=markup)

                f = open("groups_processors/chat__id.txt", "w", encoding='utf-8')
                chat__id = start.chat.id
                f.write(str(chat__id))
                f.close()
            else:
                print_time_now()
                print(f'{message.from_user.username}({message.chat.id}) пытался /start')
                bot.send_message(message.chat.id, '🚫Похоже, это не твой бот!🚫\n\n(если хочешь приобрести себе такой, напиши @UnicChan)', parse_mode='html')

        @bot.message_handler(content_types=['text']) #обработка сообщений
        def bot_message(message):
            if id_checker(message):

                def clear():
                    for ids in helper:
                        bot.delete_message(chat_id=message.chat.id, message_id=ids) #удаление вспомогательного сообщения

                    for ids in publos_id:
                        bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=ids, reply_markup=None) #удаление кнопок под всеми пабликами

                    what_deleting = 0 #id сообщения с пабликом, которое удаляли = 0 (на всякий случай)
                    publos_id.clear() #очищение списка id сообщений с пабликами
                    helper.clear() #очишение списка вспомогательных сообщений
                
                if message.chat.type == 'private':
                    if message.text.startswith('меню'): #меню со всеми возможностями
                        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                        publicks = types.KeyboardButton('монитор 💻')
                        noties = types.KeyboardButton('уведомления 💡')
                        mixer = types.KeyboardButton('миксер 🚫')

                        markup.add(publicks, noties, mixer)
                        bot.send_message(message.chat.id, '<b>✨меню✨</b>', parse_mode='html', reply_markup=markup)
                    elif message.text == 'уведомления 💡':
                        f = open('groups_processors/notifications_count.txt', 'r', encoding='utf-8')
                        message_count_4_noties = f.readline()
                        f.close()

                        markup = types.InlineKeyboardMarkup(row_width=2) #добаление кнопок под сообщением
                        on = types.InlineKeyboardButton('вкл', callback_data='on') #включить уведомления
                        off = types.InlineKeyboardButton('выкл', callback_data='off') #выключить уведомления
                        count = types.InlineKeyboardButton('изменить кол-во', callback_data='count') #изменить кол-во сообщений
                        markup.add(on, off, count)
                        bot.send_message(message.chat.id, f'Включить уведомления 💡, если постов набралось больше <b>{message_count_4_noties}</b>?', parse_mode='html', reply_markup=markup, disable_web_page_preview=True) #отправка паблика

                    elif message.text.startswith('монитор'): #действия со списком пабликов
                        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                        show = types.KeyboardButton('📄\nсписок пабликов')
                        add = types.KeyboardButton('➕\nпаблик')
                        show_posts = types.KeyboardButton('👀\nчек монитор')
                        menu = types.KeyboardButton('меню 🔙')
                        

                        markup.add(show, add, show_posts, menu)
                        bot.send_message(message.chat.id, '💻', parse_mode='html', reply_markup=markup)

                        clear()
                    elif message.text == '📄\nсписок пабликов': #список всех пабликов с возможностью их удаления
                        if os.path.getsize('publicks/publicks.txt') == 0:
                            markup = types.InlineKeyboardMarkup(row_width=1)
                            pusto = types.InlineKeyboardButton('0 добавленных', callback_data='adasd')
                            markup.add(pusto)

                            bot.send_message(message.chat.id, '📂', reply_markup=markup)
                        else:
                            number = 0
                            with open('publicks/publicks.txt', 'r', encoding='utf-8') as list_of_pub:
                                for line in list_of_pub:
                                    number += 1
                                    markup = types.InlineKeyboardMarkup(row_width=1) #добаление кнопок под каждым пабликом
                                    delete = types.InlineKeyboardButton('убрать из монитора', callback_data=f'del{number}') #удалить паблик из списка
                                    markup.add(delete)
                                    publos = bot.send_message(message.chat.id, line.strip(), reply_markup=markup, disable_web_page_preview=True) #отправка паблика
                                    publos_id.append(publos.id) #добавление id сообщения с пабликом

                            markup = types.ReplyKeyboardMarkup(resize_keyboard=True) #если ничего не надо делать со списком пабликов
                            publicks = types.KeyboardButton('монитор 🔙')
                            markup.add(publicks)
                            mini_helper = bot.send_message(message.chat.id, '<b>(если ничего не хочешь менять, переходи назад)</b>', parse_mode='html', reply_markup=markup)
                            helper.append(mini_helper.id)

                    elif message.text == '👀\nчек монитор': #показать спарсенные посты
                        if os.path.getsize('publicks/publicks.txt') == 0:
                            markup = types.InlineKeyboardMarkup(row_width=1)
                            pusto = types.InlineKeyboardButton('0 добавленных', callback_data='adasd')
                            markup.add(pusto)

                            bot.send_message(message.chat.id, '📂', reply_markup=markup)
                        else:
                            publicks_count = len(re.findall(r"[\n']+", open('publicks/publicks.txt').read())) + 1
                            for publick_number in range(1, publicks_count): #номер паблика в порядке возрастания
                                with open('publicks/publicks.txt', 'r', encoding='utf-8') as file:
                                    lines = file.readlines()
                                    file.close()
                                    posts_count = 0 #счётчик постов

                                    f = open("publicks/publicks.txt", "r", encoding='utf-8') #убираем строку из файла
                                    lines = f.readlines()
                                    f.close()

                                    for line in lines:
                                        if str(publick_number) == line.partition(':')[0]: #найти строчку, номер которой == publick_number

                                            #найти кол-во постов
                                            strin = f'{publick_number}: https://vk.com/' #строчка, которую нужно будет отсечь от строки файла со списком пабликов
                                            group_name = line.replace(strin, '')
                                            group_name = group_name.replace("\n", '') #название паблика
                                            f = open(f"publicks/{group_name}.txt", "r", encoding='utf-8') #убираем строку из файла
                                            posts_text = f.readlines()
                                            f.close()
                                            for text in posts_text:
                                                if text == '----------\n':
                                                    posts_count += 1

                                            line = line.replace(f'{publick_number}: ', '')

                                            markup = types.InlineKeyboardMarkup(row_width=1) #добаление кнопок под каждым пабликом
                                            show_posts = types.InlineKeyboardButton(f'{posts_count} new', callback_data=f'show{publick_number}') #показать посты
                                            markup.add(show_posts)
                                            stealled = bot.send_message(message.chat.id, line.strip(), reply_markup=markup, disable_web_page_preview=True) #отправка паблика
                                            stealed_posts.append(stealled.id) #добавление id сообщения с пабликом

                    elif message.text == '➕\nпаблик': #добавить паблик в список монитора

                        # функции по обработке +паблик
                        @bot.message_handler(func=lambda message: True) # 'скинь ссылку на паблик' + функция по обратоке ссылки + изменение кол-ва сообщений для уведомлений
                        def url_plus(message):
                            if len(re.findall(r"[\n']+", open('publicks/publicks.txt').read())) >= pub_limit:
                                bot.send_message(message.chat.id, '🚫Ты уже мониторишь максимальное количсество пабликов🚫\n\nЕсли хочешь добавить больше, напиши @UnicChan', parse_mode='html')
                            else:
                                sent = bot.send_message(message.chat.id, '<em>Скинь ссылку на паблик</em>', parse_mode='html')
                                bot.register_next_step_handler(sent, save_link)

                        def save_link(message): #обработка ссылки и добавление её в список монитора
                            publick_link = message.text
                            if publick_link.startswith('https://vk.com/'): #если ссылка корректна
                                if pub_checker(publick_link) != 100 : #проверить, существует ли вообще такой паблик
                                    how_many_lines = sum(1 for line in open('publicks/publicks.txt', 'r', encoding='utf-8')) + 1

                                    #проверка паблика
                                    f = open('publicks/publicks.txt', 'r', encoding='utf-8')
                                    check = f.readlines()
                                    f.close()

                                    if check == []: #если это вообще первый паблик
                                        with open('publicks/new_publick.txt', 'w', encoding='utf-8') as file:
                                            file.write(publick_link)
                                            file.close()
                                        with open('publicks/publicks.txt', 'a', encoding='utf-8') as file:
                                            file.write(str(how_many_lines) + ": " + publick_link + "\n") #добавление ссылки на паблик в каталог монитора
                                            file.close()
                                        bot.send_message(message.chat.id, "<em>Добавлено в монитор!</em>", parse_mode='html')
                                        new_publick = open(f"publicks/{publick_link.replace('https://vk.com/', '')}.txt", "w", encoding='utf-8') #создать txt с id пабликом в названии
                                    else:
                                        publicks_count = 0
                                        exist = False
                                        for line in check:
                                            publicks_count += 1
                                            strin = f'{publicks_count}: ' #строчка, которую нужно будет отсечь
                                            publick = line.replace(strin, '') 
                                            publick = publick.replace("\n", '') #ссылка паблика
                                            if publick_link == publick: #если уже мониторится паблик
                                                exist = True
                                                bot.send_message(message.chat.id, "Такой паблик уже в мониторе!\n\n(если ты передумал, нажми на любую кнопку)")
                                                url_plus(message)
                                                print_time_now()
                                                print(f'пытался добавить существующий паблик: {publick_link}')
                                            else:
                                                pass

                                        if exist == False:   
                                            with open('publicks/new_publick.txt', 'w', encoding='utf-8') as file:
                                                file.write(publick_link)
                                                file.close()
                                            with open('publicks/publicks.txt', 'a', encoding='utf-8') as file:
                                                file.write(str(how_many_lines) + ": " + publick_link + "\n") #добавление ссылки на паблик в каталог монитора
                                                file.close()
                                            bot.send_message(message.chat.id, "<em>Добавлено в монитор!</em>", parse_mode='html')
                                            new_publick = open(f"publicks/{publick_link.replace('https://vk.com/', '')}.txt", "w", encoding='utf-8') #создать txt с id пабликом в названии
                                else:
                                    bot.send_message(message.chat.id, "С пабликом что-то не так...\nПожалуйста, проверь, всё ли правильно и попробуй снова")
                                    url_plus(message)
                            elif publick_link.startswith('меню 🔙') or publick_link.startswith('📄\nсписок пабликов') or publick_link.startswith('➕\nпаблик') or publick_link.startswith('👀\nчек монитор'):
                                pass
                            else: #если ссылка некорректна
                                bot.send_message(message.chat.id, "Пожалуйста, отправь ссылку в формате: \nhttps://vk.com/id_паблика\n\n(если ты передумал, нажми на любую кнопку)")
                                url_plus(message)
            
                        url_plus(message)

                    elif message.text.startswith('миксер'):
                        bot.send_message(message.chat.id, '🚫Функция недоступна🚫\n\nЕсли хочешь её добавить, напиши @UnicChan') 
                    else:
                        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                        publicks = types.KeyboardButton('монитор 💻')
                        noties = types.KeyboardButton('уведомления 💡')
                        mixer = types.KeyboardButton('миксер ⌨️')

                        markup.add(publicks, noties, mixer)
                        bot.send_message(message.chat.id, 'Что-то не так? Лови\n       <b>✨меню✨</b>', parse_mode='html', reply_markup=markup)
                else:
                    bot.send_message(message.chat.id, '🚫Только личка!🚫')
            else:
                warning_message(message)

        @bot.callback_query_handler(func=lambda call: True) #обработка inline кнопок
        def callback_inline(call):
            try:
                if call.message:
                    
                    def clear(message_id, txt):
                        f = open("groups_processors/chat__id.txt", "r", encoding='utf-8')
                        chat__id = f.readline()
                        f.close()
                        for ids in publos_id:
                            bot.edit_message_reply_markup(chat_id=chat__id, message_id=ids, reply_markup=None) #удаление кнопок под всеми пабликами

                        for ids in helper:
                            bot.delete_message(chat_id=chat__id, message_id=ids) #удаление вспомогательного сообщения

                        bot.edit_message_text(chat_id=chat__id, message_id=message_id, text=f'<s>убран из {txt}</s>', parse_mode='html', reply_markup=None) #изменение ссылки паблика 

                        what_deleting = 0 #id сообщения с пабликом, которое удаляли = 0 (на всякий случай)
                        publos_id.clear() #очищение списка id сообщений с пабликами
                        helper.clear() #очишение списка вспомогательных сообщений

                    if call.data == 'count': #если хочет изменить кол-во сообщений для уведомлений

                        #функции по обработке изменения уведомлений
                        @bot.message_handler(func=lambda message: True)
                        def input_count(message):
                            sent = bot.send_message(message.chat.id, "Сколько сообщений ты хочешь?")
                            bot.register_next_step_handler(sent, reg_count)
                        def reg_count(message):
                            if message.text.isdigit(): #если в строке только цифры
                                if int(message.text) < 59:
                                    f = open('groups_processors/notifications_count.txt', 'w')
                                    f.write(message.text)
                                    f.close()
                                    bot.send_message(message.chat.id, f"Окей, я поменял. Можешь спать спокойно")
                                else:
                                    f = open('groups_processors/notifications_count.txt', 'w')
                                    f.write(message.text)
                                    f.close()
                                    bot.send_message(message.chat.id, "🫠")
                                    bot.send_message(message.chat.id, f"Хз, зачем вообще тебе уведомления, но окей\n\n\n(можешь выключить уведомления, есчё)")
                            else:
                                bot.send_message(message.chat.id, "Пожалуйста, только цифры")
                                input_count(message)

                        input_count(call.message)

                    if call.data == 'photo_count': #если хочет изменить кол-во фото в миксере

                        #функции по обработке изменения уведомлений
                        @bot.message_handler(func=lambda message: True)
                        def input_count(message):
                            sent = bot.send_message(message.chat.id, "Сколько фотографий должно быть в отправленном посте?")
                            bot.register_next_step_handler(sent, reg_count)
                        def reg_count(message):
                            if message.text.isdigit(): #если в строке только цифры
                                if 0 < int(message.text) <= 9:
                                    f = open('mixer/photo_count.txt', 'w', encoding='utf-8')
                                    f.write(message.text)
                                    f.close()
                                    if message.text == '1':
                                        bot.send_message(message.chat.id, f"Окей, запомнил. В предложку будут приходить посты с {message.text} фотографией")
                                    else:
                                        bot.send_message(message.chat.id, f"Окей, запомнил. В предложку будут приходить посты с {message.text} фотографиями")
                                elif int(message.text) > 9:
                                    bot.send_message(message.chat.id, "Ты же знаешь, что в вк нельзя делать посты с более чем 9-ю фотографиями!")
                                elif int(message.text) == 0:
                                    bot.send_message(message.chat.id, "0 фотографий в посте? Тогда отключи 'фотографии' в опциях миксера.")
                            else:
                                bot.send_message(message.chat.id, "Пожалуйста, только цифры")
                                input_count(message)

                        input_count(call.message)

                    if call.data == 'on':
                        f = open('groups_processors/notifications.txt', 'w', encoding='utf-8')
                        f.write('on')
                        f.close()
                        bot.send_message(chat_id=call.message.chat.id, text='Оповещения включены!', parse_mode='html')
                    elif call.data == 'off':
                        f = open('groups_processors/notifications.txt', 'w', encoding='utf-8')
                        f.close()
                        bot.send_message(chat_id=call.message.chat.id, text='Оповещения выключены!', parse_mode='html')
                    elif call.data == 'ok': #оповещение о набравшемся кол-ве сообщений
                        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
                    #если пользователь хочет очистить историю постов
                    elif call.data == 'clear_posts':
                        #очищаем посты
                        publick = call.message.text.replace('https://vk.com/', '')
                        f = open(f'publicks/{publick}.txt', 'w', encoding='utf-8')
                        f.close()

                        #изменение кол-ва постов 'new' на zero
                        markup = types.InlineKeyboardMarkup(row_width=1) #обновление кнопки под нажатым пабликом
                        zero = types.InlineKeyboardButton('0 new', callback_data='zero')
                        markup.add(zero)

                        bot.send_message(chat_id=call.message.chat.id, text='<b>Очищено! Теперь будем ждать, когда появятся новые!</b>\n(можешь включить уведомления 💡, чтобы не пропустить)', parse_mode='html')
                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'<em>{call.message.text}</em>', parse_mode='html', reply_markup=markup, disable_web_page_preview=True)

                    #удаление паблика из списка /// вывод накопленных постов каждого паблика
                    what_deleting = call.message.message_id

                    for num in range(1000):
                        #если кнопка "показать посты"
                        if call.data == f'show{num}':
                            #находим название паблика
                            f = open("publicks/publicks.txt", "r", encoding='utf-8')
                            lines = f.readlines()
                            f.close()

                            for line in lines:
                                if str(num) == line.partition(':')[0]: #найти строчку, номер которой == publick_number

                                    strin = f'{num}: https://vk.com/' #строчка, которую нужно будет отсечь от строки файла со списком пабликов
                                    group_name = line.replace(strin, '') 
                                    group_name = group_name.replace("\n", '') #название паблика

                            #достаём посты и выводим их на экран
                            f = open(f"publicks/{group_name}.txt","r", encoding='utf-8') 
                            lines = f.readlines()
                            f.close()
                            photo = []
                            for line in lines:
                                if line == '----------\n':
                                    #отправляем текст поста
                                    file = open('groups_processors/2send.txt', 'r', encoding='utf-8')
                                    send_lines = file.readlines()
                                    file.close
                                    if len(send_lines) == 0:
                                        print('странно, но пост пустой.')
                                        pass
                                    else:
                                        if len(photo) != 0:
                                            ph = 0
                                            for this in photo:
                                                p = requests.get(this)
                                                out = open(f"images/{ph}.jpg", "wb")
                                                out.write(p.content)
                                                out.close()
                                                ph += 1
                                            symbols = 0
                                            for lin in send_lines:
                                                symbols += len(lin)
                                            if symbols >= 1024:
                                                #1 половина текста
                                                send_line = ''
                                                symb = 0
                                                while symb < 900:
                                                    for o in send_lines:
                                                        for i in range(len(o)):
                                                            send_line = send_line + o[i]
                                                            symb += 1
                                                            if symb > 900:
                                                                break
                                                test_text = ''.join(send_line)
                                                send_group_img(test_text)

                                                path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'images')
                                                shutil.rmtree(path)
                                                os.mkdir('images')
                                                #2 половина текста
                                                send_line = ''
                                                while symb < symbols:
                                                    for o in send_lines:
                                                        for i in range(len(o)):
                                                            send_line = send_line + o[i]
                                                            symb += 1
                                                bot.send_message(chat_id=call.message.chat.id, text=''.join(send_line), parse_mode='html', disable_web_page_preview=True)
                                            else:
                                                test_text = ''.join(send_lines)
                                                send_group_img(test_text)
                                                path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'images')
                                                shutil.rmtree(path)
                                                os.mkdir('images')
                                            photo.clear()
                                        else:
                                            bot.send_message(chat_id=call.message.chat.id, text=''.join(send_lines), parse_mode='html', disable_web_page_preview=True)

                                        bot.send_message(chat_id=call.message.chat.id, text='-------конец_поста-------')

                                    #очищение 2send.txt для следующего поста
                                    f = open('groups_processors/2send.txt', 'w', encoding='utf-8')
                                    f.close()
                                else:
                                    f = open('groups_processors/2send.txt', 'a', encoding='utf-8')
                                    if line.startswith('<b>ФОТО:</b> '): #если попалось фото
                                        photo2add = line.replace('<b>ФОТО:</b> ', '')
                                        photo2add = photo2add.replace('\n', '')
                                        photo.append(photo2add)
                                        f.close()
                                    elif line.startswith('id поста: '): #если попаласт строка с id поста
                                        pass
                                    else:
                                        f.write(line)
                                        f.close()

                            #изменение сообщения со ссылкой на группу, посты которой выведены
                            markup = types.InlineKeyboardMarkup(row_width=1) #обновление кнопки под нажатым пабликом
                            clear_posts = types.InlineKeyboardButton('очистить посты', callback_data=f'clear_posts') #очистить посты
                            markup.add(clear_posts)

                            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"<em>{call.message.text}</em>", parse_mode='html', reply_markup=markup, disable_web_page_preview=True)


                            what_deleting = 0 #id сообщения с пабликом, которое удаляли = 0 (на всякий случай)
                            stealed_posts.clear() #очищение списка id сообщений с пабликами


                        #если кнопка "удалить пост из списка монитора"
                        elif call.data == f'del{num}':
                            #удаляем файлы, связанные с этим пабликом
                            f = open("publicks/publicks.txt", "r", encoding='utf-8')
                            lines = f.readlines()
                            f.close()
                            group_name = ''
                            for line in lines:
                                if str(num) == line.partition(':')[0]: #найти строчку, номер которой == publick_number

                                    strin = f'{num}: https://vk.com/' #строчка, которую нужно будет отсечь от строки файла со списком пабликов
                                    group_name = line.replace(strin, '') 
                                    group_name = group_name.replace("\n", '') #название паблика
                            print_time_now()
                            print(f'удалил паблик из моника: {group_name}')
                            os.remove(f'publicks/{group_name}.txt')
                            os.remove(f'groups_processors/{group_name}_id.txt')
                            os.remove(f'groups_processors/{group_name}_timer.txt')

                            #убираем строку из монитора
                            f = open("publicks/publicks.txt", "r", encoding='utf-8')
                            lines = f.readlines()
                            f.close()
                            f = open("publicks/publicks.txt", "w", encoding='utf-8')
                            for line in lines:
                                if line.partition(':')[0]!=f"{num}" :
                                    f.write(line)
                            f.close()
                            
                            #переделываем список монитора
                            f = open("publicks/publicks.txt", "r", encoding='utf-8') 
                            lines = f.readlines()
                            f.close()
                            f = open("publicks/publicks.txt", "w", encoding='utf-8')
                            for line in lines:
                                remake = ''
                                if int(line.partition(':')[0]) < num:
                                    f.write(line)
                                elif int(line.partition(':')[0]) - 1 == num:
                                    # remake = remake + str(num)
                                    # for i in range(1, len(line)):
                                    #     remake = remake + line[i]
                                    # f.write(remake)
                                    # remake = ''
                                    remake += f'{num}:'
                                    remake += line.partition(':')[2]
                                    f.write(remake)
                                else:
                                    replace2 = int(line.partition(':')[0]) - 1
                                    remake += str(replace2)
                                    # for i in range(1, len(line)):
                                    #     remake = remake + line[i]
                                    # f.write(remake)
                                    remake += f":{line.partition(':')[2]}"
                                    f.write(remake)
                            f.close()

                            text = 'монитора'
                            clear(call.message.message_id, text)

            except Exception as e:
                print_time_now()
                print(f'ошибка в обработке inline кнопки!\n{repr(e)}')   

        bot.polling(none_stop=True)

    except Exception as e:
        print(e)
        print_time_now()
        print('произошла ошибка! рестарт через 10 секунд!')
        time.sleep(10)