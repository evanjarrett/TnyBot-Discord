import asyncio
import discord
from discord import Member
from discord import Message
from discord import Server
from discord.ext import commands
from discord.ext.commands import Context

from src.cogs import BaseCog

if not discord.opus.is_loaded():
    discord.opus.load_opus("opus")


# Commands needed to mostly match Musicbot
# !play [link | text]
# !playnext [link | text] playing for the VIP
# !remove [x] -- Perms
# !undosong
# !queue
# !np|!nowplaying
# !skip owner/requester/voting
# !shuffle -- Perms
# !cq|clearqueue -- Perms
# !pause -- Perms
# !resume -- Perms
# !volume -- Perms
# !summon -- Perms
# !disconnect -- Perms
# !restart call disconnect then summon, clear out any cache -- Perms


class VoiceEntry:
    def __init__(self, message, player):
        self.requester = message.author
        self.channel = message.channel
        self.player = player

    def __str__(self):
        fmt = "*{0.title}* uploaded by {0.uploader} and requested by {1.display_name}"
        duration = self.player.duration
        if duration:
            fmt += " [length: {0[0]}m {0[1]}s]".format(divmod(duration, 60))
        return fmt.format(self.player, self.requester)


class VoiceState:
    def __init__(self, bot):
        self.current = None
        self.voice = None
        self.bot = bot
        self.play_next_song = asyncio.Event()
        self.songs = asyncio.Queue()
        self.skip_votes = set()  # a set of user_ids that voted
        self.audio_player = self.bot.loop.create_task(self.audio_player_task())

    def is_playing(self):
        if self.voice is None or self.current is None:
            return False

        player = self.current.player
        return not player.is_done()

    @property
    def player(self):
        return self.current.player

    def skip(self):
        self.skip_votes.clear()
        if self.is_playing():
            self.player.stop()

    def toggle_next(self):
        self.bot.loop.call_soon_threadsafe(self.play_next_song.set)

    async def audio_player_task(self):
        while True:
            self.play_next_song.clear()
            self.current = await self.songs.get()
            await self.bot.send_message(self.current.channel, "Now playing " + str(self.current))
            self.current.player.start()
            await self.play_next_song.wait()


class Music(BaseCog):
    """Voice related commands.
        Works in multiple servers at once.
    """
    _controls = []

    def __init__(self, bot):
        super().__init__(bot)
        self.voice_states = {}

    def get_voice_state(self, server):
        state = self.voice_states.get(server.id)
        if state is None:
            state = VoiceState(self.bot)
            self.voice_states[server.id] = state

        return state

    async def create_voice_client(self, channel):
        voice = await self.bot.join_voice_channel(channel)
        state = self.get_voice_state(channel.server)
        state.voice = voice

    def __unload(self):
        for state in self.voice_states.values():
            try:
                state.audio_player.cancel()
                if state.voice:
                    self.bot.loop.create_task(state.voice.disconnect())
            except:
                pass

    async def on_reaction_add(self, reaction, member):
        await self.do_controls(reaction, member)

    async def on_reaction_remove(self, reaction, member):
        await self.do_controls(reaction, member)

    async def do_controls(self, reaction, member):
        message = reaction.message
        if message.id in self._controls and member.id != "188766289794170880":
            if reaction.emoji == "🔀":
                await self.bot.send_message(message.channel, "Shuffling...")
            if reaction.emoji == "⏹":
                await self.do_stop(message, member)
            if reaction.emoji == "⏯":
                await self.do_resume_pause(message)
            if reaction.emoji == "⏭":
                await self.do_skip(message, member)

    @commands.command(pass_context=True, no_pm=True)
    async def controls(self, ctx):
        message = await self.bot.say("Music Controls:")
        self._controls.append(message.id)
        await self.bot.add_reaction(message, "🔀")
        await self.bot.add_reaction(message, "⏹")
        await self.bot.add_reaction(message, "⏯")
        await self.bot.add_reaction(message, "⏭")

    @commands.command(pass_context=True, no_pm=True)
    async def join(self, ctx, *, channel: discord.Channel):
        """Joins a voice channel."""
        try:
            await self.create_voice_client(channel)
        except discord.InvalidArgument:
            await self.bot.say("This is not a voice channel...")
        except discord.ClientException:
            await self.bot.say("Already in a voice channel...")
        else:
            await self.bot.say("Ready to play audio in " + channel.name)

    @commands.command(pass_context=True, no_pm=True)
    async def summon(self, ctx):
        """Summons the bot to join your voice channel."""
        summoned_channel = ctx.message.author.voice_channel
        if summoned_channel is None:
            await self.bot.say("You are not in a voice channel.")
            return False

        state = self.get_voice_state(ctx.message.server)
        if state.voice is None:
            state.voice = await self.bot.join_voice_channel(summoned_channel)
        else:
            await state.voice.move_to(summoned_channel)

        return True

    @commands.command(pass_context=True, no_pm=True)
    async def play(self, ctx, *, song: str):
        """Plays a song.
        If there is a song currently in the queue, then it is
        queued until the next song is done playing.
        This command automatically searches as well from YouTube.
        The list of supported sites can be found here:
        https://rg3.github.io/youtube-dl/supportedsites.html
        """
        state = self.get_voice_state(ctx.message.server)
        opts = {
            "default_search": "auto",
            "quiet": True,
        }

        if state.voice is None:
            success = await ctx.invoke(self.summon)
            if not success:
                return

        try:
            player = await state.voice.create_ytdl_player(song, ytdl_options=opts, after=state.toggle_next)
        except Exception as e:
            fmt = "An error occurred while processing this request: ```py\n{}: {}\n```"
            await self.bot.send_message(ctx.message.channel, fmt.format(type(e).__name__, e))
        else:
            player.volume = 0.6
            entry = VoiceEntry(ctx.message, player)
            await self.bot.say("Enqueued " + str(entry))
            await state.songs.put(entry)

    @commands.command(pass_context=True, no_pm=True)
    async def volume(self, ctx, value: int):
        """Sets the volume of the currently playing song."""

        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.volume = value / 100
            await self.bot.say("Set the volume to {:.0%}".format(player.volume))

    @commands.command(pass_context=True, no_pm=True)
    async def pause(self, ctx):
        """Pauses the currently played song."""
        await self.do_resume_pause(ctx.message.server)

    @commands.command(pass_context=True, no_pm=True)
    async def resume(self, ctx):
        """Resumes the currently played song."""
        await self.do_resume_pause(ctx.message)

    async def do_resume_pause(self, message: Message):
        state = self.get_voice_state(message.server)
        if state.is_playing():
            player = state.player
            if player.is_playing():
                player.pause()
                await self.bot.send_message(message.channel, "Pausing...")
            else:
                player.resume()
                await self.bot.send_message(message.channel, "Resuming...")

    @commands.command(pass_context=True, no_pm=True)
    async def stop(self, ctx):
        """Stops playing audio and leaves the voice channel.
        This also clears the queue.
        """
        await self.do_stop(ctx.message, ctx.message.author)

    async def do_stop(self, message: Message, member: Member):
        if member.id != "90269810016923648":
            await self.bot.send_message(message.channel, "Only the Owner can use this command")
            return

        state = self.get_voice_state(message.server)

        if state.is_playing():
            player = state.player
            player.stop()
            await self.bot.send_message(message.channel, "Stopping...")

        try:
            state.audio_player.cancel()
            del self.voice_states[message.server.id]
            await state.voice.disconnect()
            await self.bot.send_message(message.channel, "Ok bye...")
        except:
            pass

    @commands.command(pass_context=True, no_pm=True)
    async def skip(self, ctx):
        """Vote to skip a song. The song requester can automatically skip.
        3 skip votes are needed for the song to be skipped.
        """
        await self.do_skip(ctx.message, ctx.message.author)

    async def do_skip(self, message: Message, voter: Member):
        state = self.get_voice_state(message.server)
        if not state.is_playing():
            await self.bot.send_message(message.channel, "Not playing any music right now...")
            return

        if voter == state.current.requester:
            await self.bot.send_message(message.channel, "Requester requested skipping song...")
            state.skip()
        elif voter.id not in state.skip_votes:
            state.skip_votes.add(voter.id)
            total_votes = len(state.skip_votes)
            if total_votes >= 3:
                await self.bot.send_message(message.channel, "Skip vote passed, skipping song...")
                state.skip()
            else:
                await self.bot.send_message(message.channel, "Skip vote added, currently at [{}/3]".format(total_votes))
        else:
            await self.bot.send_message(message.channel, "You have already voted to skip this song.")

    @commands.command(pass_context=True, no_pm=True)
    async def shuffle(self, ctx):
        """Shuffles the queue
        """
        await self.do_shuffle(ctx.message, ctx.message.author)

    async def do_shuffle(self, message: Message, voter: Member):
        pass

    @commands.command(pass_context=True, no_pm=True)
    async def playing(self, ctx):
        """Shows info about the currently played song."""

        state = self.get_voice_state(ctx.message.server)
        if state.current is None:
            await self.bot.say("Not playing anything.")
        else:
            skip_count = len(state.skip_votes)
            await self.bot.say("Now playing {} [skips: {}/3]".format(state.current, skip_count))
