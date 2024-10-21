# SMILE SALES user microservice
This microservice is primarily designed to handle user-related functionalities within a larger application.<br>
It provides essential features such as user registration, authentication, and management of personal information, delivery addresses, and shopping cart items.

# Key Features
 - User Authentication:
   - Signup: Allows users to create new accounts.
   - Signin: Enables existing users to log in.
   - Password Reset: Provides a mechanism for users to recover their passwords.
   - Email Confirmation: Requires users to verify their email addresses before full account activation.
 - User Profile Management:
   - Read, Update: Users can view and modify their personal information.
 - Delivery Address Management:
   - Create, Read, Update, Delete: Users can manage their delivery addresses for shipping purposes.
 - Recently Viewed Items:
   - View: Users can see a list of items they have recently viewed.
 - Shopping Cart Management:
   - Create, Update, Read, Delete: Users can add, remove, and modify items in their shopping carts.

# Technology Stack
### Programming Languages
[![python](https://img.shields.io/badge/Python-3.11.9-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
### Frameworks
![Static Badge](https://img.shields.io/badge/Django-5.0.2-white?logo=django&labelColor=%23092E20)
![Static Badge](https://img.shields.io/badge/Django_Rest_Framework-3.14.0-black?labelColor=%23C20000)
### Testing Framework
![Static Badge](https://img.shields.io/badge/Unittest-(Python_3.11.9)-blue)
### Databases
![Static Badge](https://img.shields.io/badge/PostgreSQL-16-blue?logo=postgresql&logoColor=white&labelColor=black)
![Static Badge](https://img.shields.io/badge/Redis-8.0-%23FF4438?logo=redis&labelColor=black)
### Email notifications
![Static Badge](https://img.shields.io/badge/Twilio-%23F22F46?style=plastic&logo=twilio&logoColor=white)
### Other libraries
![Static Badge](https://img.shields.io/badge/Dramatiq-1.16.0-black)
![Static Badge](https://img.shields.io/badge/Django_Rest_Framework_Simple_JWT-5.2.2-blue?labelColor=white)
![Static Badge](https://img.shields.io/badge/factory--boy-3.3.0-white?labelColor=black)
![Static Badge](https://img.shields.io/badge/Faker-25.1.0-black?labelColor=blue)
![Static Badge](https://img.shields.io/badge/Gunicorn-23.0.0-white?labelColor=%23328B32)
![Static Badge](https://img.shields.io/badge/AMPQ-5.1.1-white?labelColor=orange)


# Setup
### 1. Clone repository with:
```bash
git clone https://github.com/GhostMEn20034/SM1L3_SAL3S_user_microservice.git
```
### 2. Go to directory with project
### 3. Create .env file:
on Windows (PowerShell), run:
```powershell
New-Item -Path ".env" -ItemType "File"
```
on Unix or MacOS, run:
```bash
touch .env
```
### 4. Open any editor and paste your env variables:
```sh
SUPER_USER_PWD=some_pwd # Postgres user password
SECRET_KEY=some_secret key # Django's secret key
JWT_SIGNING_KEY=some_key # Signing key for JWT Tokens
TWILIO_ACCOUNT_SID=123456 # TWILIO ACCOUND ID
TWILIO_AUTH_TOKEN=123456 # Twilio's token for authentication in twilio
TWILIO_SERVICE_SID_CHANGE_EMAIL=123456 # Service ID for sending emails when the user wants to change an email
TWILIO_SERVICE_SID_SIGNUP_CONFIRMATION=123456 # Service ID for sending emails when the user need to confirm an email address
TWILIO_SERVICE_SID_PASSWORD_RESET=123456 # Service ID for sending emails when the user need to reset a password
DEBUG=0_or_1 # Determines whether the debug mode turned on (1 - on, 0 - off)
ALLOWED_HOSTS=localhost,127.0.0.1,[::1] # Your allowed hosts
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000 # Allowed CORS Origins
CORS_ORIGIN_WHITELIST=http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001 # CORS White list
SQL_ENGINE=django.db.backends.postgresql # DB Engine
SQL_DATABASE=smile_sales_users # Database Name
SQL_USER=smile_sales_usr # Database Owner
SQL_PASSWORD=xxxx4444 # DB user's password
SQL_HOST=db # Database host
SQL_PORT=5432 # Database Port
SQL_CONN_MAX_AGE=60 # Maximum Connection's age
DB_SSL_MODE=0_or_1 # Determines whether SSL mode is enabled in DB connection (0 - disabled, 1 - enabled)
DRAMATIQ_BROKER_URL=redis_url # Redis url for dramatiq worker
DRAMATIQ_CRONTAB_BROKER_URL=redis_url # Redis url for dramatiq worker
DRAMATIQ_RESULT_BACKEND_URL=redis_url # Redis url for dramatiq worker
FLUSH_EXPIRED_TOKEN_PERIOD_HOURS=1 # How often expired tokens will be cleaned
DELETE_INACTIVE_CARTS_PERIOD_DAYS=1 # How often inactive carts will be deleted
AMPQ_CONNECTION_URL=url_rabbit_mq # URL for message broker
PRODUCT_CRUD_EXCHANGE_TOPIC_NAME=product_replication # Just copy that
USERS_DATA_CRUD_EXCHANGE_TOPIC_NAME=users_data_replication # Just copy that
ORDER_PROCESSING_EXCHANGE_TOPIC_NAME=order_processing_replication # Just copy that
```


# Running The app
If you want to run this app you have two options:
 - Run it using `docker-compose`
 - Run it using `k8s`

### 1. Running using `docker-compose`
#### 1.1 Add a permission to execute the `init-database.sh` file inside the docker-compose's Postgres service:
```bash
chmod +x init-database.sh
```
#### 1.2 Enter the command below to run the app with `docker-compose`:
```bash
docker compose up -d --build
```
#### 1.3 Go to [localhost:8000](http://localhost:8000) or [127.0.0.1:8000](http://127.0.0.1:8000) and use the API.

### 2. Running using Kubernetes resources in development environment
**Note: If you want to run this API using Kubernetes, you need to create and expose Postgres and Redis servers manually**
#### 2.1 Create a kubernetes namespace:
```bash
kubectl create namespace smile-sales-users
```
#### 2.2 Create an object with type secret from `.env` file:
```bash
kubectl create secret generic web-secrets --from-env-file=.env
```
#### 2.3 Go to directory with k8s resources:
```bash
cd k8s/dev
```
#### 2.4 Apply config maps:
```bash
kubectl apply -f config-maps/
```
#### 2.5 Apply persistent volumes:
```bash
kubectl apply -f persistent-volumes/
```
#### 2.6 Apply persistent volume claims:
```bash
kubectl apply -f persistent-volume-claims/
```
#### 2.7 Run jobs to complete migrations and collect static files:
```bash
kubectl apply -f jobs/
```
#### 2.8 Wait until jobs are completed, you can check whether they are completed with command:
```bash
kubectl get jobs
```
#### 2.9 Apply services:
```bash
kubectl apply -f services/
```
#### 2.10 Apply deployments:
```bash
kubectl apply -f deployments/
```
### 3. Running using Kubernetes resources in production on GKE server
You need to perform identical steps as in the development environment.<br>
But, there's a few nuances:
 - You need to use k8s resources from `k8s/production` directory
 - GCS Fuse bucket is required (it used as a storage for static files)
 - At the end of `k8s/production/persistent-volumes/staticfiles-pv-user-microservice.yaml` file, paste your bucket's name (see "volumeHandle" key)
 - Make sure that your kubernetes service account `gke-user` (If it's not created, create one) is bound to gcp service account which has "StorageAdmin" role and has access to the created bucket

# Run Tests
**POV: make sure you're in the default directory**<br><br>
To run tests you need to complete 3 steps:
1. Run the test app with another `docker-compose` file:
```bash
docker compose -f docker-compose-test-env.yaml up -d
```
2. Run the command below:
```bash
docker compose exec web python manage.py test -v 2
```
3. Shutdown `docker-compose` services:
```bash
docker compose -f docker-compose-test-env.yaml down
```


