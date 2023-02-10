import os
import random
import requests
from dotenv import load_dotenv

VK_API_VER = '5.131'
VK_API_URL = 'https://api.vk.com/method/'


def get_random_img_num():
    response = requests.get('https://xkcd.com/info.0.json')
    response.raise_for_status()
    img_info = response.json()
    last_img_num = img_info['num']
    first_img_num = 1
    random_img = random.randint(first_img_num, last_img_num)
    return random_img


def fetch_img_api():
    img_num = get_random_img_num()
    response = requests.get(f'https://xkcd.com/{img_num}/info.0.json')
    response.raise_for_status()
    img_info = response.json()
    img_url = img_info['img']
    comment = img_info['alt']
    filename = f'comic_pic_{img_num}.png'
    return img_url, filename, comment


def write_img():
    img_info = fetch_img_api()
    url = img_info[0]
    filename = img_info[1]
    response = requests.get(url)
    response.raise_for_status()
    with open(filename, 'wb') as file:
        file.write(response.content)
    return filename


def get_upload_server(access_token, group_id):
    url = f'{VK_API_URL}photos.getWallUploadServer'
    params = {'group_id': group_id, 'access_token': access_token,
              'v': VK_API_VER}
    response = requests.get(url, params=params)
    response.raise_for_status()
    upload_server_info = response.json()
    upload_server_url = upload_server_info['response']['upload_url']
    return upload_server_url


def upload_img(access_token, group_id):
    filename = write_img()
    url = get_upload_server(access_token, group_id)
    with open(filename, 'rb') as file:
        files = {'photo': file}
        response = requests.post(url, files=files)
        response.raise_for_status()
        send_img_info = response.json()
        return send_img_info


def save_img(group_id, access_token, user_id):
    upload_img_info = upload_img(access_token, group_id)
    server = upload_img_info['server']
    photo = upload_img_info['photo']
    hash = upload_img_info['hash']
    img_comment = fetch_img_api()[2]
    url = f'{VK_API_URL}photos.saveWallPhoto'
    params = {'user_id': user_id, 'group_id': group_id,
              'server': server, 'photo': photo,
              'hash': hash, 'caption': img_comment,
              'access_token': access_token, 'v': VK_API_VER}
    response = requests.post(url, params=params)
    response.raise_for_status()
    response_content = response.json()['response'][0]
    return response_content


def post_img(user_id, group_id, access_token):
    saved_img_info = save_img(group_id, access_token, user_id)
    media_id = saved_img_info['id']
    owner_id = saved_img_info['owner_id']
    message = saved_img_info['text']
    url = f'{VK_API_URL}wall.post'
    params = {'owner_id': f'-{group_id}',
              'message': message, 'from_group': 1,
              'attachments': f'photo{owner_id}_{media_id}',
              'access_token': access_token, 'v': VK_API_VER}
    response = requests.post(url, params=params)
    response.raise_for_status()
    posted_img_info = response.json()
    return posted_img_info


def main():
    load_dotenv('tokens.env')
    access_token = os.environ['VK_ACCESS_TOKEN']
    user_id = os.environ['VK_CLIENT_ID']
    group_id = os.environ['VK_GROUP_ID']
    filename = write_img()
    try:
        post_img(user_id, group_id, access_token)
    except requests.exceptions.HTTPError:
        print('Ошибка работы API VK')
    finally:
        os.remove(filename)


if __name__ == '__main__':
    main()
