from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from models.friend import Friend


class FriendService:
    def is_friend(self, db: Session, user_a_id, user_b_id) -> bool:
        q1 = db.query(Friend)\
            .filter(
                or_(
                    and_(Friend.user_a == user_a_id,  Friend.user_b == user_b_id),
                    and_(Friend.user_a == user_b_id,  Friend.user_b == user_a_id)
                    )
                ).scalar()
        return q1 is not None


    def get_my_friends(self, db: Session, user_id: int) -> list:
        q1 = db.query(Friend).filter(Friend.user_a == user_id)
        q2 = db.query(Friend).filter(Friend.user_b == user_id)
        fr_ids = q1.union(q2).all()
        return [i.user_b if i.user_a == user_id else i.user_a for i in fr_ids]


friend_srv = FriendService()