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

    ```json
    body = {
      "email": "",
      "username": "",
      "password": "",
      "confirm-password": "",
    }
    ```

  - POST: `/api/auth/login`

    ```json
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

  ```json
  body = {
    "username": "",
    "password": "",
    "confirm-password": "",
  }
  ```

- DELETE: `/api/auth/user?email=[email]&token=[token]`

### Trading

- POST: `/api/trading/order?email=[email]&token=[token]` (create order, execute if status=="finished")

  ```json
  body = {
    "status": "",
    "type": "",
    "pair_symbol": "",
    "input_token": "",
    "input_amount": 0,
    "output_token": "",
    "output_amount": 0,
  }
  ```

- DELETE: `/api/trading/order?email=[email]&token=[token]` (cancel non-finished order)

  ```json
  body = {
    "order_id": 0,
  }
  ```

- POST: `/api/trading/trigger?email=[email]&token=[token]` (create trigger, and its order as draft)

  ```json
  body = {
    "type": "",
    "pair_symbol": "",
    "input_token": "",
    "input_amount": 0,
    "output_token": "",
    "output_amount": 0,
    "stop_price": 0,
    "limit_price": 0
  }
  ```

- DELETE: `/api/trading/trigger?email=[email]&token=[token]` (delete trigger, and its non-finished order)

  ```json
  body = {
    "trigger_id": 0,
  }
  ```
