
The goal of this project is to explore methods for improving the performance of web applications.
Python3.10 and FastApi are used.

**Prerequisite**

No ORM, DB Postgress or MYSQL

**How to**

To start project
Build the image:

    bash build.sh

Run a container:

    docker-compose up

And access it go to the browser:

    127.0.0.1:8000/docs

To fill db with fake users:

1. create virtual environment in hl_utils
2. activate virtual environment
3. <code>pip install requriments.txt</code> from hl_utils
4. <code>python user_faker.py --users xxx</code>     (where xxx is number of users)
5. delete db_backend_mysql if exist
6. cd to project dir and <code>docker-compose up</code> (or just start db contaner)
7. wait till data from sql file will be populated
