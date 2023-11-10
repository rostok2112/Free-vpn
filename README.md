# TEST VPN WEB APP FOR [SHEEPFISH](https://sheep.fish/) COMPANY

## Tools and installation

Install Docker (for linux):

```bash
sudo apt install apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu focal stable"
sudo apt install docker-ce
sudo systemctl status docker
sudo usermod -aG docker ${USER}
su - ${USER}
```

Or install Docker desktop for windows: [Installation instruction](https://docs.docker.com/desktop/install/windows-install/)

Copy and paste values of .env.example file to .env file and edit it for your purposes:

```bash
cat .env.example > .env
```

## Run

Start application:

```bash
docker compose up -d
```

Open in browser: [Site](http://localhost:8005/)

Or write in adress line `localhost:<port>/` where <port> is a value of PORT in .env

For creating super user (Account with unlimited rights on admin panel):

```bash
docker exec -it free_vpn python /code/manage.py  createsuperuser
```

## Migrations

After any changes in models create and apply migrations:

```bash
docker exec free_vpn  python manage.py makemigrations
docker compose up -d --no-deps --build free_vpn
```

## Optionally(for development purposes)

Install python:

```bash
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.12
python -m pip install --upgrade pip
```

Install pipenv:

```bash
pip install --user pipenv
```

Sync dependencies:

```bash
pipenv sync
```

Run important inventory :

```bash
docker compose -f inventory-compose.yml up -d
```

Sync migrations:

```bash
pipenv run python manage.py migrate
```

Collect static filest to static/ directory:

```bash
pipenv run python manage.py  collectstatic
```

Create super user (Account with unlimited rights on admin panel):

```bash
pipenv run python manage.py  createsuperuser
```

Run app for development purposes:

```bash
pipenv run python manage.py runserver 8005
```


After any changes in models create and apply migrations:

```bash
pipenv run python manage.py makemigrations
pipenv run python manage.py migrate
```

## Additional commands

Delete all containers and flash all trash:

```bash
docker stop $(docker ps -aq) && docker rm $(docker ps -aq) && docker container prune -f
```

Delete all images:

```bash
docker image rm $(docker image ls -q) && docker image prune -af
```
