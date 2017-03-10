If installed as a server....

run:  service bigredbutton [start|stop|status|reload]


Run manually:

How to run this with gunicorn...

cd /mnt/hgfs/veritashealth/big-red-button-py
source ./brb_env/bin/activate   ## 'deactivate' to exist env

gunicorn --bind=0.0.0.0:8000 --workers=2 --worker-class gevent run:app

# run debug instance from within virtualenv
python run.py


REQUIREMENTS

 - redis

redis server must be installed
 $> yum install redis

python redis lib must be installed in brb_env virtual env ( should already be included )
 (brb_env) $> pip install redis

 - sqlite

( should already be installed )


USER MANAGEMENT

utilities for managing users are in src/app/bigredbutton/database
'brb.db' needs to exist in src/app/bigredbutton/database

to create a new brb database and configure an admin user...

cd src/app/bigredbutton/database
./definedb.py u=[admin_user] p=[admin_pswd]


to list add, update, or delete users for the bigredbutton app...

cd src/app/bigredbutton/database

List Users:
brbadmin.py u=[admin_user] p=[admin_pswd] --list

Add User:
brbadmin.py u=[admin_user] p=[admin_pswd] --add username=[username] password=[password] realname=[real name]

Update User (username):
brbadmin.py u=[admin_user] p=[admin_pswd] --update id=[userid] username=[username]

Update User (any fields other than username)
## update password
brbadmin.py u=[admin_user] p=[admin_pswd] --update id=[userid] password=[password]
## update user realname
brbadmin.py u=[admin_user] p=[admin_pswd] --update username=[username] realname=[realname]

Delete User:
brbadmin.py u=[admin_user] p=[admin_pswd] --delete id=[userid]
brbadmin.py u=[admin_user] p=[admin_pswd] --delete username=[username]
