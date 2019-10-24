import discord
from discord.ext import commands
import sqlite3

async def check_permissions(ctx, perms, *, check=all):
    is_owner = await ctx.bot.is_owner(ctx.author)
    if is_owner:
        return True

    resolved = ctx.channel.permissions_for(ctx.author)
    return check(getattr(resolved, name, None) == value for name, value in perms.items())

def has_permissions(*, check=all, **perms):
    async def pred(ctx):
        return await check_permissions(ctx, perms, check=check)
    return commands.check(pred)

async def check_guild_permissions(ctx, perms, *, check=all):
    is_owner = await ctx.bot.is_owner(ctx.author)
    if is_owner:
        return True

    if ctx.guild is None:
        return False

    resolved = ctx.author.guild_permissions
    return check(getattr(resolved, name, None) == value for name, value in perms.items())

def has_guild_permissions(*, check=all, **perms):
    async def pred(ctx):
        return await check_guild_permissions(ctx, perms, check=check)
    return commands.check(pred)

# These do not take channel overrides into account

def is_mod():
    async def pred(ctx):
        return await check_guild_permissions(ctx, {'manage_messages': True})
    return commands.check(pred)

def is_admin():
    async def pred(ctx):
        return await check_guild_permissions(ctx, {'administrator': True})
    return commands.check(pred)

def mod_or_permissions(**perms):
    perms['manage_messages'] = True
    async def predicate(ctx):
        return await check_guild_permissions(ctx, perms, check=any)
    return commands.check(predicate)

def admin_or_permissions(**perms):
    perms['administrator'] = True
    async def predicate(ctx):
        return await check_guild_permissions(ctx, perms, check=any)
    return commands.check(predicate)

def is_in_guilds(*guild_ids):
    def predicate(ctx):
        guild = ctx.guild
        if guild is None:
            return False
        return guild.id in guild_ids
    return commands.check(predicate)

def is_lounge_cpp():
    return is_in_guilds(466079331152822273)

def is_supporter():
    async def predicate(ctx):
        sup = discord.utils.get(ctx.guild.roles, id=436005832937701396)
        supit = discord.utils.get(ctx.guild.roles, id=535324363667537961)
        hr = discord.utils.get(ctx.guild.roles, id=532718063015952409)
        return sup in ctx.author.roles or supit in ctx.author.roles or hr in ctx.author.roles or await check_guild_permissions(ctx, {'administrator': True})
    return commands.check(predicate)

def has_review_role():
    async def predicate(ctx):
        db = sqlite3.connect('main.db')
        cursor = db.cursor()
        cursor.execute("SELECT review_role FROM settings WHERE guild_id = '{}'".format(ctx.guild.id))
        result = cursor.fetchone()
        if result is None:
            return await check_guild_permissions(ctx, {'administrator': True})
        elif result[0] == 'none':
            return await check_guild_permissions(ctx, {'administrator': True})
        else:
            role = discord.utils.get(ctx.guild.roles, id=result[0])

            return role in ctx.author.roles or await check_guild_permissions(ctx, {'administrator': True})
    return commands.check(predicate)

