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

class Apply(commands.Cog):
    """Apply module"""

    def __init__(self, bot, *args, **kwargs):
        self.bot = bot

    @commands.command()
    async def apply(self, ctx):
        db = sqlite3.connect('main.db')
        cursor = db.cursor()
        cursor.execute(f"SELECT name, questions, intro FROM applications WHERE guild_id = '{ctx.message.guild.id}'")
        result = cursor.fetchall()
        number = 1
        msg = f'**Please choose select an application below by number.**\n\n'

        for result in result:
            msg += f'**{number}.** `{result[0]}`\n'
            number += 1
            
        await ctx.send(msg)
        def check(m):
            return m.author == ctx.message.author and m.channel == ctx.message.channel
        num = await self.bot.wait_for('message', check=check)
        cursor.execute(f"SELECT name, questions, intro FROM applications WHERE guild_id = '{ctx.message.guild.id}'")
        result = cursor.fetchall()
        head, sep, tail = str(result[int(num.content) - 1]).strip('(,)').partition(',')
        await ctx.send(head.strip("'"))
        numm = head.strip("'")
        cursor.execute(f"SELECT questions FROM applications WHERE guild_id = '{ctx.message.guild.id}' and name = '{numm}'")
        result = cursor.fetchone()
        await ctx.send('Questions testing')
        for item in list(str(result[0].strip("[,],'")).split(",")):
            await ctx.send(item.replace("'", ""))
        


def setup(bot):
    bot.add_cog(Apply(bot))
    print('Apply is loaded')