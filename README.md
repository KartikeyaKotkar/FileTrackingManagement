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
  "password": "string"
}
```

---

### Login

```
POST /auth/login
```

Request:

```json
{
  "username": "string",
  "password": "string"
}
```

---

### Get Users

```
GET /auth/users
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
  "title": "string",
  "description": "string"
}
```

---

### Get Single Document

```
GET /documents/{doc_id}
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
  "file_path": "string"
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
  "from_user": "string",
  "to_user": "string",
  "status": "string"
}
```

---

## Expected Workflow

### Creating a Document

1. Call `POST /documents/`
2. Call `POST /versions/` with the returned document_id
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
