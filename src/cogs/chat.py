from chatterbot import ChatBot
from chatterbot.training.trainers import ListTrainer


class Chat:
    _sentence = []
    _chatbot = None

    def __init__(self, bot):
        self.bot = bot

    async def on_ready(self):
        print("listening in another class " + __name__)

        self._chatbot = ChatBot("Tny",
            storage_adapter="chatterbot.adapters.storage.MongoDatabaseAdapter",
            database="chatterbot-database"
        )

        # Get a response to an input statement

    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        self._sentence = message.content.split(" ")

        response = self._chatbot.get_response(message.content)
        await self.bot.send_message(message.channel, response)
