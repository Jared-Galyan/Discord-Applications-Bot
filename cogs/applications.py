import discord
from discord.ext import commands
import asyncio
import sys
import re
import inspect
import itertools
import traceback
import sqlite3
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from .utils import checks

class Applications(commands.Cog):
    """Applications module"""

    def __init__(self, bot, *args, **kwargs):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def applications(self, ctx):
        msg = """
        **Applications commands**
        > ?applications create
        """
        await ctx.send(msg)

    @applications.command()
    async def create(self, ctx):
        first = """**Please insert the name for the application.**
        > Ex: Moderator
        """
        def check(m):
            return m.author == ctx.message.author and m.channel == ctx.message.channel
        await ctx.send(first)
        name = await self.bot.wait_for('message', check=check)
        second = f"""**Please insert an introduction message for the application.**
        > Ex: Thanks for wanting to apply for {name.content}
        """
        await ctx.send(second)
        intro = await self.bot.wait_for('message', check=check)
        third = """**Please insert all your questions in seperate messages below. When done please type `done`.**
        """
        await ctx.send(third)
        quests = True
        questions = []
        while quests is True:
            question = await self.bot.wait_for('message', check=check)
            if question.content.lower() == 'done':
                quests = False
            else:
                questions.append(question.content)
        ques = ''
        for question in questions:
            ques += f'**{question}**\n`(example answer)`\n' 

        test = f"""**Application for: {name.content}**\n{intro.content}\n{ques}"""
        await ctx.send(test)
                

def setup(bot):
    bot.add_cog(Applications(bot))
    print('Applications is loaded')