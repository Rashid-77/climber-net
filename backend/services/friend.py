from typing import List

from sqlalchemy import and_, or_, text
from sqlalchemy.orm import Session

from cache.friend import friend_cache
from models.friend import Friend

from utils.log import get_logger
logger = get_logger(__name__)

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

    def get_top_popular_users_from_db(self, db: Session) -> List:
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
        return [r[0] for r in db.execute(text(stmt)) if r[1] > 0][:3]

    async def get_top_popular_users(self, db: Session) -> List:
        top_users: str = await friend_cache.get_popular_users()
        if top_users:
            return top_users
        top_users = self.get_top_popular_users_from_db(db)
        
        await friend_cache.set_popular_users(top_users)
        return top_users

    async def cache_top_popular_users(self, db: Session):
        top_users = self.get_top_popular_users_from_db(db)
        await friend_cache.set_popular_users(top_users)

    async def cache_top_users_friends(self, db: Session):
        top_users = self.get_top_popular_users_from_db(db)
        for user_id in top_users:
            ids = friend_srv.get_my_friends(db, user_id)
            await friend_cache.set_my_friends(user_id, ids)


friend_srv = FriendService()