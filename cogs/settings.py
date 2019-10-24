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
    @checks.has_review_role()
    async def settings(self, ctx):
        msg = """
        **Applications settings**
        > ?settings submitted `[<#channel_to_show_submitted apps>, none]`
        > ?settings role `[<@role>, none]`
        > ?settings dming `[true, false]`
        """
        await ctx.send(msg)

    @settings.group(invoke_without_command=True)
    @checks.has_review_role()
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
    @checks.has_review_role()
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

    @settings.group(invoke_without_command=True)
    @checks.has_review_role()
    async def role(self, ctx, role:discord.Role=None):
        if role is None:
            await ctx.send('**Please mention a role.**')
        else:
            db = sqlite3.connect('main.db')
            cursor = db.cursor()
            cursor.execute(f"SELECT review_role, guild_id FROM settings WHERE guild_id = '{ctx.message.guild.id}'")
            result = cursor.fetchone()
            if result is None:
                sql = ("INSERT INTO settings(guild_id, review_role) VALUES(?,?)")
                val = (str(ctx.guild.id), str(role.id))
                cursor.execute(sql, val)
                db.commit()
                cursor.close()
                db.close()
                await ctx.send(f"**The role** `{role.name}` **now has permissions for reviewing, applications, and settings.**")
            else:
                sql = ("UPDATE settings SET review_role = ? WHERE guild_id = ?")
                val = (str(role.id), str(ctx.guild.id))
                cursor.execute(sql, val)
                db.commit()
                cursor.close()
                db.close()
                await ctx.send(f"**The role** `{role.name}` **now has permissions for reviewing, applications, and settings.**")

    @role.command(name='none')
    @checks.has_review_role()
    async def __none(self, ctx):
        db = sqlite3.connect('main.db')
        cursor = db.cursor()
        cursor.execute(f"SELECT review_role, guild_id FROM settings WHERE guild_id = '{ctx.message.guild.id}'")
        result = cursor.fetchone()
        if result is None:
            sql = ("INSERT INTO settings(guild_id, review_role) VALUES(?,?)")
            val = (str(ctx.guild.id), 'none')
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()
            await ctx.send(f"**Set admin role to none.**")
        else:
            sql = ("UPDATE settings SET review_role = ? WHERE guild_id = ?")
            val = ('none', str(ctx.guild.id))
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()
            await ctx.send(f"**Set admin role to none.**")

    @settings.group(invoke_without_command=True)
    @checks.has_review_role()
    async def dming(self, ctx, dming=None):
        if dming is None:
            await ctx.send('**Please insert true or false with the command.**')
        else:
            db = sqlite3.connect('main.db')
            cursor = db.cursor()
            cursor.execute(f"SELECT dming, guild_id FROM settings WHERE guild_id = '{ctx.message.guild.id}'")
            result = cursor.fetchone()
            if dming.lower() == 'true':
                if result is None:
                    sql = ("INSERT INTO settings(guild_id, dming) VALUES(?,?)")
                    val = (str(ctx.guild.id), 'true')
                    cursor.execute(sql, val)
                    db.commit()
                    cursor.close()
                    db.close()
                    await ctx.send(f"**DM applying has now been enabled.**")
                else:
                    sql = ("UPDATE settings SET dming = ? WHERE guild_id = ?")
                    val = ('true', str(ctx.guild.id))
                    cursor.execute(sql, val)
                    db.commit()
                    cursor.close()
                    db.close()
                    await ctx.send(f"**DM applying has now been enabled**")
            elif dming.lower() == 'false':
                if result is None:
                    sql = ("INSERT INTO settings(guild_id, dming) VALUES(?,?)")
                    val = (str(ctx.guild.id), 'none')
                    cursor.execute(sql, val)
                    db.commit()
                    cursor.close()
                    db.close()
                    await ctx.send(f"**DM applying has now been disabled**")
                else:
                    sql = ("UPDATE settings SET dming = ? WHERE guild_id = ?")
                    val = ('none', str(ctx.guild.id))
                    cursor.execute(sql, val)
                    db.commit()
                    cursor.close()
                    db.close()
                    await ctx.send(f"**DM applying has now been disabled**")
            else:
                await ctx.send("**Please insert true or false with the command.**")

def setup(bot):
    bot.add_cog(Settings(bot))
    print('Settings is loaded')