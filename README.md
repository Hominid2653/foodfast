# FoodFast — Inventory Management API

A Flask REST API for managing retail inventory. Employees can add, view, update, and delete inventory items. Product details can be fetched from the [OpenFoodFacts](https://world.openfoodfacts.org/) API by barcode or name and imported into the local inventory.

Includes a CLI tool to interact with the API and a pytest test suite.

---

## Prerequisites

- **Python 3.10+** (3.14 tested)
- **Git** (optional, for cloning)
- An internet connection (required for OpenFoodFacts lookups)

Check your Python version:

```powershell
python --version
```

---

## Setup Instructions

### 1. Get the project

**Clone from GitHub:**

```powershell
git clone <your-repo-url>
cd foodfast
```

**Or** navigate to an existing copy:

```powershell
cd c:\Users\USER\Desktop\MORINGA\flask\foodfast
```

### 2. Create a virtual environment

```powershell
python -m venv venv
```

### 3. Activate the virtual environment

**Windows (PowerShell):**

```powershell
.\venv\Scripts\Activate.ps1
```

You should see `(venv)` at the start of your prompt.

**Windows (Command Prompt):**

```cmd
venv\Scripts\activate.bat
```

**macOS / Linux:**

```bash
source venv/bin/activate
```

> **PowerShell execution policy error?** If activation is blocked, run once:
>
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

### 4. Install dependencies

With the virtual environment active:

```powershell
pip install -r requirements.txt
```

This installs Flask, requests, pytest, and their dependencies.

### 5. Verify installation

```powershell
python -c "import flask, requests, pytest; print('OK')"
pytest --version
```

---

## Start the API

With the virtual environment active, from the project root:

```powershell
python app.py
```

Expected output:

```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

The API is available at **http://127.0.0.1:5000**.

Leave this terminal open while using the API or CLI.

### Verify the server is running

Open a **second terminal**, activate the venv, then run:

```powershell
curl http://127.0.0.1:5000/
```

Or open **http://127.0.0.1:5000/** in a browser. You should see a JSON response listing available endpoints.

### Stop the server

Press `Ctrl + C` in the terminal where `python app.py` is running.

---

## Inventory data model

Each item in the in-memory database has these fields:

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Auto-generated unique ID |
| `product_name` | string | Product name (required when creating) |
| `brands` | string | Brand name |
| `barcode` | string | Product barcode |
| `ingredients_text` | string | Ingredient list |
| `quantity` | string | Package size (e.g. `"1.89 L"`) |
| `categories` | string | Product categories |
| `price` | float | Retail price |
| `stock` | integer | Units in stock |

On startup the API seeds **3 sample items** (almond milk, oats, dark chocolate). Data is stored in memory and resets when the server restarts.

---

## API Endpoints

| Method | Endpoint | Description | Success code |
|--------|----------|-------------|--------------|
| GET | `/` | API info and endpoint list | 200 |
| GET | `/inventory` | List all items | 200 |
| GET | `/inventory/<id>` | Get one item by ID | 200 / 404 |
| POST | `/inventory` | Add a new item | 201 / 400 |
| PATCH | `/inventory/<id>` | Update an item | 200 / 404 |
| DELETE | `/inventory/<id>` | Remove an item | 204 / 404 |
| GET | `/external/product/<barcode>` | Look up product on OpenFoodFacts | 200 / 404 / 502 |
| GET | `/external/search?name=<query>` | Search OpenFoodFacts by name | 200 / 400 / 502 |
| POST | `/inventory/from-api` | Import from OpenFoodFacts into inventory | 201 / 400 / 404 / 502 |

### Example API requests (curl)

**List all inventory:**

```powershell
curl http://127.0.0.1:5000/inventory
```

**Get item by ID:**

```powershell
curl http://127.0.0.1:5000/inventory/1
```

**Add a new item:**

```powershell
curl -X POST http://127.0.0.1:5000/inventory `
  -H "Content-Type: application/json" `
  -d "{\"product_name\":\"Green Tea\",\"brands\":\"Lipton\",\"price\":4.99,\"stock\":25}"
```

**Update price and stock:**

```powershell
curl -X PATCH http://127.0.0.1:5000/inventory/1 `
  -H "Content-Type: application/json" `
  -d "{\"price\":5.99,\"stock\":50}"
```

**Delete an item:**

```powershell
curl -X DELETE http://127.0.0.1:5000/inventory/2
```

**Look up product on OpenFoodFacts (barcode):**

```powershell
curl http://127.0.0.1:5000/external/product/025293001301
```

**Search OpenFoodFacts by name:**

```powershell
curl "http://127.0.0.1:5000/external/search?name=almond%20milk"
```

**Import product from OpenFoodFacts into inventory:**

```powershell
curl -X POST http://127.0.0.1:5000/inventory/from-api `
  -H "Content-Type: application/json" `
  -d "{\"barcode\":\"025293001301\",\"price\":4.99,\"stock\":10}"
```

### Example API requests (PowerShell `Invoke-RestMethod`)

```powershell
# List inventory
Invoke-RestMethod -Uri http://127.0.0.1:5000/inventory

# Add item
Invoke-RestMethod -Method POST -Uri http://127.0.0.1:5000/inventory `
  -ContentType "application/json" `
  -Body '{"product_name":"Green Tea","brands":"Lipton","price":4.99,"stock":25}'

# Update item
Invoke-RestMethod -Method PATCH -Uri http://127.0.0.1:5000/inventory/1 `
  -ContentType "application/json" `
  -Body '{"stock":50}'
```

---

## CLI Usage

The CLI (`cli.py`) sends HTTP requests to the running API. **Start the API first** (`python app.py`), then open a second terminal.

Activate the venv in the second terminal:

```powershell
cd c:\Users\USER\Desktop\MORINGA\flask\foodfast
.\venv\Scripts\Activate.ps1
```

### CLI commands

| Command | Description |
|---------|-------------|
| `python cli.py list` | List all inventory items |
| `python cli.py show <id>` | Show details for one item |
| `python cli.py add "<name>"` | Add a new item manually |
| `python cli.py update <id>` | Update price, stock, or name |
| `python cli.py delete <id>` | Delete an item |
| `python cli.py find-barcode <barcode>` | Look up product on OpenFoodFacts |
| `python cli.py find-name "<name>"` | Search OpenFoodFacts by name |
| `python cli.py import` | Fetch from OpenFoodFacts and add to inventory |

### CLI examples

```powershell
# List all items
python cli.py list

# View item with ID 1
python cli.py show 1

# Add a manual item
python cli.py add "Green Tea" --brands Lipton --price 4.99 --stock 25

# Update stock and price
python cli.py update 1 --stock 50 --price 5.99

# Update product name only
python cli.py update 1 --name "Organic Green Tea"

# Delete item
python cli.py delete 2

# Search OpenFoodFacts (does not add to inventory)
python cli.py find-barcode 025293001301
python cli.py find-name "almond milk"

# Import from OpenFoodFacts into inventory
python cli.py import --barcode 025293001301 --price 4.99 --stock 10
python cli.py import --name "oat milk" --price 3.49 --stock 20
```

### CLI options

```powershell
# Point CLI at a different host/port
python cli.py --base-url http://127.0.0.1:5000 list

# Add with all optional fields
python cli.py add "Protein Bar" --brands "Clif" --barcode "1234567890" --ingredients "Oats, honey" --price 2.50 --stock 100
```

### CLI help

```powershell
python cli.py --help
python cli.py add --help
```

---

## Running tests

With the virtual environment active:

```powershell
pytest -v
```

Run a specific test file:

```powershell
pytest tests/test_api.py -v
pytest tests/test_cli.py -v
pytest tests/test_openfoodfacts.py -v
```

Tests use Flask's test client and `unittest.mock` for external API calls — **the server does not need to be running** for tests.

---

## Project structure

```
foodfast/
├── app.py                    # Flask app and REST routes
├── store.py                  # In-memory inventory storage and seed data
├── openfoodfacts_client.py   # OpenFoodFacts API client
├── cli.py                    # Command-line interface
├── tests/
│   ├── conftest.py           # pytest fixtures
│   ├── test_api.py           # CRUD endpoint tests
│   ├── test_cli.py           # CLI command tests
│   └── test_openfoodfacts.py # External API tests (mocked)
├── docs/
│   ├── index.md              # Assignment requirements
│   └── rubric.md             # Grading rubric
├── requirements.txt          # Python dependencies
├── .gitignore
└── README.md
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `Could not connect to API` (CLI) | Start the server first: `python app.py` |
| `Activate.ps1` blocked | Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| Port 5000 already in use | Stop the other process or change the port in `app.py` (`app.run(port=5001)`) |
| `product_name is required` | POST body must include `"product_name"` |
| OpenFoodFacts returns 404 | Barcode or name not found in their database — try another product |
| OpenFoodFacts returns 502 | Network issue or API down — check internet connection |
| Inventory resets after restart | Expected — data is stored in memory only |

---

## External API

Product data is fetched from **OpenFoodFacts**:

- **By barcode:** `https://world.openfoodfacts.org/api/v0/product/{barcode}.json`
- **By name:** `https://world.openfoodfacts.org/cgi/search.pl`

No API key is required. Responses are normalized to match the local inventory schema before storage.

---

## Quick start (copy-paste)

```powershell
cd c:\Users\USER\Desktop\MORINGA\flask\foodfast
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

In a **second terminal**:

```powershell
cd c:\Users\USER\Desktop\MORINGA\flask\foodfast
.\venv\Scripts\Activate.ps1
python cli.py list
python cli.py find-barcode 025293001301
python cli.py import --barcode 025293001301 --price 4.99 --stock 10
```
