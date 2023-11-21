from typing import List

from sqlalchemy import and_, or_, text
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
        # TODO Need optimization. Do it in raw query later
        q1 = db.query(Friend).filter(Friend.user_a == user_id)
        q2 = db.query(Friend).filter(Friend.user_b == user_id)
        fr_ids = q1.union(q2).all()
        return [i.user_b if i.user_a == user_id else i.user_a for i in fr_ids]

    def get_top_popular_users(self, db: Session) -> List:
        # TODO cache it later
        stmt = '''
                SELECT 
                    COALESCE(t1.user_a, t2.user_b) AS usr, 
                    (COALESCE(t1.cnt_a, 0) + COALESCE(t2.cnt_b, 0)) AS cnt 
                FROM 
                    (SELECT user_a, count(user_a) AS cnt_a FROM friend GROUP BY user_a) AS t1
                FULL JOIN 
                    (SELECT user_b, count(user_b) AS cnt_b FROM friend GROUP BY user_b) AS t2
                ON t1.user_a = t2.user_b
                ORDER BY cnt DESC;
                '''
        res = [r for r in db.execute(text(stmt))]
        return res

friend_srv = FriendService()