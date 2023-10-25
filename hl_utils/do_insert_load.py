import logging
import random
import string
import time

from getpass import getpass
from optparse import OptionParser

from faker import Faker
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session


logging.basicConfig(
    filename="do_insert.log",
    level=logging.DEBUG,
    format="[%(asctime)s] %(levelname).1s %(message)s",
    datefmt="%Y.%m.%d %H:%M:%S",
)
logging.info('')
logging.info('start')


fake = Faker("en_US")
chs = string.ascii_letters + string.digits
bios = (
    "Rocket is a metall pipe",
    "My favorite song is ...",
    "I like to cook",
    "I saw glowing eyes when I was in the cave",
    "The library is the best place in the whole world",
    "mmm...",
)
last_id = None


def generate_fake_user_account(users):
    """
    users is a set of uniqe users, already registered
    it returns a sql comand INSERT
    """
    if random.randint(0, 1):
        fname = fake.first_name_male().lower()
        lname = fake.last_name_male().lower()
    else:
        fname = fake.first_name_female().lower()
        lname = fake.last_name_female().lower()

    bd = fake.date_between(start_date="-80y", end_date="-13y")
    user = fname[:2] + lname[:2]
    c = 1000
    while True:
        age = random.randrange(12, 99)
        s = random.choice(["-", "_", "+"])
        x = random.choice(["-", "_", "+"])
        uniq = ''.join([random.choice(chs) for i in range(4)])
        user = f"{user}{s}{age}{x}{uniq}"
        if user not in users:
            users.add(user)
            break
        c -= 1
        if c == 0:
            raise "Stacked on generating uniqe username"

    bio = random.choice(bios)
    country = "Africa"

    pwd = "".join(
        random.choice(string.ascii_letters + string.digits) for i in range(32)
    )
    # hashing takes to much time when generating millions of accounts,
    # so it turned off for testing stage only
    # hash = pwd_context.hash(pwd)     # it useless for tests now
    hash = pwd
    logging.info(f'-- {user}')
    return (
        f"('{user}', '{fname}', '{lname}', '{bd}', "
        f"'{bio}', '{fake.city()}', '{country}', '{hash}', FALSE, FALSE)"
    )


def do_insert(users, db: Session):
    global last_id
    stmt =  ('INSERT INTO "user" ('
            'username, first_name, last_name, birthdate, '
            'bio, city, country, hashed_password, disabled, is_superuser'
            ') VALUES')
    values = generate_fake_user_account(users)
    stmt = f'{stmt} {values};'
    q = db.execute(text(stmt))
    db.commit()

    q = db.execute(text('SELECT max(id) FROM "user";'))
    res = q.fetchone()
    logging.info(res)
    last_id = res[0]
    print(f'id={res[0]}', end='\r')


def main(users_cnt, rps, pg_host, pg_port, pg_dbname, pg_user, pg_pass):
    global last_id
    users = set()
    pg_url: str = f"postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_dbname}"

    engine = create_engine(pg_url, pool_pre_ping=True)
    sess = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    db = sess()
    dt = 1 / rps
    print('Insert started')
    while True:
        st = time.time()
        
        do_insert(users, db)
        
        if users_cnt:
            users_cnt -= 1
        elif users_cnt == 0: # The None using to ignore users_cnt and insert until ctrl+c
            break

        dur = time.time() - st
        if dur >= dt:
            continue
        
        sleept = dt - dur
        
        time.sleep(sleept)


if __name__ == "__main__":
    
    op = OptionParser()
    op.add_option("--users", action="store", type=int, default=None)
    op.add_option("--rps", action="store", type=int, default=1)
    op.add_option("--host", action="store", type=str, default=None)
    op.add_option("--port", action="store", type=int, default=None)
    op.add_option("--db", action="store", type=str, default=None)
    op.add_option("--user", action="store", type=str, default=None)
    op.add_option("--pwd", action="store", type=str, default=None)
    (opts, args) = op.parse_args()
    if opts.rps <= 0:
        print("Error: --rps should be positive number !")
        exit(1)
    try:
        pwd = getpass()
        main(opts.users, opts.rps, opts.host, opts.port, opts.db, opts.user, pwd)
    except KeyboardInterrupt:
        pass

    print(f'Finished. Last id={last_id}')
