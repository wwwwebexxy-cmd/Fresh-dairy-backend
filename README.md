# Fresh Dairy backend

This repository contains the backend application source for the independent Fresh Dairy project.

## Local development

1. Create a new, empty local MySQL database and a dedicated local database user.
2. Create a virtual environment and install `requirements.txt`.
3. Copy `.env.example` to `.env` and replace the local placeholders with newly created values.
4. Run `python manage.py migrate` and then `python manage.py runserver`.

The backend reads project configuration only from `FRESH_DAIRY_*` variables. Existing database credentials, data exports, uploaded media, deployment settings, and Git remotes are intentionally not included. Production configuration and cloud setup are not defined here.
