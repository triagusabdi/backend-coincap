# JSON REST API Coincap Using FastAPI

To get started:

## Clone the repository

    https://github.com/triagusabdi/backend-coincap.git

## Run to Create a virtual environment

    python -m venv venv

## To Activate a virtual environment

    venv\Scripts\activate

## Install Requirements

    pip install -r requirements.txt

## Run FastAPI application 

    uvicorn main:app --reload

# REST API


## SignUp

### Request

    POST http://127.0.0.1:8000/sign_up/

### Body raw

    {
      "email": "agus22@agus.asdcom",
      "password": "password",
      "confirm_password": "password"
    }

### Response

    {
        "message": "user successfully registered",
        "id": 13,
        "email": "agus22@agus.asdcom",
        "password": "$2b$12$E5.hNwThEEXszt07JxolI.s6tdhSzM3O29fc6sfssSf1ScBMe65we"
    }

## SignIn

### Request

    POST http://127.0.0.1:8000/signin

### Body raw

    {
      "email": "admin",
      "password": "admin"
    }

### Response

    {
        "message": "user successfully signin",
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTcwNDczNjY2OH0.cH9yISS0bqfTvA70PUPDFagfBeaLTJ2RWctNMVPpxJI",
        "token_type": "bearer",
        "ver": {
            "sub": "admin",
            "exp": 1704736668
        }
    }

## SignOut

### Request

    DELETE http://127.0.0.1:8000/signout

### Headers
    
    Authorization: Bearer {token}
    example:

    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTcwNDczNjIxNX0.QE_nH6oN_XyAkW2b5Tmdiw_gZfZRBfKTRVaRVH5gwnY

### Response

    {
        "message": "user successfully signout",
        "user": "admin"
    }

## List Tracked Coins

### Request 

    GET http://127.0.0.1:8000/tracked_coins/

### Headers
    
    Authorization: Bearer {token}
    example:

    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTcwNDczNjIxNX0.QE_nH6oN_XyAkW2b5Tmdiw_gZfZRBfKTRVaRVH5gwnY

### Response

    {
        "message": "Data Restored Successful",
        "user": "admin",
        "data": [
            {
                "name": "Bitcoin",
                "priceIdn": "Rp654.089.056,08"
            },
            {
                "name": "Ethereum",
                "priceIdn": "Rp32.983.872,99"
            }, ...


## Add Coin

### Request 

    POST http://127.0.0.1:8000/add_coin/

### Headers
    
    Authorization: Bearer {token}
    example:

    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTcwNDczNjIxNX0.QE_nH6oN_XyAkW2b5Tmdiw_gZfZRBfKTRVaRVH5gwnY

### Body raw

    {
      "name": "Agus",
      "priceIdn": 10000
    }

### Response

    {
        "message": "Coin Added",
        "name": "Agus",
        "priceIdn": 10000.0,
        "user": "admin"
    }

## Remove Coin

### Request 

    DELETE http://127.0.0.1:8000/remove_coin/

### Headers
    
    Authorization: Bearer {token}
    example:

    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTcwNDczNjIxNX0.QE_nH6oN_XyAkW2b5Tmdiw_gZfZRBfKTRVaRVH5gwnY

### Body raw

    {
      "name": "Agus"
    }

### Response

    {
        "message": "Coin Removed",
        "name": "Agus",
        "user": "admin"
    }

## Restored Tracked Coins

### Request 

    GET http://127.0.0.1:8000/refresh_db/

### Headers
    
    Authorization: Bearer {token}
    example:

    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTcwNDczNjIxNX0.QE_nH6oN_XyAkW2b5Tmdiw_gZfZRBfKTRVaRVH5gwnY

### Response

    {
        "message": "Data Restored Successful",
        "data": [
            {
                "name": "Bitcoin",
                "priceIdn": "Rp685.518.746,66"
            },
            {
                "name": "Ethereum",
                "priceIdn": "Rp34.640.387,92"
            },

# TESTS
API tested using Postman

## SignUp
    PASS    Response status code is 200
    PASS    Response has the required fields
    PASS    Email is in a valid format
    PASS    Password meets the required criteria
    PASS    Content-Type header is application/json

## Signin
    PASS    Response status code is 200
    PASS    Response has the required fields
    PASS    Access token is a non-empty string
    PASS    Ver object is present and contains expected fields
    PASS    Expiration time is in a valid date format

## Signout
    PASS    Response status code is 200
    PASS    Response has the required fields - message and user
    PASS    Message is a non-empty string
    PASS    User is a non-empty string
    PASS    Content-Type header is application/json

## List Tracked Coins
    PASS    Response status code is 200
    PASS    Response has the required fields - message, user, and data
    PASS    Name and priceIdn are non-empty strings
    PASS    Content-Type is application/json
    PASS    Data array is present and contains at least one element

## Add Coins
    PASS    Response status code is 200
    PASS    Response has the required fields
    PASS    Name is a non-empty string
    PASS    PriceIdn is a non-negative integer
    PASS    User is not null or empty string

## Remove Coins
    PASS    Response status code is 200
    PASS    Response has the required fields - message, name, and user
    PASS    Name is a non-empty string
    PASS    User field should not be null or empty
    PASS    Content-Type header is application/json
