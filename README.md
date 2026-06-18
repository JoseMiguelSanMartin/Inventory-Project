# Django Inventory Project – What Still Needs To Be Done

## Project Overview

Create a application inventory system as a fun project so inventory doesnt need to manuely be typed!

---

## Setup Instructions

### 1. Open the Project

Open the project folder in VS Code.

Make sure you are inside the folder that contains `manage.py`.

Example:

```bash
cd django_inventory_bare_minimum
```

---

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate the virtual environment.

Git Bash:

```bash
source venv/Scripts/activate
```

PowerShell:

```bash
venv\Scripts\Activate.ps1
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Set Up the Database

Apply the migrations:

```bash
python manage.py migrate
```

---

### 5. Create an Administrator Account

```bash
python manage.py createsuperuser
```

Follow the prompts to create a username, email (optional), and password.

---

### 6. Run the Application

```bash
python manage.py runserver
```

Open the application in your browser:

```text
http://127.0.0.1:8000/
```

---

# What Has Already Been Completed

The following components have already been implemented:

* Django project configuration
* Inventory application setup
* SQLite database configuration
* Inventory model
* Authentication routing
* Login/logout functionality
* User registration functionality
* Inventory CRUD views
* Django REST Framework setup
* API skeleton
* Basic templates
* Basic CSS
* Requirements file
* Admin registration
* Login page design and styling
* Signup page design and styling
* Add better navigation (manager and worker navbar links)
* Inventory table design and status indicators
* Inventory search and filtering
* Mobile responsive inventory list (card layout on small screens)
* Role-based access control (manager vs worker)
* Add/Edit/Delete restricted to manager only
* Submit Daily Report restricted to manager only
* Daily Report page restricted to manager only
* API documentation page restricted to staff only
* Added more validation to the inventory form
* Added styling to the inventory form
* Added help texts to the inventory form
* Improved button layout for the delete confirmation

---

# What The Group Still Needs To Do

## Create User Page

File:

```text
templates/registration/signup.html
```

Tasks:

* Manager notification when daily report is submitted (email or SMS)
* Normal worker page

---

## Inventory Forms

File:

```text
templates/inventory/inventory_form.html
```

Tasks:

* Make the form visually consistent with the rest of the site.

---

## Delete Confirmation Page

File:

```text
templates/inventory/inventory_confirm_delete.html
```

Tasks:

* Improve confirmation messaging.
* Add warning styling.
* Make accidental deletion less likely.

---

## API Documentation Page

File:

```text
templates/inventory/api_docs.html
```

Tasks:

* Remove this page — restricted to staff only for now, full removal pending.

---

## CSS and Styling

File:

```text
static/css/site.css
```

Tasks:

* Create the final application design.
* Improve spacing and typography.
* Add colors and button styles.
* Make all pages visually consistent.

---

## Backend Improvements

Files:

```text
inventory/models.py
inventory/forms.py
inventory/views.py
inventory/serializers.py
inventory/urls.py
```

Possible improvements:

* Add inventory categories.
* Add notes or descriptions.
* Add storage location fields.
* Add item status fields.
* Add sorting.
* Improve validation.
* Restrict inventory to individual users if required.

---

# Suggested Group Responsibilities

## Team Member 1

Responsible for:

* Login page
* Registration page
* Navigation bar
* Base template

---

## Team Member 2

Responsible for:

* Inventory list page
* Inventory forms
* Delete confirmation page

---

## Team Member 3

Responsible for:

* API documentation page
* Serializers
* API testing

---

## Team Member 4

Responsible for:

* CSS styling
* Responsive design
* Testing
* README cleanup
* Final submission preparation

---

# Testing Checklist

Before submission, verify that:

* The project starts successfully.
* Login works correctly.
* Logout works correctly.
* User registration works.
* Inventory pages load properly.
* Inventory items can be created.
* Inventory items can be edited.
* Inventory items can be deleted.
* Inventory search bar works.
* API endpoints function as expected.
* CSS is loading properly.
* Templates render without errors.
* No broken links exist.
* All group members have tested their assigned features.
* Manager cannot access Add Item, Edit, or Delete when logged in as a worker.
* Workers cannot access the daily report page directly via URL.

---

# Useful Commands

Run the server:

```bash
python manage.py runserver
```

Create migrations:

```bash
python manage.py makemigrations
```

Apply migrations:

```bash
python manage.py migrate
```

Create an administrator account:

```bash
python manage.py createsuperuser
```

Open the Django shell:

```bash
python manage.py shell
```

---

## Final Goal

Make a successful project

## API Documentation

GET /inventory/api/items/
POST /inventory/api/items/
GET /inventory/api/items/<id>/
PUT /inventory/api/items/<id>/
DELETE /inventory/api/items/<id>/

## User Logins

Manager - Username: Admin -- Password: secret1234
Work - Username: CrewOne -- Password: edmonton1
Work - Username: CrewTwo -- Password: edmonton2
Sonnet 4.6 Low