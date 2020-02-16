from classic_tetris_project import discord
from classic_tetris_project.env import env

@discord.client.event
async def on_ready():
    import csv
    from tqdm import tqdm

    from classic_tetris_project import discord
    from classic_tetris_project.countries import countries
    from classic_tetris_project.models import User

    with open('pbs.csv', 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['twitch_id', 'twitch_username',
                                                     'discord_id', 'discord_username',
                                                     'ntsc_pb', 'ntsc_pb_updated_at',
                                                     'pal_pb', 'pal_pb_updated_at',
                                                     'country_code', 'country'])
        writer.writeheader()
        for user in tqdm(User.objects.all()):
            if user.ntsc_pb or user.pal_pb:
                d = {
                    'ntsc_pb': user.ntsc_pb,
                    'ntsc_pb_updated_at': (user.ntsc_pb_updated_at.isoformat()
                                           if user.ntsc_pb_updated_at else None),
                    'pal_pb': user.pal_pb,
                    'pal_pb_updated_at': (user.pal_pb_updated_at.isoformat()
                                          if user.pal_pb_updated_at else None),
                    'country_code': user.country,
                    'country': (countries[user.country] if user.country else None),
                }
                if hasattr(user, 'twitch_user'):
                    d['twitch_id'] = user.twitch_user.twitch_id
                    d['twitch_username'] = user.twitch_user.username
                if hasattr(user, 'discord_user'):
                    d['discord_id'] = user.discord_user.discord_id
                    if user.discord_user.user_obj:
                        d['discord_username'] = user.discord_user.username
                writer.writerow(d)
    await discord.client.logout()

discord.client.run(env("DISCORD_TOKEN"))
