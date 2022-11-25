from typing import Dict, List, Literal, Optional

import discord
from discord import Embed, Interaction, Member, app_commands
from discord.ext.commands import GroupCog
from pyrankvote import (
    Ballot,
    Candidate,
    instant_runoff_voting,
    single_transferable_vote,
)

from argus.client import ArgusClient
from argus.utils import update


class Election(GroupCog, name="election"):
    def __init__(self, bot: ArgusClient) -> None:
        self.bot = bot

        self.pm_election = False
        self.mp_election = False
        self.jd_election = False

        self.pm_election_candidates: Dict[Member, Candidate] = {}
        self.mp_election_candidates: Dict[Member, Candidate] = {}
        self.jd_election_candidates: Dict[Member, Candidate] = {}

        self.pm_election_ballots: List[Ballot] = []
        self.mp_election_ballots: List[Ballot] = []
        self.jd_election_ballots: List[Ballot] = []

        self.pm_election_roster: List[Member] = []
        self.mp_election_roster: List[Member] = []
        self.jd_election_roster: List[Member] = []

        super().__init__()

    @app_commands.command(
        name="start",
        description="Start an election.",
    )
    @app_commands.checks.has_any_role("The Crown")
    async def start(
        self,
        interaction: Interaction,
        kind: Literal["Prime Minister", "House of Commons", "Judicial Nomination"],
    ) -> None:
        if self.pm_election or self.mp_election or self.jd_election:
            await update(
                interaction,
                embed=Embed(
                    title="Election Already Running",
                    description="There is already an election running.",
                    color=0xE74C3C,
                ),
                ephemeral=True,
            )
            return

        if kind == "Prime Minister":
            self.pm_election = True
        elif kind == "House of Commons":
            self.mp_election = True
        elif kind == "Judicial Nomination":
            self.jd_election = True

        # Send Confirmation Message
        if self.pm_election:
            await update(
                interaction,
                embed=Embed(
                    title="Election Running",
                    description="The Prime Minister can now be elected.",
                    color=0x2ECC71,
                ),
            )
            return

        if self.mp_election:
            await update(
                interaction,
                embed=Embed(
                    title="Election Running",
                    description="Members of the House of Commons can now be elected.",
                    color=0x2ECC71,
                ),
            )
            return

        if self.jd_election:
            await update(
                interaction,
                embed=Embed(
                    title="Election Running",
                    description="Judges can now be elected.",
                    color=0x2ECC71,
                ),
            )
            return

    @app_commands.command(
        name="vote",
        description="Vote for a candidate.",
    )
    @app_commands.checks.has_any_role("Judge", "Citizen")
    async def vote(
        self,
        interaction: Interaction,
        first: Member,
        second: Optional[Member] = None,
        third: Optional[Member] = None,
    ) -> None:
        if self.pm_election:
            if interaction.user in self.pm_election_roster:
                await update(
                    interaction,
                    embed=Embed(
                        title="Already Voted",
                        description="You cannot cast your vote twice.",
                        color=0xE74C3C,
                    ),
                    ephemeral=True,
                )
                return

            jd = discord.utils.get(interaction.guild.roles, name="Judge")
            jd = jd.members[0]
            if jd in [first, second, third]:
                await update(
                    interaction,
                    embed=Embed(
                        title="Already Elected",
                        description=f"{jd.mention} is already a Judge.",
                        color=0xE74C3C,
                    ),
                    ephemeral=True,
                )
                return

            if first and second and third:
                self.pm_election_ballots.append(
                    Ballot(
                        ranked_candidates=[
                            self.pm_election_candidates[first],
                            self.pm_election_candidates[second],
                            self.pm_election_candidates[third],
                        ]
                    )
                )
                self.pm_election_roster.append(interaction.user)
            elif first and second and not third:
                self.pm_election_ballots.append(
                    Ballot(
                        ranked_candidates=[
                            self.pm_election_candidates[first],
                            self.pm_election_candidates[second],
                        ]
                    )
                )
                self.pm_election_roster.append(interaction.user)
            elif first and not second and not third:
                self.pm_election_ballots.append(
                    Ballot(
                        ranked_candidates=[
                            self.pm_election_candidates[first],
                        ]
                    )
                )
                self.pm_election_roster.append(interaction.user)
        elif self.mp_election:
            if interaction.user in self.mp_election_roster:
                await update(
                    interaction,
                    embed=Embed(
                        title="Already Voted",
                        description="You cannot cast your vote twice.",
                        color=0xE74C3C,
                    ),
                    ephemeral=True,
                )
                return

            pm = discord.utils.get(interaction.guild.roles, name="Prime Minister")
            pm = pm.members[0]
            if pm in [first, second, third]:
                await update(
                    interaction,
                    embed=Embed(
                        title="Already Elected",
                        description=f"{pm.mention} is already Prime Minister.",
                        color=0xE74C3C,
                    ),
                    ephemeral=True,
                )
                return

            if first and second and third:
                self.mp_election_ballots.append(
                    Ballot(
                        ranked_candidates=[
                            self.mp_election_candidates[first],
                            self.mp_election_candidates[second],
                            self.mp_election_candidates[third],
                        ]
                    )
                )
                self.mp_election_roster.append(interaction.user)
            elif first and second and not third:
                self.mp_election_ballots.append(
                    Ballot(
                        ranked_candidates=[
                            self.mp_election_candidates[first],
                            self.mp_election_candidates[second],
                        ]
                    )
                )
                self.mp_election_roster.append(interaction.user)
            elif first and not second and not third:
                self.mp_election_ballots.append(
                    Ballot(
                        ranked_candidates=[
                            self.mp_election_candidates[first],
                        ]
                    )
                )
                self.mp_election_roster.append(interaction.user)
        elif self.jd_election:
            citizen = discord.utils.get(interaction.guild.roles, name="Citizen")
            members = [first, second, third]
            for member in members:
                if member:
                    if citizen not in member.roles:
                        await update(
                            interaction,
                            embed=Embed(
                                title="Invalid Candidate",
                                description="You can only cast votes for citizens.",
                                color=0xE74C3C,
                            ),
                            ephemeral=True,
                        )
                        return

            pm = discord.utils.get(interaction.guild.roles, name="Prime Minister")
            mp = discord.utils.get(interaction.guild.roles, name="Minister")
            if pm not in interaction.user.roles or mp not in interaction.user.roles:
                await update(
                    interaction,
                    embed=Embed(
                        title="Unauthorized",
                        description=f"Only members of the House of Commons can elect judges..",
                        color=0xE74C3C,
                    ),
                    ephemeral=True,
                )
                return

            pm = pm.members[0]
            if pm in [first, second, third]:
                await update(
                    interaction,
                    embed=Embed(
                        title="Already Elected",
                        description=f"{pm.mention} is already Prime Minister.",
                        color=0xE74C3C,
                    ),
                    ephemeral=True,
                )
                return

            mp = mp.members[0]
            if mp in [first, second, third]:
                await update(
                    interaction,
                    embed=Embed(
                        title="Already Elected",
                        description=f"{mp.mention} is already a Minister.",
                        color=0xE74C3C,
                    ),
                    ephemeral=True,
                )
                return

            if interaction.user in self.jd_election_roster:
                await update(
                    interaction,
                    embed=Embed(
                        title="Already Voted",
                        description="You cannot cast your vote twice.",
                        color=0xE74C3C,
                    ),
                    ephemeral=True,
                )
                return

            if first and second and third:
                self.jd_election_ballots.append(
                    Ballot(
                        ranked_candidates=[
                            self.jd_election_candidates[first],
                            self.jd_election_candidates[second],
                            self.jd_election_candidates[third],
                        ]
                    )
                )
                self.jd_election_roster.append(interaction.user)
            elif first and second and not third:
                self.jd_election_ballots.append(
                    Ballot(
                        ranked_candidates=[
                            self.jd_election_candidates[first],
                            self.jd_election_candidates[second],
                        ]
                    )
                )
                self.jd_election_roster.append(interaction.user)
            elif first and not second and not third:
                self.jd_election_ballots.append(
                    Ballot(
                        ranked_candidates=[
                            self.jd_election_candidates[first],
                        ]
                    )
                )
                self.jd_election_roster.append(interaction.user)
        else:
            await update(
                interaction,
                embed=Embed(
                    title="No Election Running",
                    description="There is no election currently running.",
                    color=0xE74C3C,
                ),
                ephemeral=True,
            )
            return

        await update(
            interaction,
            embed=Embed(
                title="Election Vote Cast",
                description="Your vote has been recorded.",
                color=0x2ECC71,
            ),
            ephemeral=True,
        )

    @app_commands.command(
        name="stand",
        description="Stand for election.",
    )
    @app_commands.checks.has_any_role("Citizen")
    async def stand(self, interaction: Interaction) -> None:
        member = interaction.user

        if self.pm_election:
            self.pm_election_candidates[member] = Candidate(name=f"{member.id}")
        elif self.mp_election:
            self.mp_election_candidates[member] = Candidate(name=f"{member.id}")
        elif self.jd_election:
            citizen = discord.utils.get(interaction.user.roles, name="Citizen")
            if citizen in member.roles:
                self.jd_election_candidates[member] = Candidate(name=f"{member.id}")
            else:
                await update(
                    interaction,
                    embed=Embed(
                        title="Unauthorized",
                        description="Only citizens can stand for election to be a judge.",
                        color=0xE74C3C,
                    ),
                    ephemeral=True,
                )
                return
        else:
            await update(
                interaction,
                embed=Embed(
                    title="No Election Running",
                    description="There is no election currently running.",
                    color=0xE74C3C,
                ),
                ephemeral=True,
            )
            return

        await update(
            interaction,
            embed=Embed(
                title="Nomination Cast",
                description="You are now standing for election.",
                color=0x2ECC71,
            ),
            ephemeral=True,
        )

    @app_commands.command(
        name="end",
        description="End an election.",
    )
    @app_commands.checks.has_any_role("The Crown")
    async def end(self, interaction: Interaction) -> None:
        if self.pm_election:
            self.pm_election = False

            result = instant_runoff_voting(
                candidates=list(self.pm_election_candidates.values()),
                ballots=self.pm_election_ballots,
            )
            winner = result.get_winners()[0]
            winner = interaction.guild.get_member(int(winner.name))

            pm = discord.utils.get(interaction.guild.roles, name="Prime Minister")
            for member in pm.members:
                await member.remove_roles(pm, reason="Removed during election.")
            await winner.add_roles(pm, reason="Won election.")

            election_feed = discord.utils.get(
                interaction.guild.channels, name="election-feed"
            )
            embed = Embed(
                title="Prime Minister Elected",
                description=f"{winner.mention} has won the election. "
                f"They are effective immediately the Prime Minister of Open Debates",
                colour=0xEC6A5C,
            )
            await election_feed.send(embed=embed)

            self.pm_election_ballots = []
            self.pm_election_candidates = {}
            self.pm_election_roster = []

            await update(
                interaction,
                embed=Embed(
                    title="Election Ended",
                    description="Prime Minister has been elected.",
                    color=0x2ECC71,
                ),
                ephemeral=True,
            )
        elif self.mp_election:
            self.mp_election = False

            result = single_transferable_vote(
                candidates=list(self.mp_election_candidates.values()),
                ballots=self.mp_election_ballots,
                number_of_seats=min([50, len(interaction.guild.members) * 0.01]),
            )

            mp = discord.utils.get(interaction.guild.roles, name="Minister")
            for member in mp.members:
                await member.remove_roles(mp, reason="Removed during election.")
            winners = result.get_winners()

            election_feed = discord.utils.get(
                interaction.guild.channels, name="election-feed"
            )
            for winner in winners:
                winner = interaction.guild.get_member(int(winner.name))
                embed = Embed(
                    title="Minister Elected",
                    description=f"{winner.mention} is now a Minister of Open Debates ",
                    colour=0xEC6A5C,
                )
                await winner.add_roles(mp, reason="Won election.")
                await election_feed.send(embed=embed)

            self.mp_election_ballots = []
            self.mp_election_candidates = {}
            self.mp_election_roster = []

            await update(
                interaction,
                embed=Embed(
                    title="Election Ended",
                    description="Members of the House of Commons have been elected.",
                    color=0x2ECC71,
                ),
                ephemeral=True,
            )
        elif self.jd_election:
            self.jd_election = False

            result = single_transferable_vote(
                candidates=list(self.jd_election_candidates.values()),
                ballots=self.jd_election_ballots,
                number_of_seats=min([50, len(interaction.guild.members) * 0.01]),
            )

            jd = discord.utils.get(interaction.guild.roles, name="Judge")
            for member in jd.members:
                await member.remove_roles(jd, reason="Removed during election.")
            winners = result.get_winners()

            election_feed = discord.utils.get(
                interaction.guild.channels, name="election-feed"
            )
            for winner in winners:
                winner = interaction.guild.get_member(int(winner.name))
                embed = Embed(
                    title="Minister Elected",
                    description=f"{winner.mention} is now a Minister of Open Debates ",
                    colour=0xEC6A5C,
                )
                await winner.add_roles(jd, reason="Won election.")
                await election_feed.send(embed=embed)

            self.jd_election_ballots = []
            self.jd_election_candidates = {}
            self.jd_election_roster = []

            await update(
                interaction,
                embed=Embed(
                    title="Election Ended",
                    description="Judges have been elected.",
                    color=0x2ECC71,
                ),
                ephemeral=True,
            )
        else:
            await update(
                interaction,
                embed=Embed(
                    title="No Election Running",
                    description="There is no election currently running.",
                    color=0xE74C3C,
                ),
                ephemeral=True,
            )
            return


class Citizenship(GroupCog, name="citizenship"):
    def __init__(self, bot: ArgusClient) -> None:
        self.bot = bot

    @app_commands.command(
        name="grant",
        description="Grant citizenship to a Member.",
    )
    @app_commands.checks.has_any_role("The Crown", "Chancellor", "Judge")
    @app_commands.checks.cooldown(rate=1, per=600)
    async def grant(self, interaction: Interaction, member: Member) -> None:
        if "Member" not in [role.name for role in member.roles]:
            await update(
                interaction,
                embed=Embed(
                    title="Unauthorized",
                    description="You can only promote Members. Please check if they have that role.",
                    color=0xE74C3C,
                ),
                ephemeral=True,
            )
            return

        if "Citizen" in [role.name for role in member.roles]:
            await update(
                interaction,
                embed=Embed(
                    title="Unauthorized",
                    description="You can only promote Members.",
                    color=0xE74C3C,
                ),
                ephemeral=True,
            )
            return

        if "Judge" in [role.name for role in member.roles]:
            await update(
                interaction,
                embed=Embed(
                    title="Unauthorized",
                    description="You can only promote Members.",
                    color=0xE74C3C,
                ),
                ephemeral=True,
            )
            return

        citizen = discord.utils.get(interaction.guild.roles, name="Citizen")
        member_role = discord.utils.get(interaction.guild.roles, name="Member")
        await member.add_roles(citizen)
        await member.remove_roles(member_role)

        await update(
            interaction,
            embed=Embed(
                title="Citizenship Granted",
                description=f"{member.mention} is now a citizen.",
                color=0x2ECC71,
            ),
            ephemeral=True,
        )

    @app_commands.command(
        name="revoke",
        description="Demote a Citizen to Member.",
    )
    @app_commands.checks.has_any_role("The Crown", "Chancellor", "Liege", "Judge")
    @app_commands.checks.cooldown(rate=1, per=86400)
    async def revoke(self, interaction: Interaction, member: Member) -> None:
        if "Citizen" not in [role.name for role in member.roles]:
            await update(
                interaction,
                embed=Embed(
                    title="Unauthorized",
                    description="You can only demote Citizens.",
                    color=0xE74C3C,
                ),
                ephemeral=True,
            )
            return

        citizen = discord.utils.get(interaction.guild.roles, name="Citizen")
        member_role = discord.utils.get(interaction.guild.roles, name="Member")
        await member.add_roles(member_role)
        await member.remove_roles(citizen)

        await update(
            interaction,
            embed=Embed(
                title="Citizenship Revoked",
                description=f"{member.mention} is now a Member.",
                color=0x2ECC71,
            ),
            ephemeral=True,
        )


class Membership(GroupCog, name="membership"):
    def __init__(self, bot: ArgusClient) -> None:
        self.bot = bot

    @app_commands.command(
        name="grant",
        description="Grant membership to a new user.",
    )
    @app_commands.checks.has_any_role("The Crown", "Chancellor", "Liege")
    async def grant(self, interaction: Interaction, member: Member) -> None:
        role_names = [role.name for role in member.roles]
        if "Member" in role_names or "Citizen" in role_names or "Judge" in role_names:
            await update(
                interaction,
                embed=Embed(
                    title="Unauthorized",
                    description="You can only promote regular users.",
                    color=0xE74C3C,
                ),
                ephemeral=True,
            )
            return

        member_role = discord.utils.get(interaction.guild.roles, name="Member")
        await member.add_roles(member_role)

        await update(
            interaction,
            embed=Embed(
                title="Citizenship Granted",
                description=f"{member.mention} is now a Member.",
                color=0x2ECC71,
            ),
            ephemeral=True,
        )

    @app_commands.command(
        name="revoke",
        description="Demote a Citizen to Member.",
    )
    @app_commands.checks.has_any_role("The Crown", "Chancellor", "Liege")
    async def revoke(self, interaction: Interaction, member: Member) -> None:
        if "Member" not in [role.name for role in member.roles]:
            await update(
                interaction,
                embed=Embed(
                    title="Unauthorized",
                    description="You can only demote Members.",
                    color=0xE74C3C,
                ),
                ephemeral=True,
            )
            return

        member_role = discord.utils.get(interaction.guild.roles, name="Member")
        await member.remove_roles(member_role)

        await update(
            interaction,
            embed=Embed(
                title="Membership Revoked",
                description=f"{member.mention} is no longer a Member.",
                color=0x2ECC71,
            ),
            ephemeral=True,
        )


async def setup(bot: ArgusClient) -> None:
    await bot.add_cog(
        Election(bot), guilds=[discord.Object(id=bot.config["global"]["guild_id"])]
    )
    await bot.add_cog(
        Citizenship(bot), guilds=[discord.Object(id=bot.config["global"]["guild_id"])]
    )
    await bot.add_cog(
        Membership(bot), guilds=[discord.Object(id=bot.config["global"]["guild_id"])]
    )
