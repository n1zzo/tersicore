# MusicLibrary

## Setup

These are the instruction for deploying musicLibrary on an nginx environment.
You will need python3, nginx, uwsgi and python3-virtualenv.
Clone latest project tree from master branch:

    git clone https://github.com/n1zzo/musicLibrary

Inside the cloned directory create a new python virtualenv, and activate it:

    cd musicLibrary
    virtualenv tersicore_venv
    source ./tersicore_venv/bin/activate

Install the required dependencies and exit virtualenv:

    pip install -r requirements.txt
    deactivate

To bind tersicore at the URL root of nginx add this to nginx.conf:

    location / { try_files $uri @tersicore;  }
    location @tersicore {
        include uwsgi_params;
        uwsgi_pass unix:/tmp/tersicore.sock;
    }

To bind it at /tersicore use this configuration instead:

    location = /tersicore { rewrite ^ /tersicore/;  }
    location /tersicore { try_files $uri @tersicore;  }
    location @tersicore {
        include uwsgi_params;
        uwsgi_pass unix:/tmp/tersicore.sock;
    }

Set the nginx worker process user as the one you use to run uwsgi:

    user user [group];

After the configuration and database building, you can run tersicore with:

    uwsgi --ini docs/uwsgi/tersicore_rest.ini

## Configuration

Tersicore can configured with two files:

- tersicore.conf
- logging.conf

The first one defines the database parameters and the paths to be scanned
for music files.

There are two example configuration files, one for a MySQL-based setup:

    cp docs/config/tersicore_mysql.conf tersicore.conf

And another one for SQLite-based setup:

    cp docs/config/tersicore_sqlite.conf tersicore.conf

Just copy one of them and customize it as needed.

Logging format and options are defined in logging.conf.
Two example configuration files are provided, either for debug use:

    cp docs/config/logging_debug.conf logging.conf

Or production use:

    cp docs/config/logging_production.conf logging.conf

Just choose the one that fits your needs.
