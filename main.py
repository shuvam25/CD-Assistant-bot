import os

token = os.environ.get("TOKEN")

import nextcord
from nextcord import Member, role
from nextcord.ext import commands
from nextcord import Interaction, SlashOption, Attachment, ButtonStyle
from nextcord.utils import get
import json
import nextcord
from nextcord.ext import commands
import logging
import requests
from nextcord.ui import Button, Select, View, Modal, TextInput
import requests
from nextcord.utils import get
from apis import *
import random
from datetime import datetime, timedelta
import pytz
import time
import asyncio
import subprocess
import math


# Set up logging
logging.basicConfig(level=logging.INFO)

SUPPORTERS_ID = 1309911584457494588  # Replace with your supporters channel ID
GUILD_ID = 1021619736292904971
ORDER_LOG_CHANNEL_ID = 1063248635288113202  # Replace with your order logs channel ID
SUPPORT_LOG_CHANNEL_ID = 1195278351665991760  # Replace with your support logs channel ID
LOUNGE_ID = 1021619738306162690
REVIEWS_ID = 1309911036123414609  # Replace with your reviews channel ID
PROMOTION_ID = 1309857031087329391
ACTION_ID = 1309857105745936515

intents = nextcord.Intents.default()
intents.message_content = True
intents.members = True
client = commands.Bot(command_prefix='cd!', intents=intents)

# File to store order logs
ORDER_LOGS_FILE = 'order_logs.json'
SUPPORT_LOGS_FILE = 'support_logs.json'
LINKED_ACCOUNTS_FILE = 'linked_accounts.json'
# File to store permanent order logs
PERM_ORDER_LOGS_FILE = 'permorder_log.json'
PERM_SUPPORT_LOGS_FILE = 'permsupport_log.json'

# Load order logs from file
if os.path.exists(ORDER_LOGS_FILE):
    with open(ORDER_LOGS_FILE, 'r') as file:
        order_logs = json.load(file)
else:
    order_logs = {}

# Load support logs from file
if os.path.exists(SUPPORT_LOGS_FILE):
    with open(SUPPORT_LOGS_FILE, 'r') as file:
        support_logs = json.load(file)
else:
    support_logs = {}

# Load linked accounts from file
if os.path.exists(LINKED_ACCOUNTS_FILE):
    with open(LINKED_ACCOUNTS_FILE, 'r') as file:
        linked_accounts = json.load(file)
else:
    linked_accounts = {}

# Restrict commands to STAFF_ID role holders
STAFF_ID = 123456789012345678  # Replace with the actual role ID



@client.event
async def on_ready():
    logging.info('Bot is ready.')
    logging.info('----------------------')
    guild = client.get_guild(GUILD_ID)
    channel = nextcord.utils.get(guild.text_channels, id=1110779991626629252)
    if channel:
        await channel.send("Hey guys Shuvam just sent another update please use the /career_form command and /ticket_menu command in contact us channel and career channel as it needs to be updated to be able to use them, Bot is online again!\n\n <@&1302761965277544448> | <@&1108029461967945850> ")

@client.event
async def on_member_join(member):
    logging.info(f"{member} has joined the server.")  
    guild = member.guild
    member_count = guild.member_count
    channel = nextcord.utils.get(guild.text_channels, id=LOUNGE_ID)
    if channel:
        # Create the welcome message
        welcome_message = (
            "<:CD_wave:1310206456712269876> *Welcome to Comet Designs, {0.mention}!*  \n"
            "-# We hope you will enjoy being part of our community!"
        ).format(member)

        # Create the buttons
        dashboard_button = Button(
            label="Dashboard",
            url="https://discord.com/channels/1021619736292904971/1021622027297239171",
            style=ButtonStyle.link
        )
        order_button = Button(
            label="Order here",
            url="https://discord.com/channels/1021619736292904971/1224486146046955590",
            style=ButtonStyle.link
        )
        member_count_button = Button(
            label=f"Member Count: {member_count}",
            style=ButtonStyle.gray,
            disabled=True
        )

        view = View()
        view.add_item(dashboard_button)
        view.add_item(order_button)
        view.add_item(member_count_button)

        await channel.send(welcome_message, view=view)
    else:
        logging.warning("Channel not found. ----------------------")  

def safe_load_json(path, default):
    try:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    # empty file -> initialize with default
                    with open(path, 'w', encoding='utf-8') as wf:
                        json.dump(default, wf)
                    return default
                return json.loads(content)
        else:
            return default
    except json.JSONDecodeError:
        logging.warning(f"Invalid JSON in {path}, resetting to default.")
        try:
            with open(path, 'w', encoding='utf-8') as wf:
                json.dump(default, wf)
        except Exception as e:
            logging.error(f"Failed to reset {path}: {e}")
        return default
    except Exception as e:
        logging.error(f"Error loading {path}: {e}")
        return default

# Load permanent order logs from file
perm_order_logs = safe_load_json(PERM_ORDER_LOGS_FILE, {})

# Load permanent support logs from file
perm_support_logs = safe_load_json(PERM_SUPPORT_LOGS_FILE, {})
linked_accounts = safe_load_json(LINKED_ACCOUNTS_FILE, {})

# Save order logs to file
def save_order_logs():
    with open(ORDER_LOGS_FILE, 'w') as file:
        json.dump(order_logs, file)
    with open(PERM_ORDER_LOGS_FILE, 'w') as file:
        json.dump(perm_order_logs, file)

# Save support logs to file
def save_support_logs():
    with open(SUPPORT_LOGS_FILE, 'w') as file:
        json.dump(support_logs, file)
    with open(PERM_SUPPORT_LOGS_FILE, 'w') as file:
        json.dump(perm_support_logs, file)

# Save linked accounts to file
def save_linked_accounts():
    with open(LINKED_ACCOUNTS_FILE, 'w') as file:
        json.dump(linked_accounts, file)

# REVIEW SLASH COMMAND --------------------------------------------------------------------------------
@client.slash_command(guild_ids=[GUILD_ID], description="Submit a review")
async def review(
    interaction: Interaction,
    designer: nextcord.Member = SlashOption(description="Designer to review, If you are unaware put comet designs as designer.", required=True, default="<@1088788105366097930>"),
    product: str = SlashOption(description="Name of the product", required=True),
    rating: int = SlashOption(description="Rating (1-5)", required=True, choices=[1, 2, 3, 4, 5]),
    extra_notes: str = SlashOption(description="Extra notes", required=False, default="No additional notes provided.")
):
    try:
        embed = nextcord.Embed(title="**<:CD_partner:1310207556903501844> Review**", color=0xff913a)
        embed.set_author(name=f"Review from {interaction.user}", icon_url=interaction.user.avatar.url)
        embed.set_image(url="https://media.discordapp.net/attachments/1307830607262384128/1500818157882052698/Footer_banner.png?ex=69f9d154&is=69f87fd4&hm=88ed0d5062d1e972647b5835692fefcca61ef43ef825fb3fa503b47cf69e42be&=&format=webp&quality=lossless&width=1859&height=129")
        embed.add_field(name="**<:CD_dot:1310207495691567145>Designer:**", value=designer.mention, inline=True)
        embed.add_field(name="**<:CD_dot:1310207495691567145>Product:**", value=product, inline=True)
        embed.add_field(name="**<:CD_dot:1310207495691567145>Rating:**", value="".join(["<:CD_Star:1337489151154454529>"] * rating), inline=True)
        embed.add_field(name="**<:CD_dot:1310207495691567145>Extra Notes:**", value=extra_notes, inline=False)
        embed.set_footer(text="Thank you for your review", icon_url="https://media.discordapp.net/attachments/1307830343482478725/1307837864914059314/CDLOGO_MGMT_BLACK.png?ex=674c3d2d&is=674aebad&hm=f3b757b37d41bcb9d68f8c408fe55c800b84cb6e3b6bd841a118045435bc51da&=&format=webp&quality=lossless&width=481&height=481")
        embed.timestamp = interaction.created_at

        review_channel = client.get_channel(REVIEWS_ID)
        if review_channel:
            await review_channel.send(embed=embed, content= f"{designer.mention}")
            await interaction.response.send_message("Review submitted successfully!", ephemeral=True)
        else:
            await interaction.response.send_message("Review channel not found.", ephemeral=True)
    except Exception as e:
        logging.error(f"Error in review command: {e}")
        await interaction.response.send_message("An error occurred while submitting your review.", ephemeral=True)

# ORDER LOG SLASH COMMAND --------------------------------------------------------------------------------
@client.slash_command(guild_ids=[GUILD_ID], description="Use this command to log your order")
async def order_log(
    interaction: Interaction,
    designer: nextcord.Member = SlashOption(description="Designer to log", required=True),
    original_price: float = SlashOption(description="Price without tax", required=True),
    total_price: float = SlashOption(description="Price including tax", required=True),
    panel_name: str = SlashOption(description="Panel Name", required=True),
    ticket_id: str = SlashOption(description="Ticket ID", required=True),
    note: str = SlashOption(description="Additional notes", required=False, default="No additional notes provided.")
):
    try:
        # Check if the user invoking the command has the correct role
        if "Staff Team" not in [role.name for role in interaction.user.roles]:
            await interaction.response.send_message("❌ You don't have the required role to log orders.", ephemeral=True)
            return

        # Check if the designer has the required role
        if "Creative Team" not in [role.name for role in designer.roles]:
            await interaction.response.send_message("❌ The designer must have the 'Creative Team' role to be logged.", ephemeral=True)
            return

        if original_price > total_price:
            await interaction.response.send_message("❌ Original price must be less than or equal to total price.", ephemeral=True)
            return

        embed = nextcord.Embed(title="<:CD_cart:1322299968450461737> Order Log", color=0xff913a)
        embed.set_image(url="https://media.discordapp.net/attachments/1307830607262384128/1500818157882052698/Footer_banner.png?ex=69f9d154&is=69f87fd4&hm=88ed0d5062d1e972647b5835692fefcca61ef43ef825fb3fa503b47cf69e42be&=&format=webp&quality=lossless&width=1859&height=129")
        embed.add_field(name="<:CD_Discord:1310206398717755532> Designer", value=designer.mention, inline=False)
        embed.add_field(name="<:CD_robux:1310207300522213507> Original Price", value=f"${original_price:.2f}", inline=True)
        embed.add_field(name="<:CD_robux:1310207300522213507> Total Price", value=f"${total_price:.2f}", inline=True)
        embed.add_field(name="<:CD_book:1310235460270035047> Panel Name", value=panel_name, inline=True)
        embed.add_field(name="<:CD_settings:1310207018161934376> Ticket ID", value=ticket_id, inline=True)
        embed.add_field(name="<:CD_dot:1310207495691567145>Note", value=note, inline=False)
        embed.set_footer(text=f"Logged by {interaction.user}", icon_url=interaction.user.avatar.url)
        
        log_channel = client.get_channel(ORDER_LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(content=f"{designer.mention}", embed=embed)
            await interaction.response.send_message("✅ Order log successful.", ephemeral=True)
            
            # Update order logs
            if designer.name not in order_logs:
                order_logs[designer.name] = {
                    "total_logs": 0,
                    "total_earnings": 0.0
                }
            order_logs[designer.name]["total_logs"] += 1
            order_logs[designer.name]["total_earnings"] += original_price
            
            # Update permanent order logs
            if designer.name not in perm_order_logs:
                perm_order_logs[designer.name] = {
                    "total_logs": 0,
                    "total_earnings": 0.0
                }
            perm_order_logs[designer.name]["total_logs"] += 1
            perm_order_logs[designer.name]["total_earnings"] += original_price
            
            # Save order logs to file
            save_order_logs()
        else:
            await interaction.response.send_message("⚠️ Log channel not found.", ephemeral=True)
    except Exception as e:
        logging.error(f"Error in order_log command: {e}")
        await interaction.response.send_message("❌ An error occurred while logging the order.", ephemeral=True)

# SUPPORT LOG SLASH COMMAND --------------------------------------------------------------------------------
@client.slash_command(guild_ids=[GUILD_ID], description="Use this command to log your support ticket")
async def support_log(
    interaction: Interaction,
    support_staff: nextcord.Member = SlashOption(description="Support staff to log", required=True),
    date_of_opening: str = SlashOption(description="Date of opening", required=True),
    date_of_closing: str = SlashOption(description="Date of closing", required=True),
    panel_name: str = SlashOption(description="Panel Name", required=True),
    ticket_id: str = SlashOption(description="Ticket ID", required=True),
    note: str = SlashOption(description="Additional notes", required=False, default="N/A")
):
    try:
        # Check if the invoker has the correct role
        if not any(role.name in ["Support Team", "Board of Directors", "Executive Board"] for role in interaction.user.roles):
            await interaction.response.send_message("❌ You don't have the required role to log support tickets.", ephemeral=True)
            return

        # Check if the target support staff has the Support Team role
        if "Support Team" not in [role.name for role in support_staff.roles]:
            await interaction.response.send_message("❌ The support staff must have the 'Support Team' role to be logged.", ephemeral=True)
            return

        # Create the embed
        embed = nextcord.Embed(title="<:CD_Info:1310206627466711140> Support Log", color=0xff913a)
        embed.set_image(url="https://media.discordapp.net/attachments/1307830607262384128/1500818157882052698/Footer_banner.png?ex=69f9d154&is=69f87fd4&hm=88ed0d5062d1e972647b5835692fefcca61ef43ef825fb3fa503b47cf69e42be&=&format=webp&quality=lossless&width=1859&height=129")
        embed.add_field(name="<:CD_Discord:1310206398717755532> Support Staff", value=support_staff.mention, inline=False)
        embed.add_field(name="<:CD_time:1310206753379450910> Date of Opening", value=date_of_opening, inline=True)
        embed.add_field(name="<:CD_time:1310206753379450910> Date of Closing", value=date_of_closing, inline=True)
        embed.add_field(name="<:CD_book:1310235460270035047> Panel Name", value=panel_name, inline=True)
        embed.add_field(name="<:CD_settings:1310207018161934376> Ticket ID", value=ticket_id, inline=True)
        embed.add_field(name="<:CD_dot:1310207495691567145>Note", value=note, inline=False)
        embed.set_footer(text=f"Logged by {interaction.user}", icon_url=interaction.user.avatar.url)

        log_channel = client.get_channel(SUPPORT_LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(content=f"{support_staff.mention}", embed=embed)
            await interaction.response.send_message("✅ Log successful.", ephemeral=True)

            # Update support logs
            if support_staff.name not in support_logs:
                support_logs[support_staff.name] = {"total_logs": 0}
            support_logs[support_staff.name]["total_logs"] += 1

            # Update permanent support logs
            if support_staff.name not in perm_support_logs:
                perm_support_logs[support_staff.name] = {"total_logs": 0}
            perm_support_logs[support_staff.name]["total_logs"] += 1

            # Save logs
            save_support_logs()
        else:
            await interaction.response.send_message("⚠️ Log channel not found.", ephemeral=True)
    except Exception as e:
        logging.error(f"Error in support_log command: {e}")
        await interaction.response.send_message("❌ An error occurred while logging the support ticket.", ephemeral=True)


# INFRACT SLASH COMMAND --------------------------------------------------------------------------------
@client.slash_command(guild_ids=[GUILD_ID], description="Issue an infraction")
async def infract(
    interaction: Interaction,
    infraction: str = SlashOption(
        description="Type of infraction",
        required=True,
        choices=["Strike", "Termination Warning", "Termination"]
    ),
    username: nextcord.Member = SlashOption(description="User to infract", required=True),
    reason: str = SlashOption(description="Reason for infraction", required=True),
):
    # List of allowed role IDs
    allowed_roles = {1302761965277544448, 1108029461967945850, 1309883023008989265}
    
    # Check if user has any of the allowed roles
    if not any(role.id in allowed_roles for role in interaction.user.roles):
        await interaction.response.send_message("❌ You don’t have permission to use this command.", ephemeral=True)
        return

    try:
        # Create embed message
        embed = nextcord.Embed(title=f"{infraction}", color=0xff0808)
        embed.set_image(url="https://media.discordapp.net/attachments/1256596793999888447/1310712746962063370/Sin_titulo_72_x_9_in_72_x_5_in_1.png?ex=674c269e&is=674ad51e&hm=0d15dfda191f485821f4ebf88cc4800278505db750303b6ba7e1cedcf7f80375&=&format=webp&quality=lossless&width=1439&height=100")
        embed.add_field(name="<:CD_dot:1310207495691567145>Username", value=username.mention, inline=False)
        embed.add_field(name="<:CD_dot:1310207495691567145>Reason", value=reason, inline=False)
        embed.set_footer(text=f"Authorised by {interaction.user.display_name}", icon_url=interaction.user.avatar.url)

        # Send embed message in the infraction channel
        infraction_channel = client.get_channel(ACTION_ID)
        if infraction_channel:
            await infraction_channel.send(content=f"{username.mention}", embed=embed)
            await interaction.response.send_message("✅ Infraction has been successfully logged.", ephemeral=True)
        else:
            await interaction.response.send_message("⚠️ Infraction channel not found.", ephemeral=True)

        # DM the user
        dm_message = (
            f"**Infraction:** {infraction}\n"
            f"**Username:** {username.mention}\n"
            f"**Reason:** {reason}\n"
            f"**Authorised by:** {interaction.user.display_name}"
        )
        await username.send(dm_message)

    except Exception as e:
        import logging
        logging.error(f"Error in infract command: {e}")
        await interaction.response.send_message("❌ An error occurred while issuing the infraction.", ephemeral=True)



# OUTLET SLASH COMMAND --------------------------------------------------------------------------------
@client.slash_command(guild_ids=[GUILD_ID], description="Create an outlet post")
async def outlet(
    interaction: Interaction,
    product_images: Attachment = SlashOption(description="Preview of the product", required=True),
    product_name: str = SlashOption(description="Name of the product", required=True),
    description: str = SlashOption(description="Description of the product", required=True),
    price_robux: str = SlashOption(description="Price in Robux", required=True),
    price_pounds: str = SlashOption(description="Price in Pounds", required=True),
    payhip_url: str = SlashOption(description="Payhip Store URL", required=True)
):
    try:
        # ✅ Role check
        allowed_role_ids = {1302761965277544448, 1108029461967945850}
        user_role_ids = {role.id for role in interaction.user.roles}
        if not allowed_role_ids.intersection(user_role_ids):
            await interaction.response.send_message(
                "You don't have permission to use this command.",
                ephemeral=True
            )
            return

        # ✅ Image URL
        image_url = product_images.url

        # ✅ Get forum channel
        outlet_channel = interaction.guild.get_channel(1500777337850167346)
        if not outlet_channel:
            await interaction.response.send_message(
                "Outlet channel not found.",
                ephemeral=True
            )
            return

        # 🧵 Create thread with ONLY preview image
        thread = await outlet_channel.create_thread(
            name=product_name,
            content=image_url,  # 👈 preview image as main post
            auto_archive_duration=1440
        )

        # 📦 Embed (inside thread)
        embed = nextcord.Embed(
            title=f"{product_name}",
            description=f"<:CD_Info:1310206627466711140> {description}",
            color=0xff913a
        )

        embed.add_field(
            name="Price",
            value=f"<:CD_robux:1310207300522213507> {price_robux}\n<:PayPal:1495154342695801073> {price_pounds}",
            inline=False
        )

        # Footer banner
        embed.set_image(
            url="https://media.discordapp.net/attachments/1307830607262384128/1500818157882052698/Footer_banner.png?ex=69f9d154&is=69f87fd4&hm=88ed0d5062d1e972647b5835692fefcca61ef43ef825fb3fa503b47cf69e42be&=&format=webp&quality=lossless&width=1859&height=129"
        )

        # 🔘 Buttons
        view = View()
        view.add_item(Button(
            label="Roblox Store",
            url="https://www.roblox.com/games/83015037950675/Comet-Designs-Outlet",
            style=ButtonStyle.gray
        ))
        view.add_item(Button(
            label="Payhip Store",
            url=payhip_url,
            style=ButtonStyle.gray
        ))

        # ✅ Send embed INSIDE thread
        await thread.send(
            content="\u200b",  # prevents empty message error
            embed=embed,
            view=view
        )

        # ✅ Confirmation
        await interaction.response.send_message(
            "✅ Outlet post created successfully!",
            ephemeral=True
        )

    except Exception as e:
        logging.error(f"Error in outlet command: {e}")
        await interaction.response.send_message(
            "❌ An error occurred while creating the outlet post.",
            ephemeral=True
        )
        
# =================================================
# =================================================

# List of random complement messages
random_complement_messages = [
    "Your contribution deserves a standing ovation—cue the applause!",
    "Big thanks—our gratitude level just hit overdrive!",
    "You’re a real one—your contribution just saved the day!",
    "Thanks for your contribution—future generations will tell tales of your greatness!",
    "You contributed, and now you’re officially on our list of awesome people.",
    "If contributions were currency, you’d be a millionaire in our hearts.",
    "You’re basically the MVP of the day. Congrats!",
    "We’d frame your contribution if we could—it’s that good.",
    "You did the thing, and we love you for it.",
    "Thanks for making a contribution AND making us smile!",
    "You’re not just contributing—you’re conquering!",
    "Thanks for keeping the good vibes (and contributions) rolling.",
    "Your contribution has been noted—and by ‘noted,’ we mean celebrated!",
    "We’re officially upgrading you to VIP contributor status—party hat optional.",
    "You’ve just earned infinite gratitude points—redeemable now and forever.",
    "Your contribution? Absolute legend status achieved.",
    "We appreciate your contribution more than coffee on a Monday!",
    "Thanks for being the MVP we didn’t know we needed.",
    "Your contribution = instant hero vibes.",
    "Big thanks for your contribution—it’s giving main character energy.",
    "We’d send you a trophy, but this message will have to do.",
    "Your contribution just made our day 110% better!",
    "Thanks a ton—your awesomeness quota is officially maxed out!"
]



# SUPPORTER SLASH COMMAND --------------------------------------------------------------------------------
@client.slash_command(guild_ids=[GUILD_ID], description="Acknowledge a supporter")
async def supporter(
    interaction: Interaction,
    option: str = SlashOption(description="Select an option", required=True, choices=["Donator", "Comet+"]),
    user: nextcord.Member = SlashOption(description="User to acknowledge", required=True),
    amount: float = SlashOption(description="Amount donated", required=False)
):
    allowed_role_ids = {1302761965277544448, 1108029461967945850, 1309883023008989265}
    user_role_ids = {role.id for role in interaction.user.roles}
    if not allowed_role_ids.intersection(user_role_ids):
        await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        return

    try:
        embed = nextcord.Embed(color=0xff913a)
        random_complement_message = random.choice(random_complement_messages)

        if option == "Donator":
            if amount is None:
                await interaction.response.send_message("Please provide the amount donated.", ephemeral=True)
                return

            embed.title = "You’re officially fancy now"
            embed.description = f"<:CD_partner:1310207556903501844> {user.mention} donated {amount} Robux, {random_complement_message}"
        elif option == "Comet+":
            embed.title = "Comet+? Nice choice!"
            embed.description = f"<:CD_partner:1310207556903501844> {user.mention} purchased <@&1309926380624150528>, {random_complement_message}"

        supporters_channel = client.get_channel(SUPPORTERS_ID)
        if supporters_channel:
            await supporters_channel.send(embed=embed)
            await interaction.response.send_message("Supporter acknowledged successfully!", ephemeral=True)
        else:
            await interaction.response.send_message("Supporters channel not found.", ephemeral=True)
    except Exception as e:
        logging.error(f"Error in supporter command: {e}")
        await interaction.response.send_message("An error occurred while acknowledging the supporter.", ephemeral=True)


# DEMOTION SLASH COMMAND --------------------------------------------------------------------------------
@client.slash_command(guild_ids=[GUILD_ID], description="Demote a user")
async def demotion(
    interaction: Interaction,
    username: nextcord.Member = SlashOption(description="User to demote", required=True),
    old_rank: nextcord.Role = SlashOption(description="Old rank", required=True),
    new_rank: nextcord.Role = SlashOption(description="New rank", required=True),
    reason: str = SlashOption(description="Reason", required=True),
    proof: str = SlashOption(description="Proof (image URL)", required=False, default=None)
):
    allowed_roles = {EXECUTIVE, DIRECTOR}
    if any(role.id in allowed_roles for role in interaction.user.roles):
        try:
            await username.add_roles(new_rank)
            await username.remove_roles(old_rank)

            embed = nextcord.Embed(
                title="DEMOTION",
                description=(
                    f"**<:CD_dot:1310207495691567145>Username:** {username.mention}\n"
                    f"**<:mid:1411651635058577519> Old Rank:** {old_rank.mention}\n"
                    f"**<:mid:1411651635058577519> New Rank:** {new_rank.mention}\n"
                    f"**<:bottom:1411651619057307779> Reason:** {reason}"
                ),
                color=0xff0808
            )
            embed.set_footer(text=f"Authorised by {interaction.user.display_name}", icon_url=interaction.user.avatar.url)
            embed.set_image(url="https://media.discordapp.net/attachments/1307830607262384128/1323349902935457965/Sin_titulo_72_x_9_in_72_x_5_in_1_1.png?ex=67743123&is=6772dfa3&hm=d8ee04b95368ed3c3172a30f26c2ceed5de2d43b034d523f095cc583a2695e5e&=&format=webp&quality=lossless&width=756&height=52")

            if proof:
                embed.set_image(url=proof)

            demotion_channel = client.get_channel(1309857105745936515)
            if demotion_channel:
                await demotion_channel.send(embed=embed)
                await interaction.response.send_message("Demotion has been successfully logged.", ephemeral=True)
            else:
                await interaction.response.send_message("Demotion channel not found.", ephemeral=True)

            await username.send(embed=embed)
        except Exception as e:
            logging.error(f"Error in demotion command: {e}")
            await interaction.response.send_message("An error occurred while logging the demotion.", ephemeral=True)
    else:
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)


# PROMOTION SLASH COMMAND --------------------------------------------------------------------------------
@client.slash_command(guild_ids=[GUILD_ID], description="Promote a user")
async def promotion(
    interaction: Interaction,
    username: nextcord.Member = SlashOption(description="User to Promote", required=True),
    new_rank: nextcord.Role = SlashOption(description="New rank", required=True),
    reason: str = SlashOption(description="Reason", required=True)
):
    allowed_role_ids = {1302761965277544448, 1108029461967945850}
    user_role_ids = {role.id for role in interaction.user.roles}
    if not allowed_role_ids.intersection(user_role_ids):
        await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        return

    try:
        await username.add_roles(new_rank)

        embed = nextcord.Embed(title="<:CD_Light:1310205970596499487> Promotion", color=0xff913a)
        embed.set_image(url="https://media.discordapp.net/attachments/1307830607262384128/1500818157882052698/Footer_banner.png?ex=69f9d154&is=69f87fd4&hm=88ed0d5062d1e972647b5835692fefcca61ef43ef825fb3fa503b47cf69e42be&=&format=webp&quality=lossless&width=1859&height=129")
        embed.add_field(name="<:CD_dot:1310207495691567145>Username", value=username.mention, inline=True)
        embed.add_field(name="<:CD_dot:1310207495691567145>New Rank", value=new_rank.mention, inline=True)
        embed.add_field(name="<:CD_dot:1310207495691567145>Reason", value=reason, inline=False)
        embed.set_footer(text=f"Authorised by {interaction.user.display_name}", icon_url=interaction.user.avatar.url)

        promotion_channel = client.get_channel(PROMOTION_ID)
        if promotion_channel:
            await promotion_channel.send(embed=embed)
            await interaction.response.send_message("Promotion has been successfully logged.", ephemeral=True)
        else:
            await interaction.response.send_message("Promotion channel not found.", ephemeral=True)

        await username.send(embed=embed)
    except Exception as e:
        logging.error(f"Error in promotion command: {e}")
        await interaction.response.send_message("An error occurred while logging the promotion.", ephemeral=True)

# ===========================
# STAFF MANAGEMENT ==============================================================
# =========================== ============================================

STAFF_DATABASE_FILE = 'staff_database.json'

# Ensure the staff database file exists
if not os.path.exists(STAFF_DATABASE_FILE):
    with open(STAFF_DATABASE_FILE, 'w') as file:
        json.dump([], file)


    
from datetime import datetime

# ADD STAFF SLASH COMMAND --------------------------------------------------------------------------------
@client.slash_command(guild_ids=[GUILD_ID], description="Add a new staff member")
async def add_staff(
    interaction: Interaction,
    user: nextcord.Member = SlashOption(description="User to add", required=True),
    category: str = SlashOption(description="Category", required=True, choices=["Creative Team", "Marketing Team", "Support Team","Management", "Board of Directors", "Executive Board"]),
    roblox_username: str = SlashOption(description="Roblox Username", required=True)
):
    allowed_roles = {1302761965277544448, 1108029461967945850, 1309883023008989265}
    if any(role.id in allowed_roles for role in interaction.user.roles):
        try:
            with open(STAFF_DATABASE_FILE, 'r+') as file:
                staff_database = json.load(file)
                if any(member["Username"] == str(user) for member in staff_database):
                    await interaction.response.send_message("This user already exists in the database.", ephemeral=True)
                    return

                date_of_joining = datetime.now().strftime("%d/%m/%Y")
                staff_member = {
                    "Username": str(user),
                    "Roblox Username": roblox_username,
                    "Category": category,
                    "Date of Joining": date_of_joining
                }
                staff_database.append(staff_member)
                file.seek(0)
                json.dump(staff_database, file, indent=4)

            embed = nextcord.Embed(title="Staff Member Added", color=0xff913a)
            embed.add_field(name="<:CD_member:1337489055889227876> Username", value=user.mention, inline=False)
            embed.add_field(name="<:CD_roblox:1310207355002159175> Roblox Username", value=roblox_username, inline=False)
            embed.add_field(name="<:CD_bag:1310235389126115349> Category", value=category, inline=False)
            embed.add_field(name="<:CD_dot:1310207495691567145>Date of Joining", value=date_of_joining, inline=False)
            embed.set_image(url="https://media.discordapp.net/attachments/1307830607262384128/1308444839905595392/Sin_titulo_50_x_8_in_4.png?ex=6791aef7&is=67905d77&hm=a7d9123dc9d275e26f2debd9543d04d01847210112577da4afedd3652f3c088c&=&format=webp&quality=lossless&width=1439&height=173")

            await interaction.response.send_message(embed=embed, ephemeral=False)
        except Exception as e:
            logging.error(f"Error in add_staff command: {e}")
            await interaction.response.send_message("An error occurred while adding the staff member.", ephemeral=True)
    else:
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)

# UPDATE STAFF SLASH COMMAND --------------------------------------------------------------------------------
@client.slash_command(guild_ids=[GUILD_ID], description="Update a staff member's information")
async def update_staff(
    interaction: Interaction,
    user: nextcord.Member = SlashOption(description="User to update", required=True),
    update_date_of_joining: str = SlashOption(description="New Date of Joining (DD/MM/YYYY)", required=False),
    update_category: str = SlashOption(description="New Category", required=False, choices=["Creative Team", "Marketing Team", "Support Team", "Management", "Board of Directors", "Executive Board"]),
    update_roblox_username: str = SlashOption(description="New Roblox Username", required=False)
):
    allowed_roles = {1302761965277544448, 1108029461967945850, 1309883023008989265}
    if any(role.id in allowed_roles for role in interaction.user.roles):
        try:
            with open(STAFF_DATABASE_FILE, 'r+') as file:
                staff_database = json.load(file)
                staff_member = next((member for member in staff_database if member["Username"] == str(user)), None)

                if not staff_member:
                    await interaction.response.send_message("Staff member not found.", ephemeral=True)
                    return

                if update_date_of_joining:
                    staff_member["Date of Joining"] = update_date_of_joining
                if update_category:
                    staff_member["Category"] = update_category
                if update_roblox_username:
                    staff_member["Roblox Username"] = update_roblox_username

                file.seek(0)
                file.truncate()
                json.dump(staff_database, file, indent=4)

            await interaction.response.send_message(f"Information updated for {user.mention}", ephemeral=True)
        except Exception as e:
            logging.error(f"Error in update_staff command: {e}")
            await interaction.response.send_message("An error occurred while updating the staff member.", ephemeral=True)
    else:
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)

# REMOVE STAFF SLASH COMMAND --------------------------------------------------------------------------------
@client.slash_command(guild_ids=[GUILD_ID], description="Remove a staff member")
async def remove_staff(
    interaction: Interaction,
    user: nextcord.Member = SlashOption(description="User to remove", required=True)
):
    allowed_roles = {1302761965277544448, 1108029461967945850, 1309883023008989265}
    if any(role.id in allowed_roles for role in interaction.user.roles):
        try:
            with open(STAFF_DATABASE_FILE, 'r+') as file:
                staff_database = json.load(file)
                staff_database = [member for member in staff_database if member["Username"] != str(user)]
                file.seek(0)
                file.truncate()
                json.dump(staff_database, file, indent=4)

            embed = nextcord.Embed(title="Staff Member Removed", color=0xff913a)
            embed.add_field(name="<:CD_member:1337489055889227876> Username", value=user.mention, inline=False)
            embed.set_image(url="https://media.discordapp.net/attachments/1307830607262384128/1308444839905595392/Sin_titulo_50_x_8_in_4.png?ex=6791aef7&is=67905d77&hm=a7d9123dc9d275e26f2debd9543d04d01847210112577da4afedd3652f3c088c&=&format=webp&quality=lossless&width=1439&height=173")

            await interaction.response.send_message(embed=embed, ephemeral=False)
        except Exception as e:
            logging.error(f"Error in remove_staff command: {e}")
            await interaction.response.send_message("An error occurred while removing the staff member.", ephemeral=False)
    else:
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
# ==========================================================================

import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("bot.log"),
                        logging.StreamHandler()
                    ])

# Function to check if a user is in the Roblox group
def check_group_status(roblox_username):
    group_id = 16394588  # Comet Designs group ID
    try:
        # Get the user ID from the username
        user_response = requests.post("https://users.roblox.com/v1/usernames/users", json={"usernames": [roblox_username]})
        user_data = user_response.json()
        logging.info(f"User data: {user_data}")
        if not user_data['data'] or 'id' not in user_data['data'][0]:
            return "Not present"

        user_id = user_data['data'][0]['id']

        # Check if the user is in the group
        group_response = requests.get(f"https://groups.roblox.com/v1/users/{user_id}/groups/roles")
        group_data = group_response.json()
        logging.info(f"Group data: {group_data}")
        for group in group_data['data']:
            if group['group']['id'] == group_id:
                return "Present"
        return "Not present"
    except Exception as e:
        logging.error(f"Error checking group status: {e}")
        return "Not present"

def fetch_group_roles(group_id):
    try:
        response = requests.get(f"https://groups.roblox.com/v1/groups/{group_id}/roles")
        response.raise_for_status()
        roles_data = response.json()
        roles = [role['name'] for role in roles_data['roles']]
        return roles
    except Exception as e:
        logging.error(f"Error fetching group roles: {e}")
        return []

# VIEW STAFF SLASH COMMAND --------------------------------------------------------------------------------
@client.slash_command(guild_ids=[GUILD_ID], description="View staff member information")
async def view_staff(
    interaction: Interaction,
    user: nextcord.Member = SlashOption(description="User to view", required=False)
):
    allowed_roles = [1302761965277544448, 1021894722647752784]
    if not any(role.id in allowed_roles for role in interaction.user.roles):
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return

    try:
        with open(STAFF_DATABASE_FILE, 'r') as file:
            staff_database = json.load(file)

        if user:
            staff_member = next((member for member in staff_database if member["Username"] == str(user)), None)
            if staff_member:
                group_status = check_group_status(staff_member["Roblox Username"])
                embed = nextcord.Embed(title="<:CD_info:1310234839982674014> Staff Member Information", color=0xff913a)
                embed.add_field(name="<:CD_member:1337489055889227876> Username", value=staff_member["Username"], inline=False)
                embed.add_field(name="<:CD_roblox:1310207355002159175> Roblox Username", value=staff_member["Roblox Username"], inline=False)
                embed.add_field(name="<:CD_bag:1310235389126115349> Category", value=staff_member["Category"], inline=False)
                embed.add_field(name="<:CD_dot:1310207495691567145>Date of Joining", value=staff_member["Date of Joining"], inline=False)
                embed.add_field(name="<:CD_dot:1310207495691567145>Group Status", value=group_status, inline=False)
                embed.set_image(url="https://media.discordapp.net/attachments/1307830607262384128/1308444839905595392/Sin_titulo_50_x_8_in_4.png")
                await interaction.response.send_message(embed=embed, ephemeral=False)
            else:
                await interaction.response.send_message("Staff member not found.", ephemeral=False)
        else:
            embed = nextcord.Embed(title="<:CD_info:1310234839982674014> List of Staff", color=0xff913a)
            for member in staff_database:
                group_status = check_group_status(member["Roblox Username"])
                embed.add_field(
                    name=f"<:CD_member:1337489055889227876> {member['Username']}",
                    value=(
                        f"<:CD_dot:1310207495691567145>Roblox Username: {member['Roblox Username']}\n"
                        f"<:CD_dot:1310207495691567145>Category: {member['Category']}\n"
                        f"<:CD_dot:1310207495691567145>Date of Joining: {member['Date of Joining']}\n"
                        f"<:CD_dot:1310207495691567145>Group Status: {group_status}"
                    ),
                    inline=False
                )
            embed.set_image(url="https://media.discordapp.net/attachments/1307830607262384128/1308444839905595392/Sin_titulo_50_x_8_in_4.png")
            await interaction.response.send_message(embed=embed, ephemeral=False)
    except Exception as e:
        logging.error(f"Error in view_staff command: {e}")
        await interaction.response.send_message("An error occurred while viewing the staff members.", ephemeral=False)

# Define the channel ID where rank requests will be sent
RANK_REQUEST_CHANNEL_ID = 1067736199453753394

# RANK REQUEST SLASH COMMAND --------------------------------------------------------------------------------
@client.slash_command(guild_ids=[GUILD_ID], description="Submit a rank request")
async def rank_request(
    interaction: Interaction,
    roblox_username: str = SlashOption(description="The Roblox username", required=True),
    rank_requesting: str = SlashOption(description="The rank you are requesting", required=True, choices=fetch_group_roles(16394588))
):
    allowed_roles = [1306395336163463170]
    if not any(role.id in allowed_roles for role in interaction.user.roles):
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return

    try:
        if not roblox_username or not rank_requesting:
            await interaction.response.send_message("Both Roblox Username and Rank Requesting are required.", ephemeral=True)
            return

        embed = nextcord.Embed(title="Rank Request Submitted", color=0xff913a)
        embed.add_field(name="<:CD_member:1337489055889227876> Discord User", value=f"{interaction.user} ({interaction.user.id})", inline=False)
        embed.add_field(name="<:CD_dot:1310207495691567145>Roblox Username", value=roblox_username, inline=False)
        embed.add_field(name="<:CD_dot:1310207495691567145>Rank Requesting", value=rank_requesting, inline=False)
        embed.set_image(url="https://media.discordapp.net/attachments/1307830607262384128/1308444839905595392/Sin_titulo_50_x_8_in_4.png")
        embed.set_footer(text=f"Requested at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        channel = client.get_channel(RANK_REQUEST_CHANNEL_ID)
        if channel:
            await channel.send(embed=embed)
            await interaction.response.send_message("Your rank request has been submitted.", ephemeral=True)
        else:
            await interaction.response.send_message("Failed to submit your rank request. Please try again later.", ephemeral=True)
    except Exception as e:
        logging.error(f"Error in rank_request command: {e}")
        await interaction.response.send_message("An error occurred while submitting your rank request.", ephemeral=True)



# TICKET SYSTEM USING TICKET TOOLS ==============================
# Command to send the embed message with dropdown menu
# Adding a slash command version of the TicketMenu with optional input to enable/disable select options
@client.slash_command(name="ticket_menu", guild_ids=[GUILD_ID], description="Send the ticket menu with dropdown options")
async def ticket_menu_slash(
    interaction: Interaction,
    disable: str = SlashOption(
        description="Enter options to disable (comma-separated)",
        required=False
    )
):
    TICKET_ADMIN
    TICKET_MGMT 
    TICKET_CHANNEL_ID  # Channel ID where the command must be sent

    if interaction.channel.id != TICKET_CHANNEL_ID:
        await interaction.response.send_message("This command can only be used in the specified channel.", ephemeral=True)
        return

    if any(role.id == TICKET_ADMIN or role.id == TICKET_MGMT for role in interaction.user.roles):
        # First embed with the specified image
        first_embed = nextcord.Embed(
            color=0xff913a
        )
        first_embed.set_image(url="https://media.discordapp.net/attachments/1307830607262384128/1500818125569003551/CONTACT_US.png?ex=69f9d14c&is=69f87fcc&hm=a721316a943d2fb2c6e27b528b449c809beed8b37f00f09c851f405eb2c705f4&=&format=webp&quality=lossless&width=1859&height=486")

        # Second embed with the ticket menu
        second_embed = nextcord.Embed(
            description="<:CD_info:1310234839982674014> Kindly select the category that best aligns with your request from the dropdown menu.\n\nAfter opening a ticket, follow the provided instructions to ensure a faster response.\n\n ```Note: Please choose the right category to get the faster and smoother response.```\n-# Please read our Order TOS and Pricing before opening a order ticket.",
            color=0xff913a
        )
        second_embed.add_field(name="<:CD_dot:1310207495691567145> Support", value="<:CD_BP_O:1376241176990187571> Questions\n<:CD_BP_O:1376241176990187571> Concerns", inline=True)
        second_embed.add_field(name="<:CD_dot:1310207495691567145> Order", value="<:CD_BP_O:1376241176990187571> Livery\n<:CD_BP_O:1376241176990187571> Clothing\n<:CD_BP_O:1376241176990187571> Graphics\n<:CD_BP_O:1376241176990187571> Discord Utilities\n<:CD_BP_O:1376241176990187571> Development Assets", inline=True)
        second_embed.add_field(name="<:CD_dot:1310207495691567145> Management", value="<:CD_BP_O:1376241176990187571> Reports & Appeals\n<:CD_BP_O:1376241176990187571> Collaboration\n<:CD_BP_O:1376241176990187571> Concerns", inline=True)
        second_embed.set_image(url="https://media.discordapp.net/attachments/1307830607262384128/1500818157882052698/Footer_banner.png?ex=69f9d154&is=69f87fd4&hm=88ed0d5062d1e972647b5835692fefcca61ef43ef825fb3fa503b47cf69e42be&=&format=webp&quality=lossless&width=1859&height=129")

        # Parse disabled options
        disable_list = [opt.strip().lower() for opt in disable.split(",")] if disable else []

        select = Select(
            placeholder="Please Select",
            options=[
                nextcord.SelectOption(label="Please Select", description="Make a selection", emoji="<:CD_dot:1310207495691567145>", default=True),
                nextcord.SelectOption(label="Support", description="Concern & Queries", emoji="<:CD_dot:1310207495691567145>", default=False),
                nextcord.SelectOption(label="Livery", description="Order", emoji="<:CD_dot:1310207495691567145>", default=False),
                nextcord.SelectOption(label="Clothing", description="Order", emoji="<:CD_dot:1310207495691567145>", default=False),
                nextcord.SelectOption(label="Graphics", description="Order", emoji="<:CD_dot:1310207495691567145>", default=False),
                nextcord.SelectOption(label="Discord Utilities", description="Order", emoji="<:CD_dot:1310207495691567145>", default=False),
                nextcord.SelectOption(label="Development Assets", description="Order", emoji="<:CD_dot:1310207495691567145>", default=False),
                nextcord.SelectOption(label="Collaboration", description="Management", emoji="<:CD_dot:1310207495691567145>", default=False),
                nextcord.SelectOption(label="Reports & Appeals", description="Management", emoji="<:CD_dot:1310207495691567145>", default=False),
                nextcord.SelectOption(label="Misc", description="For other inquiries", emoji="<:CD_dot:1310207495691567145>", default=False),
            ]
        )

        user_cooldowns = {}

        async def select_callback(interaction):
            user_id = interaction.user.id
            current_time = time.time()
            if user_id in user_cooldowns and user_cooldowns[user_id] > current_time:
                remaining_time = int(user_cooldowns[user_id] - current_time)
                minutes, seconds = divmod(remaining_time, 60)
                await interaction.response.send_message(f"<:CD_lock:1310208201521758321> You must wait {minutes} minutes and {seconds} seconds before selecting another option.", ephemeral=True)
                return

            if select.values[0].lower() in disable_list:
                await interaction.response.send_message("This category is closed. Please wait until further notice to open a ticket.", ephemeral=True)
                return

            if select.values[0] == "Support":
                channel_id = 1492606759741690100
                message = f"$new {interaction.user.id} Support"
            elif select.values[0] == "Livery":
                channel_id = 1492606631266095415
                message = f"$new {interaction.user.id} Livery"
            elif select.values[0] == "Clothing":
                channel_id = 1492606827144413277
                message = f"$new {interaction.user.id} Clothing"
            elif select.values[0] == "Graphics":
                channel_id = 1492606698156982354  # Replace with actual channel ID
                message = f"$new {interaction.user.id} Graphics"
            elif select.values[0] == "Discord Utilities":
                channel_id = 1492606733833605191 # Replace with actual channel ID
                message = f"$new {interaction.user.id} Discord Utilities"
            elif select.values[0] == "Development Assets":
                channel_id = 1492607006492721263  # Replace with actual channel ID
                message = f"$new {interaction.user.id} Development Assets"
            elif select.values[0] == "Collaboration":
                channel_id = 1492607897253839071  # Replace with actual channel ID
                message = f"$new {interaction.user.id} Collaboration"
            elif select.values[0] == "Reports & Appeals":
                channel_id = 1492607897253839071  # Replace with actual channel ID
                message = f"$new {interaction.user.id} Reports & Appeals"
            elif select.values[0] == "Misc":
                channel_id = 1492607897253839071  # Replace with actual channel ID
                message = f"$new {interaction.user.id} Misc"
            else:
                return

            target_channel = client.get_channel(channel_id)
            if target_channel:
                await target_channel.send(message)
                await interaction.response.send_message("Your request has been sent.", ephemeral=True)

                # Set cooldown for the user
                user_cooldowns[user_id] = current_time + 300  # 5 minutes cooldown
            else:
                await interaction.response.send_message("Target channel not found.", ephemeral=True)

        select.callback = select_callback
        view = View(timeout=None)
        view.add_item(select)

        channel = client.get_channel(TICKET_CHANNEL_ID)
        if channel:
            await channel.send(embed=first_embed)
            await channel.send(embed=second_embed, view=view)
            await interaction.response.send_message("Ticket menu sent.", ephemeral=True)
        else:
            await interaction.response.send_message("Channel not found.", ephemeral=True)
    else:
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)


## CUSTOM TICKET RESPONSE ALIASES -------------------------------------------------------------------------------

# Custom ticket response commands
from nextcord.ext import commands

# Helper function to create and send an embed
def create_embed(title, description, color):
    embed = nextcord.Embed(
        title=title,
        description=description,
        color=color
    )
    return embed

# Command: cancel
@client.command(name="cancel")
async def cancel(ctx):
    if not any(role.name == "Staff Team" for role in ctx.author.roles):
        await ctx.send("❌ You don't have permission to use this command.")
        return

    embed = create_embed(
        title="Order Cancelled",
        description="*As per your request, you have decided to cancel this order.*\n\n*Have a good rest of your day!*",
        color=0xff913a
    )
    await ctx.send(embed=embed)
    await ctx.message.delete()

# Command: disrespect
@client.command(name="disrespect")
async def disrespect(ctx):
    if not any(role.name == "Staff Team" for role in ctx.author.roles):
        await ctx.send("❌ You don't have permission to use this command.")
        return

    embed = create_embed(
        title="Disrespect Not Tolerated",
        description="We do not tolerate any disrespect within our tickets. You have now been blocked from using our ticketing system in the future.",
        color=0xff913a
    )
    await ctx.send(embed=embed)
    await ctx.message.delete()

# Command: inactive
@client.command(name="inactive")
async def inactive(ctx):
    if not any(role.name == "Staff Team" for role in ctx.author.roles):
        await ctx.send("❌ You don't have permission to use this command.")
        return

    embed = create_embed(
        title="Ticket Marked as Inactive",
        description="Your ticket has been deemed as INACTIVE\nPlease send your order or contact message through using the format or this ticket will be closed.",
        color=0xff913a
    )
    await ctx.send(embed=embed)
    await ctx.message.delete()

# Command: ooh
@client.command(name="ooh")
async def ooh(ctx):
    if not any(role.name == "Staff Team" for role in ctx.author.roles):
        await ctx.send("❌ You don't have permission to use this command.")
        return

    embed = create_embed(
        title="Out of Hours",
        description="Hello, thanks for your message. Currently we are out of hours, meaning most of our support and design staff is unavailable, please expect a response in 2-10 hours.",
        color=0xff913a
    )
    await ctx.send(embed=embed)
    await ctx.message.delete()

# Command: affiliationprocess
@client.command(name="affiliationprocess")
async def affiliationprocess(ctx):
    if not any(role.name == "Staff Team" for role in ctx.author.roles):
        await ctx.send("❌ You don't have permission to use this command.")
        return

    embed = create_embed(
        title="Affiliation Process",
        description=(
            "```Answer the questions asked below ```\n\n"
            "Here are some questions you need to answer to further proceed with the affiliation process, We at comet designs take affiliation seriously and we expect our affiliated partners to take it seriously as well.\n\n"
            "- Why do you want to get affiliated with Comet designs?\n"
            "- How will the affiliation benefit Comet Designs?\n"
            "- What do you expect in this affiliation?\n"
            "- How will this benefit both servers?\n\n"
            "```Standard Terms```\n"
            "- Must have a channel dedicated to Comet designs visible to the public at all times and permission to read/write given to Comet designs representatives.\n"
            "- Our TOS is always applied on any product created by Comet designs.\n"
            "- Comet designs can terminate affiliation and take away product rights whenever they want to.\n"
            "- Role called as comet designs must be created and given to the comet representatives with colour - #fa8d3a"
        ),
        color=0xff913a
    )
    await ctx.send(embed=embed)
    await ctx.message.delete()

# Command: comet+
@client.command(name="comet+")
async def comet_plus(ctx):
    if not any(role.name == "Staff Team" for role in ctx.author.roles):
        await ctx.send("❌ You don't have permission to use this command.")
        return

    embed = create_embed(
        title="Cometᐩ Membership",
        description=(
            "<:CD_dot:1310207495691567145> To purchase [Cometᐩ](https://www.roblox.com/catalog/105509757002899/comet), click the link and complete your payment.\n"
            "<:CD_dot:1310207495691567145> After payment, send us proof of purchase, and you'll receive your role!\n"
            "# <:CD_unlock:1310206715765198928> | Perks\n"
            "`› Cometᐩ`\n\n"
            "> `1` __Special__ <@&1309926380624150528> Role\n"
            "> `2` __Special__ entries for **giveaways**\n"
            "> `3` Access to **Exclusive chat** and** Exclusive releases**\n"
            "> `4` Media permission\n"
            "> `5` __Priority__ in orders"
        ),
        color=0xff913a
    )
    await ctx.send(embed=embed)
    await ctx.message.delete()

# Command: delay
@client.command(name="delay")
async def delay(ctx):
    if not any(role.name == "Staff Team" for role in ctx.author.roles):
        await ctx.send("❌ You don't have permission to use this command.")
        return

    embed = create_embed(
        title="Delay in Response",
        description="Hello, there is currently a delay in response times due to a high influx of tickets. Please be patient and expect a response soon.",
        color=0xff913a
    )
    await ctx.send(embed=embed)
    await ctx.message.delete()

# Command: group
@client.command(name="group")
async def group(ctx):
    if not any(role.name == "Staff Team" for role in ctx.author.roles):
        await ctx.send("❌ You don't have permission to use this command.")
        return

    embed = create_embed(
        title="Official Roblox Group",
        description="Find our Roblox group here - https://www.roblox.com/communities/16394588/Official-Comet-Designs#!/about",
        color=0xff913a
    )
    await ctx.send(embed=embed)
    await ctx.message.delete()

# Command: nodesigner
@client.command(name="nodesigner")
async def nodesigner(ctx):
    if not any(role.name == "Staff Team" for role in ctx.author.roles):
        await ctx.send("❌ You don't have permission to use this command.")
        return

    embed = create_embed(
        title="No Designer Available",
        description=(
            "*No designer Available*\n"
            "Hello!\n"
            "There is currently no designers available for this order. Please expect further delays."
        ),
        color=0xff913a
    )
    await ctx.send(embed=embed)
    await ctx.message.delete()

# Command: ad
@client.command(name="ad")
async def ad(ctx):
    embed = nextcord.Embed(
        title="**COMET DESIGNS AD**",
        description="```# **COMET DESIGNS**\n ***__Your Ideas, Launched Into Orbit__***\n\n``About us``\n- We are a design server specializing in creating ERLC roleplay server assets. Our passion is to bring creativity and functionality together for your roleplay experience. We have also introduced courses and are now actively hiring staff.\n\n``Services``\n- Liveries designs    |    Clothing designs\n- Graphics designs    |    Discord services\n\n``Explore more``\n- [Discord](https://discord.gg/cYVDd5b5rn)\n- [Roblox](https://www.roblox.com/communities/16394588/Official-Comet-Designs#!/about)\n\nhttps://media.discordapp.net/attachments/1142557690460131530/1331528197468192778/CD_Past_Work.png```",
        color=0xff913a
    )
    await ctx.send(embed=embed)

@client.command(name="claim")
async def delay(ctx):
    if not any(role.name == "Staff Team" for role in ctx.author.roles):
        await ctx.send("❌ You don't have permission to use this command.")
        return

    embed = create_embed(
        title="Ticket Claimed",
        description="Hello, this ticket now will be handled by {0}.".format(ctx.author.mention),
        color=0xff913a
    )
    await ctx.send(embed=embed)
    await ctx.message.delete()
    
# Command: payment
@client.command(name="payment")
async def payment(ctx):
    embed = nextcord.Embed(
        title="**PAYMENT METHODS**",
        description="In order to recieve the products you order,  you need to pay us first and provide us with a proof of payment. We accept payments through the following gamepasses. \n\n-# Please use the payment method stated by the designer and cross check the price with the agreed price in the ticket.",
        color=0xff913a
    )
    embed.add_field(name="<:CD_dot:1310207495691567145> Payment Method 1", value="https://www.roblox.com/catalog/12266194375/Payment-Method-1", inline=False)
    embed.add_field(name="<:CD_dot:1310207495691567145> Payment Method 2", value="https://www.roblox.com/catalog/12266191292/Payment-Method-2", inline=False)
    embed.add_field(name="<:CD_dot:1310207495691567145> Payment Method 3", value="https://www.roblox.com/catalog/12257512909/Payment-Method-3", inline=False)
    embed.add_field(name="<:CD_dot:1310207495691567145> Payment Method 4", value="https://www.roblox.com/catalog/18547346737/Payment-Method-4", inline=False)


    await ctx.send(embed=embed)

# CAREER FORUM APPLICATION =============================================================================
# ==================================================================================================================
#===================================================================================================================    

# ===== CONFIG =====
CAREER_CHANNEL_ID = 1309958393292918917
APPLICATION_CATEGORY = 1100160213333573743

ALLOWED_ROLES = ["DIRECTOR", "EXECUTIVE"]

# ===== CLOSE BUTTON VIEW =====
# ===== CLOSE BUTTON VIEW =====
class TicketCloseView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @nextcord.ui.button(label="Close", style=nextcord.ButtonStyle.gray)
    async def close_button(self, button: Button, interaction: Interaction):
        allowed_roles = [EXECUTIVE, DIRECTOR, MANAGEMENT]

        # Permission check
        if not any(role.id in allowed_roles for role in interaction.user.roles):
            await interaction.response.send_message(
                "You don't have permission to close this ticket.",
                ephemeral=True
            )
            return

        # 🔥 STEP 1: Respond immediately (prevents timeout)
        await interaction.response.defer(ephemeral=True)

        # Get ticket creator
        channel_name = interaction.channel.name
        username = channel_name.replace("_application", "")

        user = None
        for member in interaction.guild.members:
            if member.name.lower().replace(" ", "-") == username:
                user = member
                break

        # Try DM
        if user:
            try:
                await user.send(
                    f"Your application ticket **{interaction.channel.name}** has been closed by {interaction.user.mention}."
                )
            except:
                pass

        # 🔥 STEP 2: Send follow-up (NOT response)
        await interaction.followup.send("Closing ticket...", ephemeral=True)

        # Optional small delay (ensures message is sent before delete)
        await asyncio.sleep(1)

        await interaction.channel.delete()

# ===== MODAL =====
class CareerApplicationModal(Modal):
    def __init__(self):
        super().__init__("Career Application Form")

        self.discord_username = TextInput(
            label="Discord Username",
            placeholder="Enter your Discord username",
            required=True,
            max_length=100
        )

        self.roblox_username = TextInput(
            label="Roblox Username",
            placeholder="Enter your Roblox username",
            required=True
        )

        self.role_applying = TextInput(
            label="Role Applying For",
            placeholder="Enter role",
            required=True
        )

        self.experience = TextInput(
            label="Experience",
            placeholder="Describe your experience",
            style=nextcord.TextInputStyle.paragraph,
            required=True
        )


        self.portfolio = TextInput(
            label="Portfolio",
            placeholder="Link or description",
            required=False
        )

        self.add_item(self.discord_username)
        self.add_item(self.roblox_username)
        self.add_item(self.role_applying)
        self.add_item(self.experience)
        self.add_item(self.portfolio)

    async def callback(self, interaction: Interaction):
        guild = interaction.guild

        category = guild.get_channel(APPLICATION_CATEGORY)

        username_clean = interaction.user.name.replace(" ", "-").lower()
        channel_name = f"{username_clean}_application"

        overwrites = {
            guild.default_role: nextcord.PermissionOverwrite(view_channel=False),
            interaction.user: nextcord.PermissionOverwrite(view_channel=True, send_messages=True)
        }

        channel = await guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites
        )

        embed = nextcord.Embed(
            title="Application",
            color=0xff913a
        )

        embed.add_field(name="Discord Username", value=self.discord_username.value, inline=True)
        embed.add_field(name="Roblox Username", value=self.roblox_username.value, inline=True)
        embed.add_field(name="Role Applying For", value=self.role_applying.value, inline=True)
        embed.add_field(name="Experience", value=self.experience.value, inline=False)
        embed.add_field(name="Portfolio", value=self.portfolio.value or "N/A", inline=False)
        embed.set_image(url="https://media.discordapp.net/attachments/1307830607262384128/1500818157882052698/Footer_banner.png?ex=69f9d154&is=69f87fd4&hm=88ed0d5062d1e972647b5835692fefcca61ef43ef825fb3fa503b47cf69e42be&=&format=webp&quality=lossless&width=1859&height=129")
        embed.set_footer(text=f"Applicant ID: {interaction.user.id}")

        msg = await channel.send(
            f"{interaction.user.mention}",
            embed=embed,
            view=TicketCloseView()
        )

        await msg.pin()

        await interaction.response.send_message(
            f" Your application has been submitted: {channel.mention}",
            ephemeral=True
        )


# ===== BUTTON VIEW =====
class CareerView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @nextcord.ui.button(label="Submit your Application", style=nextcord.ButtonStyle.gray)
    async def apply_button(self, button: Button, interaction: Interaction):
        await interaction.response.send_modal(CareerApplicationModal())


# ===== SLASH COMMAND =====
@client.slash_command(name="career_form", guild_ids=[GUILD_ID], description="Send career application panel")
async def career_form(interaction: Interaction):
    EXECUTIVE
    DIRECTOR
    CAREER_CHANNEL_ID

    if not any(role.id == EXECUTIVE or role.id == DIRECTOR for role in interaction.user.roles):
        await interaction.response.send_message(
            "You don't have permission to use this command.",
            ephemeral=True
        )
        return

    channel = client.get_channel(CAREER_CHANNEL_ID)

    first_embed = nextcord.Embed(
        color=0xff913a
    )
    first_embed.set_image(url="https://media.discordapp.net/attachments/1307830607262384128/1500818073190662264/CAREER.png?ex=69f9d140&is=69f87fc0&hm=4015f5788eae27e01d2a76c28b20fb09edd3963d71a0dc9417637f44946f4077&=&format=webp&quality=lossless&width=1859&height=486")
    second_embed = nextcord.Embed(
        description="<:CD_info:1310234839982674014> If you are interested in joining our team, please click the button below to fill out the application form. We look forward to reviewing your application and potentially welcoming you to our team!\n\n ``` Career Options ```\n \n",
        color=0xff913a
    )
    
    second_embed.add_field(name="<:CD_dot:1310207495691567145> Director of Public Relations", value="Handles community relations, feedback, and resolves concerns.", inline=False)

    second_embed.add_field(name="<:CD_dot:1310207495691567145> Director of Human Resources", value="Manages staffing, resolves conflicts, and maintains work standards.", inline=False)

    second_embed.add_field(name="<:CD_dot:1310207495691567145> Marketing Affairs Manager", value="Focuses on marketing strategies and growth opportunities.", inline=False)

    second_embed.add_field(name="<:CD_dot:1310207495691567145> HR Manager", value="Handles recruitment, conflict resolution, and HR operations.", inline=False)

    second_embed.add_field(name="<:CD_dot:1310207495691567145> Operations Coordinator", value="Assigns staff to tickets and ensures smooth workflow.", inline=False)

    second_embed.add_field(name="<:CD_dot:1310207495691567145> Recruitment Officer", value="Finds and recruits talented individuals for the team.", inline=False)

    second_embed.add_field(name="<:CD_dot:1310207495691567145> Support Team", value="Responsible for addressing questions and concerns raised by community members, handling support tickets, and providing assistance with orders.", inline=False)

    second_embed.add_field(name="<:CD_dot:1310207495691567145> Creative Team", value="This team consists of designers & developers who are responsible for handling orders and creating assets for Comet Designs.", inline=False) 
    second_embed.add_field(
    name="Categories for Creative Team",
    value="<:CD_BP_O:1376241176990187571> Clothing Designer\n<:CD_BP_O:1376241176990187571> Livery Designer\n<:CD_BP_O:1376241176990187571> Logo Designer\n<:CD_BP_O:1376241176990187571> Banner Designer\n<:CD_BP_O:1376241176990187571> GFX Designer\n<:CD_BP_O:1376241176990187571> 3D Modeller\n<:CD_BP_O:1376241176990187571> Discord Bot Developer\n<:CD_BP_O:1376241176990187571> Discord Webhook & Layout Developer",
    inline=False)
    second_embed.set_image(url="https://media.discordapp.net/attachments/1307830607262384128/1500818157882052698/Footer_banner.png?ex=69f9d154&is=69f87fd4&hm=88ed0d5062d1e972647b5835692fefcca61ef43ef825fb3fa503b47cf69e42be&=&format=webp&quality=lossless&width=1859&height=129")
    await channel.send(embed=first_embed)
    await channel.send(embed=second_embed, view=CareerView())

    await interaction.response.send_message(
        " Career form panel sent successfully.",
        ephemeral=True
    )

# ======================================================================================================

#========================================================================================================
# COURSE FIRST TIME LOGGING =============================================================================
# ==================================================================================================================

# Allowed roles (ONLY these can use command)
ALLOWED_ROLE_IDS = [1302761965277544448, 1108029461967945850]

# Channel IDs
COURSE_CHANNELS = {
    "Clothing Course": 1224486046520180767,
    "Livery Course": 1224486122348875826,
    "Graphics Course": 1224486193174020196
}

# Role pings
PING_ROLES = "<@&1302761965277544448> <@&1108029461967945850>"

# Course roles (for message)
COURSE_ROLES = {
    "Clothing Course": "<@&1495098809674502285>",
    "Graphics Course": "<@&1495098819837427883>",
    "Livery Course": "<@&1495098815244406794>"
}

IMAGE_URL = "https://media.discordapp.net/attachments/1307830607262384128/1315313835174920192/Sin_titulo_72_x_9_in_72_x_5_in_1_1.png"

# --------------------------------------- #



ALLOWED_ROLE_IDS = [1302761965277544448, 1108029461967945850]

COURSE_CHANNELS = {
    "Clothing Course": 1224486046520180767,
    "Livery Course": 1224486122348875826,
    "Graphics Course": 1224486193174020196
}

PING_ROLES = "<@&1302761965277544448> <@&1108029461967945850>"

COURSE_ROLES = {
    "Clothing Course": "<@&1495098809674502285>",
    "Graphics Course": "<@&1495098819837427883>",
    "Livery Course": "<@&1495098815244406794>"
}

IMAGE_URL = "https://media.discordapp.net/attachments/1307830607262384128/1315313835174920192/Sin_titulo_72_x_9_in_72_x_5_in_1_1.png"

# --------------------------------------- #



@client.slash_command(
    name="course_first_time",
    description="Log a first time course purchase",
    guild_ids=[GUILD_ID]
)
async def course_first_time(
    interaction: Interaction,
    discord_username: nextcord.Member = SlashOption(description="Discord Username"),
    roblox_username: str = SlashOption(description="Roblox Username"),
    email: str = SlashOption(description="Email ID"),
    course_type: str = SlashOption(
        description="Select Course Type",
        choices=["Clothing Course", "Livery Course", "Graphics Course"]
    )
):

    # ---------------- ROLE CHECK ---------------- #
    if interaction.guild is None:
        await interaction.response.send_message(
            "This command can only be used in a server.",
            ephemeral=True
        )
        return

    member = interaction.guild.get_member(interaction.user.id)

    if member is None:
        await interaction.response.send_message(
            "Could not verify your roles.",
            ephemeral=True
        )
        return

    user_roles = [role.id for role in member.roles]

    if not any(role_id in user_roles for role_id in ALLOWED_ROLE_IDS):
        await interaction.response.send_message(
            "You are not authorized to use this command.",
            ephemeral=True
        )
        return
    # ------------------------------------------------ #

    # Dates
    date_of_logging = datetime.now()
    expiry_date = date_of_logging + timedelta(days=30)

    logging_str = date_of_logging.strftime("%d %b %Y")
    expiry_str = expiry_date.strftime("%d %b %Y")

    # Embed
    embed = nextcord.Embed(
        title="First Time Purchase",
        color=0xff913a
    )

    # ✅ FIX: convert Member → string properly
    embed.add_field(
        name="Discord Username",
        value=f"{discord_username} ({discord_username.id})",
        inline=False
    )

    embed.add_field(name="Roblox Username", value=str(roblox_username), inline=False)
    embed.add_field(name="Email ID", value=str(email), inline=False)
    embed.add_field(name="Date of Logging", value=logging_str, inline=True)
    embed.add_field(name="Expiry Date", value=expiry_str, inline=True)
    embed.add_field(name="Course Type", value=course_type, inline=False)

    embed.set_image(url=IMAGE_URL)
    embed.set_footer(
        text=f"Logged by {interaction.user}",
        icon_url=interaction.user.display_avatar.url
    )

    # Send to correct channel
    channel_id = COURSE_CHANNELS[course_type]

    try:
        channel = client.get_channel(channel_id) or await client.fetch_channel(channel_id)

        await channel.send(
            content=PING_ROLES,
            embed=embed
        )

    except Exception as e:
        print(f"[ERROR] Error sending message: {e}")  # ✅ FIX (no emoji)

    # Ephemeral message
    await interaction.response.send_message(
        f"Logged successfully!\n\n"
        f"Please now use `/role temp` using Auto Role Bot to grant access for 30 days Also update the [Site Access Sheet](https://docs.google.com/spreadsheets/d/1Xwxzmbguzx33u__vUnniEuAqyOMm_-_zyhl9dOAoodk/edit?usp=sharing).\n\n"
        f"{COURSE_ROLES[course_type]}",
        ephemeral=True
    )


#========================================================================================================
# COURSE RENEWAL LOGGING =============================================================================
# ==================================================================================================================



COURSE_CHANNELSR = {
    "Clothing Course renewal": 1495097450359427252,
    "Livery Course renewal": 1495097614155382936,
    "Graphics Course renewal": 1224486303672827914
}

COURSE_ROLESR = {
    "Clothing Course renewal": "<@&1495098809674502285>",
    "Graphics Course renewal": "<@&1495098819837427883>",
    "Livery Course renewal": "<@&1495098815244406794>"
}
PING_ROLES = "<@&1302761965277544448> <@&1108029461967945850>"


IMAGE_URLR = "https://media.discordapp.net/attachments/1307830607262384128/1315313835174920192/Sin_titulo_72_x_9_in_72_x_5_in_1_1.png"

@client.slash_command(
    name="course_renewal_log",
    description="Log a course renewal",
    guild_ids=[GUILD_ID]
)
async def course_renewal_log(
    interaction: Interaction,
    discord_username: nextcord.Member = SlashOption(description="Discord Username"),
    roblox_username: str = SlashOption(description="Roblox Username"),
    email: str = SlashOption(description="Email ID"),
    course_type: str = SlashOption(
        description="Select Course Type",
        choices=["Clothing Course renewal", "Livery Course renewal", "Graphics Course renewal"]
    )
):

    # ---------------- ROLE CHECK ---------------- #
    if interaction.guild is None:
        await interaction.response.send_message(
            "This command can only be used in a server.",
            ephemeral=True
        )
        return

    member = interaction.guild.get_member(interaction.user.id)

    if member is None:
        await interaction.response.send_message(
            "Could not verify your roles.",
            ephemeral=True
        )
        return

    user_roles = [role.id for role in member.roles]

    if not any(role_id in user_roles for role_id in ALLOWED_ROLE_IDS):
        await interaction.response.send_message(
            "You are not authorized to use this command.",
            ephemeral=True
        )
        return
    # ------------------------------------------------ #

    # Dates
    date_of_logging = datetime.now()
    expiry_date = date_of_logging + timedelta(days=30)

    logging_str = date_of_logging.strftime("%d %b %Y")
    expiry_str = expiry_date.strftime("%d %b %Y")

    # Embed
    embed = nextcord.Embed(
        title="Course Renewal Log",
        color=0xff913a
    )

    # ✅ FIX: convert Member → string properly
    embed.add_field(
        name="Discord Username",
        value=f"{discord_username} ({discord_username.id})",
        inline=False
    )

    embed.add_field(name="Roblox Username", value=str(roblox_username), inline=False)
    embed.add_field(name="Email ID", value=str(email), inline=False)
    embed.add_field(name="Date of Logging", value=logging_str, inline=True)
    embed.add_field(name="Expiry Date", value=expiry_str, inline=True)
    embed.add_field(name="Course Type", value=course_type, inline=False)

    embed.set_image(url=IMAGE_URL)
    embed.set_footer(
        text=f"Logged by {interaction.user}",
        icon_url=interaction.user.display_avatar.url
    )

    # Send to correct channel
    channel_id = COURSE_CHANNELSR[course_type]

    try:
        channel = client.get_channel(channel_id) or await client.fetch_channel(channel_id)

        await channel.send(
            content=PING_ROLES,
            embed=embed
        )

    except Exception as e:
        print(f"[ERROR] Error sending message: {e}")  # ✅ FIX (no emoji)

    # Ephemeral message
    await interaction.response.send_message(
        f"Logged successfully!\n\n"
        f"Please now use `/role temp` using Auto Role Bot to grant access for 30 days Also update the [Site Access Sheet](https://docs.google.com/spreadsheets/d/1Xwxzmbguzx33u__vUnniEuAqyOMm_-_zyhl9dOAoodk/edit?usp=sharing).\n\n"
        f"{COURSE_ROLESR[course_type]}",
        ephemeral=True
    )

# PORTFOLIO THREAD CREATION =============================================================================
# ==================================================================================================================


@client.slash_command(guild_ids=[GUILD_ID], description="Create a designer portfolio thread")
async def portfolio(
    interaction: Interaction,
    designer: Member = SlashOption(description="Select the designer", required=True)
):
    try:
        # ✅ Role check
        allowed_roles = {EXECUTIVE, DIRECTOR, MANAGEMENT}
        user_roles = {role.id for role in interaction.user.roles}

        if not allowed_roles.intersection(user_roles):
            await interaction.response.send_message(
                "❌ You don't have permission to use this command.",
                ephemeral=True
            )
            return

        # ✅ Portfolio forum channel
        portfolio_channel = interaction.guild.get_channel(1309908543545151518)
        if not portfolio_channel:
            await interaction.response.send_message(
                "Portfolio channel not found.",
                ephemeral=True
            )
            return

        # 🖼️ Portfolio preview image
        preview_image = "https://media.discordapp.net/attachments/1307830607262384128/1500837849224970312/PORTFOLIO.png?ex=69f9e3ab&is=69f8922b&hm=9bfb573ecbe3b97c1ab12683ac9239098f1db1f8f96cd76705509ec012835ef8&=&format=webp&quality=lossless&width=1423&height=800"

        # 🧵 Create thread with image
        thread = await portfolio_channel.create_thread(
            name=f"{designer.name} Portfolio",
            content=preview_image,
            auto_archive_duration=1440
        )

        # 👤 Ping designer inside thread
        await thread.send(designer.mention)

        # ✅ Confirmation
        await interaction.response.send_message(
            f"✅ Portfolio created for {designer.mention}!",
            ephemeral=True
        )

    except Exception as e:
        logging.error(f"Error in portfolio command: {e}")
        await interaction.response.send_message(
            "❌ An error occurred while creating the portfolio.",
            ephemeral=True
        )

    


# Run the bot
client.run(token)
