import asyncio
import re
import os
import datetime
from random import Random, SystemRandom
import textwrap
import contextlib
import traceback
import io

import discord
from discord.ext import commands


class Wight(commands.Cog):

    agree_dict = {
        'ワイト': 'ワイト',
        'デビルマン': 'わかるマン',
        'ニコラス': 'わからずケイジ',
        'ケイジ': 'わからずケイジ',
        'キャシャーン': 'アンダスターン',
        'スパイダーマ': 'リカイダーマン',
        'ルパン': 'ルパン賛成',
        'イッパツマン': '同意ッパツマン',
        'タイガーマスク': 'わかりマスク',
        'TSUYOSHI': 'TSUYOSHI',
        'ジャガー': 'ジャガー',
    }
    agree_pattern = re.compile('.*({0}).*?はどう思う'.format('|'.join(agree_dict.keys())))
    file_prefix = '{0}{1}agrees{1}'.format(os.path.dirname(__file__), os.sep)

    def __init__(self, bot, **kwargs):
        self.bot: commands.Bot = bot
        self.ready = asyncio.Event(loop=self.bot.loop)
        self.closed = asyncio.Event(loop=self.bot.loop)
        self.firstlaunch = True
        self.random = kwargs.get('random', Random())
        self._last_result = None

    @commands.Cog.listener()
    async def on_ready(self):
        if self.firstlaunch:
            self.firstlaunch = False
            await self.bot.change_presence(
                activity=discord.Activity(
                    name='コードを新しくしたのでテスト中ですよ！',
                    type=discord.ActivityType.playing
                )
            )
            self.owner: discord.User = (await self.bot.application_info()).owner
            self.target = self.owner
            for server in self.bot.guilds:
                if self.owner not in server.members:
                    await server.leave()
                    print(server.name, 'を退出しました')
            print('{0}:起動しました'.format(self.bot.user))
            self.ready.set()

    @commands.Cog.listener()
    async def on_close(self):
        self.closed.set()

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        if self.owner not in guild.members:
            await guild.leave()

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if member == self.owner:
            await member.guild.leave()

    @staticmethod
    def embed_member(member: discord.Member):
        description = textwrap.dedent(
            f"""
            作成日時:{member.created_at + datetime.timedelta(hours=9)}
            ID:{member.id}
            """
        )
        embed = discord.Embed(description=description)
        embed.set_author(name=str(member), icon_url=member.avatar_url)
        return embed

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user or message.author.bot:
            return
        await self.ready.wait()
        match = self.agree_pattern.search(message.content)
        if match:
            value = self.agree_dict[match.group(1)]
            if value == 'ワイト':
                randint1 = self.random.randint(1,5)
                if 1 <= randint1 <= 3:
                    fp = '{0}ワイト{1}.mp3'.format(self.file_prefix, randint1)
                    await message.channel.send(files=[discord.File(f'{self.file_prefix}ワイト.png'),discord.File(fp)])
                elif 4 <= randint1 <= 5:
                    await message.channel.send(files=[discord.File('{0}ワイト{1}.png'.format(self.file_prefix, randint1))
                    ,discord.File('{0}ワイト{1}.mp3'.format(self.file_prefix, randint1))])
            else:
                await message.channel.send(
                    files=[discord.File('{0}{1}.mp3'.format(self.file_prefix, value)),
                           discord.File('{0}{1}.png'.format(self.file_prefix, value))]
                )
        elif message.content == 'すマーン！':
            await message.channel.send(file=discord.File(f'{self.file_prefix}すまん.mp3'))
            await asyncio.sleep(2)
            await message.channel.send(
                files=[discord.File(f'{self.file_prefix}わびるマン.png'),
                       discord.File(f'{self.file_prefix}わびるマン.mp3')]
            )
        elif message.content == '\\草':
            await message.channel.send(
                files=[discord.File(f'{self.file_prefix}草.mp3'),
                       discord.File(f'{self.file_prefix}草.png')]
            )
        elif message.content == 'こん＾＾':
            await message.channel.send(
                files=[discord.File(f'{self.file_prefix}こん.png'),
                       discord.File(f'{self.file_prefix}こん.mp3')]
            )
        elif message.content == '\\すごい':
            await message.channel.send(
                files=[discord.File(f'{self.file_prefix}すごいですね.png'),
                       discord.File(f'{self.file_prefix}すごいですね.mp3')]
            )
        elif 'おんなのこのやぞ' in message.content:
            await message.channel.send(file=discord.File(f'{self.file_prefix}おんなのこのやぞ.mp3'))
        elif 'おんなのこやぞ' in message.content:
            await message.channel.send(file=discord.File(f'{self.file_prefix}おんなのこやぞ.mp3'))
        elif message.content == 'なかやまおにいさん':
            await message.channel.send(textwrap.dedent('''
                顔がでかくて、首が太くて、脚が短くて
                ちょっとずんぐりむっくりな感じする
                頑丈な体をしてるのがジャガーです。

                木にも登らなあかんし、水にも入らなあかんし
                どこでも、こう、狩りしたりできるような体になってるんで。

                ヒョウの模様は丸っこい輪っかが体に散らばってますやんか。
                その丸っこい輪っかの中にさらに点々があるのがジャガーの模様です。
                '''),
                file=discord.File(f'{self.file_prefix}なかやまおにいさん.mp3')
            )
        elif message.content == 'まぁ、それはそれとして':
            await message.channel.send(file=discord.File(f'{self.file_prefix}まぁそれはそれとして.mp3'))
    
    async def on_command_error(self, ctx, error):
        if ctx.cog is self:
            raise error

    @commands.command(brief='このメッセージを表示します')
    async def help(self, ctx: commands.Context):
        async def can_run(command: commands.Command):
            if command.hidden:
                return False
            try:
                return await command.can_run(ctx)
            except:
                return False
        inline = False
        embed = discord.Embed(description='ワイトができることです' ,inline=inline)
        [embed.add_field(name=c.name, value=c.brief, inline=inline)
         for c in sorted(self.bot.commands, key=lambda c: c.name)
         if await can_run(c)]
        await ctx.send(embed=embed)

    @commands.command(brief='BOTを停止します')
    async def stop(self, ctx: commands.Context):
        if await self.bot.is_owner(ctx.author):
            await ctx.send('止めるマーン！')
            await self.bot.close()
        else:
            await ctx.send(
                f'{ctx.author.mention}\nあなたに止めることができないと、ワイトは思います'
            )
    
    @commands.guild_only()
    @commands.command(brief='ワイトが取得できるサーバーの情報を表示します')
    async def server(self, ctx: commands.Context):
        server = ctx.guild
        embed = discord.Embed(description='ワイトが取得できるサーバーの情報です。' )
        embed.set_thumbnail(url=server.icon_url)
        _Attr_dict = {'名前':'name' , 'ID':'id','サーバーリージョン':'region','AFKタイムアウト':'afk_timeout'}
        for key, value in _Attr_dict.items():
            #print(key,value,getattr(server,value))
            embed.add_field(name=key,value=getattr(server,value),inline=False)
        _Attr_dict = {'AFKチャンネル':'afk_channel','オーナー':'owner'}
        for key, value in _Attr_dict.items():
            if getattr(server,value) is not None:
                embed.add_field(name=key,value=getattr(server,value).mention,inline=False)
        _Attr_dict ={'メンバー':'members','チャンネル':'channels','役職':'roles','絵文字':'emojis'}
        for key, value in _Attr_dict.items():
            embed.add_field(
                name=key+'の数',
                value=f'len(getattr(server,value))',
                inline=False
            )
        await ctx.send(embed=embed)

    @commands.command(name="id", brief='あなたのIDを表示しますよ')
    async def _id(self, ctx: commands.Context):
        await ctx.send(f'あなたのIDはこれです```{ctx.author.id}```')

    @commands.guild_only()  
    @commands.command(brief='このサーバーの役職とIDを表示します')
    async def role(self, ctx: commands.Context, page = 0):
        try:
            page = int(page)
        except ValueError:
            await ctx.send('ちゃんと数字を入れてほしいと思います')
            return
        title = 'ワイトが取得できるロール一覧です。'
        description=''
        nowpage = 0
        for role in (i for i in reversed(ctx.guild.roles) if not i.is_default()):
            temp_description = '{1}(ID:{0})\n'.format(role.id,role.mention)
            if len(description+temp_description) <= 2048:
                description += temp_description
            elif page == nowpage:
                break
            else:
                description = temp_description
                nowpage += 1
        embed = discord.Embed(title=title,description=description)
        embed.set_footer(text=f'今のページは{nowpage + 1}です。"!k role <番号>"と打つとそのページに行くと思います')
        message1 = await ctx.send(embed=embed)

        def check(m):
            return (
                m.author == ctx.author
                and m.channel == ctx.channel
                and m.content in ('削除', '維持')
            )

        try:
            message2 = await self.bot.wait_for(
                event='message',
                check=check
            )
        except asyncio.TimeoutError:
            await message1.delete()
        else:
            if message2.content == '削除':
                await message1.delete()
            if message2.content == '維持':
                await ctx.send('このまま役職一覧を維持しますよ')
    
    @commands.command(brief='ユニコードエスケープ（？）をします←ニコラスはどう思う？←わからん（わからず・ケイジ）')
    async def uniescape(self, ctx, *, arg):
        escaped = arg.encode('unicode-escape').decode('utf-8')
        await ctx.send(escaped)
    
    @commands.command(brief='（サーバーに関係のない）あなたの情報を表示します')
    async def user(self, ctx, *, user: discord.User = None):
        if user is None:
            user = ctx.author
        embed = discord.Embed(description='ワイトが取得できる（サーバーに関わらない）あなたの情報です。' )
        embed.set_thumbnail(url=ctx.author.avatar_url)
        embed.add_field(name='名前',value=str(ctx.author),inline=False)
        embed.add_field(name='ID',value=ctx.author.id,inline=False)
        embed.add_field(name='アカウントが作られた日(UTC)',value=ctx.author.created_at.strftime('%Y/%m/%d %H:%M:%S'),inline=False)
        await ctx.send(embed=embed)
    
    @commands.command()
    async def poll(self, ctx, *args):
        if len(args) == 0:
            return
        elif len(args) == 1:
            args = (args[0], 'ワイトもそう思います', 'さまよえる亡者はそうは思いません')
        if 1 <= len(args) <= 21:
            answers = args[1:]
            emojis = [chr(0x0001f1e6 + i) for i in range(len(answers))]
            embed = discord.Embed(description='\n'.join(
                e + a for e, a in zip(emojis, answers)))
            m: discord.Message = await ctx.send('**{0}**'.format(args[0]), embed=embed)
            [self.bot.loop.create_task(m.add_reaction(e)) for e in emojis]
    
    @commands.command(brief='ここすきします(あなたのメッセージにしか反応しません)')
    async def kokosuki(self, ctx, *args):
        try: 
            await ctx.message.delete()
        except discord.errors.Forbidden:
            pass 
        if not args:
            return
        for id in map(int, args):
            m = await ctx.fetch_message(id)
            if m.author == ctx.author or await self.bot.is_owner(ctx.author):
                await self._kokosuki(m, sendowner=False)

    async def _kokosuki(self, message,  sendowner=False):
        if message.author.avatar_url != '':
            Avatar_url = message.author.avatar_url
        else:
            Avatar_url = message.author.default_avatar_url
        embed = discord.Embed(
            title='あーここすき',
            description=message.content,
            timestamp=message.created_at
        )
        embed.set_author(name=message.author.display_name,icon_url=Avatar_url)
        await message.channel.send(
            message.author.mention,
            embed=embed,
            file=discord.File('{0}あーここすき{0}.mp3'.format(self.random.randint(1,2)))
        )
        if sendowner:
            await self.owner.send('ここすき！{0}'.format(message.channel.mention))
    
    @commands.command(name='vc')
    async def _vc(self, ctx, channel: discord.VoiceChannel = None):
        if channel is None:
            if ctx.author.voice is None:
                await ctx.send('VCを指定してほしいと思います')
                return
            else:
                channel = ctx.author.voice.channel
        description = (
            '[VCに入った状態でこの文章をクリックすると画面共有ができるようになると思います]'
            f'(https://discordapp.com/channels/{channel.guild.id}/{channel.id})'
        )
        await ctx.send(embed=discord.Embed(title='画面共有用URL', description=description))

    @commands.command(brief='出されたものをランダムで選んで表示しますよ')
    async def random(self, ctx, *args):
        ret = self.random.choice(args)
        await ctx.send(ret)

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    def get_syntax_error(self, e):
        if e.text is None:
            return f'```py\n{e.__class__.__name__}: {e}\n```'
        return f'```py\n{e.text}{"^":>{e.offset}}\n{e.__class__.__name__}: {e}```'

    @commands.command(pass_context=True, hidden=True, name='eval')
    async def _eval(self, ctx):
        if not await self.bot.is_owner(ctx.author):
            await ctx.send('あなたに使うことができないとワイトは思います')
            return
        """Evaluates a code"""

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result
        }

        env.update(globals())
        await ctx.send('コマンドをどうぞ')
        message = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
        body = self.cleanup_code(message.content)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with contextlib.redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except:
                pass

            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                self._last_result = ret
                await ctx.send(f'```py\n{value}{ret}\n```')


def setup(bot, **kwargs):
    bot.add_cog(Wight(bot, **kwargs))