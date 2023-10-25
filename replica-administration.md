# Создание реплик, перевод их в режим мастера, перевод в синхр/асинхр режимы вручную.


**Меняем postgresql.conf на мастере**

<code>sudo nano pg_data/postgresql.conf</code>

в конец добавляем

        #ssl = off для ДЗ и прода лучше не ставить ?
        wal_level = replica
        max_wal_senders = 4 # expected slave num


<code>psql climber-net -U root -W</code>

смотрим пользователей

climber-net=# <code>\du</code>

<pre>
                                   List of roles
 Role name |                         Attributes                         | Member of 
-----------+------------------------------------------------------------+-----------
 root      | Superuser, Create role, Create DB, Replication, Bypass RLS | {}
</pre>

 climber-net=# <code>create role replicator with login replication password 'pass';</code>

 climber-net=# <code>\du</code>

<pre>
                                    List of roles
 Role name  |                         Attributes                         | Member of 
------------+------------------------------------------------------------+-----------
 replicator | Replication                                                | {}
 root       | Superuser, Create role, Create DB, Replication, Bypass RLS | {}
 </pre>


изменяем файл pg_hba.conf

<code>sudo nano pg_data/pg_hba.conf</code>

комментируем строку

\# host    replication     all             127.0.0.1/32            trust

в конец добавляем (адрес сети из __docker inspect climber_db__)

host    replication     replicator      172.18.0.0/16            md5

<code>docker exec -it climber_db bash</code>

<code>mkdir /pgslave</code>

<code>pg_basebackup -h climber_db -D /pgslave -U replicator -v -P --wal-method=stream</code>


**Запускаем первую реплику**

<code>docker cp climber_db:/pgslave pgslave</code>

<code>touch pgslave/standby.signal</code>

<code>sudo nano pgslave/postgresql.conf</code>

добавляем в конец

primary_conninfo = 'host=climber_db port=5432 user=replicator 

password=pass application_name=pgslave'

<code>docker run -dit -v $PWD/pgslave/:/var/lib/postgresql/data -e POSTGRES_PASSWORD=pass -p 15432:5432 --network=climber-net_default --restart=unless-stopped --name=pgslave postgres:15.0-alpine</code>

<code>docker exec -it pgslave bash</code>

<code>psql climber-net -U replicator -W</code>

<code>\dt</code>

и видим что таблицы user нет, так как репликация еще не включена


**запускаем вторую реплику**

<code>docker cp climber_db:/pgslave pgslave2</code>

Меняем postgresql.conf на реплике-2

<code>sudo nano pgslave2/postgresql.conf</code>

primary_conninfo = 'host=climber_db port=5432 user=replicator 

password=pass application_name=pgslave2'

<code>touch pgslave2/standby.signal</code>

<code>docker run -dit -v $PWD/pgslave2/:/var/lib/postgresql/data -e POSTGRES_PASSWORD=pass -p 25432:5432 --network=climber-net_default --restart=unless-stopped --name=pgslave2 postgres:15.0-alpine</code>

<code>docker exec -it pgslave2 bash</code>


**Включаем aсинхронную репликацию на мастере**

проверяем что следующие строки закоментированы

\# synchronous_commit = on

\# synchronous_standby_names = 'FIRST 1 (pgslave, pgslave2)'

обновим конфигурацию на мастере

<code>docker exec -it climber_db</code>
<code>psql climber-net -U root -W</code>

<code>select pg_reload_conf();</code>

<code>SELECT pid,usename,application_name,state,sync_state FROM </code>

<code>pg_stat_replication;</code>

<pre> pid |  usename   | application_name |   state   | sync_state 
-----+------------+------------------+-----------+------------
  28 | replicator | pgslave          | streaming | async
  29 | replicator | pgslave2         | streaming | async</pre>

Переводим приложение на чтение с первого slave, для этого
изменяем в .env
POSTGRES_HOST=pgslave2

запускаем нагрузку на чтение из (api/v1/user/get/{id} и api/v1/user/search/?)


**Включаем синхронную репликацию на мастере**

<code>sudo nano pg_data/postgresql.conf</code>

synchronous_commit = on
synchronous_standby_names = 'FIRST 1 (pgslave, pgslave2)'

обновим конфигурацию на мастере

<code>docker exec -it climber_db bash</code>
<code>psql climber-net -U root -W</code>

<code>select pg_reload_conf();</code>

<code>SELECT pid,usename,application_name,state,sync_state FROM pg_stat_replication;</code>

<pre> pid |  usename   | application_name |   state   | sync_state 
-----+------------+------------------+-----------+------------
  28 | replicator | pgslave          | streaming | sync
  29 | replicator | pgslave2         | streaming | potential</pre>

проверяем что на репликах в таблицу мы писать не можем, а на мастере можем

Нагружаем мастера записью в таблицу

нагружаем реплику-2 чтением из таблиц

отключаем мастера командой 

<code>docker stop climber_db</code>


**Промоутим pgslave до мастера**

<code>sudo nano pgslave/postgresql.conf</code>

\# primary_conninfo = 'host=climber_db port=5432 user=replicator 

password=pass application_name=pgslave'

synchronous_commit = on

synchronous_standby_names = 'ANY 1 (pgslave2)'

<code>docker exec -it pgslave bash</code>

<code>psql climber-net -U root -W</code>

Обновляем конфигурацию

<code>select pg_reload_conf();</code>

Меняем кофигурацию на pgslave2

<code>sudo nano pgslave2/postgresql.conf</code>

primary_conninfo = 'host=pgslave port=5432 user=replicator password=pass application_name=pgslave'

<code>docker exec -it pgslave2 bash</code>

<code>psql climber-net -U root -W</code>

Обновляем конфигурацию

select pg_reload_conf();

Переводим реплику-2 в режим мастера

<code>docker exec -it pgslave bash</code>

<code>select * from pg_promote();</code>

Проверяем статус репликации

climber-net=# <code>SELECT pid,usename,application_name,state,sync_state FROM pg_stat_replication;<.code>

<pre>
 pid  |  usename   | application_name |   state   | sync_state 
------+------------+------------------+-----------+------------
 6867 | replicator | pgslave2         | streaming | sync</pre>
