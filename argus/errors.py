from discord.app_commands import CheckFailure


class Unauthorized(CheckFailure):
    """
    Error raised when a user does not have authorization to run a
    command.
    """

    def __init__(self, text: str) -> None:
        self.text: str = text
        """User not authorized to run this command."""


class NoRoleFound(CheckFailure):
    """
    Error raised when a check fails it's search for an specific role.
    """

    def __init__(self, text: str) -> None:
        self.text: str = text
        """No role found."""


class NotSpecifiedRole(CheckFailure):
    """
    Error raised when a command marked as a particular role is attempted to be invoked by another user.
    """

    def __init__(self, text: str) -> None:
        self.text: str = text
        """Not specified role."""


class NotMinimumSpecifiedRole(CheckFailure):
    """
    Error raised when a command marked as at least requiring a  particular role is attempted
    to be invoked by another user.
    """

    def __init__(self, text: str) -> None:
        self.text: str = text
        """Not minimum specified role."""


class NotGuildOwner(CheckFailure):
    """
    Error raised when a command marked as guild owner only is attempted to be invoked by another user.
    """

    def __init__(self, text: str) -> None:
        self.text: str = text
        """Not owner of the guild."""


class DataMismatch(CheckFailure):
    """
    Error raised when a check fails if there is a mismatch between data in the server and the database.
    """

    def __init__(self, text: str) -> None:
        self.text: str = text
        """Data in the server does not match data in the database."""


class UnsatisfiedRequirements(CheckFailure):
    """
    Error raised when a check fails if pre-requisites for a server are not setup.
    """

    def __init__(self, text: str) -> None:
        self.text: str = text
        """Server pre-requisites are not satisfied."""


class IncorrectChannel(CheckFailure):
    """
    Error raised when a check fails if a command is run in the wrong channel.
    """

    def __init__(self, text: str) -> None:
        self.text: str = text
        """The channel used to run the command is incorrect."""


class UpdatingTopic(CheckFailure):
    """
    Error raised when a topic in a debate room is still updating.
    """

    def __init__(self, text: str) -> None:
        self.text: str = text
        """Topic is still updating."""


class ConcludingMatch(CheckFailure):
    """
    Error raised when a debate command is run while a match is still concluding.
    """

    def __init__(self, text: str) -> None:
        self.text: str = text
        """Match still concluding."""


class NoDebateRunning(CheckFailure):
    """
    Error raised when a debate command is run while no match is running.
    """

    def __init__(self, text: str) -> None:
        self.text: str = text
        """Match is not running."""
