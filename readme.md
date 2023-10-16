
The goal of this project is to explore methods for improving the performance of web applications.
Python3.10, FastApi, docker compose V2 are used.

**Prerequisite**

No ORM, DB Postgress or MYSQL

**How to**

To start project
Build project:

    bash build.sh

Run containers:

    docker-compose up

And access it go to the browser:

    127.0.0.1:8000/docs

To fill db with fake users
(_Note this'll create a user table also_):

1. create virtual environment in hl_utils
2. activate virtual environment
3. <code>cd /hl_utils</code>
4. <code>pip install requriments.txt</code>
5. <code>python user_faker.py --users xxx</code> (where xxx is number of users)
6. delete db_backend_mysql or pg_data if exist. It depends of which database is used.
7. <code>cd ..</code>
8. <code>docker-compose up</code> (or just start db contaner)
9. wait till data from sql file will be populated
<p>
If you don't want to create fake users you should:

1. build the the project <code>bash build.sh</code>
2. run containers <code>docker-compose up</code>
3. attach to the backend container <code>docker compose exec backend bash</code>
4. run a command <code>bash create_tables_and_superuser.sh</code>
5. now you can exit from backend container <code>exit</code>
