from odmantic import Model, Field

from argus.db.models import DiscordMember


class MemberModel(Model):
    member: DiscordMember = Field()
    is_member: bool = Field(default=False)
    is_citizen: bool = Field(default=False)
    mu: float = Field(default=25)
    sigma: float = Field(default=25 / 3)
    rating: float = Field(default=float(20 * ((25 - 3 * 25 / 3) + 25)))
    debate_count: int = Field(default=0)
    vote_count: int = Field(default=0)
    factual: int = Field(default=0)
    consistent: int = Field(default=0)
    charitable: int = Field(default=0)
    respectful: int = Field(default=0)

    # Schema
    class Config:
        schema_extra: dict = {
            "examples": [
                {
                    "member": 393213862620430336,
                    "is_member": False,
                    "is_citizen": False,
                    "citizenship_revoked": False,
                    "mu": 25,
                    "sigma": 25 / 3,
                    "rating": 500,
                    "debate_count": 0,
                    "vote_count": 0,
                    "factual": 0,
                    "consistent": 0,
                    "charitable": 0,
                    "respectful": 0,
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
