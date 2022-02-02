import re
from celery import shared_task
from disco.types.message import MessageEmbed
from django.template.loader import render_to_string

from . import discord_disco as discord
from .env import env


QUALIFIER_COLOR_APPROVED = 0x07D12F
QUALIFIER_COLOR_REJECTED = 0xE60000


@shared_task
def announce_qualifier(qualifier_id):
    from .models import Qualifier
    qualifier = Qualifier.objects.get(id=qualifier_id)
    event = qualifier.event
    discord_user = qualifier.user.discord_user
    twitch_user = qualifier.user.twitch_user

    # Send message to channel
    channel_id = env("DISCORD_QUALIFIER_REPORTING_CHANNEL_ID")
    if channel_id:
        message = "{discord_user} is about to qualify for {event}! Go watch live on {twitch_url}".format(
            discord_user=discord_user.user_tag,
            event=event.name,
            twitch_url=twitch_user.twitch_url,
        )
        discord.send_channel_message(channel_id, message)


@shared_task
def report_submitted_qualifier(qualifier_id):
    from .models import Qualifier
    qualifier = Qualifier.objects.get(id=qualifier_id)
    event = qualifier.event
    discord_user = qualifier.user.discord_user

    # Send message to channel
    channel_id = env("DISCORD_QUALIFIER_REPORTING_CHANNEL_ID")
    if channel_id:
        channel_embed = MessageEmbed()
        channel_embed.description = render_to_string("discord/qualifier_submitted.txt", {
            "event_name": event.name,
            "event_url": event.get_absolute_url(True),
            "qualifier": qualifier,
        }).replace("\\\n", "").strip()
        channel_embed.color = QUALIFIER_COLOR_APPROVED
        discord.send_channel_message(channel_id, embed=channel_embed)


@shared_task
def report_reviewed_qualifier(qualifier_id):
    from .models import Qualifier
    qualifier = Qualifier.objects.get(id=qualifier_id)
    event = qualifier.event
    discord_user = qualifier.user.discord_user

    # Send message to user
    user_embed = MessageEmbed()
    user_embed.description = render_to_string("discord/qualifier_reviewed.txt", {
        "event_name": event.name,
        "event_url": event.get_absolute_url(True),
        "qualifier": qualifier,
        "checks": ([(description, qualifier.review_data["checks"][check])
                    for check, description in Qualifier.REVIEWER_CHECKS
                    if check in qualifier.review_data["checks"]]
                   if qualifier.review_data["checks"] else None),
    }).replace("\\\n", "").strip()
    user_embed.color = (QUALIFIER_COLOR_APPROVED if qualifier.approved else QUALIFIER_COLOR_REJECTED)
    discord.send_direct_message(discord_user.discord_id, embed=user_embed)

@shared_task
def update_tournament_bracket(tournament_id):
    from .models import Tournament
    tournament = Tournament.objects.get(id=tournament_id)
    tournament.update_bracket()

@shared_task
def announce_scheduled_tournament_match(tournament_match_id):
    from .models import TournamentMatch
    from .facades.tournament_match_display import TournamentMatchDisplay
    tournament_match = TournamentMatch.objects.get(id=tournament_match_id)
    match = tournament_match.match
    match_display = TournamentMatchDisplay(tournament_match)
    tournament = tournament_match.tournament
    user1 = tournament_match.player1.user if tournament_match.player1 else None
    user2 = tournament_match.player2.user if tournament_match.player2 else None

    channel_id = env("DISCORD_TOURNAMENT_REPORTING_CHANNEL_ID")
    if channel_id:
        embed = MessageEmbed()
        embed.title = "{} Match {} Scheduled".format(
            tournament.discord_emote_string or tournament.short_name,
            tournament_match.match_number
        )
        embed.url = tournament_match.get_absolute_url(True)
        embed.color = tournament.color_int()
        embed.description = "{} vs {}".format(
            (user1.discord_user.user_tag
             if user1 and hasattr(user1, "discord_user")
             else match_display.player1_display_name()),
            (user2.discord_user.user_tag
             if user2 and hasattr(user2, "discord_user")
             else match_display.player2_display_name()),
        )
        embed.add_field(name="Tournament",
                        value="[{}]({})".format(tournament.name, tournament.get_absolute_url(True)),
                        inline=False)
        embed.add_field(name="Player 1",
                        value=("[{}]({}) ({})".format(user1.display_name,
                                                      user1.get_absolute_url(True),
                                                      tournament_match.player1.seed)
                               if user1 else match_display.player1_display_name()),
                        inline=True)
        embed.add_field(name="Player 2",
                        value=("[{}]({}) ({})".format(user2.display_name,
                                                      user2.get_absolute_url(True),
                                                      tournament_match.player2.seed)
                               if user2 else match_display.player2_display_name()),
                        inline=True)
        embed.add_field(name="Time",
                        value=("<t:{}:f>".format(int(match.start_date.timestamp()))
                               if match and match.start_date else None),
                        inline=False)
        embed.add_field(name="Streamed at",
                        value=(match.channel.twitch_url() if match.channel else None),
                        inline=False)

        discord.send_channel_message(channel_id, embed=embed)

@shared_task
def report_tournament_match(tournament_match_id):
    from .models import TournamentMatch
    from .facades.tournament_match_display import TournamentMatchDisplay
    tournament_match = TournamentMatch.objects.get(id=tournament_match_id)
    match = tournament_match.match
    match_display = TournamentMatchDisplay(tournament_match)
    tournament = tournament_match.tournament
    user1 = tournament_match.player1.user if tournament_match.player1 else None
    user2 = tournament_match.player2.user if tournament_match.player2 else None
    winner = tournament_match.winner.user if tournament_match.winner else None

    channel_id = env("DISCORD_TOURNAMENT_REPORTING_CHANNEL_ID")
    if channel_id and match and winner:
        discord_winner = (discord.API.users_get(winner.discord_user.discord_id)
                          if hasattr(winner, "discord_user") else None)

        embed = MessageEmbed()
        embed.title = "{} Match {} Completed".format(
            tournament.discord_emote_string or tournament.short_name,
            tournament_match.match_number
        )
        embed.url = tournament_match.get_absolute_url(True)
        embed.color = tournament.color_int()
        if discord_winner:
            embed.thumbnail.url = discord_winner.avatar_url
        embed.description = "Winner: [{}]({}) ({}-{})".format(
            winner.display_name,
            winner.get_absolute_url(True),
            match.winner_wins(),
            match.loser_wins(),
        )
        embed.add_field(name="Tournament",
                        value="[{}]({})".format(tournament.name, tournament.get_absolute_url(True)),
                        inline=False)
        embed.add_field(name="Player 1",
                        value=("[{}]({}) ({})".format(user1.display_name,
                                                      user1.get_absolute_url(True),
                                                      tournament_match.player1.seed)
                               if user1 else match_display.player1_display_name()),
                        inline=True)
        embed.add_field(name="Player 2",
                        value=("[{}]({}) ({})".format(user2.display_name,
                                                      user2.get_absolute_url(True),
                                                      tournament_match.player2.seed)
                               if user2 else match_display.player2_display_name()),
                        inline=True)
        if match.vod:
            embed.add_field(name="VOD", value=match.vod)

        discord.send_channel_message(channel_id, embed=embed)
