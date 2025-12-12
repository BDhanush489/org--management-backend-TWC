# Organization Management Service

A scalable multi-tenant backend application built using FastAPI, MongoDB Atlas, and JWT authentication. Each organization gets a dynamically generated collection, and admin users are authenticated using secure hashed passwords.

---

## Project Overview

This project demonstrates:

- **Multi-tenant architecture** with isolated data per organization
- **Dynamic collection creation** for each organization
- **Role-based behavior** with admin-controlled operations
- **JWT-based authentication** with secure token management
- **Modular, class-based backend design** for maintainability
- **Production-ready security patterns** including password hashing

---

## Features

### Multi-Tenant Organization Management

- Create an organization with dynamic collection generation (`org_<organization_name>`)
- Store metadata in a master database
- Update organization details
- Delete organization with proper authorization

### Secure Admin Authentication

- Admin registration per organization
- JWT login and token generation
- Password hashing using bcrypt/argon2

### Clean, Production-Ready Architecture

- Fully modular file structure
- Class-based service layer
- Easy to extend and maintain
- MongoDB Atlas-safe operations

---

## Project Structure

```
org-management-backend/
├── app/
│   ├── __init__.py
│   ├── db.py                 # MongoDB connection + master DB setup
│   ├── auth.py               # JWT creation + password hashing validation
│   ├── models.py             # Pydantic request/response models
│   ├── services/
│   │   ├── __init__.py
│   │   └── org_service.py    # Core business logic for organizations
│   └── routers/
│       ├── __init__.py
│       ├── org_router.py     # Routes: create, update, delete, get org
│       └── auth_router.py    # Admin login
│
├── main.py                   # FastAPI application entrypoint
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (ignored in Git)
├── .gitignore                # Ignore secrets and cache
├── screenshots/              # API output screenshots (optional)
└── README.md                 # Project documentation
```

---

## Tech Stack

| Component | Technology                        |
|-----------|-----------------------------------|
| Backend Framework | FastAPI                   |
| Database | MongoDB Atlas (cloud)              |
| ORM/Driver | Motor (Async MongoDB)            |
| Auth | JWT (PyJWT)                            |
| Security | bcrypt / argon2 password hashing   |
| Validation | Pydantic v2                      |
| Deployment | Uvicorn                          |

---

## Requirements & Installation

### 1. Install Python 3.10 – 3.12

Download from: https://www.python.org/downloads/

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

> **Note:** If bcrypt errors appear (Python 3.12), install:

> ```bash
> pip install "bcrypt==4.0.1"
> ```

---

## Setting Up MongoDB Atlas

### Step 1: Create an account

Visit: https://www.mongodb.com/cloud/atlas/register

### Step 2: Create a FREE Cluster (M0 Tier)

1. Choose **Shared** → **M0 Free Cluster**
2. Select a region → **Create Cluster**

### Step 3: Create a Database User

1. Go to: **Security** → **Database Access** → **Add New Database User**
2. Set:
   - Username: `yourname`
   - Password: `yourpassword`
   - Permissions: **Read & Write to Any Database**

### Step 4: Allow your IP

1. Go to: **Security** → **Network Access** → **Add IP Address**
2. Select: **Allow access from anywhere (0.0.0.0/0)**

### Step 5: Get the MongoDB URI

1. Go to: **Cluster** → **Connect** → **Drivers**
2. Copy the URI:

```
mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

> **If your password includes special characters**, encode them using URL encoding:
> 
> | Character | Encode As |
> |-----------|-----------|
> | @         | %40       |
> | #         | %23       |
> | ?         | %3F       |
> | /         | %2F       |
> 
> **Example:** `Dhanush@123` → `Dhanush%40123`

---

## Generating JWT Secret Key

Generate a secure secret key using Python:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**Example output:**
```
a4f93b018dda4551ef89c8e3e0fefe72e48fbd91f87b0e3c879
```

Use this inside `.env`.

---

## Environment Variables (.env)

Create a file named `.env` in the project root:

```env
MONGO_URI=mongodb+srv://username:encodedPassword@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
MASTER_DB=org_master_db

JWT_SECRET=your_generated_secret_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```
---

## Running the Application

Start the backend server:

```bash
uvicorn main:app --reload
```

---

## API Endpoints

### 1. Create Organization

**POST** `/org/create`

```json
{
  "organization_name": "SRM",
  "email": "admin@SRM.com",
  "password": "secret123"
}
```

### 2. Admin Login

**POST** `/admin/login`

```json
{
  "email": "admin@SRM.com",
  "password": "secret123"
}
```

**Returns:**

```json
{
  "access_token": "<jwt_token>",
  "token_type": "bearer"
}
```

### 3. Get Organization

**GET** `/org/get?organization_name=SRM`

### 4. Update Organization

**PUT** `/org/update`

```json
{
  "organization_name": "SRM",
  "email": "newadmin@SRM.com"
}
```

### 5. Delete Organization

**DELETE** `/org/delete?organization_name=SRM`

**Header:**
```
X-Admin-Email: admin@SRM.com
```

---

## Architecture Overview

```
        +---------------------------+
        |        FastAPI App        |
        +---------------------------+
                    |
                    v
        +---------------------------+
        |        Routers Layer      |
        |  (org_router, auth_router)|
        +---------------------------+
                    |
                    v
        +---------------------------+
        |     Services Layer        |
        |  Business Logic (OOP)     |
        +---------------------------+
                    |
                    v
        +---------------------------+
        |    MongoDB Master DB      |
        | organizations | admins    |
        +---------------------------+
                    |
                    v
        +---------------------------+
        |  Dynamic Org Collection   |
        |  org_SRM, org_test, etc  |
        +---------------------------+
```

---

## Testing

Use **VSCode REST Client** or **Postman** with the provided `api_tests.http` file.

For screenshots of API outputs, see the `output/` folder.

---

## Steps to a Scalability Enterprise-Grade Architecture

### 1. Too many collections when scaling to thousands of organizations

**Issue:**
- 1 org = 1 collection
- 10,000 orgs = 10,000 collections

This may cause:
- Longer startup times
- Increased memory usage
- Index overhead

**Solution:**

Use **database-per-organization** OR **sharding** OR **shared collections with tenant filters** if scaling beyond thousands.

---

### 2. No enforcement of schema

**Issue:**

MongoDB is schema-less. If each org collection grows differently, maintaining consistency becomes hard.

**Solution:**
- Use **Pydantic models** for schema validation
- Enable **MongoDB schema validation rules**

---

### 3. Deleting orgs via header (X-Admin-Email) is not fully secure

**Issue:**

Current implementation uses a simple header check.

**Better approach:**
- Validate admin → extract admin identity from **JWT**
- Check admin belongs to organization
- Use **role-based permissions (RBAC)**

---

### 4. All organizations stored on one cluster

**Issue:**

If you onboard 10,000+ orgs with heavy traffic, a single cluster may become slow.

**Solution:**

Build **multi-cluster deployment** → route organizations to different clusters dynamically.

---

### 5. Renaming an organization requires migrating all data

**Issue:**

Collection names depend on organization names.

**Better approach:**

Use a **unique stable ID (UUID)** and never rename collections:

```
org_<orgId>  # Example: org_b47f1c
```

Then renaming org becomes a **metadata change only** with:
- No data migration needed
- Zero downtime

---

### 6. Add Request Limiting & Audit Logging using SlowAPI

#### Request Limiting using SlowAPI (Rate Limiting)

**What is Rate Limiting?**

Limiting how many requests a user or IP can send within a specific time.

**Examples:**
- Max **10 requests per second** per IP
- Max **50 login attempts per hour** per user
- Max **1000 API calls per day** per organization

**What does it protect against?**

**Prevents DoS / DDoS-style attacks**
- Attackers try to overload your server by sending thousands of requests
- Rate limiting stops them with: `429 Too Many Requests`

**Prevents brute-force login attempts**
- If a hacker tries millions of passwords on `/admin/login`, rate limiting blocks them

**Protects your resources**
- Database connections
- CPU usage
- Network bandwidth

---

**Benefits:**
- Security compliance
- Debugging issues
- Forensic analysis

---

## Screenshots

API output screenshots are available in the `screenshots/` folder:

- `create_org.png` - Organization creation
- `admin_login.png` - Admin login with JWT
- `get_org.png` - Get organization details
- `update_org.png` - Update organization
- `delete_org.png` - Delete organization

---

## License

This project is created as part of a job application assignment.

---

## Author

**Dhanush Boggarrapu**

---
