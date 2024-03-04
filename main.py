import disnake
import asyncio
import json
import sqlite3
import random
import time
import secrets
import aioconsole
import traceback
import aiohttp
import atexit
import requests
import pickle
from datetime import datetime, timedelta
from typing import Optional
from disnake.ext import commands, tasks
from disnake.colour import Color
from disnake.ext.commands import Bot
from disnake.ext import commands
from disnake.ext.commands import check
from disnake.ui import Modal, Button, Select, View
from disnake import OptionType, Embed, SelectMenu, SelectOption, TextInputStyle, ButtonStyle

conn = sqlite3.connect('your_database.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_cooldowns (
        user_id INTEGER PRIMARY KEY,
        last_execution REAL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS claimed_promocodes (
        user_id INTEGER,
        promocode TEXT,
        PRIMARY KEY (user_id, promocode)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS ranks (
        rank_id INTEGER PRIMARY KEY,
        rank_name TEXT,
        min_noodles INTEGER
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS daily_bonus (
        user_id INTEGER PRIMARY KEY,
        last_claimed_date TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS promocodes (
        code TEXT PRIMARY KEY,
        coins INTEGER,
        noodles_length INTEGER
    )
''')

cursor.execute('''CREATE TABLE IF NOT EXISTS titles (
                    user_id INTEGER PRIMARY KEY,
                    title TEXT
                )''')

cursor.executemany('''
    INSERT OR REPLACE INTO ranks (rank_id, rank_name, min_noodles) VALUES (?, ?, ?)
''', [
    (1, 'Бронза', 100),
    (2, 'Серебро', 250),
    (3, 'Золото', 500),
    (4, 'Платина', 1200),
    (5, 'Алмаз', 2000),
    (6, 'Элита', 3000),
    (6, 'Легенда', 5000),
    (7, 'Невозможно', 10000),
])

cursor.execute('''
    CREATE TABLE IF NOT EXISTS skins (
        user_id INTEGER,
        skin_name TEXT,
        rarity TEXT,
        PRIMARY KEY (user_id, skin_name),
        FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS boiling (
        user_id INTEGER PRIMARY KEY,
        noodles_length INTEGER
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS active_skins (
        user_id INTEGER,
        active_skin TEXT,
        rarity TEXT,
    PRIMARY KEY (user_id, active_skin)
)
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS store (
        skin_id INTEGER PRIMARY KEY,
        skin_name TEXT,
        rarity TEXT,
        price INTEGER
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS diamond_store (
        skin_id INTEGER PRIMARY KEY,
        skin_name TEXT,
        rarity TEXT,
        price_in_diamonds INTEGER
    )
''')

cursor.executemany('''
    INSERT OR REPLACE INTO diamond_store (skin_id, skin_name, rarity, price_in_diamonds) VALUES (?, ?, ?, ?)
''', [
    (9, 'Алмазик', 'Премиум', 100),
    (10, 'Pepe', 'Премиум', 100),
    (11, 'Mr.Beast', 'Премиум', 200),
])

cursor.executemany('''
    INSERT OR REPLACE INTO store (skin_id, skin_name, rarity, price) VALUES (?, ?, ?, ?)
''', [
    (1, 'Робот', 'Обычный', 100),
    (2, 'Камуфляж', 'Необычный', 150),
    (3, 'Космос', 'Редкий', 170),
    (4, 'Земля', 'Эпический', 250),
    (5, 'Toxic', 'Мифический', 300),
    (6, 'Водичка', 'Мифический', 400),
    (7, 'Сыр', 'Легендарный', 500),
    (8, 'Весельчак', 'Коллекционный', 1000)
])

cursor.execute('''
    CREATE TABLE IF NOT EXISTS event_store (
        skin_id INTEGER PRIMARY KEY,
        skin_name TEXT,
        rarity TEXT,
        price INTEGER
    )
''')

cursor.execute('DELETE FROM event_store')

cursor.executemany('''
    INSERT INTO event_store (skin_id, skin_name, rarity, price) VALUES (?, ?, ?, ?)
''', [
    (1, 'Сладкая Любовь', 'Коллекционный', 900),
    (2, 'Сердечный Защитник', 'Коллекционный', 900),
    (3, 'Raffaello', 'Коллекционный', 900),
])

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        coins INTEGER,
        diamonds INTEGER DEFAULT 0,
        bonus_granted INTEGER DEFAULT 0,
        referral_code TEXT UNIQUE, 
        referring_user_id INTEGER DEFAULT NULL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS purchased_cases (
        user_id INTEGER,
        case_type TEXT,
        purchase_date DATE
    )
''')

conn.commit()

intents = disnake.Intents.all()

client = commands.Bot(command_prefix="m", intents=intents)

client.remove_command("help")

class SDCApi:
    def __init__(self, client, sdc_token):
        self.client = client
        self.sdc_token = sdc_token
        self.session = aiohttp.ClientSession()

    @tasks.loop(minutes=1)
    async def sdc_stats(self):
        headers = {
            'Authorization': f"SDC {self.sdc_token}",
        }
        data = {
            "servers": len(self.client.guilds),
            "shards": 1,  
        }
        url = f"https://api.server-discord.com/v2/bots/1197598948131618826/stats"
        async with self.session.post(url, headers=headers, json=data) as resp:
            if resp.status == 200:
                pass
            else:
                print("Ошибка при отправке статистики.")

    @sdc_stats.before_loop
    async def before_sdc_stats(self):
        await self.client.wait_until_ready()

@client.event
async def on_ready():
    print("Miwi запущен!")

    while True:
        sdc_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjExOTc1OTg5NDgxMzE2MTg4MjYiLCJwZXJtcyI6MCwiaWF0IjoxNzA3NjUwNjI0fQ.7OHtG7MDKnXCHIlPaDqhL978OlioAbNh7bCYJnZuCg4"
        sdc_api = SDCApi(client, sdc_token)
        sdc_api.sdc_stats.start()
        print("Miwi обновила статус")
        bot_id = '1197598948131618826'
        url = f'https://api.boticord.top/v3/bots/{bot_id}/stats'

        data = {
            'members': len(client.users),
            'servers': len(client.guilds),
            'shards': 1,
        }

        headers = {
            'Authorization': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjYwNjM3MTkzNDE3MDUxMzQyOCIsInRva2VuIjoib3c3bjZIcHJPZUlSeHVOZkxaQlZsZzEzeUMyV0V2QzIwN3pkbm0wd2Ryc0IwdVVzeC8vL3M0OXIwbi9HU1FOYSIsInR5cGUiOiJib3QiLCJyZWRpcmVjdCI6ItGC0Ysg0LTRg9C80LDQuyDRgtGD0YIg0YfRgtC-LdGC0L4g0LHRg9C00LXRgj8iLCJwZXJtaXNzaW9ucyI6MCwiaWF0IjoxNzA3MDM2NjAzfQ.EGY_P04IZlkUijoVKc56Qw0gsz2uIpfwH1La7v_Y_mY',
            'Content-Type': 'application/json'
        }

        response = requests.post(url, json=data, headers=headers)

        await asyncio.sleep(180)
        await client.change_presence(status=disnake.Status.idle, activity=disnake.Activity(type=disnake.ActivityType.watching, name=f"{len(client.guilds)} сервера(ов)"))

@client.slash_command(name="check_rank", description="Проверить ранг и выдать скин.")
@commands.bot_has_permissions(view_channel=True)
async def check_rank_skin(ctx):
    user_id = ctx.author.id

    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT user_id FROM users WHERE user_id=?', (user_id,))
    existing_user = cursor.fetchone()

    if not existing_user:
        await ctx.send("Вы делаете всё не по инструкции. Пожалуйста, воспользуйтесь командой /help и следуйте инструкциям.")
        conn.close()
        return

    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT noodles_length FROM boiling WHERE user_id=?', (user_id,))
    existing_length = cursor.fetchone()

    if existing_length:
        noodles_length = existing_length[0]

        cursor.execute('SELECT rank_name FROM ranks WHERE ? >= min_noodles ORDER BY min_noodles DESC LIMIT 1', (noodles_length,))
        rank_result = cursor.fetchone()

        if rank_result:
            user_rank = rank_result[0]

            cursor.execute('SELECT * FROM skins WHERE user_id=? AND skin_name=?', (user_id, user_rank))
            existing_skin = cursor.fetchone()

            if not existing_skin:
                cursor.execute('INSERT INTO skins (user_id, skin_name, rarity) VALUES (?, ?, ?)', (user_id, user_rank, 'Ранговый'))
                await ctx.send(embed=disnake.Embed(description=f"Поздравляем! Вы достигли ранга '{user_rank}' и получили ранговый скин.", color=0xe8b11a))
            else:
                await ctx.send("У вас уже есть скин этого ранга.")
        else:
            await ctx.send("У вас нет ранга.")
    else:
        await ctx.send("Вы не варили лапшу.")

    conn.commit()
    conn.close()

@client.slash_command(name="delete-data", description="Удалить все данные пользователя.",  guild_ids=[1136737936273055886])
@commands.bot_has_permissions(view_channel=True)
async def delete_data(ctx, member: disnake.User):
    if ctx.author.id not in [606371934170513428]:
        return

    user_id = member.id

    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()

    cursor.execute('DELETE FROM boiling WHERE user_id=?', (user_id,))

    cursor.execute('DELETE FROM active_skins WHERE user_id=?', (user_id,))

    cursor.execute('DELETE FROM skins WHERE user_id=?', (user_id,))

    cursor.execute('DELETE FROM trades WHERE sender_id=? OR recipient_id=?', (user_id, user_id))

    cursor.execute('DELETE FROM user_cooldowns WHERE user_id=?', (user_id,))

    cursor.execute('DELETE FROM users WHERE user_id=?', (user_id,))

    conn.commit()
    conn.close()

    await ctx.send(embed=disnake.Embed(description=f"Все данные пользователя {member.display_name} были успешно удалены.", color=0xe8b11a))


@client.slash_command(name="update_promocode", description="Обновить настройки промокода.",  guild_ids=[1136737936273055886])
@commands.has_permissions(administrator=True)
async def update_promocode(ctx, code: str, coins: int, noodles_length: int = 0):
    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM promocodes WHERE code=?', (code,))
    existing_promocode = cursor.fetchone()

    if existing_promocode:
        cursor.execute('UPDATE promocodes SET coins = ?, noodles_length = ? WHERE code = ?', (coins, noodles_length, code))
        conn.commit()

        await ctx.send(embed=disnake.Embed(description=f"Настройки промокода '{code}' успешно обновлены.", color=0xe8b11a))
    else:
        cursor.execute('INSERT INTO promocodes (code, coins, noodles_length) VALUES (?, ?, ?)', (code, coins, noodles_length))
        conn.commit()

        await ctx.send(embed=disnake.Embed(description=f"Промокод '{code}' успешно установлен с настройками: монеты={coins}, длина лапши={noodles_length}.", color=0xe8b11a))

    conn.close()

@client.slash_command(name="view", description="Посмотреть скин.")
@commands.bot_has_permissions(view_channel=True)
async def view(ctx, member: Optional[disnake.Member] = None):
    target_member = member or ctx.author

    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT user_id FROM users WHERE user_id=?', (target_member.id,))
    existing_user = cursor.fetchone()

    if not existing_user:
        await ctx.send("Вы делаете всё не по инструкции. Пожалуйста, воспользуйтесь командой /help и следуйте инструкциям.")
        conn.close()
        return

    cursor.execute('SELECT active_skin, rarity FROM active_skins WHERE user_id=?', (target_member.id,))
    active_skin_data = cursor.fetchone()

    if active_skin_data:
        active_skin_name, rarity = active_skin_data
        image_path = f"skin/{active_skin_name}.png"

        file = disnake.File(image_path, filename="skin.png")

        embed = disnake.Embed(
            title=f"{active_skin_name} [{rarity}]",
            color=0xe8b11a
        )
        embed.set_image(url=f"attachment://skin.png")

        await ctx.send(embed=embed, file=file)
    else:
        image_path = "skin/none.png"
        active_skin = "Начальный"
        rarity = "Обычный"

        file = disnake.File(image_path, filename="skin.png")

        embed = disnake.Embed(
            title=f"{active_skin} [{rarity}]",
            color=0xe8b11a
        )
        embed.set_image(url=f"attachment://skin.png")

        await ctx.send(embed=embed, file=file)

    conn.close()

class CasesCategoryMenu(disnake.ui.Select):
    def __init__(self, ctx) -> None:
        options = [
            disnake.SelectOption(label="📦 Редкий Кейс", value="rare"),
            disnake.SelectOption(label="📦 Эпический Кейс", value="epic"),
            disnake.SelectOption(label="📦 Мифический Кейс", value="mythical"),
        ]

        super().__init__(placeholder="Выберите кейс", options=options)
        self.ctx = ctx

    async def callback(self, interaction):
        if interaction.user.id != interaction.author.id:
            await interaction.response.send_message(
                content="Вы не можете использовать эту кнопку, так как вы не являетесь ее автором.",
                ephemeral=True
            )
            return

        user_id = interaction.author.id
        selected_value = interaction.data['values'][0]

        if not self.check_daily_limit(user_id, selected_value):
            await interaction.response.send_message(
                content="Вы достигли дневного лимита для этого типа кейса.",
                ephemeral=True
            )
            return

        self.record_purchase(user_id, selected_value)

        embed = disnake.Embed(
            title="Кейс куплен!",
            description=f"Вы успешно купили {selected_value} кейсов.",
            color=0xe8b11a  
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    def check_daily_limit(self, user_id, case_type):
        conn = sqlite3.connect('your_database.db')
        cursor = conn.cursor()

        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)

        cursor.execute('''
            SELECT COUNT(*)
            FROM purchased_cases
            WHERE user_id = ? AND case_type = ? AND purchase_date >= ? AND purchase_date < ?
        ''', (user_id, case_type, today_start, today_end))

        count = cursor.fetchone()[0]

        conn.close()

        limits = {'rare': 3, 'epic': 2, 'mific': 1}
        return count < limits.get(case_type, 0)

    def record_purchase(self, user_id, case_type):
        conn = sqlite3.connect('your_database.db')
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO purchased_cases (user_id, case_type, purchase_date)
            VALUES (?, ?, ?)
        ''', (user_id, case_type, datetime.now()))

        conn.commit()
        conn.close()

class CoinsCategoryMenu(disnake.ui.Select):
    def __init__(self, ctx) -> None:
        options = [
            disnake.SelectOption(label="🪙 300 Монет\nСтоимость: 10💎", value="300"),
            disnake.SelectOption(label="🪙 1500 Монет\nСтоимость: 50💎", value="1500"),
            disnake.SelectOption(label="🪙 3500 Монет\nСтоимость: 100💎", value="3500"),
            disnake.SelectOption(label="🪙 20000 монеток\nСтоимость: 500💎", value="20000"),
        ]

        super().__init__(placeholder="Выберите количество", options=options)
        self.ctx = ctx

    async def callback(self, interaction):
        if interaction.user.id != interaction.author.id:
            print(f"{interaction.user.id} and {interaction.author.id}")
            await interaction.response.send_message(
                content="Вы не можете использовать эту кнопку, так как вы не являетесь ее автором.",
                ephemeral=True
            )
            return
        user_id = interaction.author.id
        selected_value = int(interaction.data['values'][0])

        cost_in_diamonds = 0
        granted_coins = 0

        if selected_value == 300:
            cost_in_diamonds = 10
            granted_coins = 300
        elif selected_value == 1500:
            cost_in_diamonds = 50
            granted_coins = 1500
        elif selected_value == 3500:
            cost_in_diamonds = 100
            granted_coins = 3500
        elif selected_value == 20000:
            cost_in_diamonds = 500
            granted_coins = 20000

        cursor.execute('SELECT diamonds FROM users WHERE user_id=?', (user_id,))
        user_diamonds = cursor.fetchone()

        if user_diamonds is not None and user_diamonds[0] is not None:
            if user_diamonds[0] >= cost_in_diamonds:
                new_diamond_balance = user_diamonds[0] - cost_in_diamonds
                cursor.execute('UPDATE users SET diamonds=? WHERE user_id=?', (new_diamond_balance, user_id))

                cursor.execute('SELECT coins FROM users WHERE user_id=?', (user_id,))
                user_coins = cursor.fetchone()

                if user_coins is not None and user_coins[0] is not None:
                    new_coin_balance = user_coins[0] + granted_coins
                    cursor.execute('UPDATE users SET coins=? WHERE user_id=?', (new_coin_balance, user_id))

                    conn.commit()
                    await interaction.response.send_message(f"Успех конвертации!", ephemeral=True)
                else:
                    await interaction.response.send_message("Ошибка при получении информации о монетах пользователя.", ephemeral=True)
            else:
                await interaction.response.send_message("Недостаточно алмазов для конвертации.", ephemeral=True)
        else:
            await interaction.response.send_message("Ошибка при получении информации об алмазах пользователя.", ephemeral=True)

class EventSkinsCategoryMenu(disnake.ui.Select):
    def __init__(self, ctx) -> None:
        super().__init__(placeholder="Выберите скин", options=[])
        self.ctx = ctx
        self.author_id = ctx.author.id
        self.menu_id = self.custom_id
        self._fetch_skin_options()

    def _fetch_skin_options(self):
        cursor.execute('SELECT skin_name FROM event_store')
        store_skins = cursor.fetchall()

        all_skins = store_skins

        for (skin_name,) in all_skins:
            self.add_option(label=f"{skin_name}", value=skin_name)

    async def callback(self, interaction):
        author_id = self.ctx.author.id

        if interaction.user.id != author_id:
            await interaction.response.send_message(
                content="Вы не можете использовать эту менюшку, так как вы не являетесь ее автором.",
                ephemeral=True
            )
            return

        selected_skin = self.values[0]

        image_path = f"skin/{selected_skin}.png"
        file = disnake.File(image_path, filename="skin.png")

        confirmation_embed = disnake.Embed(
            title=f"Подтвердите покупку скина: {selected_skin}",
            color=0x00ff00,
        )

        confirmation_embed.set_image(file=file)

        confirmation_message = await interaction.response.edit_message(embed=confirmation_embed, view=await self.get_confirmation_view(interaction))



    async def get_confirmation_view(self, interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                content="Вы не можете использовать эту кнопку, так как вы не являетесь ее автором.",
                ephemeral=True
            )
            return

        view = disnake.ui.View(timeout=None)
        view.add_item(disnake.ui.Button(label="Купить", custom_id="buy_event_skin", style=disnake.ButtonStyle.green))
        view.add_item(disnake.ui.Button(label="🗑️ Удалить", custom_id="delete_message", style=disnake.ButtonStyle.red))
        return view

class SkinsCategoryMenu(disnake.ui.Select):
    def __init__(self, ctx) -> None:
        super().__init__(placeholder="Выберите скин", options=[])
        self.ctx = ctx
        self.author_id = ctx.author.id
        self.menu_id = self.custom_id
        self._fetch_skin_options()

    def _fetch_skin_options(self):
        cursor.execute('SELECT skin_name FROM store')
        store_skins = cursor.fetchall()

        cursor.execute('SELECT skin_name FROM diamond_store')
        diamond_skins = cursor.fetchall()

        all_skins = store_skins + diamond_skins

        for (skin_name,) in all_skins:
            self.add_option(label=f"{skin_name}", value=skin_name)

    async def callback(self, interaction):
        author_id = self.ctx.author.id

        if interaction.user.id != author_id:
            await interaction.response.send_message(
                content="Вы не можете использовать эту менюшку, так как вы не являетесь ее автором.",
                ephemeral=True
            )
            return

        selected_skin = self.values[0]

        image_path = f"skin/{selected_skin}.png"
        file = disnake.File(image_path, filename="skin.png")

        confirmation_embed = disnake.Embed(
            title=f"Подтвердите покупку скина: {selected_skin}",
            color=0x00ff00,
        )

        confirmation_embed.set_image(file=file)

        confirmation_message = await interaction.response.edit_message(embed=confirmation_embed, view=await self.get_confirmation_view(interaction))



    async def get_confirmation_view(self, interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                content="Вы не можете использовать эту кнопку, так как вы не являетесь ее автором.",
                ephemeral=True
            )
            return

        view = disnake.ui.View(timeout=None)
        view.add_item(disnake.ui.Button(label="Купить", custom_id="buy_skin", style=disnake.ButtonStyle.green))
        view.add_item(disnake.ui.Button(label="🗑️ Удалить", custom_id="delete_message", style=disnake.ButtonStyle.red))
        return view

class StoreCategoryMenu(disnake.ui.Select):
    def __init__(self, ctx) -> None:
        super().__init__(
            placeholder="Выберите категорию",
            options=[
                #disnake.SelectOption(label="Любовные образы", value="event_skins", description="Особые скины дял профиля ко Дню Валентина", emoji="💝"),
                disnake.SelectOption(label="Скины", value="skins", description="Уникальные облики для вашего профиля", emoji="🤩"),
                disnake.SelectOption(label="Монеты", value="coins", description="Обменяйте брилианты на монеты", emoji="🪙"),
            ]
        )

        self.ctx = ctx

    async def callback(self, interaction):
        author_id = self.ctx.author.id

        if interaction.user.id != author_id:
            await interaction.response.send_message(
                content="Вы не можете использовать эту менюшку, так как вы не являетесь ее автором.",
                ephemeral=True
            )
            return

        if self.values[0] == "shop":
            embed=disnake.Embed(title="📃 Магазин", description="", color=0xe8b11a)
            embed.add_field(name=f"Сдесь вы можете купить себе ценные предметы для апгрейда.", value=f"⠀", inline=False)
            embed.add_field(name=f"🧲 Магнит", value=f"\n```Простой и доступный способ сделать вашу любимую лапшу еще дороже!\n\nЦена 100🪙```", inline=True)
            embed.add_field(name=f"👨🏻‍🍳 Плита", value=f"\n```Она может быть использована для приготовления вкусного рамена.\n\nЦена 500🪙```", inline=True)
            await interaction.response.edit_message(embed=embed)

        elif self.values[0] == "skins":
            embed = disnake.Embed(title="🤩 Скины", color=0xe8b11a)
            embed.description = "Приветствую в разделе скинов! Укрась свой профиль уникальными обликами."

            cursor.execute('SELECT skin_name, rarity, price FROM store')
            skins_data = cursor.fetchall()

            cursor.execute('SELECT skin_name, rarity, price_in_diamonds FROM diamond_store')
            diamond_skins_data = cursor.fetchall()

            for skin_name, rarity, price_in_diamonds in diamond_skins_data:
                embed.add_field(name=f"{skin_name} [{rarity}]", value=f"\n```Цена: {price_in_diamonds}💎```", inline=True)

            for skin_name, rarity, price in skins_data:
                embed.add_field(name=f"{skin_name} [{rarity}]", value=f"\n```Цена: {price}🪙```", inline=True)

            select = SkinsCategoryMenu(self.ctx)
            view = View(timeout=None)
            view.add_item(select)
            await interaction.response.edit_message(embed=embed, view=view)
        elif self.values[0] == "event_skins":
            embed = disnake.Embed(title="🤩 Скины", color=0xe8b11a)
            embed.description = "Приветствую в разделе скинов! Укрась свой профиль уникальными обликами."

            cursor.execute('SELECT skin_name, rarity, price FROM event_store')
            skins_data = cursor.fetchall()

            for skin_name, rarity, price in skins_data:
                embed.add_field(name=f"{skin_name} [{rarity}]", value=f"\n```Цена: {price}🪙```", inline=True)

            select = EventSkinsCategoryMenu(self.ctx)
            view = View(timeout=None)
            view.add_item(select)
            await interaction.response.edit_message(embed=embed, view=view)
        elif self.values[0] == "coins":
            select = CoinsCategoryMenu(self.ctx)
            view = View(timeout=None)
            view.add_item(select)
            embed=disnake.Embed(title="🪙 Монеты:", description="**Вы можете купить кристалы у [MVXXL](https://discord.com/channels/@me/606371934170513428) или на сервере [тех.поддержки](https://discord.gg/ARbKXWbnCs).**", color=0xe8b11a)
            embed.add_field(name=f"🪙 300 Монет", value=f"\n```Стоимость: 10💎```", inline=True)
            embed.add_field(name=f"🪙 1500 Монет", value=f"\n```Стоимость: 50💎```", inline=True)
            embed.add_field(name=f"🪙 3500 Монет", value=f"\n```Стоимость: 100💎\n(выгода и популярность)```", inline=False)
            embed.add_field(name=f"🪙 20000 Монет", value=f"\n```Стоимость: 500💎\n(выгода)```", inline=False)
            await interaction.response.edit_message(embed=embed, view=view)


@client.event
async def on_button_click(interaction):
    if interaction.component.custom_id == "buy_skin":
        if interaction.user.id != interaction.author.id:
            print(f"{interaction.user.id} and {interaction.author.id}")
            await interaction.response.send_message(
                content="Вы не можете использовать эту кнопку, так как вы не являетесь ее автором.",
                ephemeral=True
            )
            return
        await handle_buy_skin(interaction)
    elif interaction.component.custom_id == "buy_event_skin":
        if interaction.user.id != interaction.author.id:
            print(f"{interaction.user.id} and {interaction.author.id}")
            await interaction.response.send_message(
                content="Вы не можете использовать эту кнопку, так как вы не являетесь ее автором.",
                ephemeral=True
            )
            return
        await handle_buy_event_skin(interaction)
    elif interaction.component.custom_id == "delete_message":
        if interaction.user.id != interaction.author.id:
            print(f"{interaction.user.id} and {interaction.author.id}")
            await interaction.response.send_message(
                content="Вы не можете использовать эту кнопку, так как вы не являетесь ее автором.",
                ephemeral=True
            )
            return
        await interaction.message.delete()
    elif interaction.component.custom_id == "referral_enter_code":
        await interaction.response.send_modal(modal=ReferModal())

async def handle_buy_skin(interaction):
    user_id = interaction.author.id

    selected_skin = interaction.message.embeds[0].title.split(": ")[1]

    cursor.execute('SELECT skin_name, rarity, price FROM store WHERE skin_name=?', (selected_skin,))
    result = cursor.fetchone()

    if result:
        skin_name, rarity, price = result

        cursor.execute('SELECT coins FROM users WHERE user_id=?', (user_id,))
        user_coins = cursor.fetchone()

        cursor.execute('SELECT skin_name FROM skins WHERE user_id=? AND skin_name=?', (user_id, skin_name))
        existing_skin = cursor.fetchone()

        if existing_skin:
            embed = disnake.Embed(description=f"У вас уже есть скин '{skin_name}'. Вы не можете купить его снова.", color=0xe8b11a)
            await interaction.message.delete()
            await interaction.response.send_message(embed=embed)  
        elif user_coins and user_coins[0] >= price:
            new_balance = user_coins[0] - price
            cursor.execute('INSERT OR REPLACE INTO users (user_id, coins) VALUES (?, ?)', (user_id, new_balance))

            cursor.execute('INSERT OR REPLACE INTO skins (user_id, skin_name, rarity) VALUES (?, ?, ?)',
                           (user_id, skin_name, rarity))

            conn.commit()

            confirmation_embed = disnake.Embed(
                title=f"Спасибо за покупку скина: {skin_name}",
                color=0x00ff00 
            )
            await interaction.message.delete()
            await interaction.response.send_message(embed=confirmation_embed) 
        else:
            await interaction.message.delete()
            embed = disnake.Embed(description="У вас недостаточно монет для покупки этого скина.", color=0xe8b11a)
            await interaction.response.send_message(embed=embed)  
    else:
        await interaction.message.delete()
        embed = disnake.Embed(description="Указан неверный идентификатор скина.", color=0xe8b11a)
        await interaction.response.send_message(embed=embed)  

async def handle_buy_event_skin(interaction):
    user_id = interaction.author.id

    selected_skin = interaction.message.embeds[0].title.split(": ")[1]

    cursor.execute('SELECT skin_name, rarity, price FROM event_store WHERE skin_name=?', (selected_skin,))
    result = cursor.fetchone()

    if result:
        skin_name, rarity, price = result

        cursor.execute('SELECT coins FROM users WHERE user_id=?', (user_id,))
        user_coins = cursor.fetchone()

        cursor.execute('SELECT skin_name FROM skins WHERE user_id=? AND skin_name=?', (user_id, skin_name))
        existing_skin = cursor.fetchone()

        if existing_skin:
            embed = disnake.Embed(description=f"У вас уже есть скин '{skin_name}'. Вы не можете купить его снова.", color=0xe8b11a)
            await interaction.message.delete()
            await interaction.response.send_message(embed=embed)  
        elif user_coins and user_coins[0] >= price:
            new_balance = user_coins[0] - price
            cursor.execute('INSERT OR REPLACE INTO users (user_id, coins) VALUES (?, ?)', (user_id, new_balance))

            cursor.execute('INSERT OR REPLACE INTO skins (user_id, skin_name, rarity) VALUES (?, ?, ?)',
                           (user_id, skin_name, rarity))

            conn.commit()

            confirmation_embed = disnake.Embed(
                title=f"Спасибо за покупку скина: {skin_name}",
                color=0x00ff00 
            )
            await interaction.message.delete()
            await interaction.response.send_message(embed=confirmation_embed) 
        else:
            await interaction.message.delete()
            embed = disnake.Embed(description="У вас недостаточно монет для покупки этого скина.", color=0xe8b11a)
            await interaction.response.send_message(embed=embed)  
    else:
        await interaction.message.delete()
        embed = disnake.Embed(description="Указан неверный идентификатор скина.", color=0xe8b11a)
        await interaction.response.send_message(embed=embed)  

@client.slash_command(name="store", description="Доступные скины в магазине.")
@commands.bot_has_permissions(view_channel=True)
async def store(ctx):
    user_id = ctx.author.id

    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT user_id FROM users WHERE user_id=?', (user_id,))
    existing_user = cursor.fetchone()

    if not existing_user:
        await ctx.send("Вы делаете всё не по инструкции. Пожалуйста, воспользуйтесь командой /help и следуйте инструкциям.")
        conn.close()
        return

    cursor.execute('SELECT bonus_granted FROM users WHERE user_id = ?', (user_id,))
    bonus_granted = cursor.fetchone()

    select = StoreCategoryMenu(ctx)
    view = View(timeout=None)
    view.add_item(select)

    if bonus_granted and bonus_granted[0] != 1:
        await ctx.send(embed=disnake.Embed(description=f"Выберите категорию магазина.", color=0xe8b11a), view=view)
    
        cursor.execute('UPDATE users SET diamonds = IFNULL(diamonds, 0) + 5, bonus_granted = 1 WHERE user_id = ?', (user_id,))
        conn.commit()

        cursor.execute('SELECT diamonds FROM users WHERE user_id = ?', (user_id,))
        user_diamonds = cursor.fetchone()

        new_diamond_balance = user_diamonds[0] if user_diamonds is not None and user_diamonds[0] is not None else 0
    else:
        await ctx.send(embed=disnake.Embed(description=f"Выберите категорию магазина.", color=0xe8b11a), view=view)
    conn.close()

@client.slash_command(name="top", description="Показать топ пользователей по длине лапши или количеству монет.")
@commands.bot_has_permissions(view_channel=True)
async def top_noodles(ctx, option: str = commands.Param(choices=["money", "noodles"])):
    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()

    if option == "money":
        cursor.execute('SELECT user_id, coins FROM users ORDER BY coins DESC LIMIT 10')
        top_users = cursor.fetchall()
        title = "Топ пользователей по количеству монет"
        unit = "монет(-а)"
    else:  # option == "noodles"
        cursor.execute('SELECT user_id, noodles_length FROM boiling ORDER BY noodles_length DESC LIMIT 10')
        top_users = cursor.fetchall()
        title = "Топ пользователей по длине лапши"
        unit = "метр(-ов)"

    if top_users:
        embed = disnake.Embed(title=title, color=0xe8b11a)
        for position, (user_id, value) in enumerate(top_users, start=1):
            user = await client.fetch_user(user_id)
            username = user.display_name if user else f"User ID: {user_id}"
            embed.add_field(name=f"{position}. {username}", value=f"{value} {unit}", inline=False)
        await ctx.send(embed=embed)
    else:
        await ctx.send(embed=disnake.Embed(description=f"Топ по {title} пока что пуст.", color=0xe8b11a))

@client.slash_command(name="profile", description="Показать информацию о пользователе.")
@commands.bot_has_permissions(view_channel=True)
async def profile(ctx, member: disnake.Member = None):
    user_id = ctx.author.id

    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT user_id FROM users WHERE user_id=?', (user_id,))
    existing_user = cursor.fetchone()

    if not existing_user:
        await ctx.send("Вы делаете всё не по инструкции. Пожалуйста, воспользуйтесь командой /help и следуйте инструкциям.")
        conn.close()
        return

    if member is None:
        member = ctx.author

    if member and not member.bot:
        user_id = member.id

        cursor.execute('SELECT coins, diamonds FROM users WHERE user_id=?', (user_id,))
        user_data = cursor.fetchone()

        cursor.execute('SELECT title FROM titles WHERE user_id=?', (user_id,))
        user_title_tuple = cursor.fetchone()
        if user_title_tuple:
            user_title = user_title_tuple[0]  
            user_title = user_title.strip("'")  
        else:
            user_title = "Нету"

        cursor.execute('SELECT noodles_length FROM boiling WHERE user_id=?', (user_id,))
        noodles_length = cursor.fetchone()

        user_rank = None
        if noodles_length:
            cursor.execute('''
                SELECT rank_name
                FROM ranks
                WHERE ? >= min_noodles
                ORDER BY min_noodles DESC
                LIMIT 1
            ''', (noodles_length[0],))

            result = cursor.fetchone()
            user_rank = result[0] if result else None

            if user_rank:
                cursor.execute('SELECT * FROM skins WHERE user_id=? AND skin_name=?', (user_id, user_rank))
                existing_skin = cursor.fetchone()

                if not existing_skin:
                    cursor.execute('INSERT INTO skins (user_id, skin_name, rarity) VALUES (?, ?, ?)', (user_id, user_rank, 'Ранговый'))
                    await ctx.send(embed=disnake.Embed(description=f"Поздравляем! Вы достигли ранга '{user_rank}' и получили ранговый скин.", color=0xe8b11a))

        if user_data is None:
            user_coins = "0"
            user_diamonds = "0"
        else:
            user_coins, user_diamonds = user_data

        cursor.execute('SELECT COUNT(*) FROM boiling WHERE noodles_length > (SELECT noodles_length FROM boiling WHERE user_id=?)', (user_id,))
        user_place = cursor.fetchone()[0] + 1

        if user_rank is None:
            user_rank = "Нету"

        if noodles_length is None:
            noodles_length = "0"

        if user_place is None:
            user_place = "Нету"

        cursor.execute('SELECT active_skin, rarity FROM active_skins WHERE user_id=?', (member.id,))
        active_skin_data = cursor.fetchone()
        
        if active_skin_data:
            active_skin_name, rarity = active_skin_data
            image_path = f"skin/{active_skin_name}.png"

            file = disnake.File(image_path, filename="skin.png")

            embed = disnake.Embed(title=f"Профиль {member.display_name}", description=f"**Баланс:** {user_coins} 🪙 {user_diamonds} 💎\n**Титул:** {user_title}\n\n**Ранг:** {user_rank}\n**Длина лапши:** {noodles_length[0]} 🍜\n", color=0xe8b11a)
            embed.set_thumbnail(url=f"attachment://skin.png")  
        else:
            image_path = "skin/none.png"
            active_skin = "Начальный"
            rarity = "Обычный"

            file = disnake.File(image_path, filename="skin.png")

            embed = disnake.Embed(title=f"Профиль {member.display_name}", description=f"**Баланс:** {user_coins} 🪙 {user_diamonds} 💎\n**Титул:** {user_title}\n\n**Ранг:** {user_rank}\n**Длина лапши:** {noodles_length[0]} 🍜\n", color=0xe8b11a)
            embed.set_thumbnail(url=f"attachment://skin.png")
        await ctx.send(embed=embed, file=file)
    else:
        await ctx.send("Команда не применима к ботам.", ephemeral=True)

@client.slash_command(name="daily_bonus", description="Получить ежедневный бонус монет.")
@commands.bot_has_permissions(view_channel=True)
async def daily_bonus(ctx):
    user_id = ctx.author.id

    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT user_id FROM users WHERE user_id=?', (user_id,))
    existing_user = cursor.fetchone()

    if not existing_user:
        await ctx.send("Вы делаете всё не по инструкции. Пожалуйста, воспользуйтесь командой /help и следуйте инструкциям.")
        conn.close()
        return

    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()

    current_date = datetime.now().strftime("%Y-%m-%d")

    cursor.execute('SELECT last_claimed_date FROM daily_bonus WHERE user_id=?', (user_id,))
    last_claimed_date = cursor.fetchone()

    if last_claimed_date and last_claimed_date[0] == current_date:
        await ctx.send("Вы уже получили ежедневный бонус сегодня.")
    else:
        bonus_coins = 100

        cursor.execute('INSERT OR REPLACE INTO daily_bonus (user_id, last_claimed_date) VALUES (?, ?)', (user_id, current_date))
        cursor.execute('UPDATE users SET coins = coins + ? WHERE user_id = ?', (bonus_coins, user_id))

        embed = disnake.Embed(description=f"Вы получили ежедневный бонус: {bonus_coins} 🪙", color=0xe8b11a)
        await ctx.send(embed=embed)

    conn.commit()
    conn.close()

@client.slash_command(name="help", description="Помощь новичкам.")
@commands.bot_has_permissions(view_channel=True)
async def help_command(ctx):
    embed = disnake.Embed(title="**Помощь по использованию бота Miwi**", color=0xe8b11a)

    # Шаг 1
    embed.add_field(name="**Шаг 1: Приготовление лапши**", value="Используйте `/boil`, чтобы приготовить лапшу и начать свое приключение.", inline=False)

    # Шаг 2
    embed.add_field(name="**Шаг 2: Покушайте лапшу**", value="Используйте `/eat`, чтобы поесть лапшу и получить монеты.", inline=False)

    # Шаг 3
    embed.add_field(name="**Шаг 3: Магазин скинов**", value="Используйте `/store`, чтобы посмотреть доступные скины в магазине.", inline=False)

    # Шаг 4
    embed.add_field(name="**Шаг 4: Покупка скинов**", value="Используйте `/buy-skin`, чтобы купить скин из магазина.", inline=False)

    # Шаг 5
    embed.add_field(name="**Шаг 5: Инвентарь скинов**", value="Используйте `/inventory`, чтобы посмотреть свои приобретенные скины.", inline=False)

    # Шаг 6
    embed.add_field(name="**Шаг 6: Установка скина**", value="Используйте `/set-skin`, чтобы установить скин из инвентаря.", inline=False)

    # Шаг 7
    embed.add_field(name="**Шаг 7: Просмотр скина**", value="Используйте `/view`, чтобы посмотреть активный скин.", inline=False)

    await ctx.send(embed=embed)


@client.slash_command(name="transfer", description="Перекинуть деньги другому игроку.")
@commands.bot_has_permissions(view_channel=True)
@commands.cooldown(3, 60, commands.BucketType.user) 
async def transfer(ctx, amount: int, recipient: disnake.User):
    user_id = ctx.author.id

    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT user_id FROM users WHERE user_id=?', (user_id,))
    existing_user = cursor.fetchone()

    if not existing_user:
        await ctx.send("Вы делаете всё не по инструкции. Пожалуйста, воспользуйтесь командой /help и следуйте инструкциям.")
        conn.close()
        return

    if ctx.author.bot or recipient.bot:
        await ctx.send("Команда не применима к ботам.", ephemeral=True)
        return

    if amount <= 0:
        await ctx.send(embed=disnake.Embed(description="Введите положительную сумму для перевода.", color=0xff0000))
        return

    sender_id = ctx.author.id
    recipient_id = recipient.id

    cursor.execute('SELECT coins FROM users WHERE user_id=?', (sender_id,))
    sender_balance = cursor.fetchone()

    if sender_balance and sender_balance[0] >= amount:
        cursor.execute('UPDATE users SET coins = coins - ? WHERE user_id=?', (amount, sender_id))

        cursor.execute('INSERT OR REPLACE INTO users (user_id, coins) VALUES (?, COALESCE((SELECT coins FROM users WHERE user_id = ?), 0) + ?)',
                       (recipient_id, recipient_id, amount))

        conn.commit()

        await ctx.send(embed=disnake.Embed(description=f"Вы успешно перевели {amount} монет пользователю {recipient.display_name}.", color=0x00ff00))
        await recipient.send(embed=disnake.Embed(description=f"{ctx.author.name} перевёл вам {amount}🪙.", color=0x00ff00))
    else:
        await ctx.send(embed=disnake.Embed(description="У вас недостаточно средств для перевода указанной суммы.", color=0xff0000))


@client.slash_command(name="eat", description="Покушать и получить денег.")
@commands.bot_has_permissions(view_channel=True)
@commands.cooldown(1, 3600, commands.BucketType.user) 
async def eat(ctx):
    user_id = ctx.author.id

    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT noodles_length FROM boiling WHERE user_id=?', (user_id,))
    noodles_length = cursor.fetchone()

    if noodles_length and noodles_length[0] > 0:
        noodles_length = noodles_length[0] - 1
        cursor.execute('UPDATE boiling SET noodles_length=? WHERE user_id=?', (noodles_length, user_id))

        earned_coins = random.randint(10, 70)
        cursor.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
        cursor.execute('UPDATE users SET coins = COALESCE(coins, 0) + ? WHERE user_id = ?', (earned_coins, user_id))

        conn.commit()

        embed = disnake.Embed(description=f"Ничего себе, а за то что едят получают деньги? Ну ладно, ты получил {earned_coins} монет.", color=0xe8b11a)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)
    else:
        await ctx.send(embed=disnake.Embed(description="Самый умный(-ая)? Сначала приготовь её с помощью: `/boil`.", color=0xe8b11a))

@client.slash_command(name="boil", description="Поварить лапшу.")
@commands.bot_has_permissions(view_channel=True)
@commands.cooldown(1, 3600, commands.BucketType.user)
async def boil(ctx):
    user_id = ctx.author.id

    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT noodles_length FROM boiling WHERE user_id=?', (user_id,))
    existing_length = cursor.fetchone()

    if existing_length:
        noodles_length = existing_length[0] + random.randint(1, 10)
        cursor.execute('UPDATE boiling SET noodles_length=? WHERE user_id=?', (noodles_length, user_id))
    else:
        noodles_length = random.randint(1, 10)
        cursor.execute('INSERT INTO boiling (user_id, noodles_length) VALUES (?, ?)', (user_id, noodles_length))

        cursor.execute('SELECT rank_name FROM ranks WHERE ? >= min_noodles ORDER BY min_noodles DESC LIMIT 1', (noodles_length,))
        rank_result = cursor.fetchone()

        if rank_result:
            user_rank = rank_result[0]

            cursor.execute('SELECT * FROM skins WHERE user_id=? AND skin_name=?', (user_id, user_rank))
            existing_skin = cursor.fetchone()

            if not existing_skin:
                cursor.execute('INSERT INTO skins (user_id, skin_name, rarity) VALUES (?, ?, ?)', (user_id, user_rank, 'Ранговый'))
                await ctx.send(embed=disnake.Embed(description=f"Поздравляем! Вы достигли ранга '{user_rank}' и получили ранговый скин.", color=0xe8b11a))


    conn.commit()
    conn.close()
    embed=disnake.Embed(description=f"Мммм, лапша, вкусняшка. У тебя уже {noodles_length}м.", color=0xe8b11a)
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
    await ctx.send(embed=embed)

@transfer.error
@eat.error
@boil.error
async def eat_boil_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        retry_after_seconds = int(error.retry_after)
        cooldown_embed = disnake.Embed(title="Ошибка!", description=f"Вы сможете использовать команду <t:{int(time.time() + retry_after_seconds)}:R>", color=0xe8b11a)
        await ctx.response.send_message(embed=cooldown_embed, ephemeral=True)

        if retry_after_seconds == 0:
            cooldown_notification_embed = disnake.Embed(title="Уведомление", description="Вы уже можете снова использовать команду.", color=0xe8b11a)
            await ctx.author.send(embed=cooldown_notification_embed)
    else:
        await ctx.send(f"Unhandled error: {error}")

@client.slash_command(name="refer", description="Получить реферальный код")
async def refer(ctx):
    user_id = ctx.author.id

    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT user_id FROM users WHERE user_id=?', (user_id,))
    existing_user = cursor.fetchone()

    if not existing_user:
        await ctx.send("Вы делаете всё не по инструкции. Пожалуйста, воспользуйтесь командой /help и следуйте инструкциям.")
        conn.close()
        return

    cursor.execute('SELECT referral_code FROM users WHERE user_id = ?', (user_id,))
    existing_referral_code = cursor.fetchone()

    if existing_referral_code and existing_referral_code[0]:
        embed = disnake.Embed(description=f"Ваш реферальный код: `{existing_referral_code[0]}`", color=0xe8b11a)
        enter_code_button = disnake.ui.Button(
            label="Ввести код",
            style=disnake.ButtonStyle.primary,
            custom_id="referral_enter_code"  
        )
        action_row = disnake.ui.ActionRow(enter_code_button)
        await ctx.send(embed=embed, components=[action_row])
    else:
        new_referral_code = generate_referral_code()

        cursor.execute('UPDATE users SET referral_code = ? WHERE user_id = ?', (new_referral_code, user_id))
        conn.commit()

        conn.close()  

        embed = disnake.Embed(description=f"Ваш новый реферальный код: `{new_referral_code}`", color=0xe8b11a)
        await ctx.send(embed=embed)

@client.command(name='add_money')
@commands.has_permissions(administrator=True)
async def add_money(ctx, member: disnake.Member, amount: int):
    user_id = member.id

    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM bute WHERE user_id = ?', (user_id,))
    existing_user_bute = cursor.fetchone()

    if existing_user_bute:
        new_amount_bute = existing_user_bute[1] + 1
        cursor.execute('UPDATE bute SET numbers = ? WHERE user_id = ?', (new_amount_bute, user_id))
    else:
        cursor.execute('INSERT INTO bute (user_id, numbers) VALUES (?, ?)', (user_id, 1))

    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    existing_user = cursor.fetchone()

    if existing_user:
        new_amount = existing_user[1] + amount
        cursor.execute('UPDATE users SET coins = ? WHERE user_id = ?', (new_amount, user_id))
    else:
        cursor.execute('INSERT INTO users (user_id, coins) VALUES (?, ?)', (user_id, amount))

    conn.commit()

    cursor.execute('SELECT coins FROM users WHERE user_id = ?', (user_id,))
    updated_coins = cursor.fetchone()[0]

    conn.close()

    await ctx.send(f'{amount} монет добавлено пользователю {member.mention}. Теперь у него {updated_coins} монет.')

class ReferModal(disnake.ui.Modal):
    def __init__(self):
        components = [
            disnake.ui.TextInput(
                label="Код реферрала",
                placeholder="Введите реферральный код",
                custom_id="referral_code",
                style=TextInputStyle.paragraph
            ),
        ]
        super().__init__(title="Активация реферрального кода", components=components)

    async def callback(self, interaction: disnake.ModalInteraction):
        referral_code = interaction.text_values.get("referral_code", "None")
        await activate_referral_code(interaction, referral_code)

async def activate_referral_code(interaction, referral_code: str):
    user_id = interaction.user.id

    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT user_id FROM users WHERE user_id=?', (user_id,))
    existing_user = cursor.fetchone()

    if not existing_user:
        await interaction.response.send_message("Вы делаете всё не по инструкции. Пожалуйста, воспользуйтесь командой /help и следуйте инструкциям.")
        conn.close()
        return

    cursor.execute('SELECT user_id FROM users WHERE referral_code = ? AND user_id = ?', (referral_code, user_id))
    self_activation = cursor.fetchone()

    if self_activation:
        embed = disnake.Embed(description="Вы не можете активировать свой собственный реферальный код.", color=0xe8b11a)
        await interaction.response.send_message(embed=embed)
        conn.close()
        return

    cursor.execute('SELECT user_id FROM users WHERE referral_code = ?', (referral_code,))
    referred_user_id = cursor.fetchone()

    if not referred_user_id:
        embed = disnake.Embed(description="Указанный реферальный код не существует.", color=0xe8b11a)
        await interaction.response.send_message(embed=embed)
        conn.close()
        return

    referred_user_id = referred_user_id[0]

    cursor.execute('SELECT referring_user_id FROM users WHERE user_id = ?', (user_id,))
    existing_referring_user_id = cursor.fetchone()

    if existing_referring_user_id and existing_referring_user_id[0]:
        embed = disnake.Embed(description="Вы уже активировали реферальный код.", color=0xe8b11a)
        await interaction.response.send_message(embed=embed)
        conn.close()
        return

    cursor.execute('UPDATE users SET referring_user_id = ? WHERE user_id = ?', (referred_user_id, user_id))
    conn.commit()

    grant_coins_and_diamonds(user_id, referred_user_id)

    embed = disnake.Embed(description=f"Реферальный код успешно активирован! Получено 50 монет и 5 диамантов.", color=0xe8b11a)
    await interaction.response.send_message(embed=embed)
    conn.close()


def grant_coins_and_diamonds(user_id, referred_user_id):
    cursor.execute('UPDATE users SET coins = IFNULL(coins, 0) + 50, diamonds = IFNULL(diamonds, 0) + 5 WHERE user_id IN (?, ?)', (user_id, referred_user_id))
    conn.commit()

def generate_referral_code(max_attempts=10):
    code_length = 6

    for _ in range(max_attempts):
        referral_code = secrets.token_hex(code_length // 2).upper()

        cursor.execute('SELECT user_id FROM users WHERE referral_code = ?', (referral_code,))
        existing_user_id = cursor.fetchone()

        if not existing_user_id:
            conn.close() 
            return referral_code

    conn.close()  
    return None

# class LolCategoryMenu(Select):
#     def __init__(self, ctx, skins) -> None:
#         options = [
#             SelectOption(label=skin[0], value=skin[0])  
#             for skin in skins
#         ]

#         super().__init__(placeholder="Выберите скин для установки", options=options)
#         self.ctx = ctx
#         self.skins = skins  

#     async def callback(self, interaction):
#         if interaction.user.id != interaction.author.id:
#             await interaction.response.send_message(
#                 content="Вы не можете использовать эту кнопку, так как вы не являетесь ее автором.",
#                 ephemeral=True
#             )
#             return

#         author = interaction.author.id
#         selected_value = interaction.data['values'][0]

#         if selected_value in [skin[0] for skin in self.skins]:
#             self.update_active_skin(author, selected_value) 
#             message = f"Скин **{selected_value}** успешно изменен!"
#         else:
#             message = f"Скин с именем **{selected_value}** уже установлен! Пожалуйста, выберите другой скин."

#         await interaction.response.send_message(
#             content=message,
#             ephemeral=True
#         )

#     def update_active_skin(self, author, selected_skin):
#         user_id = author
#         conn = sqlite3.connect('your_database.db')
#         cursor = conn.cursor()

#         try:
#             cursor.execute('SELECT skin_name, rarity FROM skins WHERE user_id=? AND skin_name=?', (user_id, selected_skin))
#             existing_skin = cursor.fetchone()

#             if existing_skin:
#                 existing_skin_name, existing_rarity = existing_skin

#                 cursor.execute('INSERT OR IGNORE INTO active_skins (user_id, active_skin, rarity) VALUES (?, ?, ?)', (user_id, existing_skin_name, existing_rarity))
#                 conn.commit()

#         except sqlite3.Error as e:
#             print(f"SQLite error: {e}")
#             pass

#         conn.close()

@client.slash_command(name="closet", description="Просмотреть список приобретенных скинов.")
@commands.bot_has_permissions(view_channel=True)
async def closet(ctx, member: Optional[disnake.Member] = None):
    user_id = member.id if member else ctx.author.id

    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT skin_name, rarity FROM skins WHERE user_id=?', (user_id,))
    results = cursor.fetchall()
    # select = LolCategoryMenu(ctx, results)  
    # view = View(timeout=None)
    # view.add_item(select)
    if results:
        rarities_order = ["Премиум", "Коллекционный", "Легендарный", "Мифический", "Эпический", "Редкий", "Необычный", "Обычный", "Ранговый"]
        rarities_mapping = {rarity: index for index, rarity in enumerate(rarities_order)}
        results_sorted = sorted(results, key=lambda x: rarities_mapping[x[1]])

        embed = disnake.Embed(title="Гардероб скинов", description="Воу гардеробчик, и что тут у тебя?", color=0xe8b11a)
        for i, (skin_name, rarity) in enumerate(results_sorted):
            if i % 4 < 2:  
                embed.add_field(name=f"**{skin_name}**", value=f"```Редкость: {rarity}```", inline=True)
            else:
                embed.add_field(name=f"**{skin_name}**", value=f"```Редкость: {rarity}```", inline=False)
        await ctx.send(embed=embed)
    else:
        embed = disnake.Embed(title="Гардероб скинов", description="Ты, как мода, только что вышел. Гардероб твоих скинов - пуст!.", color=0xe8b11a)
        await ctx.send(embed=embed)

    conn.close()

@client.slash_command(name="set-skin", description="Установить скин на упаковку лапши.")
@commands.bot_has_permissions(view_channel=True)
async def set_skin(ctx, skinname: str = commands.Param(name="название-скина", description="введите название скина который хотити применить.")):
    user_id = ctx.author.id

    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT user_id FROM users WHERE user_id=?', (user_id,))
    existing_user = cursor.fetchone()

    if not existing_user:
        await ctx.send("Вы делаете всё не по инструкции. Пожалуйста, воспользуйтесь командой /help и следуйте инструкциям.")
        conn.close()
        return

    try:
        cursor.execute('SELECT skin_name, rarity FROM skins WHERE user_id=? AND skin_name=?', (user_id, skinname))
        existing_skin = cursor.fetchone()

        if existing_skin:
            existing_skin_name, existing_rarity = existing_skin

            cursor.execute('SELECT * FROM active_skins WHERE user_id=?', (user_id,))
            existing_active_skin = cursor.fetchone()

            if existing_active_skin:
                cursor.execute('UPDATE active_skins SET active_skin=?, rarity=? WHERE user_id=?', (existing_skin_name, existing_rarity, user_id))
            else:
                cursor.execute('INSERT INTO active_skins (user_id, active_skin, rarity) VALUES (?, ?, ?)', (user_id, existing_skin_name, existing_rarity))

            conn.commit()

            embed = disnake.Embed(title=f"Скин успешно установлен [{existing_skin_name}]", color=0xe8b11a)
            await ctx.send(embed=embed)
        else:
            await ctx.send(embed=disnake.Embed(description="У вас нет такого скина в инвентаре.", color=0xe8b11a))

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        await ctx.send(embed=disnake.Embed(description="Произошла ошибка при попытке сменить скин.", color=0xe8b11a))

@client.slash_command(name="promocode", description="Использовать промокод.")
@commands.bot_has_permissions(view_channel=True)
async def promocode(ctx, code: str = commands.Param(name="код-промокода", description="Введите промокод.")):
    user_id = ctx.author.id

    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT user_id FROM users WHERE user_id=?', (user_id,))
    existing_user = cursor.fetchone()

    if not existing_user:
        await ctx.send("Вы делаете всё не по инструкции. Пожалуйста, воспользуйтесь командой /help и следуйте инструкциям.")
        conn.close()
        return

    cursor.execute('SELECT * FROM promocodes WHERE code=?', (code,))
    existing_promocode = cursor.fetchone()

    if existing_promocode:
        cursor.execute('SELECT * FROM claimed_promocodes WHERE user_id=? AND promocode=?', (user_id, code))
        existing_claim = cursor.fetchone()

        if not existing_claim:
            bonus_coins = existing_promocode[1]  
            noodles_length = existing_promocode[2]  

            cursor.execute('INSERT INTO claimed_promocodes (user_id, promocode) VALUES (?, ?)', (user_id, code))
            cursor.execute('UPDATE users SET coins = coins + ?, noodles_length = noodles_length + ? WHERE user_id = ?', (bonus_coins, noodles_length, user_id))
            conn.commit()

            await ctx.send(embed=disnake.Embed(description=f"Промокод успешно использован! Вам начислено {bonus_coins} 🪙. Длина лапши увеличена на {noodles_length} метров.", color=0xe8b11a))
        else:
            await ctx.send(embed=disnake.Embed(description="Вы уже использовали этот промокод.", color=0xe8b11a))

    else:
        await ctx.send(embed=disnake.Embed(description="Неверный промокод.", color=0xe8b11a))

    conn.close()


@client.command(name='exec')
async def genius_exec(ctx, *, code: str) -> None:
    if ctx.author.id not in [606371934170513428]:
        return
    PREFIXES = ['```python\n', '```py\n', '```\n', '``', '`']
    for prefix in PREFIXES:
        if code.startswith(prefix):
            code = code[len(prefix):]
            break
    SUFFIXES = ['\n```', '```', '``', '`']
    for suffix in SUFFIXES:
        if code.endswith(suffix):
            code = code[:-len(suffix)]
            break
    CODE_START: str = "```py\n"
    CODE_END: str = "\n```"
    LIMIT: int = 2000 - (len(CODE_START) + len(CODE_END))
    try:
        await aioconsole.aexec(
            code,
            local=globals() | locals() | {'ctx': ctx, 'bot': client},
            filename="<discord>",
        )
    except BaseException as e:
        print(e)
        await ctx.message.add_reaction("😿")
        stacktrace = ''.join(traceback.format_exception(e))
        await ctx.author.send(f"{CODE_START}{stacktrace[:LIMIT]}{CODE_END}")
    else:
        await ctx.message.add_reaction("😸")

@client.event
async def on_bot_disconnect():
    conn.close()

client.run("")