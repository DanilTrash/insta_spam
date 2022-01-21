import argparse
from instapy import InstaPy


def parse_target(target):
    username = 'katiamalinovskaia46'
    password = 'miriam310789'
    insta = InstaPy(username, password,
                    browser_executable_path=r'C:\Users\KIEV-COP-4\AppData\Local\Mozilla Firefox\firefox.exe')
    insta.login()
    grebbed_followings = insta.grab_following(target, amount='full')
    with open(f'{target}_followings.csv', 'w+', encoding='utf-8') as f:
        f.write('\n'.join(grebbed_followings))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(dest='target')
    args = parser.parse_args()
    parse_target(args.target)
