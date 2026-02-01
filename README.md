# Pet Store Microservices with CI/CD Pipeline

A production-ready pet store application demonstrating microservices architecture, containerization best practices, and automated CI/CD workflows with GitHub Actions.

[![CI/CD Pipeline](https://github.com/your-username/pet-store-microservices/actions/workflows/assignment4.yml/badge.svg)](https://github.com/your-username/pet-store-microservices/actions)

## Highlights

- **Microservices Architecture** - Loosely coupled services with dedicated databases
- **Full CI/CD Automation** - Three-stage GitHub Actions pipeline with artifact management
- **Container Orchestration** - Docker Compose with health checks and service dependencies
- **Automated Testing** - pytest integration with dynamic test injection
- **Dynamic Query Execution** - Runtime query processing from external input files

---

## CI/CD Pipeline

The heart of this project is a sophisticated **GitHub Actions workflow** that automates the entire build-test-deploy cycle.

### Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        GitHub Actions Workflow                               │
│                                                                              │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────────────────────┐  │
│  │             │      │             │      │                             │  │
│  │    BUILD    │─────▶│    TEST     │─────▶│          QUERY              │  │
│  │             │      │             │      │                             │  │
│  └─────────────┘      └─────────────┘      └─────────────────────────────┘  │
│        │                    │                           │                    │
│        ▼                    ▼                           ▼                    │
│  ┌───────────┐       ┌───────────┐              ┌─────────────┐             │
│  │ Docker    │       │ pytest    │              │ Dynamic     │             │
│  │ Images    │       │ Results   │              │ Query       │             │
│  │ Artifacts │       │ Artifact  │              │ Results     │             │
│  └───────────┘       └───────────┘              └─────────────┘             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Job 1: Build

Compiles Docker images for both microservices with comprehensive logging.

```yaml
- name: Build and export pet-store
  uses: docker/build-push-action@v5
  with:
    context: ./pet-store
    tags: pet-store:latest
    outputs: type=docker,dest=/tmp/pet-store.tar
```

**Features:**
- Parallel image builds using Docker Buildx
- Image export as tar archives for cross-job sharing
- Build status logging with timestamps
- Failure handling with detailed error reporting

### Job 2: Test

Runs automated tests against containerized services.

```yaml
- name: Run tests
  run: pytest -v tests/assn4_tests.py > assn4_test_results.txt
```

**Features:**
- Container orchestration with proper startup sequencing
- MongoDB health checks before service startup
- pytest execution with verbose output
- Test results preserved as downloadable artifacts
- Supports test file replacement for external validation

### Job 3: Query

Executes dynamic queries and purchases from an input file against live services. This job allows external testers to inject custom test cases at runtime.

---

#### How It Works

1. **Startup**: The job spins up all containers (pet-store1, pet-store2, pet-order, MongoDB instances)
2. **Database Population**: Automatically populates the database with predefined pet types and pets (same data as the test job)
3. **Query Execution**: Reads `query.txt` and executes each entry sequentially
4. **Output Generation**: Writes results to `response.txt` and uploads as artifact

---

#### Input File: `query.txt`

| Property | Value |
|----------|-------|
| **Location** | Root of the repository (`./query.txt`) |
| **Format** | Plain text file |
| **Encoding** | UTF-8 |

The file contains a sequence of entries, each ending with a semicolon (`;`). There are two types of entries:

---

##### Entry Type 1: `query`

Executes a **GET request** to the `/pet-types` endpoint of a specific pet store.

**Syntax:**
```
query: <store-number>,<query-string>;
```

| Field | Description | Values |
|-------|-------------|--------|
| `<store-number>` | Which pet store to query | `1` or `2` |
| `<query-string>` | URL query parameters | `<field>=<value>` |

**Available query fields:**
- `type` - Animal type (e.g., `Golden Retriever`)
- `family` - Taxonomic family (e.g., `Canidae`)
- `genus` - Taxonomic genus (e.g., `Canis`)
- `lifespan` - Lifespan in years (e.g., `12`)

**Examples:**
```
query: 1,type=Golden Retriever;
query: 2,family=Canidae;
query: 1,genus=Felis;
query: 2,lifespan=15;
```

---

##### Entry Type 2: `purchase`

Executes a **POST request** to the `/purchases` endpoint of the pet-order service.

**Syntax:**
```
purchase: <json-object>;
```

| Field | Description | Required |
|-------|-------------|----------|
| `purchaser` | Name of the buyer | Yes |
| `pet-type` | Type of pet to purchase | Yes |
| `store` | Store number (1 or 2) | No |
| `pet-name` | Specific pet name | No (requires `store`) |

**Examples:**
```
purchase: {"purchaser": "John", "pet-type": "Golden Retriever"};
purchase: {"purchaser": "Jane", "pet-type": "bulldog", "store": 2};
purchase: {"purchaser": "Bob", "pet-type": "Abyssinian", "store": 1, "pet-name": "Muscles"};
```

---

#### Complete `query.txt` Example

```
query: 1,type=Golden Retriever;
query: 2,family=Canidae;
query: 1,genus=Felis;
query: 2,lifespan=15;
query: 1,type=bulldog;
query: 2,genus=NonExistent;
purchase: {"purchaser": "John", "pet-type": "Golden Retriever", "store": 1};
purchase: {"purchaser": "Jane", "pet-type": "bulldog", "store": 2, "pet-name": "Lazy"};
purchase: {"purchaser": "Bob", "pet-type": "Abyssinian"};
purchase: {"purchaser": "Alice", "pet-type": "NonExistentAnimal", "store": 1};
```

---

#### Output File: `response.txt`

| Property | Value |
|----------|-------|
| **Location** | Generated in repository root, uploaded as artifact |
| **Format** | Plain text file |

For **each entry** in `query.txt`, the output contains:

```
<status-code>
<payload>
;
```

| Field | Description |
|-------|-------------|
| `<status-code>` | HTTP status code returned (e.g., `200`, `201`, `400`) |
| `<payload>` | JSON response if successful, or `NONE` if request failed |

**Success conditions:**
- `query` entries: Status `200` returns the JSON array, otherwise `NONE`
- `purchase` entries: Status `201` returns the purchase JSON, otherwise `NONE`

---

#### Complete `response.txt` Example

For the `query.txt` example above, the output would be:

```
200
[{"id": "1", "type": "Golden Retriever", "family": "Canidae", "genus": "Canis", ...}]
;
200
[{"id": "1", "type": "Golden Retriever", ...}, {"id": "2", "type": "Australian Shepherd", ...}, {"id": "3", "type": "bulldog", ...}]
;
200
[{"id": "3", "type": "Abyssinian", "family": "Felidae", "genus": "Felis", ...}]
;
200
[{"id": "2", "type": "Australian Shepherd", ...}]
;
200
[]
;
200
[]
;
201
{"purchaser": "John", "pet-type": "Golden Retriever", "store": 1, "pet-name": "Lander", "purchase-id": "1"}
;
201
{"purchaser": "Jane", "pet-type": "bulldog", "store": 2, "pet-name": "Lazy", "purchase-id": "2"}
;
201
{"purchaser": "Bob", "pet-type": "Abyssinian", "store": 1, "pet-name": "Muscles", "purchase-id": "3"}
;
400
NONE
;
```

---

#### Key Points

- Entries are processed **in order** - results appear in the same sequence
- Each entry **must end with a semicolon** (`;`)
- Empty results return an empty array `[]`, not `NONE`
- Failed requests return the status code with `NONE` as payload
- The database is **pre-populated** before queries run (6 pet types, 8 pets total)

### Pipeline Artifacts

| Artifact | Stage | Description |
|----------|-------|-------------|
| `docker-images` | Build | Compiled Docker images (tar format) |
| `build-log` | Build | Build status and timestamps |
| `pytest` | Test | Test execution results |
| `log` | Test | Container startup status |
| `response` | Query | Query execution results |

### Triggering the Pipeline

The workflow triggers on every push:


---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Docker Network                                 │
│                                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────────┐   │
│  │  pet-store1  │    │  pet-store2  │    │     MongoDB (Stores)     │   │
│  │  :5001       │    │  :5002       │    │   - pet_types_store1     │   │
│  │              │────│              │────│   - pet_types_store2     │   │
│  │  Flask API   │    │  Flask API   │    │   - pets_store1/2        │   │
│  └──────────────┘    └──────────────┘    └──────────────────────────┘   │
│         │                   │                                            │
│         └─────────┬─────────┘                                            │
│                   ▼                                                      │
│          ┌──────────────┐              ┌──────────────────────────┐     │
│          │  pet-order   │              │  MongoDB (Transactions)  │     │
│          │  :5003       │──────────────│   - transactions         │     │
│          │  Flask API   │              └──────────────────────────┘     │
│          └──────────────┘                                               │
└─────────────────────────────────────────────────────────────────────────┘
```

### Services

| Service | Port | Description |
|---------|------|-------------|
| pet-store1 | 5001 | Pet inventory management (Store 1) |
| pet-store2 | 5002 | Pet inventory management (Store 2) |
| pet-order | 5003 | Purchase processing & transactions |
| mongodb-stores | 27018 | Shared database for both stores |
| mongodb-transactions | 27019 | Transaction records |

---

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.9+ (for local testing)

### Run Locally

```bash
# Start all services
docker-compose up --build

# Verify services are running
curl http://localhost:5001/pet-types
curl http://localhost:5002/pet-types
curl http://localhost:5003/purchases
```

### Run Tests

```bash
pip install pytest requests
pytest -v tests/assn4_tests.py
```

### Execute Custom Queries

```bash
# Create a query.txt file
echo 'query: 1,family=Canidae;' > query.txt

# Run the query executor
pip install requests
python scripts/execute_queries.py

# Check results
cat response.txt
```

---

## API Endpoints

### Pet Store (`/pet-types`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/pet-types` | Create pet type (auto-populates from Ninja API) |
| `GET` | `/pet-types?family=X` | List/filter pet types |
| `GET` | `/pet-types/{id}` | Get specific pet type |
| `DELETE` | `/pet-types/{id}` | Remove pet type |

### Pet Store (`/pets`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/pet-types/{id}/pets` | Add pet to inventory |
| `GET` | `/pet-types/{id}/pets` | List pets with filtering |
| `PUT` | `/pet-types/{id}/pets/{name}` | Update pet details |
| `DELETE` | `/pet-types/{id}/pets/{name}` | Remove pet |

### Pet Order

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/purchases` | Process pet purchase |
| `GET` | `/transactions` | View transactions (requires `OwnerPC` header) |

---

## Project Structure

```
.
├── .github/workflows/
│   └── assignment4.yml       # CI/CD pipeline definition
├── pet-store/
│   ├── Dockerfile
│   └── pet_store.py          # Store inventory API
├── pet-order/
│   ├── Dockerfile
│   └── pet_order.py          # Purchase processing API
├── tests/
│   └── assn4_tests.py        # Automated test suite
├── scripts/
│   └── execute_queries.py    # Dynamic query executor
├── docker-compose.yml        # Local orchestration
└── query_example.txt         # Sample query format
```

---

## Configuration

### Environment Variables

| Variable | Service | Description |
|----------|---------|-------------|
| `MONGO_URI` | All | MongoDB connection string |
| `STORE_ID` | pet-store | Store identifier (1 or 2) |
| `OWNER_PASSWORD` | pet-order | Auth for `/transactions` |
| `NINJA_API_KEY` | pet-store | External API key |

### Docker Compose Services

All services are configured with:
- Automatic restart policies
- Health-check dependencies
- Isolated Docker network
- Persistent volumes for images

---

## Testing Strategy

### Unit Tests (pytest)

The test suite validates:

1. **Pet Type Creation** - POST requests with API data enrichment
2. **Unique ID Generation** - Ensuring no ID collisions across stores
3. **Pet Management** - CRUD operations on pet inventory
4. **Data Integrity** - Field validation against expected values
5. **Cross-Store Queries** - Filtering and retrieval accuracy

### Integration Tests (Query Job)

Dynamic query execution tests:
- Store-specific filtering
- Purchase workflow end-to-end
- Error handling for invalid requests
- Transaction recording

---
