import requests
from time import sleep
import random
from params import my_token, timer
import os
from datetime import datetime, timedelta

token = my_token
sleeper = timer

def print_time_now():
    time = datetime.now()
    time = time.strftime('%m-%d %H:%M:%S')
    print(f'--{time}--')

def id_checker(line): #проверка id на наличие в списке использованных постов
    current_id = line.replace('id поста: ', '') 
    f = open('mixer/used_posts_id.txt', 'r', encoding='utf-8')
    all_ids = f.readlines()
    f.close()
    aviable = False
    if all_ids == []: #чистый список id
        pass
    else:
        for this in all_ids: #смотрим, найдётся ли этот id в списке
            if this == current_id:
                aviable = True
                break
            else:
                pass
    if aviable: #если нашёлся
        pass
    else:# если не нашёлся (пост ещё не был добавлен в миксер)
        f = open('mixer/used_posts_id.txt', 'a', encoding='utf-8') #добавляем id поста в список
        f.write(f'{current_id}') 
        f.close
    return aviable
def pht_switch(): #вкл/выкл фото
    if os.path.getsize('mixer/photo_switcher.txt') == 0:
        return False
    else:
        return True
def pht_cnt():    #кол-во фото
    f = open('mixer/photo_count.txt', 'r', encoding='utf-8')
    cnt = f.readline()
    f.close
    return int(cnt)
def mus_switch(): #вкл/выкл музыка
    if os.path.getsize('mixer/music_switcher.txt') == 0:
        return False
    else:
        return True
def vid_switch(): #вкл/выкл видео
    if os.path.getsize('mixer/video_switcher.txt') == 0:
        return False
    else:
        return True
def content_delete(cntnt): #удалить строчку контента в миксере
    f = open('mixer/mixer.txt', 'r', encoding='utf-8')
    all_content = f.readlines()
    f.close()
    f = open('mixer/mixer.txt', 'w', encoding='utf-8')
    for content in all_content:
        if content != cntnt:
            f.write(content)
    f.close()
def get_photo_content(publick, id_): #получить данные фото для последующей отправки в reauest.get
    id_.replace('id поста: ', '')
    id_.replace('\n', '')

    #id группы
    url = f'https://api.vk.com/method/groups.getById?group_id={publick}&access_token={token}&v=5.131'
    r = requests.get(url)
    src = r.json()
    publick_id = src['response'][0]['id']

    #вытягиваем данные фото
    url = f'https://api.vk.com/method/wall.getById?posts=-{publick_id}_{id_}&access_token={token}&v=5.131'
    r = requests.get(url)
    src = r.json()

    photos = []
    this = src['response'][0]
    this = this['attachments']
    for item in this:
        if item['type'] == 'photo': #если нашлось фото
            sizes_count = len(item['photo']['sizes']) - 1
            post_with_photo = item['photo']['sizes']
            owner_id = item['photo']['owner_id']
            _id = item['photo']['id']
            photo = f'photo{owner_id}_{_id}\n'
            photos.append(photo)
    sleep(1)
    return photos
def get_video_content(url2check): #получить данные видео для последующей отправки в reauest.get
    url2check = url2check.partition('%')[0]
    url2check = url2check.partition('?z=')[2]
    url2check += '\n'
    return url2check

def check_timer():
    if os.path.getsize('sender/sender_timer.txt') == 0:
        return True
    else:
        f = open('sender/sender_timer.txt', 'r', encoding='utf-8')
        timer = f.readline()
        f.close
        timer = datetime.strptime(timer, '%Y-%m-%d %H:%M:%S.%f')

        if timer < datetime.now() + timedelta(hours=sleeper):
            sleep(600)
            return False
        else:
            return True

while True:

    f = open('sender/from_here/from_here.txt', 'r', encoding='utf-8')
    groups = f.readlines()
    f.close
    how_many = 0
    for group in groups:
        how_many += 1

    if how_many < 2: #если добавлено < 2 групп
        sleep(300)
        pass
    elif check_timer():
        if os.path.getsize('sender/to_here/to_here.txt') == 0:
            sleep(300)
            pass
        else:
            print_time_now()
            #сбор контента
            for group in groups:
                group_name = group.partition('https://vk.com/')[2]
                group_name = group_name.replace("\n", '') #название группы
                #копируем посты из монитора паблика в общий файл с миксом
                f = open(f'publicks/{group_name}.txt', 'r', encoding='utf-8')
                posts_text = f.readlines()
                f.close

                _2_mix_ = True #нужно ли отправлять контент в миксер
                photos_taken = False
                for line in posts_text:
                    if line.startswith('id поста:'): #смотрим, скопирован ли уже этот пост
                        photos_taken = False
                        id_ = ''
                        if id_checker(line):
                            _2_mix_ = False #нужно пропустить все строки и ничего не записывать
                        else:
                            _2_mix_ = True #добавляем нужную инфу из поста в миксер
                            id_ = line.replace('id поста: ', '')
                            id_ = id_.replace('\n', '')
                            print(f'сбор контента из: {group_name}')
                    if _2_mix_:
                        if line.startswith('<b>ФОТО:</b> ') and pht_switch() and photos_taken == False:
                            photos = get_photo_content(group_name, id_)
                            f = open('mixer/content2mix.txt', 'a', encoding='utf-8')
                            for photo in photos:
                                f.write(photo)
                            f.close()
                            photos_taken = True
                        elif line.startswith('<b>ВИДЕО:</b> ') and vid_switch():
                            url2check = line.replace('<b>ВИДЕО:</b> ', '')
                            video = get_video_content(url2check)
                            f = open('mixer/content2mix.txt', 'a', encoding='utf-8')
                            f.write(video)
                            f.close()
                        elif line.startswith('<b>ТРЕК:</b> ') and mus_switch():
                            audio = line.replace('<b>ТРЕК:</b> https://vk.com/', '')
                            f = open('mixer/content2mix.txt', 'a', encoding='utf-8')
                            f.write(audio)
                            f.close()
                        else:
                            pass

            #начало микса

            f = open('mixer/content2mix.txt', 'r', encoding='utf-8')
            content = f.readlines()                                      #достаём новый контент
            f.close()
            f = open('mixer/content2mix.txt', 'w', encoding='utf-8')     #очищаем файл с контентом
            f.close()
            random.shuffle(content)                                      #перемешиваем контент
            f = open('mixer/mixer.txt', 'a', encoding='utf-8')
            f.writelines(content)                                        #добавляем в миксер
            f.close()
            f = open('mixer/mixer.txt', 'r', encoding='utf-8')
            content = f.readlines()                                      #достаём весь контент из миксера
            f.close
            i = 10
            while i != 0:
                random.shuffle(content)                                  #перемешиваем контент
                i -= 1
            f = open('mixer/mixer.txt', 'w', encoding='utf-8')
            f.writelines(content)                                        #записываем в миксер перемешанный контент
            f.close()

            #проверить, достаточно ли контента для отправки 
            f = open('mixer/mixer.txt', 'r', encoding='utf-8')
            content = f.readlines()
            f.close()
            pht_count = 0
            vid_count = 0
            mus_count = 0
            for line in content:
                if line.startswith('photo'):
                    pht_count += 1
                elif line.startswith('video'):
                    vid_count += 1
                elif line.startswith('audio'):
                    mus_count += 1

            #проверка, какой контент нужно отправлять
            
            send_photo = False
            if pht_switch():
                if pht_count >= 30: #pht_count >= pht_cnt():
                    send_photo = True
            send_video = False
            if vid_switch():
                if vid_count >= 1:
                    send_video = True
            send_music = False
            if mus_switch():
                if mus_count >= 1:
                    send_music = True

            #подготовка контента
            go = False
            if pht_switch() == send_photo and vid_switch() == send_video and mus_switch() == send_music:
                go = True
                print('скоро будет отправлен пост в группу.')
            else:
                print('миксер ещё не готов')
                sleep(3600)

            if go == True:
                f = open('mixer/mixer.txt', 'r', encoding='utf-8')
                content = f.readlines()
                f.close
                how_many_video = 0
                how_many_music = 0
                how_many_photo = 0
                if pht_switch():
                    how_many_photo = pht_cnt()
                if mus_switch():
                    how_many_music = 1
                if vid_switch():
                    how_many_video = 1
                for line in content:
                    if pht_switch() and how_many_photo != 0:
                        if line.startswith('photo'):
                            f = open('mixer/ready4send.txt', 'a', encoding='utf-8')
                            f.write(line)
                            f.close()
                            content_delete(line)
                            how_many_photo -= 1
                    if vid_switch() and how_many_video != 0:
                        if line.startswith('video'):
                            f = open('mixer/ready4send.txt', 'a', encoding='utf-8')
                            f.write(line)
                            f.close()
                            content_delete(line)
                            how_many_video -= 1
                    if mus_switch() and how_many_music != 0:
                        if line.startswith('audio'):
                            f = open('mixer/ready4send.txt', 'a', encoding='utf-8')
                            f.write(line)
                            f.close()
                            content_delete(line)
                            how_many_music -= 1

            #отправка контента
            if go == True:
                f = open('sender/to_here/to_here.txt', 'r', encoding='utf-8')
                publick_url = f.readline() #группа, куда отправлять контент
                f.close()
                nedo_id = publick_url.replace('https://vk.com/', '')

                print(f'отправляется пост в паблик: {nedo_id}')
                f = open(f'sender/{nedo_id}.txt', 'r', encoding='utf-8')
                were = f.readline()
                were = int(were) + 1
                f.close()
                f = open(f'sender/{nedo_id}.txt', 'w', encoding='utf-8')
                f.write(str(were))
                f.close()

                # ПОЛУЧИТЬ ID ПАБЛИКА
                url = f'https://api.vk.com/method/groups.getById?group_id={nedo_id}&access_token={token}&v=5.131'
                r = requests.get(url)
                src = r.json()
                # print(r.text)

                publick_id = src['response'][0]['id']

                #ОТПРАВИТЬ ПОСТ В ПРЕДЛОЖКУ

                publick_id = f'-{publick_id}'

                f = open('mixer/ready4send.txt', 'r', encoding='utf-8')
                content = f.readlines()
                f.close()

                photo = ''
                audio = ''
                video = ''
                message = ''
                for line in content:
                    if line.startswith('photo'):
                        photo += f'{line},'
                    elif line.startswith('video'):
                        video += f'{line}'
                    elif line.startswith('audio'):
                        audio += f'{line}'

                params = (
                    ('v', '5.131'),
                    ('access_token', token),
                    ('owner_id', publick_id),
                    ('message', message),
                    ('attachments', photo + ',' + audio + ',' + video),
                    ('friends_only', 0),
                    ('from_group', 1)
                )
                response = requests.get('https://api.vk.com/method/wall.post?', params=params)
                # print(response.text)
                f = open('mixer/ready4send.txt', 'w', encoding='utf-8')
                f.close()
                f = open('sender/sender_timer.txt', 'w', encoding='utf-8')
                f.write(str(datetime.now()))
                f.close()
    else:
        sleep(600)