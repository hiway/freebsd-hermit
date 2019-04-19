import os
import sys
import click
import readline

base_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(base_dir, "data")


def hermit(debug=False):
    from .bot import HermitBot
    args = list(sys.argv)
    message = ' '.join(args[1:])
    bot = HermitBot(data_dir, debug=debug)
    reply = bot.reply(message)
    print(reply)


def hermit_show():
    hermit(debug=True)


@click.group()
def main():
    pass


@main.command()
@click.option('--debug/--no-debug', is_flag=True, default=False)
def chat(debug):
    from .bot import HermitBot
    bot = HermitBot(data_dir, debug=debug)
    while True:
        try:
            message = input("> ")
            reply = bot.reply(message)
            print(reply)
        except (KeyboardInterrupt, EOFError):
            print('')
            break

@main.command()
@click.option('--debug/--no-debug', is_flag=True, default=False)
def telegram(debug):
    from .telegram import main
    main()


@main.command()
@click.option('--debug/--no-debug', is_flag=True, default=False)
def tg(debug):
    from .tg import main
    main()


# if __name__ == '__main__':
#     main()
