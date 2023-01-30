# Trading Sandbox APIs

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

- Manual

  - POST: `/api/auth/signup`

    ```json
    {
      "email": "",
      "username": "",
      "password": "",
      "confirm-password": ""
    }
    ```

  - POST: `/api/auth/login`

    ```json
    {
      "email": "",
      "password": ""
    }
    ```

- OAuth

  - GET: `/api/auth/login/google`
  - GET: `/api/auth/login/github`

### Auth - user profile

- GET: `/api/auth/user?email=[email]`
- PUT: `/api/auth/user?email=[email]&token=[token]`

  ```json
  {
    "username": "",
    "password": "",
    "confirm-password": ""
  }
  ```

- DELETE: `/api/auth/user?email=[email]&token=[token]`

### Trading

- POST: `/api/trading/order?email=[email]&token=[token]` (create order, execute if status=="finished")

  ```json
  {
    "status": "",
    "flag": "",
    "pair_symbol": "",
    "input_amount": 0,
    "output_amount": 0
  }
  ```

- DELETE: `/api/trading/order?email=[email]&token=[token]` (cancel non-finished order)

  ```json
  {
    "order_id": 0
  }
  ```

- POST: `/api/trading/trigger?email=[email]&token=[token]` (create trigger, and its order as draft)

  ```json
  {
    "flag": "",
    "pair_symbol": "",
    "input_amount": 0,
    "output_amount": 0,
    "stop_price": 0
  }
  ```

- DELETE: `/api/trading/trigger?email=[email]&token=[token]` (delete trigger, and its non-finished order)

  ```json
  {
    "trigger_id": 0
  }
  ```

### Info

- GET: `/api/info/pairs`
- GET: `/api/info/orders`

### Service

- POST: `/api/service/update_market`

  ```json
  {
    "pair_symbol": "",
    "price": 0
  }
  ```
