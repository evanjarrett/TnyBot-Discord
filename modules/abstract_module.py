from abc import ABCMeta, abstractmethod

from exceptions.expections import SameUserException


class AbstractMethod(metaclass=ABCMeta):
    def __init__(self, bot):
        self.bot = bot
        bot.add_listener(self.on_ready)
        bot.add_listener(self.on_message)

    @abstractmethod
    def on_ready(self):
        pass

    @abstractmethod
    def on_message(self, message):
        if message.author == self.bot.user:
            raise SameUserException()
