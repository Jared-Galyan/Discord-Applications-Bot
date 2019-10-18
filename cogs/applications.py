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
    @checks.is_admin()
    async def applications(self, ctx):
        msg = """
        **Applications commands**
        > ?applications create
        > ?applications list
        > ?applications remove
        """
        await ctx.send(msg)

    @applications.command()
    @checks.is_admin()
    async def create(self, ctx):
        first = """**Please insert the name for the application.**
        > Ex: Moderator
        """
        def check(m):
            return m.author == ctx.message.author and m.channel == ctx.message.channel
        await ctx.send(first)
        name = await self.bot.wait_for('message', check=check)
        db = sqlite3.connect('main.db')
        cursor = db.cursor()
        cursor.execute(f"SELECT name FROM applications WHERE guild_id = '{ctx.message.guild.id}' and name = '{name.content}'")
        result = cursor.fetchone()
        if result is None:
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

            conf = f"""**Application for: {name.content}**\n{intro.content}\n{ques}\n\n**If everything looks correct please react with** ✅"""
            confirm = await ctx.send(conf)
            
            def check1(reaction, user):
                return user == ctx.message.author and str(reaction.emoji) == '✅' and reaction.message.id == confirm.id

            try:
                await self.bot.wait_for('reaction_add', timeout=60.0, check=check1)
            except asyncio.TimeoutError:
                await ctx.send('**Creation of Application timed out.**')
            else:
                sql = ("INSERT INTO applications(guild_id, name, questions, intro) VALUES(?,?,?,?)")
                val = (str(ctx.guild.id), name.content, str(questions), intro.content)
                cursor.execute(sql, val)
                db.commit()
                cursor.close()
                db.close()
                await ctx.send('Application Created')
        else:
            await ctx.send('**An application already exists with that name.**')
                

def setup(bot):
    bot.add_cog(Applications(bot))
    print('Applications is loaded')