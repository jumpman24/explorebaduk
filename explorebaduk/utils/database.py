import datetime
import itertools
import random
import string
from typing import List

from explorebaduk.models import BlockedUserModel, FriendModel, TokenModel, UserModel


def generate_token(user_id: int, minutes: int) -> TokenModel:
    return TokenModel(
        user_id=user_id,
        token="".join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=64)),
        expire=datetime.datetime.utcnow() + datetime.timedelta(minutes=minutes),
    )


def generate_user(num: int) -> UserModel:
    return UserModel(
        username=f"johndoe{num}",
        first_name=f"John#{num}",
        last_name=f"Doe#{num}",
        password="$2y$10$N5ohEZckAk/9Exus/Py/5OM7pZgr8Gk6scZpH95FjvOSRWo00tVoC",  # Abcdefg1
        email=f"johndoe{num}@explorebaduk.com",
        rating=random.randint(100, 3000),
        puzzle_rating=random.randint(100, 3000),
    )


def generate_friend(user_id: int, friend_id: int, *, muted=False) -> FriendModel:
    return FriendModel(
        user_id=user_id,
        friend_id=friend_id,
        muted=muted,
    )


def generate_blocked_user(user_id: int, blocked_user_id: int) -> BlockedUserModel:
    return BlockedUserModel(
        user_id=user_id,
        blocked_user_id=blocked_user_id,
    )


def generate_users(session, number_of_users: int = 20) -> List[UserModel]:
    users = [generate_user(i) for i in range(number_of_users)]
    session.add_all(users)
    session.flush()
    return users


def generate_tokens(session, users: list, minutes: int = 60) -> List[TokenModel]:
    tokens = [generate_token(user.user_id, minutes) for user in users]
    session.add_all(tokens)
    session.flush()

    return tokens


def generate_friends(
    session,
    users: list,
    number_of_friends: int = 20,
    exclude_pairs: list = None,
) -> List[FriendModel]:
    all_pairs = list(itertools.combinations(users, 2))
    if exclude_pairs:
        all_pairs = [pair for pair in all_pairs if pair not in exclude_pairs]

    pairs = random.sample(all_pairs, number_of_friends)
    pairs += [(friend, user) for user, friend in pairs]

    friends = [
        generate_friend(user.user_id, friend.user_id, muted=random.choice([True, False])) for user, friend in pairs
    ]

    session.add_all(friends)
    session.flush()

    return friends


def generate_blocked_users(
    session,
    users: list,
    number_of_blocked_users: int = 20,
    friends: List[FriendModel] = None,
) -> List[BlockedUserModel]:
    all_pairs = list(itertools.combinations(users, 2))
    if friends:
        all_friend_pairs = [(friend.user_id, friend.friend_id) for friend in friends]
        all_pairs = [pair for pair in all_pairs if pair not in all_friend_pairs]

    pairs = random.sample(all_pairs, number_of_blocked_users)

    blocked_users = [generate_blocked_user(user.user_id, blocked_user.user_id) for user, blocked_user in pairs]

    session.add_all(blocked_users)
    session.flush()

    return blocked_users
