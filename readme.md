# Event Scheduler Backend

A Django 5 and DRF-based REST API for an event scheduling system with complex recurrence support.

## Setup Instructions

1. Clone the repository: `git clone https://github.com/yourusername/event-scheduler`
2. Ensure Docker and Docker Compose are installed.
3. Run `docker-compose up` to start the backend and PostgreSQL database.
4. Access the API at `http://localhost:8000/api/`.
5. Create a superuser: `docker-compose exec backend python manage.py createsuperuser`.
6. Obtain a JWT token via `POST /api/token/` with username and password.

## Run/Test Guidelines

- **API Endpoints**:
  - `POST /api/token/`: Authenticate and obtain JWT token (US-11, US-12).
  - `GET/POST /api/events/`: List or create events (US-01, US-02, US-03, US-04, US-05, US-06, US-07).
  - `GET/PUT/DELETE /api/events/<id>/`: Retrieve, update, or delete an event (US-08, US-09).
  - `POST /api/events/<id>/cancel_instance/`: Cancel a specific instance of a recurring event (US-09).
  - Query parameters: `?start=<iso-date>&end=<iso-date>` for date range filtering (US-06, US-07).
- **Run Tests**: `docker-compose exec backend python manage.py test`
- **Validation**: API returns clear error messages for invalid inputs (US-10).

## Architecture Decisions

- **Framework**: Django 5 with DRF for robust API development.
- **Authentication**: JWT via `djangorestframework-simplejwt` for secure, token-based authentication (US-11, US-12, US-13).
- **Database**: PostgreSQL for relational data storage.
- **Recurrence**: Uses `python-dateutil` for RRULE-based recurrence handling, supporting daily, weekly, monthly, yearly, intervals, weekday selection, and relative-date patterns (US-02, US-03, US-04, US-05).
- **Models**: `Event` for main event details, `EventInstance` for specific instances of recurring events to support individual cancellations (US-09).
- **Pagination**: Enabled with a default page size of 10 for list views (US-07).
- **Docker**: Ensures consistent setup across environments.

## Shortcuts/Assumptions

- Complex recurrence patterns (e.g., "last weekday of every year") are supported via `bysetpos` and `byweekday` fields.
- Recurrence instances are generated up to the `until` date or a reasonable limit to avoid performance issues.
- Logout is handled via Django’s built-in session management or client-side token removal (US-13).
- Frontend will be implemented using Django templates (not included in this backend).

## Notes

- The API is designed to integrate with a Django template-based frontend.
- Stretch goals (e.g., .ics export, multiple calendars, test coverage) can be added based on time availability.
- No turn-key calendar solutions used, as per rules.
