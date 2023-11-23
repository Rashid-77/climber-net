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
            ids = db.query(Post.id).filter(Post.wall_user_id == user.id).all()
            post_ids = [id[0] for id in ids]
        return post_ids

    async def save_post(self, db: Session, user: User, post_in: schemas.PostCreate) -> Post:
        ''' Save every ordinary user post to cache with short ttl
            Save popular user post to cache with long ttl '''
        tops = await friend_srv.get_top_popular_users(db)
        if not user.id in tops:
            post = crud.post.create(db, obj_in=post_in, current_user=user)
            await post_cache.set_post(post, PostCache.POSTS_EX)
            return post
        
        post_ids = await self.get_post_ids(db, user)

        post = crud.post.create(db, obj_in=post_in, current_user=user)
        await post_cache.set_post(post, PostCache.POSTS_POP_EX)

        post_ids.append(post.id)
        await post_cache.set_posts_ids(user.id, tuple(post_ids))
        return post

    async def load_post(self, db: Session, post_id: int) -> Post:
        ''' Load post by id from cache or from db '''
        post = await post_cache.get_post(post_id)
        if not post:
            post = crud.post.get(db, post_id)
            if post:
                await post_cache.set_post(post)
        return post

    async def feed_friends_posts(self, db: Session, user: User) -> List:
        friends_ids = friend_srv.get_my_friends(db, user.id)
        tops = await friend_srv.get_top_popular_users(db)
        all_posts = []
        for f in friends_ids:
            if f in tops:
                try:
                    tops.remove(f)
                except ValueError:
                    pass
                # get last x post ids
                ids = await post_cache.get_posts_ids(f)
                if not len(ids):
                    posts = crud.post.get_posts(db, f, limit=PostService.LAST_POPULAR_USERS_POST)
                    for p in posts:
                        await post_cache.set_post(p, expire=PostCache.POSTS_POP_EX)
                    ids = [post.id for post in posts]
                    await post_cache.set_posts_ids(f, ids)
                else:
                    ids = ids[:(PostService.LAST_POPULAR_USERS_POST+1):1]
                    # get last x posts from cache
                    posts = []
                    for i in ids:
                        p = await post_cache.get_post(i)
                        if not p:
                            p = crud.post.get(db, i)
                            await post_cache.set_post(p, expire=PostCache.POSTS_POP_EX)
                        posts.append(p)
            else:
                # get posts from db
                posts = crud.post.get_posts(db, f, limit=PostService.LAST_USERS_POST)
                ids = [post.id for post in posts]
            all_posts.extend(posts)
        # TODO sort posts by date
        return all_posts

    async def warming_up_post_cache(self, db: Session):
        '''
            Cache wil be filled with post from popular users at startup
            The "tops_limit" and "posts_limit" from each popular user 
            will be defined automatically.
        '''
        posts_limit = 1000
        tops_limit = 1000
        tops = await friend_srv.get_top_popular_users(db)
        for user in tops[:tops_limit]:
            posts = crud.post.get_posts(db, user_id=user, offset=0, limit=posts_limit)
            for p in posts:
                await post_cache.set_post(p, PostCache.POSTS_POP_EX)
            ids = [post.id for post in posts]
            await post_cache.set_posts_ids(user_id=user, ids=ids)
        


post_srv = PostService()