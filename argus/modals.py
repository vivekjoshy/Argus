import uuid

import discord
from discord import Embed, Interaction, ui

from argus.db.models.user import MemberModel
from argus.utils import update


class CustomModal(ui.Modal):
    def __init__(self, states, *args, **kwargs):
        self.states = states
        super(CustomModal, self).__init__(*args, **kwargs)


class DebateVotingRubric(CustomModal, title="Voter Rubric"):
    select = ui.Select(
        placeholder="Select all that apply and click submit to vote.",
        min_values=0,
        max_values=4,
    )
    select.add_option(
        label="Debater's arguments were factual.",
        value="Factual",
    )
    select.add_option(
        label="Debater's arguments were consistent or logically valid.",
        value="Consistent",
    )
    select.add_option(
        label="Debater observed the principle of charity.", value="Charitable"
    )
    select.add_option(label="Debater was respectful to others.", value="Respectful")

    async def on_submit(self, interaction: Interaction):
        room = self.states["room"]
        author = self.states["author"]
        candidate = self.states["candidate"]
        result = room.match.vote(voter=author, candidate=candidate)

        if result is None:
            embed = Embed(
                title="Stance Not Set",
                description="You must set a stance for or against the topic.",
                color=0xE74C3C,
            )
            await update(interaction, embed=embed, ephemeral=True)
            return
        elif not result:
            embed = Embed(
                title="Invalid Candidate",
                description="You can only vote for debaters.",
                color=0xE74C3C,
            )
            await update(interaction, embed=embed, ephemeral=True)
            return

        candidate_data = await interaction.client.engine.find_one(
            MemberModel, MemberModel.member == candidate.id
        )
        if "Factual" in self.select.values:
            candidate_data.factual += 1
        if "Consistent" in self.select.values:
            candidate_data.consistent += 1
        if "Charitable" in self.select.values:
            candidate_data.charitable += 1
        if "Respectful" in self.select.values:
            candidate_data.respectful += 1

        candidate_data.vote_count += 1

        await interaction.client.engine.save(candidate_data)

        embed = Embed(
            title="Vote Cast", description="Your vote has been cast", color=0x2ECC71
        )
        await update(interaction, embed=embed, ephemeral=True)


class MotionProposal(CustomModal, title="Motion Proposal"):
    motion_title = ui.TextInput(
        label="Title", required=True, min_length=5, max_length=256
    )
    body = ui.TextInput(
        label="Body",
        placeholder="Discord Markdown is Supported",
        style=discord.TextStyle.paragraph,
        required=True,
        min_length=10,
        max_length=1024,
    )

    async def on_submit(self, interaction: Interaction):
        if self.states.hl_enabled:
            self.states.hl_id = uuid.uuid4().hex.upper()
            embed = Embed(
                title=f"Motion Proposed - {self.states.hl_id}",
                description="**Drafted in the House of Lords**",
            )
            embed.add_field(name=f"{self.motion_title}", value=f"{self.body}")
            self.states.hl_motion["embed"] = embed
            self.states.hl_last_embed = embed
            await self.states.motions.send(embeds=[embed])
            self.states.hl_enabled = False
        elif self.states.hc_enabled:
            self.states.hc_id = uuid.uuid4().hex.upper()
            embed = Embed(
                title=f"Motion Proposed - {self.states.hc_id}",
                description="**Drafted in the House of Commons**",
            )
            embed.add_field(name=f"{self.motion_title}", value=f"{self.body}")
            self.states.hc_motion["embed"] = embed
            self.states.hc_last_embed = embed
            await self.states.motions.send(embeds=[embed])
            self.states.hc_enabled = False

        embed = Embed(
            title="Motion Proposed",
            description="Your motion has been sent for deliberation.",
            color=0x2ECC71,
        )
        await update(interaction, embed=embed, ephemeral=True)
