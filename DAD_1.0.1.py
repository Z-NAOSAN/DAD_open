import discord
from discord.ext import commands
from datetime import datetime, timedelta
import locale

intents = discord.Intents.default()
intents.typing = False
intents.presences = False

bot = commands.Bot(command_prefix="!", intents=intents)

# 通知メッセージとボタンの情報を格納する辞書
notifications = {}

# 通知・返信先のテキストチャンネル
notification_channel_id = None

# 通知するユーザーロール
notification_role_id = None

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user.name}")

@bot.slash_command(name="バッチ更新コマンド")
async def batch_update_command(ctx):
    today = datetime.now().date()
    future_date_20 = today + timedelta(days=20)
    future_date_25 = today + timedelta(days=25)
    
    # 曜日の日本語表示を設定
    locale.setlocale(locale.LC_TIME, 'ja_JP.UTF-8')
    
    formatted_date_20 = future_date_20.strftime("%Y年%m月%d日（%A）")
    formatted_date_25 = future_date_25.strftime("%Y年%m月%d日（%A）")
    
    # メンションするロールのID
    role_id = notification_role_id
    
    response = f"{formatted_date_20} にまたバッチ更新コマンドを入力してください。"
    await ctx.send(response)
    
    # メンションするロールに対して通知とボタンを含んだメッセージを送信
    role = ctx.guild.get_role(role_id)
    if role is not None:
        mention = role.mention
        notification_20 = f"{mention} バッチ更新の日が近づいています！"
        notification_25 = f"{mention} バッチ更新の日が迫っています！"
        
        # ボタンの作成
        button_label = "バッチ更新コマンドを実行する"
        button_style = discord.ButtonStyle.primary
        button_emoji = "🔄"
        
        # ボタンコンポーネントの作成
        button = discord.Button(label=button_label, style=button_style, emoji=button_emoji, custom_id="batch_update")
        
        # 20日目の通知を送信
        notification_message_20 = await bot.get_channel(notification_channel_id).send(notification_20, components=[button])
        notifications[ctx.author.id] = notification_message_20
        
        # 25日目の通知を予め作成し、非表示にする
        notification_message_25 = await bot.get_channel(notification_channel_id).send(notification_25, components=[button], visible=False)
        notifications[ctx.author.id] = notification_message_25
    

@bot.event
async def on_button_click(interaction):
    if interaction.custom_id == "batch_update":
        await interaction.respond(content="/a")
        # ボタンを押したユーザーの通知メッセージを削除
        if interaction.user.id in notifications:
            notification_message = notifications.pop(interaction.user.id)
            await notification_message.delete()

@bot.slash_command(name="通知ロール設定")
async def set_notification_role(ctx, role: discord.Role):
    global notification_role_id
    guild = ctx.guild
    # 既存の通知ロールを削除
    for existing_role_id in notification_role_id:
        existing_role = guild.get_role(existing_role_id)
        if existing_role is not None:
            await existing_role.edit(mentionable=False)
    # 新しい通知ロールを設定
    notification_role_id = role.id
    await role.edit(mentionable=True)
    await ctx.send(f"通知するユーザーロールを `{role.name}` に設定しました。")

@bot.slash_command(name="通知チャンネル設定")
async def set_notification_channel(ctx, channel: discord.TextChannel):
    global notification_channel_id
    notification_channel_id = channel.id
    await ctx.send(f"通知・返信先のチャンネルを `{channel.name}` に設定しました。")

bot.run("YOUR_BOT_TOKEN")
