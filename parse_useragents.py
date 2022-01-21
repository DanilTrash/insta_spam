import json
import re


with open('user-agents_instagram-app_application_android-1.txt') as f:
    useragents = f.read().splitlines()[::-1]
for useragent in useragents:
    after_word_instagram = re.split(r'Instagram', useragent)[1]
    after_word_instagram_list = re.split(r' ', after_word_instagram)
    android_version = re.sub(r'\D', '', after_word_instagram_list[3].split('/')[0])
    android_release = re.sub(r'\D', '', after_word_instagram_list[3].split('/')[1])
    app_version = after_word_instagram_list[1]
    dpi = re.split(r' ', after_word_instagram)[4][:-1]
    resolution = re.split(r' ', after_word_instagram)[5][:-1]
    manufacturer = re.split(r' ', after_word_instagram)[6][:-1]
    device = re.split(r' ', after_word_instagram)[7][:-1]
    model = re.split(r' ', after_word_instagram)[8][:-1]
    cpu = re.split(r' ', after_word_instagram)[9][:-1]
    version_code = re.split(r' ', after_word_instagram)[11][:-1]
    device_settings = {"device_settings": {"app_version": app_version,"android_version": android_version,"android_release": android_release,"dpi": dpi,"resolution": resolution,"manufacturer": manufacturer,"device": device,"model": model,"cpu": cpu,"version_code": version_code},"user_agent": 'Instagram' + after_word_instagram,"country": "RU", "locale": "ru_RU"}
    print(json.dumps(device_settings))
