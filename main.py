import os

token = os.environ.get("TOKEN")

import nextcord
from nextcord.ext import commands
from nextcord import Interaction, SlashOption, Attachment, ButtonStyle
from nextcord.utils import get
import json
import nextcord
from nextcord.ext import commands
import logging
import requests
from nextcord.ui import Button, View, Modal, TextInput
import requests
from nextcord.utils import get
from apis import *
import random
from datetime import datetime

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

@client.event
async def on_ready():
    logging.info('Bot is ready.')
    logging.info('----------------------')

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
        embed.set_image(url="https://media.discordapp.net/attachments/1110779991626629252/1312520876239097876/Sin_titulo_72_x_9_in_72_x_5_in_1_1.png?ex=674ccbd2&is=674b7a52&hm=f6228f89e71982bdbcd236455249a0f0fba8796855434204803f0d108e8c7157&=&format=webp&quality=lossless&width=1439&height=100")
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
        embed.set_image(url="https://media.discordapp.net/attachments/1110779991626629252/1312520876239097876/Sin_titulo_72_x_9_in_72_x_5_in_1_1.png?ex=674ccbd2&is=674b7a52&hm=f6228f89e71982bdbcd236455249a0f0fba8796855434204803f0d108e8c7157&=&format=webp&quality=lossless&width=1439&height=100")
        embed.add_field(name="<:CD_Discord:1310206398717755532> Designer", value=designer.mention, inline=False)
        embed.add_field(name="<:CD_robux:1310207300522213507> Original Price", value=f"${original_price:.2f}", inline=True)
        embed.add_field(name="<:CD_robux:1310207300522213507> Total Price", value=f"${total_price:.2f}", inline=True)
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
        embed.set_image(url="https://media.discordapp.net/attachments/1110779991626629252/1312520876239097876/Sin_titulo_72_x_9_in_72_x_5_in_1_1.png?ex=674ccbd2&is=674b7a52&hm=f6228f89e71982bdbcd236455249a0f0fba8796855434204803f0d108e8c7157&=&format=webp&quality=lossless&width=1439&height=100")
        embed.add_field(name="<:CD_Discord:1310206398717755532> Support Staff", value=support_staff.mention, inline=False)
        embed.add_field(name="<:CD_time:1310206753379450910> Date of Opening", value=date_of_opening, inline=True)
        embed.add_field(name="<:CD_time:1310206753379450910> Date of Closing", value=date_of_closing, inline=True)
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
    thread: nextcord.Thread = SlashOption(description="Thread to send the message", required=True),
    product_images: str = SlashOption(description="Comma-separated URLs of the product images", required=True),
    type_of_product: str = SlashOption(description="Type of product", required=True),
    product_name: str = SlashOption(description="Name of the product", required=True),
    description: str = SlashOption(description="Description of the product", required=True),
    price: str = SlashOption(description="Price of the product", required=True),
    enable_button1: bool = SlashOption(description="Enable Purchasing Hub button", required=True, choices=[True, False]),
    enable_button2: bool = SlashOption(description="Enable Packables button", required=True, choices=[True, False]),
    enable_button3: bool = SlashOption(description="Enable Website button", required=True, choices=[True, False])
):
    try:
        # Role ID check
        allowed_role_ids = {1302761965277544448, 1108029461967945850}
        user_role_ids = {role.id for role in interaction.user.roles}
        if not allowed_role_ids.intersection(user_role_ids):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
            return

        # Parse image URLs
        image_urls = [url.strip() for url in product_images.split(',')]

        # Embed for each image
        embeds = [nextcord.Embed(color=0xff913a).set_image(url=url) for url in image_urls]

        # Add final embed with product info
        embed_details = nextcord.Embed(
            title=f"<:CD_cart:1310206827946049546> {product_name}",
            description=f"<:CD_Info:1310206627466711140> {description}",
            color=0xff913a
        )
        embed_details.set_image(url="https://media.discordapp.net/attachments/1110779991626629252/1312520876239097876/Sin_titulo_72_x_9_in_72_x_5_in_1_1.png?ex=674ccbd2&is=674b7a52&hm=f6228f89e71982bdbcd236455249a0f0fba8796855434204803f0d108e8c7157&=&format=webp&quality=lossless&width=1439&height=100")
        embed_details.add_field(name="Price", value=f"<:CD_robux:1310207300522213507> {price}", inline=False)
        embed_details.set_footer(text=f"{type_of_product}")
        embeds.append(embed_details)

        # Create button view
        view = View()
        view.add_item(Button(label="Purchasing Hub", url="https://www.roblox.com/games/83015037950675/Comet-Designs-Purchasing-Hub", disabled=not enable_button1))
        view.add_item(Button(label="Packables", url="https://packables.store/652a9f90c7a0a2091d0a906e", disabled=not enable_button2))
        view.add_item(Button(label="Website", url="https://cometdesigns.co.uk/collection/home-page", disabled=not enable_button3))

        # Post to thread
        await thread.send(embeds=embeds, view=view)
        await interaction.response.send_message("✅ Outlet post created successfully!", ephemeral=True)

    except Exception as e:
        logging.error(f"Error in outlet command: {e}")
        await interaction.response.send_message("❌ An error occurred while creating the outlet post.", ephemeral=True)


# TAX CALCULATOR SLASH COMMAND --------------------------------------------------------------------------------
@client.slash_command(guild_ids=[GUILD_ID], description="Calculate the total amount including tax")
async def tax(
    interaction: Interaction,
    robux: float = SlashOption(description="Enter the amount of Robux", required=True)
):
    try:
        # Calculate the total amount including tax
        total_amount = robux * 1.43

        # Create embed message
        embed = nextcord.Embed(title="<:CD_settings:1310207018161934376> Tax Calculator", color=0xff913a)
        embed.set_image(url="https://media.discordapp.net/attachments/1307830607262384128/1315313835174920192/Sin_titulo_72_x_9_in_72_x_5_in_1_1.png?ex=6756f4f7&is=6755a377&hm=97fd75f4b6aab203e05b203c1f5b49df8707a8ac939b6e4f05222898384873f3&=&format=webp&quality=lossless&width=1439&height=100")
        embed.add_field(name="<:CD_robux:1310207300522213507> Robux", value=f"{robux} Robux", inline=False)
        embed.add_field(name="<:CD_robux:1310207300522213507> Total Amount (including 43% tax)", value=f"{total_amount:.2f} Robux", inline=False)

        # Send hidden embed message
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        logging.error(f"Error in tax command: {e}")
        await interaction.response.send_message("An error occurred while calculating the tax.", ephemeral=True)

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
        embed.set_image(url="https://media.discordapp.net/attachments/1110779991626629252/1312520876239097876/Sin_titulo_72_x_9_in_72_x_5_in_1_1.png?ex=674ccbd2&is=674b7a52&hm=f6228f89e71982bdbcd236455249a0f0fba8796855434204803f0d108e8c7157&=&format=webp&quality=lossless&width=1439&height=100")
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
        
client.run(token)
