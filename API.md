# 📝 AquaSentinel-AI API documentation

This document outlines the REST API endpoints provided by the AquaSentinel-AI backend service under the `/api/v1` version prefix.

---

## 🔐 Authentication Endpoints

### 1. `POST /api/v1/auth/register`
Creates a new user profile and returns access and refresh tokens.
* **Payload:**
  ```json
  {
    "name": "User Name",
    "email": "user@example.com",
    "password": "securepassword"
  }
  ```

### 2. `POST /api/v1/auth/login`
Logs in a user, returning a JWT token pair.
* **Payload:**
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword"
  }
  ```

### 3. `GET /api/v1/auth/me`
Retrieves currently authenticated user details. Requires `Authorization: Bearer <token>` header.

---

## 💬 Chat & Orchestration Endpoints

### 1. `POST /api/v1/chat/message`
Sends a message to the LangGraph orchestration pipeline. Accept `multipart/form-data` payloads.
* **Headers:** `Authorization: Bearer <token>`
* **Form Fields:**
  * `message`: Chat text query.
  * `session_id` (Optional): ID to maintain memory.
  * `image` (Optional): Uploaded file.
  * `ph`, `tds`, `turbidity` (Optional): Chemical parameter values.

### 2. `GET /api/v1/chat/history`
Returns historical chat logs for a given session.

---

## 📊 Dashboard & Reports Endpoints

### 1. `GET /api/v1/analysis/dashboard`
Calculates dashboard stats (Total checks, reports generated, photos analyzed, average score) and unified recent activity timeline list. Requires Bearer JWT.

### 2. `GET /api/v1/reports`
Fetches a list of generated reports for the current user.

### 3. `GET /api/v1/reports/download/{report_id}/{format}`
Downloads a report file from the server.
* **Path Parameters:**
  * `report_id`: Unique UUID of the report.
  * `format`: Exporter formats (`pdf`, `markdown`, `json`).

---

## 🩺 System Monitoring Endpoints

### 1. `GET /health` (Public)
Public load balancer endpoint verifying that the backend is alive.

### 2. `GET /api/v1/monitoring/health`
Detailed database, reports, and Gemini API provider checks.

### 3. `GET /api/v1/monitoring/metrics`
Exposes server system metrics (Memory usage, CPU usage, and database query latency).
