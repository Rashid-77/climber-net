from typing import List

from sqlalchemy.orm import Session

import crud
import schemas

from cache.post import post_cache, PostCache
from models import Post, User
from services.friend import friend_srv

from utils.log import get_logger
logger = get_logger(__name__)


class PostService:
    LAST_POPULAR_USERS_POST = 1000
    LAST_USERS_POST = 100

    async def get_post_ids(self, db: Session, user: User) -> List:
        ''' Get all post id of user from cache 
            or from db and save to cache 
        '''
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
        ''' Save every ordinary user post to cache with short ttl
            Save popular user post to cache with long ttl '''
        logger.info(f'save_post()')
        tops = await friend_srv.get_top_popular_users(db)
        logger.info(f'{tops=}')
        if not user.id in tops:
            post = crud.post.create(db, obj_in=post_in, current_user=user)
            await post_cache.set_post(post, PostCache.POSTS_EX)
            return post
        
        post_ids = await self.get_post_ids(db, user)
        logger.info(f' {post_ids=}, {type(post_ids)=}')

        post = crud.post.create(db, obj_in=post_in, current_user=user)
        await post_cache.set_post(post, PostCache.POSTS_POP_EX)

        post_ids.append(post.id)
        await post_cache.set_posts_ids(user.id, tuple(post_ids))
        logger.info(f' {post_ids=}, {type(post_ids)=}')
        return post

    async def load_post(self, db: Session, post_id: int) -> Post:
        ''' Load post by id from cache or from db '''
        post = await post_cache.get_post(post_id)
        if not post:
            logger.info('-- post from db')
            post = crud.post.get(db, post_id)
            if post:
                await post_cache.set_post(post)
        else:
            logger.info('-- post from cache')
        return post

    async def feed_friends_posts(self, db: Session, user: User) -> List:
        logger.info('post_srv.feed_friends_posts()')
        friends_ids = friend_srv.get_my_friends(db, user.id)
        logger.info(f"{friends_ids=}")
        tops = await friend_srv.get_top_popular_users(db)
        logger.info(f"{tops=}")
        all_posts = []
        for f in friends_ids:
            logger.info(f' {f=}')
            if f in tops:
                try:
                    tops.remove(f)
                except ValueError:
                    pass
                # get last x post ids
                ids = await post_cache.get_posts_ids(f)
                logger.info(f' top has posts={ids}')
                if not len(ids):
                    logger.info(' raed it from DB')
                    posts = crud.post.get_posts(db, f, limit=PostService.LAST_POPULAR_USERS_POST)
                    for p in posts:
                        await post_cache.set_post(p, expire=PostCache.POSTS_POP_EX)
                    ids = [post.id for post in posts]
                    await post_cache.set_posts_ids(f, ids)
                    logger.info(f' he has posts={ids}, {len(posts)=}')
                else:
                    ids = ids[:(PostService.LAST_POPULAR_USERS_POST+1):1]
                    # get last x posts from cache
                    posts = []
                    for i in ids:
                        p = await post_cache.get_post(i)
                        if not p:
                            logger.info(f'  from DB {i=}')
                            p = crud.post.get(db, i)
                            await post_cache.set_post(p, expire=PostCache.POSTS_POP_EX)
                        else:
                            logger.info(f'  from CACHE {i=}')
                        posts.append(p)
            else:
                # get posts from db
                logger.info(' read DB')
                posts = crud.post.get_posts(db, f, limit=PostService.LAST_USERS_POST)
                ids = [post.id for post in posts]
                logger.info(f' he has posts={ids}, {len(posts)=}')
            # merge posts
            all_posts.extend(posts)
        # sort posts by date
        logger.info(f'{all_posts=}')
        return all_posts


post_srv = PostService()