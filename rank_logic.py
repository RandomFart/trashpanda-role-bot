from dataclasses import dataclass


@dataclass(frozen=True)
class Rank:
    name: str
    role_id: int
    required_days: int


def get_days_since_joined(member, now):
    """
    Returns how many full days a Discord member has been in the server.
    """
    if member.joined_at is None:
        return None

    return (now - member.joined_at).days


def get_qualified_rank(days_in_server, ranks):
    """
    Given a member's server age and a list of ranks,
    return the highest rank they qualify for.

    Returns None if they do not qualify for anything above Private.
    """
    if days_in_server is None:
        return None

    qualified_rank = None

    for rank in ranks:
        if days_in_server >= rank.required_days:
            qualified_rank = rank
        else:
            break

    return qualified_rank