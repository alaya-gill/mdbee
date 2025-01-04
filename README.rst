MDBEE
===============

MDBEE environment:

* ` git clone https://github.com/alaya-gill/mdbee.git `

Dev Setup Notes
---------------


 1. Install python3.8.19 using PYENV, postgresql 14.13 and redis on Linux
     Pyenv managing multiple python versions: https://realpython.com/intro-to-pyenv/

 1.1 Redis
     For UBUNTU
```sudo apt update
sudo apt install redis-server```;
 1.2 Confirm redis is running 
```sudo systemctl status redis-server```;

     For MacOS
```brew update
brew install redis```;
 1.3 Start redis 
```brew services start redis```;


 2. Setup postgresql and createsuperuser
 Add Database configurations in config/settings/base.py
```DATABASES = {

    'default': {

        'ENGINE': 'django.db.backends.postgresql_psycopg2',

        'NAME': <name>,

        'USER': <USER>,

        'PASSWORD': <PASSWORD>,

        'HOST': 'localhost',

        'PORT': '5432',

    }

}````

Go to directory where manage.oy file is located and run in terminal:
``` ./manage.py createsuperuser ```

Make sure to activate and put is_staff=True superuser using localhost:8000/admin url

 3. Create and activate virtualenv outside the repository folder
```
pyenv install 3.8.19
pyenv local 3.8.19
pyenv virtualenv 3.8.19 <environment_name>

# Load pyenv automatically
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

pyenv activate <environment_name>

```

 4. Install requirements
```pip install -r requirements/local.txt```

 5. Run migrations
```./manage.py migrate```

 6. Run server  
 
 ```./manage.py runserver```
 

7. Populate initial database

```./manage.py populate_countries```


Basic Commands
--------------

1. Create Migrations
```./manage.py makemigrations <app_name>```

2. Run Migrations
```./manage.py migrate <app_name>```

3. Django Shell or Shell Plus
```./manage.py shell```
```./manage.py shell_plus```

Frontend Setup (Vite + Reactjs)
------------------

Go to folder Frontend (cd Frontend)

1. Install Dependencies

1.1 npm install

2.Development

2.2 npm run dev
The application will be available at http://localhost:5173.


