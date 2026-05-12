# MyStore

A full-featured e-commerce web application built with Flask. Supports product browsing with search and category filtering, a session-based shopping cart, Stripe-powered checkout, user authentication, order history, and an admin panel for managing products and orders.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | Flask 3.1 |
| Database ORM | Flask-SQLAlchemy 3.1 / SQLAlchemy 2.0 |
| Migrations | Flask-Migrate (Alembic) |
| Authentication | Flask-Login |
| Payments | Stripe (Payment Intents API) |
| Email | Flask-Mail |
| Templating | Jinja2 |
| Styling | Vanilla CSS (custom design system in `app/static/css/main.css`) |
| Database (dev) | SQLite |

---

## Project Structure

```
e-Commerce Site/
├── run.py                   # App entry point
├── seed.py                  # Database seeding script
├── products.json            # Sample product data
├── requirements.txt
├── .env                     # Local environment variables (not committed)
├── instance/
│   └── store_dev.db         # SQLite database (generated on first run)
├── migrations/              # Alembic migration files
└── app/
    ├── __init__.py          # App factory
    ├── config.py            # Dev / Testing / Production config classes
    ├── extensions.py        # SQLAlchemy, LoginManager, Migrate, Mail
    ├── static/
    │   ├── css/main.css
    │   └── images/
    └── templates/
    │   ├── base.html
    │   ├── store/
    │   ├── auth/
    │   ├── cart/
    │   ├── checkout/
    │   ├── orders/
    │   └── admin/
    ├── store/               # Product listing + detail
    ├── auth/                # Register, login, logout
    ├── cart/                # Session-based cart
    ├── checkout/            # Stripe checkout + webhook
    ├── orders/              # Order history (authenticated users)
    └── admin/               # Admin dashboard (admin users only)
```

---

## Local Setup

### 1. Clone and create a virtual environment

```bash
git clone <repo-url>
cd "e-Commerce Site"
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create a `.env` file

Create a `.env` file in the project root with the following variables:

```env
SECRET_KEY=your-secret-key-here

# Stripe — use test keys during development
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Mail (optional for local dev)
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USERNAME=your@email.com
MAIL_PASSWORD=your-password

# Leave blank to use the default SQLite dev database
# DATABASE_URL=sqlite:///store_dev.db
```

Stripe test keys are available in your [Stripe Dashboard](https://dashboard.stripe.com/test/apikeys). The webhook secret is generated when you create a webhook endpoint (see Stripe section below).

### 4. Initialise the database

```bash
flask db upgrade
```

### 5. Seed sample products (optional)

```bash
python seed.py
```

### 6. Run the development server

```bash
python run.py
```

The app will be available at `http://127.0.0.1:5000`.

---

## Environment Variables Reference

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | Yes | Flask session signing key |
| `STRIPE_PUBLIC_KEY` | Yes | Publishable key from Stripe |
| `STRIPE_SECRET_KEY` | Yes | Secret key from Stripe |
| `STRIPE_WEBHOOK_SECRET` | Yes | Webhook signing secret from Stripe |
| `DATABASE_URL` | Production only | Full DB connection string |
| `MAIL_SERVER` | No | SMTP host |
| `MAIL_PORT` | No | SMTP port (default 587) |
| `MAIL_USERNAME` | No | SMTP username |
| `MAIL_PASSWORD` | No | SMTP password |

---

## Stripe Integration

Payments use the **Payment Intents API** with Stripe Elements.

### Local webhook testing

Stripe cannot reach `localhost` directly. Use the [Stripe CLI](https://stripe.com/docs/stripe-cli) to forward events:

```bash
stripe listen --forward-to localhost:5000/checkout/webhook
```

The CLI will print a webhook signing secret (`whsec_...`) — paste it into your `.env` as `STRIPE_WEBHOOK_SECRET`.

### Test cards

| Card number | Scenario |
|---|---|
| `4242 4242 4242 4242` | Successful payment |
| `4000 0025 0000 3155` | 3D Secure required |
| `4000 0000 0000 9995` | Payment declined |

Use any future expiry date and any 3-digit CVC.

---

## Running Tests

```bash
pytest
```

Tests use an in-memory SQLite database and a fake Stripe key — no real credentials are needed.

---

## Database Migrations

After changing a model, generate and apply a migration:

```bash
flask db migrate -m "describe your change"
flask db upgrade
```

---

## Configuration Modes

The app factory reads the `FLASK_ENV` environment variable (defaults to `development`):

| Mode | Class | Database |
|---|---|---|
| `development` | `DevelopmentConfig` | SQLite (`instance/store_dev.db`) |
| `testing` | `TestingConfig` | In-memory SQLite |
| `production` | `ProductionConfig` | `DATABASE_URL` env var (required) |

In production, `ProductionConfig.validate()` is called at startup and raises immediately if any required variable is missing.

---

## Admin Access

A user is granted admin access by setting `is_admin = True` on their `User` record directly in the database. The admin panel lives at `/admin/` and is protected by both `@login_required` and a custom `@admin_required` decorator.

---

## URL Map (quick reference)

| URL | Description |
|---|---|
| `/` | Product listing with search and category filter |
| `/product/<id>` | Product detail page |
| `/auth/register` | Create account |
| `/auth/login` | Log in |
| `/auth/logout` | Log out |
| `/cart/` | View cart |
| `/cart/add/<id>` | Add item to cart (POST) |
| `/cart/update/<id>` | Update quantity (POST) |
| `/cart/remove/<id>` | Remove item (POST) |
| `/cart/clear` | Clear cart (POST) |
| `/checkout/` | Shipping details form |
| `/checkout/payment` | Stripe payment page |
| `/checkout/confirm` | Post-payment confirmation |
| `/checkout/webhook` | Stripe webhook receiver |
| `/orders/` | Order history (login required) |
| `/orders/<id>` | Order detail (login required) |
| `/admin/` | Admin dashboard (admin only) |
| `/admin/products` | Manage products |
| `/admin/orders` | Manage orders |
