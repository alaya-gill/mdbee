django-synergy
===============

Django Synergy environment:

.. image:: https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg
     :target: https://github.com/pydanny/cookiecutter-django/
     :alt: Built with Cookiecutter Django

.. image:: https://img.shields.io/badge/environment-ubuntu%2019.04-blue
     :target: https://ubuntu.com/
     :alt: Ubuntu 19.04

.. image:: https://img.shields.io/badge/python-3.7-green
     :target: https://www.python.org/downloads/release/python-370/
     :alt: Ubuntu 19.04

.. image:: https://img.shields.io/badge/postgres-12.1-lightgrey
     :target: https://www.postgresql.org/docs/12/release-12-1.html
     :alt: Ubuntu 19.04

Dev Setup Notes
---------------


 1. Install python3.7, postgresql 12.1 and redis on Ubuntu 19.04

 1.1 Redis
```sudo apt update
sudo apt install redis-server```;
 1.2 Confirm redis is running 
```sudo systemctl status redis-server```;


 2. Setup postgresql, create user and database
```CREATE USER 'synergy' with encrypted password 'synergy';
```CREATE DATABASE synergy WITH OWNER synergy ENCODING 'UTF8' LC_COLLATE = 'en_US.UTF-8' LC_CTYPE = 'en_US.UTF-8';```
```GRANT ALL PRIVILEGES ON DATABASE synergy to synergy;```

 3. Create and activate virtualenv outside the repository folder
```
python3 -m venv venv_mdbee
source venv_mdbee/bin/activate```

 4. Install requirements
```pip install -r requirements/local.txt```

 5. Run migrations
```./manage.py migrate```
Server is now running on localhost:8000

 6. Run server  
 
 ```./manage.py runserver```
 
 Application creates a MDBee Admin login during migration using the following credentials:  
    - email: synergy.cloud.MDBee@gmail.com
    - password: ************

Password will be provided on a need to know basis.

7. Populate initial database

```./manage.py populate_countries```

8. Setup the Django Site

Update the domain to  'localhost:8000' and name to 'Dental Bee' in django_site table

Settings
--------

If introducing new settings variables that can be set from the environment, remember to prefix the environment variable name with DJANGO_ to make it play well with scripts that generate the required environment.

Moved to settings_.

.. _settings: http://cookiecutter-django.readthedocs.io/en/latest/settings.html



Basic Commands
--------------

1. Create Migrations
```./manage.py makemigrations <app_name>```

2. Run Migrations
```./manage.py migrate <app_name>```

3. Django Shell or Shell Plus
```./manage.py shell```
```./manage.py shell_plus```

Docker Setup Notes
------------------

Install Docker & Docker Engine

1. Older versions of Docker were called docker, docker.io , or docker-engine. If these are installed, uninstall them:

sudo apt-get remove docker docker-engine docker.io containerd runc


2. sudo apt-get update

3. Install packages to allow apt to use a repository over HTTPS:

sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common


4. Add Docker’s official GPG key:

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -


5. Verify that you now have the key with the fingerprint 9DC8 5822 9FC7 DD38 854A E2D8 8D81 803C 0EBF CD88

sudo apt-key fingerprint 0EBFCD88

6. Use the following command to set up the stable repository.

sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"

7. sudo apt-get update


8. Install the latest version of Docker Engine - Community and containerd

sudo apt-get install docker-ce docker-ce-cli containerd.io

9. Test Docker

sudo docker run hello-world




Install Docker Compose

1. Download latest stable release binary

sudo curl -L "https://github.com/docker/compose/releases/download/1.25.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

2. Apply executable permission to the binary:

sudo chmod +x /usr/local/bin/docker-compose

3. Test docker compose

docker-compose --version




Install Docker Machine


1. Download Docker Machine and extract it to your PATH:

base=https://github.com/docker/machine/releases/download/v0.16.0 &&
  curl -L $base/docker-machine-$(uname -s)-$(uname -m) >/tmp/docker-machine &&
  sudo mv /tmp/docker-machine /usr/local/bin/docker-machine &&
  chmod +x /usr/local/bin/docker-machine

2. Test docker machine

docker-machine version



Setup Django Backend with Docker

1. Clone Django Synergy Repository

git clone https://gitlab.com/hasnain095/django-syergy.git

1. Create Docker host within root of your Djnago Project (have to install virtual box)

docker-machine create --driver virtualbox dev
eval $(docker-machine env dev)


2. View Docker Machines, and its IP

docker-machine ls
docker-machine ip dev


3. Fire up everything

docker-compose -f local.yml build
docker-compose -f local.yml up

4. Test Django is running

docker-compose -f local.yml run django python manage.py makemigrations
docker-compose -f local.yml run django python manage.py migrate
docker-compose -f local.yml run django python manage.py createsuperuser

5. Django is running on your localhost port 8000

