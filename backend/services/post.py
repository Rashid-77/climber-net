from typing import List

from sqlalchemy.orm import Session

import crud
import schemas
from cache.post import post_cache
from models import Post, User

from utils.log import get_logger
logger = get_logger(__name__)


class PostService:
    async def get_post_ids(self, db: Session, user: User) -> List:
        post_ids = await post_cache.get_posts_ids(user.id)
        if not post_ids:
            logger.info('-- post_ids from db')
            ids = db.query(Post.id).filter(Post.wall_user_id == user.id).all()
            post_ids = [id[0] for id in ids]
        else:
            logger.info('-- post_ids from cache')
        logger.info(f'{post_ids=}, {type(post_ids)=}')
        return post_ids

    async def save_post(self, db: Session, user: User, post_in: schemas.PostCreate) -> Post:
        logger.info(f'save_post()')
        post = crud.post.create(db, obj_in=post_in, current_user=user)
        await post_cache.set_post(post)
        post_ids = await self.get_post_ids(db, user)
        logger.info(f'{post_ids=}, {type(post_ids)=}')
        post_ids.append(post.id)
        await post_cache.set_posts_ids(user.id, tuple(post_ids))
        return post

    async def load_post(self, db: Session, post_id: int) -> Post:
        post = await post_cache.get_post(post_id)
        if not post:
            logger.info('-- post from db')
            post = crud.post.get(db, post_id)
            if post:
                await post_cache.set_post(post)
        else:
            logger.info('-- post from cache')
        return post



post_srv = PostService()