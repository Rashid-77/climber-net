import random
import string
from optparse import OptionParser

from faker import Faker
from passlib.context import CryptContext  # from passlib[bcrypt]

FILE_DEST = "../db_init/table/people"

fake = Faker("ru_RU")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

bios = (
    "Футбол, это вся моя жизнь..",
    "Живу не тужу",
    "Моя биография начинается с детства",
    "Вяжу крючком",
    "Жизнь не те дни что прожиты а те что запомнились",
    "Кто не играет в хоккей?",
    "Здесь нет биографии",
    "Ничего нет, проходите мимо",
    "Полет нормальный",
    "Первый первый, я второй, как слышно",
    "В боьшой семье клювом не щелкают",
    "Снег пошел ....",
    "Где ?",
)


def generate_fake_user_account(users):
    """
    users is a set of uniqe users, already registered
    it returns a sql comand INSERT
    """
    if random.randint(0, 1):
        fname = fake.first_name_male()
        lname = fake.last_name_male()
    else:
        fname = fake.first_name_female()
        lname = fake.last_name_female()

    bd = fake.date_between(start_date="-80y", end_date="-13y")
    user = fname[:2] + lname[:2]
    if user not in users:
        users.add(user)
    else:
        c = 1000
        while True:
            age = random.randrange(12, 99)
            s = random.choice(["-", "_", "+"])
            user = f"{user}{s}{age}"
            if user not in users:
                users.add(user)
                break
            c -= 1
            if c == 0:
                raise "Stacked on generating uniqe username"

    bio = random.choice(bios)
    country = "Russia"

    pwd = "".join(
        random.choice(string.ascii_letters + string.digits) for i in range(32)
    )

    # hashing takes to much time when generating millions of accounts,
    # so it turned off
    # hash = pwd_context.hash(pwd)     # it useless for tests now
    hash = pwd
    return str(
        f"INSERT INTO users (username, first_name, last_name, birthdate, "
        f"bio, city, country, password, disabled) VALUES "
        f"('{user}', '{fname}', '{lname}', '{bd}', "
        f"'{bio}', '{fake.city()}', '{country}', '{hash}', 0);\n"
    )


def main(limit_peoples):
    print(f"Start generating sql for {limit_peoples} users")
    users = set()
    with open(f"{FILE_DEST}-{limit_peoples}.sql", "w", encoding="utf-8") as f:
        for n in range(limit_peoples):
            if not n % 1000:
                print(f"{n:7}", end="\r")
            line = generate_fake_user_account(users)
            f.writelines(line)

    print(f"Finished. Users {len(users)}")


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("--users", action="store", type=int, default=1000)
    (opts, args) = op.parse_args()
    print(opts.users)
    main(opts.users)
