# Dr appointment

This is an application for a doctor appointment service.
The user can arrange an appointment:
* manually
* in the first available date.

# Prerequisites:

1. [Python 3.8](https://www.python.org/downloads)<br> 
2. [Postgres Server 12.2](https://www.postgresql.org)<br>
3. [IDE Pycharm Community](https://www.jetbrains.com/pycharm/download)<br>
4. [Git Version Control](https://git-scm.com/downloads)<br>

# Database: 

<span class="pl-c"><span class="pl-c">#</span> In linux environment:</span><br>
sudo -u postgres psql

<span class="pl-c"><span class="pl-c">#</span> Create the database named postgres</span><br>
 postgres=# create database postgres;
 
<span class="pl-c"><span class="pl-c">#</span> Create user named postgres</span><br> 
 postgres=# create user postgres with encrypted password 'root';

<span class="pl-c"><span class="pl-c">#</span> Give all privileges to the user</span><br> 
 postgres=# grant all privileges on database postgres to postgres;
 
# Install application:<br>

<span class="pl-c"><span class="pl-c">#</span> Install files from:</span><br>
https://github.com/Nikitas15/dr_appointment.git 

<span class="pl-c"><span class="pl-c">#</span>Install dependencies writing in command line:</span><br>
$ sudo pip install -r requirements.txt

<span class="pl-c"><span class="pl-c">#</span>Connect to the database In folder groupsw go to settings.py and add:</span><br>
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'root',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

<span class="pl-c"><span class="pl-c">#</span>Add data from the dataset insurance.csv and the library [faker](https://faker.readthedocs.io/en/master) to create last year data. Run filler in command line:</span><br>//  <br>
python run filler.py

<span class="pl-c"><span class="pl-c">#</span>Start django server:</span><br>
python manage.py runserver
