import discord
from discord.ext import commands
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import asyncio

intents = discord.Intents.default()
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)


TOKEN = 'MTI5ODcxMDAzODQ5MTI5OTkwMA.GZY--1.uCt6kJf_zfRs1BVUC4lR3LWhSXR4MIXh4OVLeg'
CHANNEL_ID = 1298674219974004796  # Replace with your Discord channel ID

# Set up the Selenium WebDriver for Twitch
def setup_twitch_chat(twitch_url):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    
    driver.get(twitch_url)
    time.sleep(5)  # Wait for the page to load

    return driver

# Scrape the chat messages
def get_twitch_chat_messages(driver):
    chat_selector = 'div[data-a-target="chat-message-text"]'
    chat_elements = driver.find_elements(By.CSS_SELECTOR, chat_selector)

    messages = []
    for element in chat_elements:
        messages.append(element.text)

    return messages

# Send messages to Discord
async def send_to_discord_channel(channel_id, message):
    channel = bot.get_channel(channel_id)
    if channel:
        await channel.send(message)

# Monitor Twitch chat and send messages to Discord
async def monitor_twitch_chat(twitch_url, channel_id):
    driver = setup_twitch_chat(twitch_url)
    last_seen_messages = set()

    while True:
        messages = get_twitch_chat_messages(driver)

        # Send only new messages
        new_messages = [msg for msg in messages if msg not in last_seen_messages]
        last_seen_messages.update(new_messages)

        for message in new_messages:
            await send_to_discord_channel(channel_id, message)
        
        await asyncio.sleep(5)  

@bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {bot.user}')

# Get Twitch username input before starting the bot
def get_twitch_username():
    twitch_user = input("Please enter the Twitch username: ")
    return twitch_user.strip()

# Command to start Twitch chat monitoring
@bot.command(name='start_twitch_chat')
async def start_twitch_chat(ctx):
    twitch_user = get_twitch_username()  # Get the username directly
    twitch_url = f"https://www.twitch.tv/{twitch_user}"
    await ctx.send(f"Starting Twitch chat monitoring for {twitch_url}...")
    bot.loop.create_task(monitor_twitch_chat(twitch_url, ctx.channel.id))

bot.run(TOKEN)