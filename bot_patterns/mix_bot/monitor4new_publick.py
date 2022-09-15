import requests
from time import sleep
import os
from datetime import datetime

#переменные
from params import my_token

token = my_token

access = True

def print_time_now():
    time = datetime.now()
    time = time.strftime('%m-%d %H:%M:%S')
    print(f'--{time}--')

while access:

    if os.path.getsize('publicks/new_publick.txt') == 0:
        sleep(1)
        pass
    else:
        #обрабатываем паблик
        f = open("publicks/new_publick.txt","r", encoding='utf-8') 
        publick = f.readline()
        f.close()
        
        publick = publick.replace('https://vk.com/', '') #id паблика
        print_time_now()
        print(publick)

        url = f'https://api.vk.com/method/wall.get?domain={publick}&count=10&access_token={token}&v=5.131'
        r = requests.get(url)
        src = r.json()
        # print(r.text) #посмотреть json code

        posts = src['response']['items']
        
        ######

        #добавление id новых постов

        fresh_posts_id = []
        change = False

        if not os.path.exists(f'groups_processors/{publick}_timer.txt'): #проверить, существует ли файл с новейшей датой поста

            #создаём файл
            with open(f'groups_processors/{publick}_timer.txt', 'w', encoding='utf-8') as file:
                if int(posts[0]['date']) < int(posts[1]['date']):
                    date = posts[1]['date']
                else:
                    date = posts[0]['date']
                file.write(str(date)) #добавляем дату
                file.close()

            #добавление 1 поста в список фреш постов
            fresh_post_id = posts[0]
            fresh_posts_id.append(fresh_post_id)
            print('впервые добавляется пост.')

            change = False #заменять дату не нужно, потому что её и не было.
        else: 
            print(f'хз, но файлы паблика {publick} уже существуют...')

        #если новых постов не появилось, то ничего не делаем.если же есть, то идём дальше по коду
        if len(fresh_post_id) == 0: #проверь, выполняется ли это условие
            break
        else:
            #изменяем дату свежего поста (или нет)
            if change:

                f = open(f'groups_processors/{publick}_timer.txt', 'w', encoding='utf-8')
                if int(posts[0]['date']) < int(posts[1]['date']):
                    date = posts[1]['date']
                else:
                    date = posts[0]['date']
                f.write(str(date))
                f.close()


            #записываем в файл группы посты в виде кода, чтобы обработать 
            with open(f'groups_processors/{publick}_id.txt', 'w', encoding='utf-8') as file:
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
                file = open(f'publicks/{publick}.txt', 'a', encoding='utf-8')
                file.write(f'id поста: {post_id}' + '\n')
                file.close()

                try:
                    #забираем текст
                    if post['text'] != "":
                        text = post['text']
                        # print('ТЕКСТ: ', text)
                        file = open(f'publicks/{publick}.txt', 'a', encoding='utf-8')
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
                                file = open(f'publicks/{publick}.txt', 'a', encoding='utf-8')
                                file.write(f'\n<b>ФОТО:</b> {photo_url}' + '\n')
                                file.close()
                            elif post[0]['type'] == 'video': #если видео
                                post_with_video = post[0]['video']
                                video_url = f'https://vk.com/{publick}?z=video{post_with_video["owner_id"]}_{post_with_video["id"]}%{post_with_video["access_key"]}%2Fpl_wall_{post_with_video["owner_id"]}'
                                # print('ВИДЕО: ', video_url)
                                file = open(f'publicks/{publick}.txt', 'a', encoding='utf-8')
                                file.write(f'\n<b>ВИДЕО:</b> {video_url}' + '\n')
                                file.close()
                            elif post[0]['type'] == 'audio': #если трек
                                post_with_audio = post[0]['audio']
                                audio_url = f'https://vk.com/audio{post_with_audio["owner_id"]}_{post_with_audio["id"]}'
                                # print(audio_url)
                                file = open(f'publicks/{publick}.txt', 'a', encoding='utf-8')
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
                                    file = open(f'publicks/{publick}.txt', 'a', encoding='utf-8')
                                    file.write(f'\n<b>ФОТО:</b> {photo_url}' + '\n')
                                    file.close()
                                elif post_item['type'] == 'video': #если нашлось видео
                                    post_with_video = post_item['video']
                                    video_url = f'https://vk.com/{publick}?z=video{post_with_video["owner_id"]}_{post_with_video["id"]}%{post_with_video["access_key"]}%2Fpl_wall_{post_with_video["owner_id"]}'
                                    # print('ВИДЕО: ', video_url)
                                    file = open(f'publicks/{publick}.txt', 'a', encoding='utf-8')
                                    file.write(f'\n<b>ВИДЕО:</b> {video_url}' + '\n')
                                    file.close()
                                elif post_item['type'] == 'audio': #если аудио
                                    post_with_audio = post_item['audio']
                                    audio_url = f'https://vk.com/audio{post_with_audio["owner_id"]}_{post_with_audio["id"]}'
                                    # print('ТРЕК: ', audio_url)
                                    file = open(f'publicks/{publick}.txt', 'a', encoding='utf-8')
                                    file.write(f'\n<b>ТРЕК:</b> {audio_url}' + '\n')
                                    file.close()
                
                except Exception:
                    print('хз, но что-то не так с постом')

                file = open(f'publicks/{publick}.txt', 'a', encoding='utf-8')
                file.write('----------' + '\n')
                file.close()
    

            #очищаем файл от постов
            with open(f'groups_processors/{publick}_id.txt', 'w', encoding='utf-8') as file:
                file.close()
            #очищаем файл new_publick.txt
            with open(f'publicks/new_publick.txt', 'w', encoding='utf-8') as file:
                file.close()