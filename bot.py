import os
import discord
import config
from dotenv import load_dotenv
from rank_logic import get_days_since_joined, get_qualified_rank

DRY_RUN = False

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN is missing from .env")


intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    now = discord.utils.utcnow()

    print(f"Logged in as {client.user}")

    guild = client.get_guild(config.GUILD_ID)

    if guild is None:
        print("Could not find guild. Check GUILD_ID and make sure the bot is in the server.")
        await client.close()
        return

    print(f"Connected to server: {guild.name}")

    # Build quick lookup tables once.
    # This avoids repeatedly searching through guild.roles like a caveman.
    role_by_id = {
        role.id: role
        for role in guild.roles
    }

    rank_role_ids = {
        rank.role_id
        for rank in config.RANKS
    }

    managed_role_ids = rank_role_ids | {config.PRIVATE_ROLE_ID}

    promotions_channel = guild.get_channel(config.PROMOTIONS_CHANNEL_ID)

    if promotions_channel is None:
        print("Warning: promotions channel not found. Check PROMOTIONS_CHANNEL_ID.")

    print()
    print("Member rank preview:")
    print("--------------------")
    
    if not DRY_RUN:
        print("LIVE MODE ENABLED: applying role changes")
    else:
        print("DRY RUN: no role changes applied")

    member_count = 0
    skipped_bots = 0
    skipped_exempt = 0
    planned_changes = 0

    async for member in guild.fetch_members(limit=None):
        member_count += 1

        if member.bot:
            skipped_bots += 1
            continue

        if any(role.id in config.EXEMPT_ROLE_IDS for role in member.roles):
            skipped_exempt += 1
            continue

        days = get_days_since_joined(member, now)
        desired_rank = get_qualified_rank(days, config.RANKS)

        current_managed_roles = [
            role
            for role in member.roles
            if role.id in managed_role_ids
        ]

        current_managed_role_ids = {
            role.id
            for role in current_managed_roles
        }

        if desired_rank is None:
            desired_role = role_by_id[config.PRIVATE_ROLE_ID]
        else:
            desired_role = role_by_id[desired_rank.role_id]

        role_ids_to_keep = {desired_role.id}

        roles_to_remove = [
            role
            for role in current_managed_roles
            if role.id not in role_ids_to_keep
        ]

        if desired_role.id in current_managed_role_ids:
            roles_to_add = []
        else:
            roles_to_add = [desired_role]
        

        rank_name = desired_rank.name if desired_rank else "Private / no promotion yet"

        if roles_to_add or roles_to_remove:
            planned_changes += 1

            print(f"{member.display_name}: {days} days -> {rank_name}")

            if roles_to_remove:
                print("  Remove:")
                for role in roles_to_remove:
                    print(f"    - {role.name}")

            if roles_to_add:
                print("  Add:")
                for role in roles_to_add:
                    print(f"    + {role.name}")

            if not DRY_RUN:
                if roles_to_remove:
                    await member.remove_roles(*roles_to_remove, reason="Timed rank update")
                
                if roles_to_add:
                    await member.add_roles(*roles_to_add, reason="Timed rank update")
                
                 # Only congratulate actual rank promotions, not "you stayed Private" cleanup.
                if (
                    config.ANNOUNCE_PROMOTIONS
                    and promotions_channel is not None
                    and desired_rank is not None
                    and desired_role in roles_to_add
                ):
        
                    await promotions_channel.send(
                        f"🎖️ Attention, citizens. {member.mention} has been promoted to "
                        f"**{desired_rank.name}**. Super Earth acknowledges this acceptable display of loyalty."
        )

    print()
    print(f"Fetched members: {member_count}")
    print(f"Skipped bots: {skipped_bots}")
    print(f"Skipped exempt members: {skipped_exempt}")
    print(f"Members with planned changes: {planned_changes}")
    print(f"Dry run: {DRY_RUN}")

    await client.close()


client.run(TOKEN)