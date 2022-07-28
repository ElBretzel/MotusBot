import random
import asyncio
import os
import discord
from discord.ext import commands, tasks

MAX_TIMEOUT = 90
MIN_TIMEOUT = 90

def wrong_choice(letter):
    return f"~~{letter}~~"

def correct_choice(letter):
    return f"**{letter}**"

def load_words():
    with open("d.txt", "r") as f:
        return f.read().split("\n")

def check_letters(message, botChoice, botOutput):
    for i, k in enumerate(message.content):
        if botChoice[i] == k:
            botOutput[i] = correct_choice(k)
        elif botChoice.count(k) >= 1:
            botOutput[i] = k
        else:
            botOutput[i] = wrong_choice(k)
    return botOutput

def response_display(user, message):
    return f"**✧ 𝐄𝐕𝐄𝐍𝐄𝐌𝐄𝐍𝐓 ✧**" if user == "event" else f"<@{message.author.id}>"

def respect_motus_rules(message, botChoice):
    return message.content[0] == botChoice[0] and len(message.content) == len(botChoice)

def all_correct(botOutput):
    return all(bool(i.startswith("**")) for i in botOutput)

def startup_display(user, botChoice, botOutput):
    if user=="event":
        return "\n||@here||\n**{:✧^30}**\n🔮 Quizz motus lancé ({} lettres).\n🎲 Bonne chance!\n\n{}".format(" 𝐄𝐕𝐄𝐍𝐄𝐌𝐄𝐍𝐓 ", len(botChoice), ' '.join(botOutput))
    return f"🔮 Quizz motus lancé ({len(botChoice)} lettres).\n🎲 Bonne chance!\n\n{' '.join(botOutput)}"

def set_timer(user, channel):
    if user == "event":
        return max(MAX_TIMEOUT - len([1 for i in channel.guild.members if i.status == discord.Status.online and not i.bot]), MIN_TIMEOUT)
    return MIN_TIMEOUT

class Motus(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.automatic_motus.start()

    @tasks.loop(seconds=random.randint(3600, 3600*6))
    async def automatic_motus(self):
        await asyncio.sleep(10)
        await self.start(self.client.get_channel(805060685641678912))

    @commands.command()
    async def motus_start(self, ctx, *args):
        await self.start(ctx.channel, ctx.author.id)

    async def start(self, channel, user="event"):

        botChoice = random.choice(load_words()).lower()
        botOutput = [f"**{botChoice[0]}**"] + ["-"]*(len(botChoice)-1)

        timeout = set_timer(user, channel)
        await channel.send(startup_display(user, botChoice, botOutput))

        finished, pending = await asyncio.wait([self.main_game(channel, user, botChoice, botOutput),
                                                self.timer(channel, timeout)],
                                                return_when=asyncio.FIRST_COMPLETED)

        for p in pending:
            p.cancel()
        task_result = ''.join(i.result() for i in finished)

        await channel.send(f"{task_result}\n📜 La réponse était **{botChoice}**")

    async def timer(self, channel, initial_time):

        async def timer_action(i):
            timer_position = initial_time-i
            if timer_position in [60, 30, 10]:
                await channel.send(f"⏳ Il vous reste {timer_position} secondes")

        for i in range(initial_time):
            await asyncio.sleep(1)
            await timer_action(i)

        return "⏰ Le temps est écoulé..."

    async def main_game(self, channel, user, botChoice, botOutput):

        def check_message(m):
            if user == "event":
                return m.channel.id == channel.id and not m.author.bot
            return m.channel.id == channel.id and user == m.author.id

        while not all_correct(botOutput):
            message = await self.client.wait_for('message', check=check_message)
            if respect_motus_rules(message, botChoice):
                botOutput = check_letters(message, botChoice, botOutput)
            else:
                await channel.send(f"❌ <@{message.author.id}> Erreur, votre mot ne correspond pas à la grille.")
            await channel.send(f"{response_display(user, message)} ➟ {' '.join(botOutput)}")

        return f"💸 <@{message.author.id}> Bravo vous avez gagné!"

def setup(client):
    client.add_cog(Motus(client))
