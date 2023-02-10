# Comic Publisher in VK  
The script allows to publish random comics from xkcd website to needed VK group wall.
## How to install
- Python3 should already be installed.   
- Use `pip` (or `pip3`, if there is a conflict with Python2) to install dependencies:
```
pip install -r requirements.txt
```
- Create a file **tokens.env** to store environment variables.
- VK user access token is needed. Follow instructions [VK API](https://dev.vk.com/api/access-token/implicit-flow-user) for gaining the token.  
Save your token in **tokens.env** file under variable **VK_ACCESS_TOKEN**
- Save your user id in **tokens.env**  file under variable **VK_CLIENT_ID**. You can check your user id [here](https://regvk.com/id/)
- Save your group id in **tokens.env**  file  under variable **VK_GROUP_ID**. You can check your group id [here](https://regvk.com/id/)
## How to use
Just run file **comics.py**
```
$ python3 comics.py
```
## Project Goals

This code was written for educational purposes as part of an online course for web developers at [dvmn.org](https://dvmn.org/).
