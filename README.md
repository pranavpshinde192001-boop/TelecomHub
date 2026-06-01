# TeleSupportHub

TeleSupportHub is a production-style telecom support SaaS built with Flask and MySQL. It includes customer onboarding, ticketing workflows, service purchases, agent operations, and analytics dashboards with a modern glassmorphism UI.

## Features

- Customer registration, login, and session management
- Raise tickets, track status, and view ticket history
- Purchase telecom services and view purchase history
- Agent dashboard to manage all tickets with status updates
- Search and filter tickets by ID, customer, and status
- Analytics dashboards with charts and real-time metrics
- Secure password hashing with bcrypt
- Flash notifications for key actions

## Tech Stack

- Backend: Flask, MySQL Connector
- Database: MySQL (AWS RDS compatible)
- Frontend: Bootstrap 5, AOS animations, custom glass UI
- Charts: Plotly
- Security: bcrypt

## Project Structure

```
TeleSupportHub/
├── app.py
├── db_config.py
├── requirements.txt
├── static/
│   ├── css/
│   │   └── style.css
│   ├── images/
│   └── js/
├── templates/
│   ├── agent_dashboard.html
│   ├── agent_login.html
│   ├── all_tickets.html
│   ├── buy_service.html
│   ├── dashboard.html
│   ├── index.html
│   ├── login.html
│   ├── my_purchases.html
│   ├── my_tickets.html
│   ├── raise_ticket.html
│   ├── register.html
│   └── tickets.html
└── database/
	└── schema.sql
```

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```
pip install -r requirements.txt
```

3. Configure database connection in `db_config.py`.
4. Run the app:

```
python app.py
```

App runs at `http://127.0.0.1:5000`.

## Database

Ensure the following tables exist:

- `customers`
- `tickets`
- `purchases`
- `agents`

See [database/schema.sql](database/schema.sql).

## Default Agent Login

Create an agent record in the `agents` table and use those credentials for agent access.

## Production Notes

- Store secrets and database credentials in environment variables.
- Use a production server (e.g., gunicorn) behind a reverse proxy.
- Enable HTTPS and secure cookie settings.
- Consider adding rate limiting and request logging.

## Screens

The UI is optimized for a modern SaaS look with glassmorphism cards, dashboard analytics, and animated transitions.
