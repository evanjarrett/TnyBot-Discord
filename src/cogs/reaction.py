from discord.ext import commands
from discord.ext.commands import MissingRequiredArgument

from src.cogs import BaseCog


class Reaction(BaseCog):
    _polls = {}
    _lucky = []

    async def on_message(self, message):
        if " chungha " in message.content.lower() and message.author.id != self.bot.user.id:
            await self.bot.add_reaction(message, "😍")
            # if message.author.id == "90269810016923648":
            #     await self.bot.add_reaction(message, "👍")
            #     pass

    async def on_reaction_add(self, reaction, member):
        message = reaction.message
        if message.id in self._lucky and member.id != "188766289794170880":
            if reaction.emoji == "👍":
                await self.bot.send_message(member, "https://streamable.com/q0nh")
            if reaction.emoji == "👎":
                await self.bot.send_message(member, "https://streamable.com/5wgl")
        if reaction.emoji == "🤦":
            await self.bot.remove_reaction(message, "😍", self.bot.user)

    @commands.command(pass_context=True, no_pm=True)
    async def secret(self, ctx, *, content=None):
        if ctx.message.author.id != "90269810016923648":
            return

        message = await self.bot.say("Feeling lucky?".format(content))
        self._lucky.append(message.id)
        await self.bot.add_reaction(message, "👍")
        await self.bot.add_reaction(message, "👎")

    @commands.command(pass_context=True, no_pm=True)
    async def vote(self, ctx, *, content=None):
        """Vote for something"""
        if ctx.message.author.id != "90269810016923648":
            return
        if content is not None:
            message = await self.bot.say("A vote for: `{}` has started".format(content))
            self._polls[message.id] = message
            await self.bot.add_reaction(message, "✅")
            await self.bot.add_reaction(message, "❌")
            await self.bot.say("Use this id to end the vote: {}".format(message.id))

    @commands.command(pass_context=True, no_pm=True)
    async def endvote(self, ctx, message_id):
        """End the vote for something"""
        if ctx.message.author.id != "90269810016923648":
            return
        logs = self.bot.logs_from(ctx.message.channel)
        async for msg in logs:
            if msg.id == message_id and message_id in self._polls:
                reacts = msg.reactions
                yes_count = 0
                no_count = 0
                for r in reacts:
                    if r.emoji == "✅":
                        yes_count = r.count - 1
                    if r.emoji == "❌":
                        no_count = r.count - 1

                if yes_count > no_count:
                    await self.bot.say("The vote ended with {} ✅ as the winner".format(yes_count))
                elif no_count > yes_count:
                    await self.bot.say("The vote ended with {} ❌".format(no_count))
                else:
                    await self.bot.say("The vote ended in a tie")
                return

    @endvote.error
    async def on_endvote_error(self, exception, ctx):
        if isinstance(exception, MissingRequiredArgument()):
            await self.bot.send_message(ctx.message.channel, "Oops, I need a message id to end the vote")
