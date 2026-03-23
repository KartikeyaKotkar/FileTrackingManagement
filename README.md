# File Tracking System — Frontend Integration Guide

## Overview

This backend is built using FastAPI and provides APIs for:

- User authentication
- Document management
- Version control
- Movement tracking

All APIs are RESTful and return JSON responses.

Interactive API documentation is available at:

```
http://localhost:8000/docs
```

---

## Base URL

```
http://127.0.0.1:8000
```

---

## Getting Started (Frontend)

### 1. Start the Backend Server

From the backend root directory:

``` 
export ADMIN_KEY=replace-with-a-strong-secret
uvicorn app.main:app --reload
```

Ensure the backend is running before integrating APIs.

---

## Authentication APIs

### Register

```
POST /auth/register
```

Request:

```json
{
  "username": "string",
  "fullname": "string",
  "password": "string",
  "email": "string",
  "phone": "string",
  "role_id": 1,
  "created_by": 1
}
```

Header required:

```
X-Admin-Key: <ADMIN_KEY>
```

---

### Login

```
POST /auth/login
```

Request:

```json
{
  "login": "string",
  "password": "string"
}
```

---

### Get Users

```
GET /auth/users
```

Header required:

```
X-Admin-Key: <ADMIN_KEY>
```

---

## Documents APIs

### Get All Documents

```
GET /documents/
```

---

### Create Document

```
POST /documents/
```

Request:

```json
{
  "reference_no": "DOC-001",
  "title": "string",
  "department_id": 1,
  "created_by": 1
}
```

---

### Get Single Document

```
GET /documents/{doc_id}
```

### Update Document Status

```
PATCH /documents/{doc_id}/status
```

Request:

```json
{
  "status": "Closed"
}
```

---

## Versions APIs

### Get All Versions of a Document

```
GET /versions/{document_id}
```

---

### Get Current Version

```
GET /versions/{document_id}/current
```

---

### Create Version

```
POST /versions/
```

Request:

```json
{
  "document_id": 1,
  "version_no": 2,
  "file_name": "contract-v2.pdf",
  "file_path": "files/contract-v2.pdf",
  "file_hash": "optional",
  "file_size": 12345,
  "created_by": 1
}
```

---

## Movement APIs

### Get Movement History

```
GET /movement/{document_id}
```

---

### Create Movement Entry

```
POST /movement/
```

Request:

```json
{
  "document_id": 1,
  "from_dept": 1,
  "to_dept": 2,
  "movement_type": "Transfer",
  "approved_by": 1,
  "moved_by": 1,
  "remarks": "optional"
}
```

---

## Expected Workflow

### Creating a Document

1. Call `POST /documents/`
2. Call `POST /versions/` with the returned document_id when the first file is available
3. Optionally call `POST /movement/`

---

### Viewing a Document

1. Fetch document using `/documents/{id}`
2. Fetch versions using `/versions/{id}`
3. Fetch current version using `/versions/{id}/current`
4. Fetch movement history using `/movement/{id}`

---

## Notes for Frontend Developers

- All endpoints return JSON
- IDs such as `document_id` are required for most operations
- Do not assume order; always fetch fresh data
- Use `/docs` to verify request/response formats
- Ensure correct payload structure to avoid 422 errors

---

## Project Structure (Backend Reference)

```
backend/
 └── app/
      ├── main.py
      ├── database.py
      ├── routers/
      ├── models/
```

---

## Testing

You can test all endpoints using:

- Swagger UI: `/docs`
- Postman or any API client

---
