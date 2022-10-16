import discord
import datetime
from discord.ext import commands
#sql
from discord import *
import sqlite3
class User(commands.Cog):
    def __init__(self,bot:commands.Bot):
        self.bot = bot
        

    @commands.command()
    async def kayit(self,ctx):
        '''
        Kayıt olmak için kullanılır.
        '''
        db = sqlite3.connect("db.sqlite3")
        cursor = db.cursor()
        cursor.execute(f"SELECT user_id FROM main WHERE user_id = {ctx.author.id}")
        result = cursor.fetchone()
        if result is None:
            sql = (f'''
                INSERT INTO main(user_id,signDate,takeDate) VALUES(?,?,?)
            ''')
            val = (ctx.author.id,datetime.datetime.now(),datetime.datetime.now())
            cursor.execute(sql,val)
            await ctx.send(f"Kayıt yapıldı.{ctx.author.id}")
            sql1 = (f'''
                INSERT INTO exp(user_id,exp,level,amount) VALUES(?,?,?,?)
            ''')
            val = (ctx.author.id,100,0,100)
            cursor.execute(sql1,val)
            await ctx.send(f"Expler yüklendi.{ctx.author.id}")
            db.commit()
        else:
            await ctx.send(f"Zaten kayıtlısın id:{ctx.author.id}")
        cursor.close()
    
    @commands.group(describe="Liderlik görüntülemek için kullanılır.")
    async def leaderboard(self,ctx):
        '''
        Liderlik tablosunu görüntülemek için kullanılır.
        '''
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(title="~leaderboard",description="Leaderboard görüntüleme komutları",colour=discord.Colour.random())  
            embed.add_field(name="~leaderboard exp",value="Exp liderliğini görüntülemek için kullanılır.",inline=False)
            embed.add_field(name="~leaderboard amount",value="Amount liderliğini görüntülemek için kullanılır.",inline=False)
            await ctx.send(embed=embed)

    @leaderboard.command()
    async def exp(self,ctx):    
        '''
        Exp liderliğini görüntülemek için kullanılır.
        '''
        db = sqlite3.connect("db.sqlite3") 
        cursor = db.cursor()
        cursor.execute(f"SELECT user_id,exp FROM exp ORDER BY exp DESC LIMIT 10")
        result = cursor.fetchall()
        embed = discord.Embed(title="Leaderboard",color=discord.Colour.random())
        for i in result:
            embed.add_field(name=f"{self.bot.get_user(i[0])}",value=f"{i[1]} exp",inline=False)
        embed.set_footer(text=f"{ctx.author.name} tarafından sorgulandı.")
        await ctx.send(embed=embed) 
        cursor.close()
    @leaderboard.command()
    async def amount(self,ctx):
        db = sqlite3.connect("db.sqlite3")
        cursor = db.cursor()
        cursor.execute(f"SELECT user_id,amount FROM exp ORDER BY amount DESC LIMIT 10")
        result = cursor.fetchall()
        embed = discord.Embed(title="Leaderboard",color=discord.Colour.random())
        for i in result:
            embed.add_field(name=f"{self.bot.get_user(i[0])}",value=f"{i[1]} amount",inline=False)
        embed.set_footer(text=f"{ctx.author.name} tarafından sorgulandı.")
        await ctx.send(embed=embed) 
        cursor.close()
    
    @commands.command()
    async def goruntule(self,ctx:commands.Context,member:discord.Member=None):
        '''
        Profilinizi görüntülemek için kullanılır.(içerik:exp,amount,level,avatar)
        '''
        if member == None:
            member = ctx.author
        name = member.display_name
        pfp = member.display_avatar
        
        db = sqlite3.connect("db.sqlite3")
        cursor = db.cursor()
        cursor.execute(f"SELECT exp,level,amount FROM exp WHERE user_id = {member.id}")
        result = cursor.fetchone()
        print(result)
        print(member.id)
        if result is None:
            await ctx.send(f"{member.mention} kayıtlı değil!")
        else:
            exp,level,amount = result
            embed = discord.Embed(title="Üye bilgi", description="Üye",colour=discord.Colour.random())
            #embed.set_image(url=pfp)
            embed.set_author(name=f"{name}",icon_url=pfp)
            embed.add_field(name="Exp",value=f"{exp}")
            embed.add_field(name="Level",value=f"{level}",inline=True)
            embed.add_field(name="Amount",value=f"{amount}",inline=False)
            embed.set_footer(text=f"{name} Made this banner")
            
            await ctx.send(embed=embed)

    @commands.command()
    async def daily(self,ctx):
        '''
        Günlük ödül almak için kullanılır.
        '''
        db = sqlite3.connect("db.sqlite3")
        cursor = db.cursor()
        cursor.execute(f"SELECT user_id,takeDate FROM main WHERE user_id = {ctx.author.id}")
        result = cursor.fetchone()
        if result is None:
            await ctx.send("Kayıt olmadan daily alamazsın")
        else:
            user_id,takeDate = result
            print(result)
            print(takeDate)
            print(datetime.datetime.now())
            if datetime.datetime.strptime(takeDate,'%Y-%m-%d %H:%M:%S.%f') < datetime.datetime.now():
                cursor.execute(f"SELECT exp,amount FROM exp WHERE user_id = {ctx.author.id}")
                result = cursor.fetchone()
                exp,amount = result
                amount += 100
                sql = (f'''
                    UPDATE exp SET amount = ? WHERE user_id = ?
                ''')
                val = (amount,ctx.author.id)
                cursor.execute(sql,val)
                await ctx.send(f"Daily alındı exp +{amount}")
                sql1 = (f'''
                    UPDATE main SET takeDate = ? WHERE user_id = ?
                ''')
                val = (datetime.datetime.now() + datetime.timedelta(days=1),ctx.author.id)
                cursor.execute(sql1,val)
                db.commit()
            else:
                await ctx.send(f"Daily alamazsın {takeDate}")
        cursor.close()



async def setup(bot):
    await bot.add_cog(User(bot))
