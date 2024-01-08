from fastapi import FastAPI, HTTPException, Depends
from models import Item, SignUp, Login, Tracker, TrackerDelete
import sqlite3
import bcrypt
from typing import List
import secrets
import jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
import requests
import locale

app = FastAPI()

DATABASE_FILE = "data.db"

locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8')

def get_database_connection():
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        print("Connected")
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to the database: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


SECRET_KEY = secrets.token_urlsafe(32)
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_jwt_token(data: dict, expires_delta: timedelta):
    expire = datetime.utcnow() + expires_delta
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_jwt_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def authenticate_token(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=401,
            detail=f"Failed to authenticate token. Error: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return email


def get_exchange_rate():
    exchange_rate = 15000
    return exchange_rate


def insert_tracked_coins(conn, tracked_coins):
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM tracked_coins")
        exchange_rate = get_exchange_rate()
        for coin in tracked_coins:
            cursor.execute(
                "INSERT INTO tracked_coins (id, name, priceIdn) VALUES (?, ?, ?)",
                (
                    coin["id"],
                    coin["name"],
                    float(coin.get("priceUsd", 0)) * exchange_rate,
                ),
            )

        conn.commit()
    except sqlite3.Error as e:
        print(f"Error inserting tracked coins: {e}")
        conn.rollback()


@app.get("/")
def read_root():
    return {"Hello": "World", "Hello": "World"}


@app.get("/user_list", response_model=List[Item])
def read_item():
    conn = get_database_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM user")
        results = cursor.fetchall()
        if not results:
            raise HTTPException(status_code=404, detail="User not found")
        return [
            {"id": result[0], "email": result[1], "password": result[2]}
            for result in results
        ]
    except sqlite3.Error as e:
        print(f"Error executing SQL query: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        conn.close()


@app.post("/sign_up/", response_model=Item)
def sign_up(item: SignUp):
    if item.password != item.confirm_password:
        raise HTTPException(
            status_code=400, detail="Password and confirm_password do not match"
        )
    conn = get_database_connection()
    cursor = conn.cursor()
    try:
        hashed_password = bcrypt.hashpw(item.password.encode("utf-8"), bcrypt.gensalt())
        cursor.execute(
            "INSERT INTO user (email, password) VALUES (?, ?)",
            (
                item.email,
                hashed_password,
            ),
        )
        conn.commit()

        new_item_id = cursor.lastrowid

        cursor.execute(
            "SELECT id, email, password FROM user WHERE id=?", (new_item_id,)
        )
        result = cursor.fetchone()

        return {"id": result[0], "email": result[1], "password": result[2]}
    except sqlite3.Error as e:
        print(f"Error executing SQL query: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        conn.close()


@app.post("/login/", response_model=dict)
def login(item: Login):
    conn = get_database_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id, email, password FROM user WHERE email=?", (item.email,)
        )
        result = cursor.fetchone()

        if not result or not bcrypt.checkpw(item.password.encode("utf-8"), result[2]):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        access_token_expires = timedelta(minutes=15)
        access_token = create_jwt_token(
            data={"sub": item.email}, expires_delta=access_token_expires
        )
        ver = verify_jwt_token(access_token)

        return {
            "message": "Login Success",
            "access_token": access_token,
            "token_type": "bearer",
            "ver": ver,
        }
    except sqlite3.Error as e:
        print(f"Error executing SQL query: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        conn.close()


@app.delete("/logout/")
def logout(
    current_user: str = Depends(authenticate_token),
):
    return {"message": "Logout success", "user": current_user}

@app.get("/tracked_coins/", response_model=dict)
def list_tracked_coins(current_user: str = Depends(authenticate_token)):
    conn = get_database_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM tracked_coins")
        results = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error executing SQL query: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        conn.close()
    
    return {
        "message": "Data Restored Successful",
        "user": current_user,
        "data": [
            {"name": result[0], "priceIdn": locale.currency(result[1], grouping=True)}
            for result in results
        ],
    }

@app.get("/refresh_db/", response_model=dict)
def refresh_tracked_db(current_user: str = Depends(authenticate_token)):
    url = "https://api.coincap.io/v2/assets"
    response = requests.get(url)

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code, detail="Failed to fetch tracked coins"
        )

    data = response.json().get("data", [])

    conn = get_database_connection()
    cursor = conn.cursor()
    insert_tracked_coins(conn, data)

    cursor.execute("SELECT * FROM tracked_coins")
    results = cursor.fetchall()
    conn.close()

    return {
        "message": "Data Restored Successful",
        "data": [
            {"name": result[0], "priceIdn": locale.currency(result[1], grouping=True)}
            for result in results
        ],
    }


@app.post("/add_coin/", response_model=dict)
def add_coin(item: Tracker, current_user: str = Depends(authenticate_token)):
    conn = get_database_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO tracked_coins (name, priceIdn) VALUES (?, ?)", (item.name,item.priceIdn,)
        )
        
        conn.commit()
        return {
            "message": "Coin Added",
            "name": item.name,
            "priceIdn": item.priceIdn,
            "user": current_user
        }
    except sqlite3.Error as e:
        print(f"Error executing SQL query: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        conn.close()

@app.delete("/remove_coin/", response_model=dict)
def remove_coin(item: TrackerDelete, current_user: str = Depends(authenticate_token)):
    conn = get_database_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "DELETE FROM tracked_coins WHERE name=?", (item.name,)
        )

        conn.commit()
        return {
            "message": "Coin Removed",
            "name": item.name,
            "user": current_user
        }
    except sqlite3.Error as e:
        print(f"Error executing SQL query: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        conn.close()
