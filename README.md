# Mailmerge

Simple Django-based mail merge project for managing campaigns, recipients, and send attempts.

## Features
- Campaigns with templated email bodies
- Recipient import-ready data model
- Send attempt tracking and suppression list
- Custom user model for future extensibility

## Tech Stack
- Python 3
- Django 4.2
- SQLite (default)

## Setup
1) Create and activate a virtual environment.
2) Install dependencies:
   - `pip install -r requirements.txt`
3) Run migrations:
   - `python manage.py makemigrations`
   - `python manage.py migrate`
4) Create a superuser (optional):
   - `python manage.py createsuperuser`
5) Start the server:
   - `python manage.py runserver`

## Project Structure
- `config/` — Django project settings and entrypoints
- `mailmerge/` — Core app (models, admin, etc.)
- `manage.py` — Django management entrypoint

## Notes
- Email template syntax uses `{{field}}` placeholders.
- `AUTH_USER_MODEL` is set to `mailmerge.User`.
