# Trading Sandbox Backend

## Quick Start

1. create/config [.env](.env.sample)

2. run docker-compose

   ```bash
   docker compose up
   ```

## Docs

- [mongoengine](http://docs.mongoengine.org/tutorial.html): ORM

## APIs Endpoints

### Auth

- GET: `/api/auth/logout?email=[email]&token=[token]` (not supposed to be, but easier)
- GET: `/api/auth/check?email=[email]&token=[token]`

- Manual

  - POST: `/api/auth/signup`

    ```py
    body = {
      "email": "",
      "username": "",
      "password": "",
      "confirm-password": "",
    }
    ```

  - POST: `/api/auth/login`

    ```py
    body = {
      "email": "",
      "password": "",
    }
    ```

- OAuth

  - GET: `/api/auth/login/google`
  - GET: `/api/auth/login/github`

### Auth - user profile

- GET: `/api/auth/user?email=[email]`
- PUT: `/api/auth/user?email=[email]&token=[token]`

  ```py
  body = {
    "username": "",
    "password": "",
    "confirm-password": "",
  }
  ```

- DELETE: `/api/auth/user?email=[email]&token=[token]`
