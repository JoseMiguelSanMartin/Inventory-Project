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

---

# What The Group Still Needs To Do

## Login Page

File:

```text
templates/registration/login.html
```

Tasks:

* Design the final login page layout.
* Improve the appearance of the login form.
* Add user-friendly error messages.
* Add links to registration or password recovery if required.
* Ensure the page matches the overall application style.

---

## Create User Page

File:

```text
templates/registration/signup.html
```

Tasks:

* Create a polished registration page.
* Improve form layout.
* Add instructions for users.
* Style validation errors.
* Include navigation back to the login page.

---

## Inventory Dashboard

File:

```text
templates/inventory/inventory_list.html
```

Tasks:

* Improve the table design.
* Add better navigation.
* Display status indicators.
* Add search or filtering if required.
* Improve the overall user experience.

---

## Inventory Forms

File:

```text
templates/inventory/inventory_form.html
```

Tasks:

* Improve form styling.
* Add placeholders or help text.
* Add validation feedback.
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
* Improve button layout.
* Make accidental deletion less likely.

---

## API Documentation Page

File:

```text
templates/inventory/api_docs.html
```

Tasks:

* Explain the purpose of each endpoint.
* Add example requests.
* Add example JSON responses.
* Explain authentication requirements.
* Improve the page design.

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
* Ensure the application works on mobile devices.
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
* Add searching.
* Add filtering.
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
* API endpoints function as expected.
* CSS is loading properly.
* Templates render without errors.
* No broken links exist.
* All group members have tested their assigned features.

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
