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

def setup(bot):
    bot.add_cog(Settings(bot))
    print('Settings is loaded')