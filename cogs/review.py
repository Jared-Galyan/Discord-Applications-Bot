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

class Review(commands.Cog):
    """Review module"""

    def __init__(self, bot, *args, **kwargs):
        self.bot = bot

    @commands.command()
    @checks.has_review_role()
    async def review(self, ctx):
        db = sqlite3.connect('main.db')
        cursor = db.cursor()
        cursor.execute(f"SELECT user_id, app FROM submits WHERE guild_id = '{ctx.message.guild.id}'")
        result = cursor.fetchall()
        number = 1
        msg = f'**Please choose an application to review below by number.**\n\n'

        for result in result:
            user = self.bot.get_user(int(result[0]))
            msg += f'**{number}.** `{user.name}`, Application: `{result[1]}`\n'
            number += 1
            
        await ctx.send(msg)
        def check(m):
            return m.author == ctx.message.author and m.channel == ctx.message.channel
        num = await self.bot.wait_for('message', check=check)
        cursor.execute(f"SELECT user_id, app, answers, timestamp, id FROM submits WHERE guild_id = '{ctx.message.guild.id}'")
        result = cursor.fetchall()
        numm = 0
        for result in result:
            if numm != (int(num.content) - 1):
                numm += 1
            else:
                userr = self.bot.get_user(int(result[0]))
                
                await ctx.send(f"**Application `{result[1]}` from:** {userr}\n> Timestamp: {result[3]}\n\n{result[2]}")
                name = result[1]
                idd = result[4]
                break
        confirm = await ctx.send('**What would you like to do with this application.**\n\n> ✅ To accept the application\n> ⏹ To do nothing with it right now\n> ❌ To deny the application')
        await confirm.add_reaction('✅')
        await confirm.add_reaction('⏹')
        await confirm.add_reaction('❌')
        def check1(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) == '✅' and reaction.message.id == confirm.id or user == ctx.message.author and str(reaction.emoji) == '⏹' and reaction.message.id == confirm.id or user == ctx.message.author and str(reaction.emoji) == '❌' and reaction.message.id == confirm.id

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=120.0, check=check1)
        except:
            await ctx.send('**Action Cancelled.**')
        if str(reaction) == '✅':
            await ctx.send('Application accepted')
            cursor.execute(f"SELECT submit FROM settings WHERE guild_id = '{ctx.message.guild.id}'")
            result = cursor.fetchone()
            if result is None:
                cursor.execute(f"DELETE FROM submits WHERE guild_id = '{str(ctx.guild.id)}' and user_id = '{userr.id}' and app = '{name}' and id = '{idd}'")
                db.commit()
                try:
                    await userr.send(f'**Your application for** `{name}` **has been accepted in** `{ctx.guild.name}`')
                except:
                    print('Could not send message to user.')
            else:
                chan = ctx.guild.get_channel(int(result[0]))
                try:
                    await userr.send(f'**Your application for** `{name}` **has been accepted in** `{ctx.guild.name}`')
                except:
                    print('Could not send message to user.')
                await chan.send(f'**{name} Application for:** `{userr} ({user.id})` **Accepted by:** `{ctx.message.author} ({ctx.message.author.id})`')
                cursor.execute(f"DELETE FROM submits WHERE guild_id = '{str(ctx.guild.id)}' and user_id = '{userr.id}' and app = '{name}' and id = '{idd}'")
                db.commit()
        elif str(reaction) == '⏹':
            await ctx.send('Application ignored')
        elif str(reaction) == '❌':
            await ctx.send('Application denied')
            cursor.execute(f"SELECT submit FROM settings WHERE guild_id = '{ctx.message.guild.id}'")
            result = cursor.fetchone()
            if result is None:
                cursor.execute(f"DELETE FROM submits WHERE guild_id = '{str(ctx.guild.id)}' and user_id = '{userr.id}' and app = '{name}' and id = '{idd}'")
                db.commit()
                try:
                    await userr.send(f'**Your application for** `{name}` **has been denied in** `{ctx.guild.name}`')
                except:
                    print('Could not send message to user.')
            else:
                chan = ctx.guild.get_channel(int(result[0]))
                try:
                    await userr.send(f'**Your application for** `{name}` **has been denied in** `{ctx.guild.name}`')
                except:
                    print('Could not send message to user.')
                await chan.send(f'**{name} Application for:** `{userr} ({user.id})` **Denied by:** `{ctx.message.author} ({ctx.message.author.id})`')
                cursor.execute(f"DELETE FROM submits WHERE guild_id = '{str(ctx.guild.id)}' and user_id = '{userr.id}' and app = '{name}' and id = '{idd}'")
                db.commit()
        cursor.close()
        db.close()
        
            

def setup(bot):
    bot.add_cog(Review(bot))
    print('Review is loaded')