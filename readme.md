
The goal of this project is to explore methods for improving the performance of web applications.
Python3.10, FastApi, docker compose V2 are used.

**Prerequisite**

No ORM, DB Postgress or MYSQL

**How to:**

To start project
Build project:

    bash build.sh

Run containers:

    docker compose up

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

**To start project with DB sharding capability**

Run containers:

    docker compose up -f docker-compose-citus.yml

1. then attach to the citus master 
    
    docker compose exec master bash

2. connect to the db:

    <code>psql -U ${POSTGRES_USER} -d ${POSTGRES_DB}</code>

3. create reference table:

    SELECT create_reference_table('user');

4. create distributed table from "dialogmessage" table:

    SELECT create_distributed_table('dialogmessage', 'id');

5. You can change the number of shards. Default is 32 shards.

    SELECT alter_distributed_table('dialogmessage', shard_count:=6 cascade_to_colocated:=true);

**If you need to increase the number of workers**

Run command below with desired worker number in parameter --scale worker=

    POSTGRES_USER=your_postgres_user POSTGRES_PASSWORD=your_postgres_password docker compose -f docker-compose_add_citus_workers.yml up --scale worker=2

    POSTGRES_USER=your_postgres_user POSTGRES_PASSWORD=your_postgres_password docker compose -f docker-compose_add_citus_workers.yml restart

    SELECT master_get_active_worker_nodes();

    SELECT nodename, count(*) FROM citus_shards GROUP BY nodename;

    alter system set wal_level = logical;

    SELECT run_command_on_workers('alter system set wal_level = logical');

Then detach from citus master and restart citus:

    POSTGRES_USER=root POSTGRES_PASSWORD=pwd docker compose -f docker-compose_add_citus_workers.yml restart

Then attach again to citus master:

    show wal_level;

Now you can see "logical level"

    SELECT master_get_active_worker_nodes();

Then start rebalancing:

    SELECT citus_rebalance_start();

    SELECT * FROM citus_rebalance_status();

After rebalancing is completed, check that the data is evenly distributed across the shards:

    SELECT nodename, count(*) FROM citus_shards GROUP BY nodename;

**To disable inactive nodes use new worker number in --scale worker=**

    POSTGRES_USER=your_postgres_user POSTGRES_PASSWORD=your_postgres_password docker compose -f docker-compose_add_citus_workers.yml up --scale worker=1

Then attach to citus master as in step 1 and step 2 previosly described and run:
    SELECT * from citus_disable_node('name_of_your_inactive_node', 5432);

**Scaling websocket service** 

 Haproxy is used here to loadbalance websocket service.
 After new instance of websocket service was started you should add host name and port to the haproxy.cfg in the haproxy folder of the project. After that haproxy have to be reloaded, not restarted. 
 Do it with command <code>systemctl reload haproxy</code> inside haproxy container.


**To make RabbitMq cluster**

1. <code>docker compose up</code>
2. Go to rabbit-master admin. Start browser then past and go http://127.0.0.1:15672
3. username "guest", password "guest" (without doublequotes)
4. <code>docker exec -it rmq-slave-1 bash</code>
   
   <code>rabbitmqctl stop_app</code>
   
   <code>rabbitmqctl join_cluster rabbit@rabbit</code>
   
   <code>rabbitmqctl start_app</code>

5. To check the cluster operation launch another tab in the browser and then paste and go http://127.0.0.1:15673
6. Сheck that there are two nodes rabbit@rabbit and rabbit@rabbit-slave

In a RabbitMq cluster there is no concept of a “master” node. All nodes are equal and can be stopped and started in any order. Except for one exception. If we stop all the cluster services one at a time, then the one that stopped last should start first when we start turning them back on.