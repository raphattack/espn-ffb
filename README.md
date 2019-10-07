# espn-ffb

espn-ffb is a project to query fantasy football data from ESPN's API and persist it in your own database. There is a very basic web component with a few views built using Flask that allows you to self-host your own fantasy football league page.

Until all [raw SQL is converted to ORM](https://github.com/raphattack/espn-ffb/issues/1), this will only work with PostgreSQL, but you can modify the queries in [query.py](espn_ffb/db/query.py) to work with other databases supported by [SQLAlchemy](https://docs.sqlalchemy.org/en/13/core/engines.html).

#### Sample views:
- Recap - [desktop](sample/images/recap-desktop.png), [mobile](sample/images/recap-mobile.png)
- Standings - [desktop](sample/images/standings.png)
- Head-to-head records - [mobile](sample/images/h2h-records.png)
- Matchup history - [mobile](sample/images/matchup-history.png)
- Playoffs - [desktop](sample/images/playoffs.png)

# Setup

Two modes are supported:
* Run with Docker (easiest)
* Run locally (requires PostgreSQL instance)

# Pre-requisites:

### Run with Docker
- [Docker](https://docs.docker.com/compose/install/)

### Run locally
- [Python3](https://www.python.org/download/releases/3.0/)
- [PostgreSQL](https://www.postgresql.org/download/)
- [uWSGI](https://uwsgi-docs.readthedocs.io/en/latest/Install.html) (optional, but recommended if running in production)

# Config:

Edit [config.py](espn_ffb/config.py) with your own:

- Database credentials in `DevConfig` and `ProdConfig`.
- `LEAGUE_ID`
- `swid` (private leagues)
- `espn_s2` (private leagues)

To find your `swid` and `espn_s2` in Chrome, go to **DevTools > Application > Cookies >** https://fantasy.espn.com.

# Run with Docker

### Set up .env file
```bash
cp .env.sample .env
```

Edit `.env` and replace `POSTGRES_PASSWORD` with your preferred password.

### Run
```bash
docker-compose up -d
```

Open browser to http://localhost:5000.

### Set up database
To set up the database the first time, you can run the following command:
```bash
docker-compose run web sh ./setup.sh
```

### Update
```bash
docker-compose run web sh ./update.sh
```

If you are running with Docker, stop here.

# Run locally

### Requirements:
```
pip3 install -r requirements.txt
```

### Set up database:
```bash
python3 -m espn_ffb.setup -e {dev|prod}
```

### Run:
```bash
# run with python3
python3 -m espn_ffb.app -e {dev|prod}

# run with uwsgi
uwsgi --http 0.0.0.0:5000 --ini conf/espn-ffb-{dev|prod}.ini
```

Open browser to http://localhost:5000.

### Update:
```bash
python3 -m espn_ffb.db.update -e {dev|prod}
```

# Deploy as Debian package

### Build:
```bash
./gradlew clean build buildDeb -PbuildNumber=local
```

### Install:
```bash
sudo dpkg -i build/distributions/espn-ffb*.deb
```

The `.deb` package includes two `.service` files:
- `espn-ffb.service`: Starts espn-ffb Flask app
- `espn-ffb-update.service`: Updates espn-ffb database

# Recaps:

Sample [recap templates](espn_ffb/templates/recap/2018/2) as an example of how to structure written recaps.

### Generate a new blank recap template:
```bash
python3 -m espn_ffb.scripts.generate_recap -e {dev|prod} -y {year} -w {week}
```

# Contributors

* [yorch](https://github.com/yorch) - Thank you for the Docker support!
