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

class Settings(commands.Cog):
    """Settings module"""

    def __init__(self, bot, *args, **kwargs):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    @checks.is_admin()
    async def settings(self, ctx):
        msg = """
        **Applications settings**
        > ?settings submitted `<#channel_to_show_submitted apps>`
        """
        await ctx.send(msg)

    @settings.group(invoke_without_command=True)
    @checks.is_admin()
    async def submitted(self, ctx, channel:discord.TextChannel=None):
        if channel is None:
            await ctx.send('**Please mention a channel.**')
        else:
            db = sqlite3.connect('main.db')
            cursor = db.cursor()
            cursor.execute(f"SELECT submit, guild_id FROM settings WHERE guild_id = '{ctx.message.guild.id}'")
            result = cursor.fetchone()
            if result is None:
                sql = ("INSERT INTO settings(guild_id, submit) VALUES(?,?)")
                val = (str(ctx.guild.id), str(channel.id))
                cursor.execute(sql, val)
                db.commit()
                cursor.close()
                db.close()
                await ctx.send(f"**You'll now get notifications in** {channel.mention} **when someone submits an application.**")
            else:
                sql = ("UPDATE settings SET submit = ? WHERE guild_id = ?")
                val = (str(channel.id), str(ctx.guild.id))
                cursor.execute(sql, val)
                db.commit()
                cursor.close()
                db.close()
                await ctx.send(f"**You'll now get notifications in** {channel.mention} **when someone submits an application.**")
    
    @submitted.command(name='none')
    @checks.is_admin()
    async def _none(self, ctx):
        db = sqlite3.connect('main.db')
        cursor = db.cursor()
        cursor.execute(f"SELECT submit, guild_id FROM settings WHERE guild_id = '{ctx.message.guild.id}'")
        result = cursor.fetchone()
        if result is None:
            sql = ("INSERT INTO settings(guild_id, submit) VALUES(?,?)")
            val = (str(ctx.guild.id), 'none')
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()
            await ctx.send(f"**You'll no longer get notifications when someone submits an application.**")
        else:
            sql = ("UPDATE settings SET submit = ? WHERE guild_id = ?")
            val = ('none', str(ctx.guild.id))
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()
            await ctx.send(f"**You'll no longer get notifications when someone submits an application.**")

def setup(bot):
    bot.add_cog(Settings(bot))
    print('Settings is loaded')