# Bear Necessities

Bear Necessities is a productivity tool designed to help manage browser tabs efficiently. It incentivizes tab management by providing features like smart tab grouping, productivity scoring, and analytics.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Contributing](#contributing)
- [License](#license)

## Features

- Smart tab grouping by project and task to maintain focus
- Productivity scoring to track tab health over time
- Analytics to identify time-wasting tab habits
- Leaderboard to compete on who has the best tab management

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/netrajosh1/bear-necessities.git
    cd bear-necessities
2. Install the dependencies for the frontend:
    ```sh
    cd my-modern-app
    npm install
    ```

3. Install the dependencies for the backend:
    ```sh
    cd ../server
    pip install -r requirements.txt
    ```

## Usage

1. Start the backend server:
    ```sh
    cd server
    python server.py
    ```

2. Start the frontend development server:
    ```sh
    cd ../my-modern-app
    npm start
    ```

3. Open your browser and navigate to `http://localhost:3000`.

## API Endpoints

### Categorize a Tab

- **URL:** `/categorize`
- **Method:** `POST`
- **Request Body:**
    ```json
    {
        "title": "Tab Title",
        "url": "http://example.com"
    }
    ```
- **Response:**
    ```json
    {
        "output": "category",
        "score": 100
    }
    ```

### Login

- **URL:** `/login`
- **Method:** `POST`
- **Request Body:**
    ```json
    {
        "username": "your_username"
    }
    ```
- **Response:**
    ```json
    {
        "message": "Login successful"
    }
    ```

### Get User Tabs

- **URL:** `/get-usertabs`
- **Method:** `POST`
- **Request Body:**
    ```json
    {
        "username": "your_username"
    }
    ```
- **Response:**
    ```json
    {
        "points": 1000,
        "tabs": [...]
    }
    ```
