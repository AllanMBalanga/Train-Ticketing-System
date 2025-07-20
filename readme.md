# 🚆 Train Ticketing API System 

A backend train ticketing system built using **MongoDB**, **FastAPI**, and **Python**, with full JWT-based authentication and role-based access control. Designed to simulate a digital ticketing system for the Philippine railway, removing the need for physical tickets or beep cards.

## 📘 Features

- 🔐 **JWT Authentication** (users vs admins)
- 🔒 **Password Hashing** with `bcrypt`
- 🧾 **7 MongoDB Collections**:
  - `users`, `balances`, `transactions`, `trains`, `stations`, `travels`, `payments`
- 🧮 **Fare calculation** based on station positions
- 💸 **Payment validation** against user balance
- 🧑‍⚖️ **Role-based access control** (different permissions for users and admins)
- 🗃️ **Soft and hard delete** support
- ✅ **Pydantic-based request/response validation**
- 🔄 **Postman-ready** with token-based authorization
- 🧩 **ERD provided** to visualize NoSQL relationships
- 📊 **Tested** via Postman and Swagger UI
  
---

## 🔗 API Endpoints

### ✅ USERS

`/users`

| Method | Path                     | Description                | Role               |
| ------ | ------------------------ | -------------------------- | ------------------ |
| GET    | /users                   | Get all users              | user, admin        |
| POST   | /users                   | Create new user (register) | Public             |
| GET    | /users/{user\_id}        | Get single user            | user (self), admin |
| PUT    | /users/{user\_id}        | Full update                | user (self), admin |
| PATCH  | /users/{user\_id}        | Partial update             | user (self), admin |
| DELETE | /users/{user\_id}        | Hard delete user           | admin              |
| DELETE | /users/{user\_id}/delete | Soft delete user           | user (self), admin |

### ✅ BALANCES

`/users/{user_id}/balances`

| Method | Path                              | Description         | Role               |
| ------ | --------------------------------- | ------------------- | ------------------ |
| GET    | /users/{user\_id}/balances        | Get balance         | user (self), admin |
| PUT    | /users/{user\_id}/balances        | Update balance      | admin              |
| DELETE | /users/{user\_id}/balances        | Hard delete balance | admin              |
| DELETE | /users/{user\_id}/balances/delete | Soft delete balance | user (self), admin |

### ✅ TRANSACTIONS

`/users/{user_id}/balances/{balance_id}/transactions`

| Method | Path                                                                           | Description          | Role               |
| ------ | ------------------------------------------------------------------------------ | -------------------- | ------------------ |
| GET    | /users/{user\_id}/balances/{balance\_id}/transactions                          | Get all transactions | user (self), admin |
| POST   | /users/{user\_id}/balances/{balance\_id}/transactions                          | Create transaction   | user (self)        |
| GET    | /users/{user\_id}/balances/{balance\_id}/transactions/{transaction\_id}        | Get one              | user (self), admin |
| PUT    | /users/{user\_id}/balances/{balance\_id}/transactions/{transaction\_id}        | Update               | admin              |
| PATCH  | /users/{user\_id}/balances/{balance\_id}/transactions/{transaction\_id}        | Partial update       | admin              |
| DELETE | /users/{user\_id}/balances/{balance\_id}/transactions/{transaction\_id}        | Hard delete          | admin              |
| DELETE | /users/{user\_id}/balances/{balance\_id}/transactions/{transaction\_id}/delete | Soft delete          | admin              |

### ✅ TRAINS

`/trains`

| Method | Path                       | Description    | Role        |
| ------ | -------------------------- | -------------- | ----------- |
| GET    | /trains                    | Get all trains | user, admin |
| POST   | /trains                    | Create train   | admin       |
| GET    | /trains/{train\_id}        | Get one train  | user, admin |
| PUT    | /trains/{train\_id}        | Update train   | admin       |
| DELETE | /trains/{train\_id}        | Hard delete    | admin       |
| DELETE | /trains/{train\_id}/delete | Soft delete    | admin       |

### ✅ STATIONS

`/trains/{train_id}/stations`

| Method | Path                                              | Description               | Role        |
| ------ | ------------------------------------------------- | ------------------------- | ----------- |
| GET    | /trains/{train\_id}/stations                      | Get all stations of train | user, admin |
| POST   | /trains/{train\_id}/stations                      | Create station            | admin       |
| GET    | /trains/{train\_id}/stations/{station\_id}        | Get one station           | user, admin |
| PUT    | /trains/{train\_id}/stations/{station\_id}        | Update station            | admin       |
| PATCH  | /trains/{train\_id}/stations/{station\_id}        | Partial update            | admin       |
| DELETE | /trains/{train\_id}/stations/{station\_id}        | Hard delete               | admin       |
| DELETE | /trains/{train\_id}/stations/{station\_id}/delete | Soft delete               | admin       |

### ✅ TRAVELS

`/trains/{train_id}/travels`

| Method | Path                                            | Description     | Role               |
| ------ | ----------------------------------------------- | --------------- | ------------------ |
| GET    | /trains/{train\_id}/travels                     | Get all travels | user, admin        |
| POST   | /trains/{train\_id}/travels                     | Create travel   | user               |
| GET    | /trains/{train\_id}/travels/{travel\_id}        | Get one travel  | user, admin        |
| PUT    | /trains/{train\_id}/travels/{travel\_id}        | Update travel   | admin              |
| PATCH  | /trains/{train\_id}/travels/{travel\_id}        | Partial update  | admin              |
| DELETE | /trains/{train\_id}/travels/{travel\_id}        | Hard delete     | admin              |
| DELETE | /trains/{train\_id}/travels/{travel\_id}/delete | Soft delete     | user (self), admin |

### ✅ PAYMENTS

`/users/{user_id}/payments`

| Method | Path                                            | Description      | Role               |
| ------ | ----------------------------------------------- | ---------------- | ------------------ |
| GET    | /users/{user\_id}/payments                      | Get all payments | user (self), admin |
| POST   | /users/{user\_id}/payments                      | Create payment   | user (self)        |
| GET    | /users/{user\_id}/payments/{payment\_id}        | Get one payment  | user (self), admin |
| PUT    | /users/{user\_id}/payments/{payment\_id}        | Update payment   | admin              |
| DELETE | /users/{user\_id}/payments/{payment\_id}        | Hard delete      | admin              |
| DELETE | /users/{user\_id}/payments/{payment\_id}/delete | Soft delete      | user (self), admin |

---

## 🧪 Postman Setup Tips

- **Login first** → Get token and set it in Postman as Bearer Token.
- **Set Base URL** → Use `{{base_url}}/` and configure it as a Postman environment variable.
- **Organize folders** → Group endpoints by feature: Users, Balances, Trains, etc.
- **Save examples** → For test data and expected responses.
- **Use global variables** → For `user_id`, `token`, `train_id`, etc. to simplify path testing.

```js
const json = pm.response.json();
pm.environment.set("user_id", json.user_id); // or json.data.id
pm.environment.set("access_token", json.access_token);
pm.environment.set("role", json.role);
```

---

## 📊 ERD for NoSQL Structure

To help visualize the relationships between MongoDB collections—even without a relational database—I created a **NoSQL ERD-style diagram**. This allows developers to clearly see how collections relate via fields like `user_id`, `train_id`, and `balance_id`, despite MongoDB not enforcing foreign keys.

🖼️ You can find the diagram in the `diagram/` folder of this repository.

---

## ✅ Status Codes Used

- `200 OK`
- `201 Created`
- `204 No Content`
- `400 Bad Request`
- `401 Unauthorized`
- `403 Forbidden`
- `404 Not Found`
- `409 Conflict`
- `422 Unprocessable Entity`
- `500 Internal Server Error`

---

## 🔐 Authentication & Authorization

- **JWT Access Tokens**
- Separate user and admin routes
- Role checks enforced in every route using FastAPI dependencies

---

## 🔧 Tech Stack

- Language: Python
- Framework: FastAPI
- Database: MongoDB (via PyMongo)
- Validation: Pydantic
- Auth: JWT tokens
- Security: bcrypt
- Testing: Postman, Swagger UI

---

## 🚧 Future Improvements

- Add Stripe or GCash integration for live payments
- Add frontend UI 
- Add payment system that is passable in train swiping systems

---

## 📂 Repo Structure

```bash
app/
├── routers/
├── body.py
├── config.py
├── database.py
├── main.py
├── oauth2.py
├── queries.py
├── response.py
├── status_codes.py
├── updates.py
└── utils.py
```

---

## 🌍 How to Run

```bash
python -m venv venv
source venv/bin/activate.bat  # or venv\Scripts\activate.bat on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

## 🧠 Summary

This project is a robust, backend system designed to manage train ticketing workflows in a realistic Philippine setting. It handles multiple complex models with strict role separation, fare calculation, and financial logic using MongoDB.

📬 Feel free to fork, test, or extend it! Contributions are welcome.

