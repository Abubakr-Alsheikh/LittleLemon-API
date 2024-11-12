# LittleLemon Restaurant API

This repository contains the code for a Django REST Framework (DRF) API project designed for the Coursera assignment related to "APIs from meta". The project implements various API endpoints to manage restaurant operations.


## Features

* **Menu Item Management:** Create, read, update, and delete menu items (CRUD operations).
* **User Group Management:** Assign users to different groups (Manager, Customer, Delivery Crew) to control access permissions.
* **Shopping Cart Management:**  Add and remove items from a user's shopping cart.
* **Order Management:** Create, view, update (by Manager/Delivery Crew), and delete orders.
* **Authentication:** User registration, login, and token-based authentication using Djoser and JWT (JSON Web Token).
* **Filtering, Pagination, and Sorting:**  Efficiently manage large datasets.
* **Throttling:** Limits request rates to prevent abuse and ensure API stability.

## Technologies Used

* Python
* Django
* Django REST Framework (DRF)
* Djoser (for user management)
* Simple JWT (for JWT authentication)
* SQLite (database)


**Installation and Running**

1. **Clone the repository:** 
   ```bash
   git clone https://github.com/Abubakr-Alsheikh/LittleLemon-API
   ```
2. **Navigate to the project directory:** 
   ```bash
   cd LittleLemon
   ```
3. **Create a virtual environment:** 
   ```bash
   pipenv install
   ```
4. **Activate the virtual environment:** 
   ```bash
   pipenv shell
   ```
5. **Run migrations:** 
   ```bash
   python manage.py migrate 
   ```
6. **Start the development server:**
   ```bash
   python manage.py runserver
   ```

## API Endpoints

You can access the API endpoints in your browser or using tools like Insomnia or Postman:

* **Authentication:**
    - `/auth/users/` (POST): User registration
    - `/auth/token/login/` (POST):  Login and token generation
    - `/auth/users/me/` (GET):  Retrieve current user
* **Menu Items:**
    - `/api/menu-items/` (GET): List all menu items
    - `/api/menu-items/{menuItem_id}/` (GET): Retrieve a single menu item
* **Cart:**
    - `/api/cart/menu-items/` (GET): View cart items
    - `/api/cart/menu-items/` (POST): Add an item to the cart
    - `/api/cart/menu-items/` (DELETE): Clear the cart
* **Orders:**
    - `/api/orders/` (GET): List orders (filtered by user role)
    - `/api/orders/` (POST): Create a new order
    - `/api/orders/{orderId}/` (GET): View order details
    - `/api/orders/{orderId}/` (PUT/PATCH): Update an order (permissions apply)
    - `/api/orders/{orderId}/` (DELETE): Delete an order (manager permission required)
* **User Group Management:**
    - `/api/groups/manager/users/` (GET):  List managers
    - `/api/groups/manager/users/` (POST): Assign a user to the manager group
    - `/api/groups/manager/users/{userId}/` (DELETE): Remove a user from the manager group 
    - Similar endpoints exist for the "Delivery Crew" group.

## Assignment Details

This project fulfills the requirements of the following assignments from the Coursera course:

*   Building a REST API with Django REST Framework.
*   Implementing filtering, searching, and pagination.
*   Applying throttling to the API.


## Note
This project is for educational purposes. More robust security measures, including proper password hashing, would be required for a production environment.