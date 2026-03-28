from typing import List
from models.comment import Comment


def get_ordered_comments_by_likes(comments: List[Comment]) -> List[Comment]:
    return sorted(comments, key=lambda comment: comment.like_count, reverse=True)