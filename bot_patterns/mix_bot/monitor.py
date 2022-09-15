import requests
from time import sleep
import os
import re
from datetime import datetime, timedelta

#переменные
from params import my_token, timer

token = my_token
sleeper = timer

def print_time_now():
    time = datetime.now()
    time = time.strftime('%m-%d %H:%M:%S')
    print(f'--{time}--')

def check_timer():
    if os.path.getsize('groups_processors/monitor_timer.txt') == 0:
        return True
    else:
        f = open('groups_processors/monitor_timer.txt', 'r', encoding='utf-8')
        timer = f.readline()
        f.close
        timer = datetime.strptime(timer, '%Y-%m-%d %H:%M:%S.%f')

        if timer < datetime.now() + timedelta(hours=sleeper):
            sleep(600)
            return False
        else:
            return True

while True:
    try:

        if len(os.listdir('./publicks')) == 2:
            sleep(5)
            pass
        elif check_timer():
            #сколько всего пабликов обработать нужно
            publicks_count = len(re.findall(r"[\n']+", open('publicks/publicks.txt').read())) + 1 

            #обрабатываем каждый паблик
            for pub in range(publicks_count - 1):
                #достаём id паблика из списка
                f = open("publicks/publicks.txt","r", encoding='utf-8') 
                lines = f.readlines()
                f.close()
                
                publick = lines[pub]
                strin = f'{pub+1}: https://vk.com/' #строчка, которую нужно будет отсечь от строки файла со списком пабликов
                group_name = publick.replace(strin, '') 
                group_name = group_name.replace("\n", '') #id паблика
                print_time_now()
                print(f'{group_name}')

                url = f'https://api.vk.com/method/wall.get?domain={group_name}&count=10&access_token={token}&v=5.131'
                r = requests.get(url)
                src = r.json()
                # print(r.text) #посмотреть json code

                posts = src['response']['items']
                
                ######

                #добавление id новых постов

                fresh_posts_id = []
                change = False

                if True: #если уже сущетсвует файл с датой

                    with open(f'groups_processors/{group_name}_timer.txt', 'r', encoding='utf-8') as file:
                        past_date = file.read() #достаём прошлую "свежую" дату
                        file.close()

                    #сравниваем даты у постов
                    for fresh_post_id in posts:
                        if int(fresh_post_id['date']) > int(past_date):
                                add_id = fresh_post_id['id']
                                fresh_posts_id.append(add_id)
                                print(f'id поста: {add_id}')
                    print('прибавилось постов:')
                    print(len(fresh_posts_id))

                    if len(fresh_posts_id) > 0:
                        change = True #заменять дату нужно

                #если новых постов не появилось, то ничего не делаем.если же есть, то идём дальше по коду
                if len(fresh_post_id) == 0: #проверь, выполняется ли это условие
                    break
                else:
                    #изменяем дату свежего поста (или нет)
                    if change:

                        f = open(f'groups_processors/{group_name}_timer.txt', 'w', encoding='utf-8')
                        if int(posts[0]['date']) < int(posts[1]['date']):
                            date = posts[1]['date']
                        else:
                            date = posts[0]['date']
                        f.write(str(date))
                        f.close()


                    #записываем в файл группы посты в виде кода, чтобы обработать 
                    with open(f'groups_processors/{group_name}_id.txt', 'w', encoding='utf-8') as file:
                        for item in fresh_posts_id:
                            file.write(str(item) + '\n')
                        file.close()

                    #извлекаем данные из постов

                    for post in fresh_posts_id:

                        #небольшой костыль. можно забить(наверное...)
                        for this in posts: 
                            if this['id'] == post:
                                post = this

                        post_id = post['id']
                        file = open(f'publicks/{group_name}.txt', 'a', encoding='utf-8')
                        file.write(f'id поста: {post_id}' + '\n')
                        file.close()

                        try:
                            #забираем текст
                            if post['text'] != "":
                                text = post['text']
                                # print('ТЕКСТ: ', text)
                                file = open(f'publicks/{group_name}.txt', 'a', encoding='utf-8')
                                file.write(f'\n<b>ТЕКСТ:</b> {text}' + '\n')
                                file.close()

                            #забираем всё остальное
                            if 'attachments' in post:
                                post = post['attachments']

                                #если 1 вложение
                                if len(post) == 1:
                                    if post[0]['type'] == 'photo':  #если фото
                                        sizes_count = len(post[0]['photo']['sizes']) - 1

                                        post_with_photo = post[0]['photo']['sizes']
                                        photo_url = post_with_photo[sizes_count]['url']
                                        # print(photo_url)
                                        file = open(f'publicks/{group_name}.txt', 'a', encoding='utf-8')
                                        file.write(f'\n<b>ФОТО:</b> {photo_url}' + '\n')
                                        file.close()
                                    elif post[0]['type'] == 'video': #если видео
                                        post_with_video = post[0]['video']
                                        video_url = f'https://vk.com/{group_name}?z=video{post_with_video["owner_id"]}_{post_with_video["id"]}%{post_with_video["access_key"]}%2Fpl_wall_{post_with_video["owner_id"]}'
                                        # print('ВИДЕО: ', video_url)
                                        file = open(f'publicks/{group_name}.txt', 'a', encoding='utf-8')
                                        file.write(f'\n<b>ВИДЕО:</b> {video_url}' + '\n')
                                        file.close()
                                    elif post[0]['type'] == 'audio': #если трек
                                        post_with_audio = post[0]['audio']
                                        audio_url = f'https://vk.com/audio{post_with_audio["owner_id"]}_{post_with_audio["id"]}'
                                        # print(audio_url)
                                        file = open(f'publicks/{group_name}.txt', 'a', encoding='utf-8')
                                        file.write(f'\n<b>ТРЕК:</b> {audio_url}' + '\n')
                                        file.close()
                                #если больше 1 вложения
                                else:
                                    for post_item in post:
                                        if post_item['type'] == 'photo': #если нашлось фото
                                            sizes_count = len(post_item['photo']['sizes']) - 1
                                            post_with_photo = post_item['photo']['sizes']
                                            photo_url = post_with_photo[sizes_count]['url']
                                            # print('ФОТО: ', photo_url)
                                            file = open(f'publicks/{group_name}.txt', 'a', encoding='utf-8')
                                            file.write(f'\n<b>ФОТО:</b> {photo_url}' + '\n')
                                            file.close()
                                        elif post_item['type'] == 'video': #если нашлось видео
                                            post_with_video = post_item['video']
                                            video_url = f'https://vk.com/{group_name}?z=video{post_with_video["owner_id"]}_{post_with_video["id"]}%{post_with_video["access_key"]}%2Fpl_wall_{post_with_video["owner_id"]}'
                                            # print('ВИДЕО: ', video_url)
                                            file = open(f'publicks/{group_name}.txt', 'a', encoding='utf-8')
                                            file.write(f'\n<b>ВИДЕО:</b> {video_url}' + '\n')
                                            file.close()
                                        elif post_item['type'] == 'audio': #если аудио
                                            post_with_audio = post_item['audio']
                                            audio_url = f'https://vk.com/audio{post_with_audio["owner_id"]}_{post_with_audio["id"]}'
                                            # print('ТРЕК: ', audio_url)
                                            file = open(f'publicks/{group_name}.txt', 'a', encoding='utf-8')
                                            file.write(f'\n<b>ТРЕК:</b> {audio_url}' + '\n')
                                            file.close()
                        
                        except Exception:
                            print('хз, но что-то не так с постом')

                        file = open(f'publicks/{group_name}.txt', 'a', encoding='utf-8')
                        file.write('----------' + '\n')
                        file.close()
            
                    #очищаем файл от постов
                    with open(f'groups_processors/{group_name}_id.txt', 'w', encoding='utf-8') as file:
                        file.close()

                    #задержка перед следующим пабликом
                    sleep(3)
                    
            f = open('groups_processors/monitor_timer.txt', 'w', encoding='utf-8')
            f.write(str(datetime.now()))
            f.close()

    except Exception as e:
        print(e)
        print_time_now()
        print('ошибка в мониторе! рестарт через 10 секунд')
        sleep(10)