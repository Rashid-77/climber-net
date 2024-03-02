#!/usr/bin/env tarantool

function init()
    box.schema.space.create('dialog')
    box.execute(
        [[
            CREATE TABLE dialog 
            (
                id UNSIGNED PRIMARY KEY AUTOINCREMENT,
                user1_id UNSIGNED,
                user2_id UNSIGNED,
                created DATETIME
            );
        ]])
        box.schema.space.create('dialog')
        box.execute(
            [[
                CREATE TABLE dialogmessage 
                (
                    id UNSIGNED PRIMARY KEY AUTOINCREMENT,
                    dialog_id UNSIGNED,
                    from_user_id UNSIGNED,
                    to_user_id UNSIGNED,
                    content STRING,
                    read BOOLEAN,
                    del_by_sender BOOLEAN,
                    del_by_recipient BOOLEAN,
                    created DATETIME,
                    updated DATETIME
                );
            ]])
    end


box.cfg{listen = 3301}
box.once('init', init)

-------------------------------------------------------------------------------
function dialog_insert(u_id1, u_id2, msg)
    return box.execute(
        [[INSERT INTO dialog VALUES (NULL, ?, ?, now());]], {u_id1, u_id2}
    )
end


function dialog_select(id)
    return box.execute([[SELECT * FROM dialog WHERE id=(?);]], {id})
end

function dialog_select_by_users(u_id1, u_id2)
    return box.execute(
        [[SELECT * FROM dialog WHERE user1_id=(?) and user2_id=(?);]], {u_id1, u_id2}
    )
end

function dialog_select_all()
    return box.execute([[SELECT * FROM dialog;]])
end


function dialog_del(id)
    return box.execute([[DELETE FROM dialog WHERE id=(?);]], {id})
end

-------------------------------------------------------------------------------
function dialmsg_insert(dial_id, u_id1, u_id2, msg)
    return box.execute(
        [[INSERT INTO dialogmessage VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, now(), now());]], 
        {dial_id, u_id1, u_id2, msg, FALSE, FALSE, FALSE, dt, dt}
    )
end


-- function dialmsg_select(u_id1, u_id2, limit, offset)
--     return box.execute([[SELECT * FROM dialogmessage WHERE id=(?);]], {id})
-- end

