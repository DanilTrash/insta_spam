from bot import Bot


def main():
    with Bot(1) as bot:
        result = bot.login()
    return


if __name__ == '__main__':
    main()
