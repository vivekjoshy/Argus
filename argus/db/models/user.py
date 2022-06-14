from odmantic import Model, Field

from argus.db.models import DiscordMember


class MemberModel(Model):
    member: DiscordMember = Field()
    is_member: bool = Field(default=False)
    is_citizen: bool = Field(default=False)
    mu: float = Field(default=25)
    sigma: float = Field(default=25 / 3)

    # Schema
    class Config:
        schema_extra: dict = {
            "examples": [
                {
                    "member": 393213862620430336,
                    "is_member": False,
                    "is_citizen": False,
                    "mu": 25,
                    "sigma": 25 / 3,
                }
            ]
        }


class CandidatesModel(Model):
    member: DiscordMember = Field()

    # Schema
    class Config:
        schema_extra: dict = {
            "examples": [
                {
                    "member": 393213862620430336,
                }
            ]
        }
