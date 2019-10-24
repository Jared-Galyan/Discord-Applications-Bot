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
import datetime
from .utils import checks



class Apply(commands.Cog):
    """Apply module"""

    def __init__(self, bot, *args, **kwargs):
        self.bot = bot

    def dm_or_channel(self, guild):
        db = sqlite3.connect('main.db')
        cursor = db.cursor()
        cursor.execute(f"SELECT dming FROM settings WHERE guild_id = '{guild}'")
        result = cursor.fetchone()
        if result is None:
            cursor.close()
            db.close()
            return False
        elif str(result[0]) == 'none':
            cursor.close()
            db.close()
            return False
        else:
            cursor.close()
            db.close()
            return True

    @commands.command()
    async def apply(self, ctx):
        dming = self.dm_or_channel(ctx.guild.id)
        if dming is False:
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
            numm = head.strip("'")
            cursor.execute(f"SELECT questions, intro FROM applications WHERE guild_id = '{ctx.message.guild.id}' and name = '{numm}'")
            result = cursor.fetchone()
            msgg = await ctx.send(f'**Applying for: {numm}**\n{result[1]}')
            for item in list(str(result[0].strip("[,],'")).split(",")):
                question = item.replace("'", "")
                await msgg.edit(content=f'{msgg.content}\n\n**{question}**')
                answer = await self.bot.wait_for('message', check=check)
                await msgg.edit(content=f'{msgg.content}\n`{answer.content}`')
            await ctx.send(msgg.content)
            confirm = await ctx.send(f'**Please react with ✅ to submit. React with anything else to cancel.**')
            await confirm.add_reaction('✅')
            def check1(reaction, user):
                return user == ctx.message.author and str(reaction.emoji) == '✅' and reaction.message.id == confirm.id

            try:
                await self.bot.wait_for('reaction_add', timeout=60.0, check=check1)
            except:
                await ctx.send('**Application Cancelled.**')
            else:
                sql = ("INSERT INTO submits(guild_id, user_id, answers, app, timestamp) VALUES(?,?,?,?,?)")
                val = (str(ctx.guild.id), str(ctx.message.author.id), str(msgg.content).replace(f'**Applying for: {numm}**\n{result[1]}\n\n', ''), numm, str(datetime.datetime.utcnow()))
                cursor.execute(sql, val)
                db.commit()
                await ctx.send("Application Submitted")
                cursor.execute(f"SELECT submit FROM settings WHERE guild_id = '{ctx.message.guild.id}'")
                result2 = cursor.fetchone()
                if result is None:
                    return
                elif str(result[0]).lower() == 'none':
                    return
                else:
                    chan = ctx.guild.get_channel(int(result2[0]))
                    await chan.send(f'**An application for** `{numm}` **has been submitted by** `{ctx.message.author} ({ctx.message.author.id})`')
            cursor.close()
            db.close()
        else:
            db = sqlite3.connect('main.db')
            cursor = db.cursor()
            cursor.execute(f"SELECT name, questions, intro FROM applications WHERE guild_id = '{ctx.message.guild.id}'")
            result = cursor.fetchall()
            number = 1
            msg = f'**Please choose select an application below by number.**\n\n'
            userrr = ctx.message.author
            for result in result:
                msg += f'**{number}.** `{result[0]}`\n'
                number += 1
                
            await userrr.send(msg)
            def check(m):
                return m.author == ctx.message.author
            num = await self.bot.wait_for('message', check=check)
            cursor.execute(f"SELECT name, questions, intro FROM applications WHERE guild_id = '{ctx.message.guild.id}'")
            result = cursor.fetchall()
            head, sep, tail = str(result[int(num.content) - 1]).strip('(,)').partition(',')
            numm = head.strip("'")
            cursor.execute(f"SELECT questions, intro FROM applications WHERE guild_id = '{ctx.message.guild.id}' and name = '{numm}'")
            result = cursor.fetchone()
            msgg = await userrr.send(f'**Applying for: {numm}**\n{result[1]}')
            for item in list(str(result[0].strip("[,],'")).split(",")):
                question = item.replace("'", "")
                await msgg.edit(content=f'{msgg.content}\n\n**{question}**')
                answer = await self.bot.wait_for('message', check=check)
                await msgg.edit(content=f'{msgg.content}\n`{answer.content}`')
            await userrr.send(msgg.content)
            confirm = await userrr.send(f'**Please react with ✅ to submit. React with anything else to cancel.**')
            await confirm.add_reaction('✅')
            def check1(reaction, user):
                return user == ctx.message.author and str(reaction.emoji) == '✅' and reaction.message.id == confirm.id

            try:
                await self.bot.wait_for('reaction_add', timeout=60.0, check=check1)
            except:
                await userrr.send('**Application Cancelled.**')
            else:
                sql = ("INSERT INTO submits(guild_id, user_id, answers, app, timestamp) VALUES(?,?,?,?,?)")
                val = (str(ctx.guild.id), str(ctx.message.author.id), str(msgg.content).replace(f'**Applying for: {numm}**\n{result[1]}\n\n', ''), numm, str(datetime.datetime.utcnow()))
                cursor.execute(sql, val)
                db.commit()
                await userrr.send("Application Submitted")
                cursor.execute(f"SELECT submit FROM settings WHERE guild_id = '{ctx.message.guild.id}'")
                result2 = cursor.fetchone()
                if result is None:
                    return
                elif str(result[0]).lower() == 'none':
                    return
                else:
                    chan = ctx.guild.get_channel(int(result2[0]))
                    await chan.send(f'**An application for** `{numm}` **has been submitted by** `{ctx.message.author} ({ctx.message.author.id})`')
            cursor.close()
            db.close()


def setup(bot):
    bot.add_cog(Apply(bot))
    print('Apply is loaded')