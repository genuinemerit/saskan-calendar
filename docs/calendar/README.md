# mint

A simple interactive CLI and web app to manage calendrical and astronomical calculations for an RPG called Saskantinon.
It is a Gunicorn-driven Flask (Python, Jinja2) web app.

## Setup in Development Environment

Note: the following is boilerplate. Currently in pre-development status.

### 🔧 Step 0: Define the environment

- Install poetry, then use poetry to pull in remaining dependencies and
generate pyproject.toml file.

- Clone the project from github.

### 🔧 Step 1: Run the Flask CLI command to create the database

Before using the application, you need to create the database.
In development it is a SQLlite database.
From the project root, run:

```sh
poetry run mint create_db
```

#### 🔧 Step 2: Run the Flask CLI command to create an admin

Before using the application, you also need to create the first admin user.
From the project root, run:

```sh
poetry run mint create_admin
```

##### 🔧 Step 3: Start up the mint web app

From the project root, run:

```sh
poetry run mint run
```

## Setup in Deployed Environment

1. Configure PostgreSQL database, accounts, privileges.
2. Configure NGINX as proxy server for the Gunicorn-driven Flask app.
3. Configure certbot to generate certificates support HTTPS.
4. Configure systemd unit service to handle app start, restart.
