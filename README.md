# Project 6 – Brevet Time Calculator REST Service

Author: Leon Wong  
Email: tatwingw@uoregon.edu 

This project exposes brevet control times stored in MongoDB as a RESTful API, and provides a simple web consumer that interacts with the API.  
The data model and MongoDB collection are based on Project 5 (brevet time calculator with MongoDB).

---

## 1. Repository Structure

Only the relevant parts for this project are shown:

```text
proj6-rest/
├── DockerRestAPI/
│   ├── docker-compose.yml
│   ├── laptop/              # Flask REST API service
│   │   ├── Dockerfile
│   │   ├── api.py
│   │   ├── acp_times.py     # From Project 5 (not used directly by the API)
│   │   └── requirements.txt
│   └── website/             # Consumer (PHP)
│       ├── Dockerfile
│       └── index.php
├── data-samples/            # Example brevet data
│   ├── sample-data.json
│   ├── sample-data.csv
│   └── sample-data-pivoted.csv
├── README.md
```

- **`laptop/api.py`**  
  Flask / Flask-RESTful application that connects to MongoDB and implements the required endpoints:
  - `/listAll`
  - `/listOpenOnly`
  - `/listCloseOnly`
  - `/health` (health check)

- **`website/index.php`**  
  PHP consumer UI that calls the API and displays JSON or CSV results.

---

## 2. Docker Services

`DockerRestAPI/docker-compose.yml` defines three services.

### 2.1 `db` – MongoDB

- Image: `mongo:4.4`  
- Container name: `brevet-mongodb`  
- Exposes MongoDB on host port `27017` → `mongodb://localhost:27017/`  
- Database: `brevets_db`  
- Collection: `controls`

### 2.2 `laptop` – API Service

- Build context: `./laptop`  
- Image name: `dockerrestapi-laptop`  
- Runs `api.py` (Flask-RESTful)  
- Listens inside the container on port `5000`  
- Mapped to host port `5001`  
  → Base URL from host: `http://localhost:5001`  
- Connects to MongoDB using the Docker service name: `mongodb://db:27017/`

### 2.3 `website` – Consumer

- Build context: `./website`  
- Image name: `dockerrestapi-website`  
- Based on `php:7.4-apache`  
- Serves `index.php` via Apache  
- Listens inside the container on port `80`  
- Mapped to host port `8080`  
  → URL from host: `http://localhost:8080`  
- Calls the API using the service name `laptop` (for example `http://laptop:5000/...`)

---

## 3. How to Build and Run

### 3.1 Prerequisites

- Docker Desktop (or Docker Engine) installed  
- `docker compose` command available

### 3.2 Start the System

Open a terminal:

```bash
cd /path/to/proj6-rest/DockerRestAPI
docker compose up --build
```

This command:

- Builds the images for `laptop` and `website`
- Starts the containers:
  - `brevet-mongodb` (MongoDB)
  - `brevet-laptop` (Flask API)
  - `brevet-website` (PHP consumer)

In another terminal, you can check their status:

```bash
cd /path/to/proj6-rest/DockerRestAPI
docker compose ps
```

Example output:

```text
NAME             SERVICE   STATUS          PORTS
brevet-laptop    laptop    Up              0.0.0.0:5001->5000/tcp
brevet-mongodb   db        Up              0.0.0.0:27017->27017/tcp
brevet-website   website   Up              0.0.0.0:8080->80/tcp
```

### 3.3 Stop the System

From the same directory:

```bash
docker compose down
```

---

## 4. Data Model

The `controls` collection in `brevets_db` contains one document per control point, with fields such as:

- `brevet_distance` – total distance of the brevet (for example 200, 1000)
- `begin_date` – brevet start date
- `begin_time` – brevet start time
- `km` – control distance in kilometers
- `miles` – control distance in miles
- `location` – control location description
- `open` – control open time as a string
- `close` – control close time as a string

These documents are created by the Project 5 application or loaded from sample data.

---

## 5. REST API Endpoints

Base URL from the host: `http://localhost:5001`  
Internally (from other containers), the API is available at `http://laptop:5000`.

If the database is empty, the list endpoints return:

```json
{ "message": "No data available" }
```

### 5.1 `/listAll`

Returns both open and close times.

- JSON:

  ```http
  GET /listAll/json
  ```

  Example response:

  ```json
  {
    "open_times": [
      { "km": 0, "miles": 0, "location": "begin", "open": "12/01/2021 18:06" },
      { "km": 100, "miles": 62, "location": null, "open": "12/01/2021 21:02" }
    ],
    "close_times": [
      { "km": 0, "miles": 0, "location": "begin", "close": "12/01/2021 19:06" },
      { "km": 100, "miles": 62, "location": null, "close": "12/02/2021 00:46" }
    ]
  }
  ```

- CSV:

  ```http
  GET /listAll/csv
  ```

  Example format:

  ```csv
  km,miles,location,open_time,close_time
  0,0,begin,12/01/2021 18:06,12/01/2021 19:06
  100,62,,12/01/2021 21:02,12/02/2021 00:46
  ```

### 5.2 `/listOpenOnly`

Returns only open times.

- JSON:

  ```http
  GET /listOpenOnly/json
  ```

  Example response:

  ```json
  [
    { "km": 0, "miles": 0, "location": "begin", "open": "12/01/2021 18:06" },
    { "km": 100, "miles": 62, "location": null, "open": "12/01/2021 21:02" }
  ]
  ```

- CSV:

  ```http
  GET /listOpenOnly/csv
  ```

  Example format:

  ```csv
  km,miles,location,open_time
  0,0,begin,12/01/2021 18:06
  100,62,,12/01/2021 21:02
  ```

### 5.3 `/listCloseOnly`

Returns only close times.

- JSON:

  ```http
  GET /listCloseOnly/json
  ```

  Example response:

  ```json
  [
    { "km": 0, "miles": 0, "location": "begin", "close": "12/01/2021 19:06" },
    { "km": 100, "miles": 62, "location": null, "close": "12/02/2021 00:46" }
  ]
  ```

- CSV:

  ```http
  GET /listCloseOnly/csv
  ```

  Example format:

  ```csv
  km,miles,location,close_time
  0,0,begin,12/01/2021 19:06
  100,62,,12/02/2021 00:46
  ```

### 5.4 Top K query parameter

All three list endpoints support an optional `top` query parameter, which returns only the earliest `K` controls (sorted in ascending order of open time).

Examples:

```bash
# Top 3 open times (JSON)
curl "http://localhost:5001/listOpenOnly/json?top=3"

# Top 5 close times (CSV)
curl "http://localhost:5001/listCloseOnly/csv?top=5"

# Top 2 open and close pairs (JSON) from /listAll
curl "http://localhost:5001/listAll/json?top=2"
```

Implementation notes:

- The API sorts controls by the `open` field in ascending order.
- If `top` is present and valid, slicing is applied to the sorted list(s):
  - `data[:top_k]` for open-only or close-only
  - `open_times[:top_k]` and `close_times[:top_k]` for `/listAll`.

### 5.5 `/health`

Health-check endpoint:

```http
GET /health
```

Example when the API and MongoDB are healthy:

```json
{
  "status": "healthy",
  "database": "connected",
  "controls_count": 6
}
```

Example when MongoDB is not reachable:

```json
{
  "status": "unhealthy",
  "database": "disconnected"
}
```

---

## 6. Consumer Web Interface (PHP)

The consumer application is implemented in `website/index.php` and is served via Apache in the `website` container.

After running `docker compose up --build`, open in a browser:

```text
http://localhost:8080
```

Features:

- Buttons:
  - `List All Times`
  - `List Open Only`
  - `List Close Only`
- Output format selector:
  - JSON
  - CSV
- Optional `Top K Results` input:
  - When filled, appends `?top=K` to the API request.
- Display area:
  - For JSON: pretty-printed JSON text.
  - For CSV: HTML table rendered from the CSV response.

The consumer calls the API using Docker internal URLs, for example:

- `http://laptop:5000/listAll/json`
- `http://laptop:5000/listOpenOnly/csv?top=3`

---

## 7. Loading Sample Data (Optional)

To test the API with realistic data, you can load `data-samples/sample-data.json` into MongoDB.

### 7.1 Copy sample JSON into the MongoDB container

From the project root:

```bash
cd /path/to/proj6-rest
docker cp data-samples/sample-data.json brevet-mongodb:/tmp/sample-data.json
```

### 7.2 Insert data using the Mongo shell

Enter the Mongo shell:

```bash
cd DockerRestAPI
docker compose exec db mongo
```

In the shell:

```javascript
use brevets_db

var raw = cat('/tmp/sample-data.json');
var obj = JSON.parse(raw);

// Optional: clear existing controls
db.controls.deleteMany({});

// Flatten sample data into one document per control
obj.brevets.forEach(function(br) {
  br.controls.forEach(function(c) {
    db.controls.insertOne({
      brevet_distance: br.distance,
      begin_date: br.begin_date,
      begin_time: br.begin_time,
      km: c.km,
      miles: c.mi,
      location: c.location,
      open: c.open,
      close: c.close
    });
  });
});

// Check the inserted documents
db.controls.find().pretty();
```

Type `exit` to leave the Mongo shell.

Now the API and the consumer should display real control times based on `sample-data.json`.

---

## 8. Dependencies

The API service uses the following Python packages (see `laptop/requirements.txt`):

- `Flask==2.0.3`
- `Werkzeug==2.0.3`
- `flask-restful==0.3.10`
- `pymongo==3.12.3`
- `arrow==1.2.3`

They are installed inside the `laptop` container as part of the Docker build.

The consumer uses PHP 7.4 with Apache, based on the official `php:7.4-apache` image.

---