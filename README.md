# Subscription Billing Backend

## Running Locally

Copy the sample.env to a `.env` file and make sure to set appropriate values. 

Then run the following command:
```
docker compose up -d
```

Connect to the `db` container and connect to `psql`

```
psql -U postgres
```

Once connected, run the following:

```
CREATE USER <POSTGRES_DB_USER> WITH SUPERUSER PASSWORD '<POSTGRES_DB_PASSWORD>';
CREATE DATABASE <POSTGRESQL_DB_NAME> WITH OWNER <POSTGRESQL_DB_USER>;
```

Also, make sure to connect to the `web` container and run migrations:

```
uv run python manage.py migrate
```

## Core Features:

**Assumption: Product differentiation is not in place. So, assuming this to be a billing backend for a single product.**

### APIs:

APIs for User subscribing/unsubscribing:
1. API for Subscribing - http://localhost:8000/api/subscriptions/subscribe/
2. API for Unsubscribing - http://localhost:8000/api/subscriptions/unsubscribe/

APIs for Invoices:
1. Invoice Viewset - http://localhost:8000/api/invoices
2. Payment Status - http://localhost:8000/payment/status

#### Miscellaneous
Standard CRUD Endpoints for:
- User
- Plan
- Subscription
- Invoice

### Periodic Celery Tasks:
 
1. `schedule_invoices` - Automatically generate invoices daily for subscriptions starting that day - Takes care of Monthly, Quaterly and Yearly subscriptions.
2. `mark_unpaid_invoices` - Marks overdue invoices if due_date has passed without payment.
3. `mark_expired_subscriptions` - Scheduled Daily Task which marks subscriptions which have expired.

## Bonus

1. `send_remainder_emails` - Scheduled Daily Task which sends remainder emails to Pending and Overdue Invoices
2. Stripe Integration - APIs along with UI for purchasing plan - http://localhost:8000/purchase/pricing
3. Management Command `populate_data` - Sets up basic plans along with their associated Stripe entities
