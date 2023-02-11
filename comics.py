import os
import random
import requests
from dotenv import load_dotenv

VK_API_VER = '5.131'
VK_API_URL = 'https://api.vk.com/method/'


def get_random_img_num():
    first_img_num = 1
    response = requests.get('https://xkcd.com/info.0.json')
    response.raise_for_status()
    last_img_num = response.json()['num']
    random_img_num = random.randint(first_img_num, last_img_num)
    return random_img_num


def fetch_img(img_num):
    response = requests.get(f'https://xkcd.com/{img_num}/info.0.json')
    response.raise_for_status()
    img_items = response.json()
    img_url = img_items['img']
    comment = img_items['alt']
    filename = f'comic_pic_{img_num}.png'
    return img_url, filename, comment


def write_img(img_url, filename):
    response = requests.get(img_url, filename)
    response.raise_for_status()
    with open(filename, 'wb') as file:
        file.write(response.content)
    return filename


def raise_vk_error(response):
    if 'error' in response:
        raise requests.HTTPError(response['error']['error_msg'])


def get_server(access_token, group_id):
    url = f'{VK_API_URL}photos.getWallUploadServer'
    params = {'group_id': group_id, 'access_token': access_token,
              'v': VK_API_VER}
    response = requests.get(url, params=params)
    response.raise_for_status()
    raise_vk_error(response.json())
    upload_server_url = response.json()['response']['upload_url']
    return upload_server_url


def upload_img(img, server_url):
    with open(img, 'rb') as file:
        file = {'photo': file}
        response = requests.post(server_url, files=file)
    response.raise_for_status()
    raise_vk_error(response.json())
    img_data = response.json()
    server = img_data['server']
    photo = img_data['photo']
    hash = img_data['hash']
    return server, photo, hash


def save_img(group_id, access_token, user_id, server, photo, hash):
    url = f'{VK_API_URL}photos.saveWallPhoto'
    params = {'user_id': user_id, 'group_id': group_id,
              'server': server, 'photo': photo,
              'hash': hash, 'v': VK_API_VER,
              'access_token': access_token}
    response = requests.post(url, params=params)
    response.raise_for_status()
    raise_vk_error(response.json())
    saved_img_items = response.json()['response'][0]
    media_id = saved_img_items['id']
    owner_id = saved_img_items['owner_id']
    return media_id, owner_id


def post_img(group_id, access_token, comment, media_id, owner_id):
    url = f'{VK_API_URL}wall.post'
    params = {'owner_id': f'-{group_id}',
              'message': comment, 'from_group': 1,
              'attachments': f'photo{owner_id}_{media_id}',
              'access_token': access_token, 'v': VK_API_VER}
    response = requests.post(url, params=params)
    response.raise_for_status()
    raise_vk_error(response.json())
    return response.json()


def main():
    load_dotenv('tokens.env')
    access_token = os.environ['VK_ACCESS_TOKEN']
    user_id = os.environ['VK_CLIENT_ID']
    group_id = os.environ['VK_GROUP_ID']
    try:
        img_num = get_random_img_num()
        img_url, filename, comment = fetch_img(img_num)
        img = write_img(img_url, filename)
        server_url = get_server(access_token, group_id)
        server, photo, hash = upload_img(img, server_url)
        media_id, owner_id = save_img(group_id, access_token,
                                      user_id, server, photo,
                                      hash)
        post_img(group_id, access_token, comment, media_id, owner_id)
    except requests.exceptions.HTTPError:
        print('Ошибка работы API VK')
    finally:
        if os.path.exists(filename):
            os.remove(filename)


if __name__ == '__main__':
    main()
