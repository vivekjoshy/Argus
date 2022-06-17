import datetime
from typing import Optional, Tuple, List

import discord
import openskill
from discord import VoiceChannel, Member


class DebateTopic:
    def __init__(self, member: discord.Member, message: str = ""):
        self.author = member
        self.message = message
        self.voters = [self.author]
        self.prioritized = False
        self.created_at = datetime.datetime.utcnow()

    def __repr__(self):
        if self.prioritized:
            representation = (
                f'Topic(author="{self.author}", '
                f'votes="{self.votes}", '
                f'prioritized="{self.prioritized}", '
                f'message="{self.message}")'
            )
        else:
            representation = (
                f'Topic(author="{self.author}", '
                f'votes="{self.votes}",'
                f'message="{self.message}")'
            )
        return representation

    def __str__(self):
        if self.message.strip() == "":
            return ""
        else:
            return self.message

    @property
    def votes(self):
        if self.prioritized:
            return len(self.voters) + 1
        else:
            return len(self.voters)

    def add_voter(self, member):
        if member not in self.voters:
            self.voters.append(member)

    def remove_voter(self, member):
        if member in self.voters:
            self.voters.remove(member)


class DebateParticipant:
    def __init__(
        self, member: discord.Member, mu, sigma, session_start: datetime.datetime
    ):
        self.member = member
        self.debater = False
        self.votes: List[DebateParticipant] = []
        self.place = None
        self.against = None

        self.mu_pre = mu
        self.mu_post = 0

        self.sigma_pre = sigma
        self.sigma_post = 0

        self.session_start: datetime.datetime = session_start
        self.session_end: Optional[datetime.datetime] = None
        self.session_duration: float = 0

    def __repr__(self):
        return (
            f"{self.member.display_name}(mu_post={self.mu_post}, "
            f"sigma_post={self.sigma_post}, "
            f"total_votes={self.total_votes()}, place={self.place}), "
            f"session_duration={self.session_duration}"
        )

    def type(self):
        if self.debater:
            if self.against:
                return "(D) [A]"
            else:
                return "(D) [ F]"
        else:
            if self.against:
                return "(V) [A]"
            else:
                return "(V) [ F]"

    def time_spent(self):
        session_time = self.session_end - self.session_start
        return session_time.total_seconds()

    def update_duration(self):
        self.session_duration += float(self.time_spent())

    def voting_power(self) -> float:
        if self.debater:
            return 1 * (1.039582 * (self.session_duration**1.579646))
        else:
            return 0.5 * (1.039582 * (self.session_duration**1.579646))

    def total_votes(self):
        votes: float = 0
        for voter in self.votes:
            if voter.against == self.against:
                vote = voter.voting_power()
                votes += vote
            else:
                vote = voter.voting_power() + 1
                votes += vote
        return votes


class DebateMatch:
    def __init__(self, topic):
        self.topic = topic
        self.participants: List[DebateParticipant] = []

        self.session_start: Optional[datetime.datetime] = None
        self.session_end: Optional[datetime.datetime] = None

        # Progress States
        self.concluding = False
        self.concluded = False

    def add_for(self, participant: DebateParticipant):
        p = participant
        for _ in self.participants:
            if _.member == p.member:
                p.against = False
                return
        p.against = False

        # Reset session start time for first participant to prevent
        # first mover advantage.
        if len(self.participants) == 1:
            time_now = datetime.datetime.utcnow()
            self.participants[0].session_start = time_now
            p.session_start = time_now

        self.participants.append(p)

    def add_against(self, participant: DebateParticipant):
        p = participant
        for _ in self.participants:
            if _.member == p.member:
                p.against = True
                return
        p.against = True

        # Reset session start time for first participant to prevent
        # first mover advantage.
        if len(self.participants) == 1:
            time_now = datetime.datetime.utcnow()
            self.participants[0].session_start = time_now
            p.session_start = time_now

        self.participants.append(p)

    def remove_participant(self, member: discord.Member):
        """Remove a participant by passing a discord.Member object"""
        for m in self.participants:
            if m.member == member:
                if not m.debater:
                    self.participants.remove(m)

    def check_participant(self, member: discord.Member):
        """Check if a member is an active participant."""
        for m in self.participants:
            if m.member == member:
                return True
        return False

    def switched_position(self, member: discord.Member) -> Optional[bool]:
        """Check is a voter switched their position."""
        checked_member = self.get_participant(member)
        for debater in self.get_debaters():
            if checked_member in [v.member for v in debater.votes]:
                if checked_member.against == debater.against:
                    return False
                else:
                    return True
        return None

    def add_debater(self, member: discord.Member):
        if not self.session_start:
            self.session_start = datetime.datetime.utcnow()

        for m in self.participants:
            if m.member == member:
                m.debater = True
                m.session_start = datetime.datetime.utcnow()
                break

    def get_debaters(self):
        debaters = []
        for p in self.participants:
            if p.debater:
                debaters.append(p)
        return debaters

    def check_debater(self, member: discord.Member):
        """Check if a member is a debater."""
        debaters = [d.member for d in self.get_debaters()]
        return member in debaters

    def vote(self, voter: discord.Member, candidate: discord.Member):
        for d in self.get_debaters():
            if d.member == candidate:
                voter_participant = self.get_participant(voter)
                if not voter_participant:
                    return None
                voter_index = self.participants.index(voter_participant)
                voter = self.participants[voter_index]
                d.votes.append(voter)
                return True
        else:
            return False

    def check_voters(self):
        """Check if there are any voters."""
        for debater in self.get_debaters():
            if len(debater.votes) > 0:
                return True
        return False

    def get_debater(self, member: discord.Member):
        debaters = self.get_debaters()
        for d in debaters:
            if d.member == member:
                return d

    def get_participant(self, member: discord.Member):
        for p in self.participants:
            if p.member == member:
                return p

    def calculate_places(self):
        debaters = self.get_debaters()
        debaters = sorted(debaters, key=lambda x: float((x.total_votes())))[::-1]
        place = 0
        previous_debater = None
        for debater in debaters:
            if previous_debater:
                if previous_debater.total_votes() == debater.total_votes():
                    debater.place = previous_debater.place
                    previous_debater = debater
                else:
                    place += 1
                    debater.place = place
                    previous_debater = debater
            else:
                place += 1
                debater.place = place
                previous_debater = debater

    def calculate_ratings(self):
        debaters = self.get_debaters()
        sorted_debaters = sorted(debaters, key=lambda _: _.place)
        debater_ratings = openskill.rate(
            [
                [openskill.create_rating([debater.mu_pre, debater.sigma_pre])]
                for debater in sorted_debaters
            ]
        )
        for raw_rating in debater_ratings:
            rating = raw_rating[0]
            sorted_debaters[debater_ratings.index(raw_rating)].mu_post = rating.mu
            sorted_debaters[debater_ratings.index(raw_rating)].sigma_post = rating.sigma

    def stop(self):
        self.session_end = datetime.datetime.utcnow()
        for participant in self.participants:
            participant.session_end = self.session_end
            participant.update_duration()

        self.calculate_places()
        self.calculate_ratings()


class DebateRoom:
    def __init__(self, number: int, vc: VoiceChannel):
        self.number = number
        self.vc: VoiceChannel = vc

        # Dynamic
        self.topics: List[DebateTopic] = []
        self._topic_voters: List[discord.Member] = []
        self.match: Optional[DebateMatch] = None
        self._conclude_voters: List[Member] = []
        self.current_topic: Optional[DebateTopic] = None

        # Studio Variables
        self.studio = False
        self.studio_engineer: Optional[Member] = None
        self.studio_participants: List[Member] = []

        # Private Match
        self.private = False
        self.private_debaters: List[Member] = []

        # Progress State
        self.updating_topic = False

    def __repr__(self):
        return f"DebateRoom(number={self.number})"

    def __gt__(self, other):
        return self.number > other.number

    def __lt__(self, other):
        return self.number < other.number

    def __ge__(self, other):
        return self.number >= other.number

    def __le__(self, other):
        return self.number <= other.number

    def __eq__(self, other):
        return self.number == other.number

    def number_from_channel(self, channel: discord.VoiceChannel) -> Optional[int]:
        """Get the number of a DebateRoom instance."""
        if channel == self.vc:
            return self.number
        else:
            return None

    def get_topic_members(self) -> List[Member]:
        """Generate the unique Members of all Topics."""
        if self.topics:
            return [topic.author for topic in self.topics]
        else:
            return []

    # Topic Methods

    def topic_from_member(self, member: discord.Member) -> Optional[DebateTopic]:
        """Get a Topic from a Member."""
        if self.topics:
            topic = [t for t in self.topics if t.author == member]
            if len(topic) > 0:
                return topic[0]

    def topics_from_authors(self, topics: List[DebateTopic]) -> List[DebateTopic]:
        """Get a list of topics from possible authors."""
        final_topics = []
        for topic in topics:
            final_topics.append(topic)
        return final_topics

    def reset_topic_creation(self, author: discord.Member):
        """Reset when a topic was a created. Useful for when a member leaves and
        rejoins a room.
        """
        topic = self.topic_from_member(author)
        if topic:
            topic.created_at = datetime.datetime.utcnow()

    def update_prioritized_topic(self) -> bool:
        """Updates the oldest topic to current topic"""
        if len(self.topics) == 0:
            return False
        sorted_topics = sorted(self.topics, key=lambda topic: topic.created_at)
        sorted_topics = self.topics_from_authors(sorted_topics)
        if len(sorted_topics) == 0:
            return False
        oldest_topic = sorted_topics[0]
        oldest_topic_index = self.topics.index(oldest_topic)
        for topic in self.topics:
            topic.prioritized = False
        self.topics[oldest_topic_index].prioritized = True
        return True

    def remove_voter_from_topics(self, voter: discord.Member):
        """Removes a voter from all topics."""
        if self.topics:
            for topic in self.topics:
                topic.remove_voter(voter)

    def remove_priority_from_topic(self, author: discord.Member):
        """Removes priority from topic based on topic author."""
        if self.topics:
            for topic in self.topics:
                if topic.author == author:
                    topic.prioritized = False

    def add_topic(self, topic: DebateTopic) -> bool:
        """Add a new topic if the member is new. If old member, then overwrite
        the topic which by default has only 1 vote.
        Returns
        -------
        True
            Topic was updated instead of inserted.
        """
        if topic.author in self.get_topic_members():
            index = self.get_topic_members().index(topic.author)
            self.remove_voter_from_topics(topic.author)
            self.topics[index] = topic
            return True
        else:
            self.topics.append(topic)
            return False

    def _calculate_max_voted_topics(self) -> List[DebateTopic]:
        """Calculates maximum voted topics."""
        if len(self.topics) == 0:
            return []
        max_topic = max(self.topics, key=lambda topic: topic.votes)
        max_voted_topics = [
            topic
            for index, topic in enumerate(self.topics)
            if topic.votes == max_topic.votes
        ]
        return max_voted_topics

    def set_current_topic(self) -> bool:
        """Set the current topic.
        Returns
        -------
        True
            Topic was changed or updated on setting topic.
        False
            Topic was the same and caused no change to current topic.
        """
        self.update_prioritized_topic()
        max_voted_topics = self._calculate_max_voted_topics()
        for topic in max_voted_topics:
            if topic.prioritized:
                if self.current_topic == topic:
                    self.current_topic = topic
                    return False
                else:
                    self.current_topic = topic
                    return True

        if len(max_voted_topics) == 1:
            if self.current_topic == max_voted_topics[0]:
                self.current_topic = max_voted_topics[0]
                return False
            else:
                self.current_topic = max_voted_topics[0]
                return True

        if self.current_topic:
            self.current_topic = None
            return True
        return False

    def topic_updated(self) -> bool:
        if self.current_topic == self.set_current_topic():
            return True
        else:
            return False

    def vote_topic(self, voter: discord.Member, candidate: discord.Member):
        """Increment a vote on a topic."""
        members = self.get_topic_members()
        if candidate in members:
            self.remove_voter_from_topics(voter)

            topic = self.topic_from_member(candidate)
            topic.add_voter(voter)
            return topic

    def remove_topic(self, author: discord.Member):
        """Remove a topic from room."""
        topic = self.topic_from_member(author)
        if topic:
            self.topics.remove(topic)

    def remove_obsolete_topics(self):
        """Remove all topics that hit 0 votes and the author is not in the room."""
        for topic in self.topics:
            if topic.votes == 0 and topic.author not in self.vc.members:
                if topic == self.current_topic:
                    self.current_topic = None
                self.topics.remove(topic)

        if self.current_topic:
            return True
        else:
            return False

    # Topic Voter Methods

    def add_topic_voter(self, member: discord.Member):
        """Add topic voters."""
        if member in self._topic_voters:
            pass
        else:
            self._topic_voters.append(member)

    def remove_topic_voter(self, member: discord.Member):
        """Remove topic voters."""
        try:
            self._topic_voters.remove(member)
        except ValueError as e_info:
            pass
        self.remove_voter_from_topics(member)

    def get_topic_voters(self) -> List[discord.Member]:
        """Return voter ids."""
        return self._topic_voters

    # Debate Match Methods
    def start_match(self, topic):
        self.match = DebateMatch(topic)

    def check_match(self):
        if self.match:
            return True
        else:
            return False

    def stop_match(self):
        """Stop the match if one is running."""
        debaters = self.match.get_debaters()
        if self.match:
            if len(self.match.get_debaters()) > 1:
                self.match.stop()
            return debaters
        else:
            return None

    def vote_conclude(
        self, voter: discord.Member
    ) -> Tuple[Optional[List[DebateParticipant]], Optional[bool], Optional[bool]]:
        if self.match:
            if self.match.check_participant(voter):
                if voter not in self._conclude_voters:
                    self._conclude_voters.append(voter)

            if len(self.match.participants) < 1:
                if self.match.check_voters():
                    debaters = self.stop_match()
                    return debaters, True, True
                else:
                    debaters = self.stop_match()
                    return debaters, True, False

            if (len(self._conclude_voters) / len(self.match.participants)) > 0.5:
                if self.match.check_voters():
                    debaters = self.stop_match()
                    return debaters, True, True  # Debaters , Concluded
                else:
                    debaters = self.match.get_debaters()
                    return debaters, True, False
            else:
                return None, False, None
        else:
            return None, None, None  # No match to stop

    def remove_conclude_voters(self):
        self._conclude_voters = []

    def purge_topics(self):
        if self.topics:
            self.topics = []
