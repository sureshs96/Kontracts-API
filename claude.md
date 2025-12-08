# Lease Accounting API - Project Context

## Project Overview
A FastAPI-based application for generating ASC 842 (US GAAP) and IFRS 16 (International) lease accounting schedules with PostgreSQL persistence. This API helps organizations calculate lease liabilities, right-of-use assets, and generate period-by-period amortization schedules compliant with modern lease accounting standards.

## Tech Stack
- **Framework**: FastAPI 0.115.0
- **Server**: Uvicorn 0.30.6
- **Database**: PostgreSQL with SQLAlchemy 2.0.35 ORM
- **Migrations**: Alembic 1.13.3
- **Validation**: Pydantic 2.9.2
- **Data Processing**: Pandas 2.2.3, NumPy 2.1.2
- **Deployment**: Docker & Docker Compose
- **Python**: 3.11+

## Architecture

### Project Structure
```
app/
├── api/v1/
│   ├── leases.py          # Lease CRUD endpoints
│   └── schedules.py       # Schedule generation endpoints
├── models/
│   ├── lease.py           # Lease ORM models
│   └── schedule.py        # Schedule ORM models
├── schemas/
│   ├── lease.py           # Pydantic schemas for leases
│   └── schedule.py        # Pydantic schemas for schedules
├── services/
│   ├── asc842_calculator.py   # ASC 842 calculation logic
│   └── ifrs16_calculator.py   # IFRS 16 calculation logic
├── database.py            # Database configuration
└── main.py                # FastAPI application entry point
```

### Key Components
1. **API Layer** (`app/api/v1/`): RESTful endpoints for lease management and schedule generation
2. **Models Layer** (`app/models/`): SQLAlchemy ORM models for database persistence
3. **Schemas Layer** (`app/schemas/`): Pydantic models for request/response validation
4. **Services Layer** (`app/services/`): Business logic for lease calculations
5. **Database Layer** (`app/database.py`): Database session management and configuration

## Domain Knowledge

### Lease Accounting Standards

#### ASC 842 (US GAAP)
- **Finance Leases**: Front-loaded expense recognition with separate interest expense and ROU asset amortization
- **Operating Leases**: Straight-line total expense recognition (interest + amortization combined)
- Both require recognition of lease liability and ROU asset on balance sheet
- Uses Incremental Borrowing Rate (IBR) for present value calculations

#### IFRS 16 (International)
- **Single Model**: All leases treated similarly (no operating vs. finance distinction)
- Straight-line depreciation of ROU asset
- Interest expense calculated using effective interest method
- Results in front-loaded total expense pattern
- Uses discount rate (typically IBR) for present value

### Key Calculations

#### Present Value Formula
```
PV = PMT × [(1 - (1 + r)^-n) / r] + RV / (1 + r)^n
```
- PMT: Periodic payment amount
- r: Periodic discount rate (annual rate / payment frequency)
- n: Total number of payment periods
- RV: Residual value at lease end

#### Initial Measurements
```
Lease Liability = PV of lease payments
ROU Asset = Lease Liability + Initial Direct Costs + Prepaid Rent - Lease Incentives
```

#### Finance Lease Calculations (ASC 842)
```
Interest Expense = Beginning Lease Liability × Periodic Rate
Principal Reduction = Payment - Interest Expense
Amortization = ROU Asset / Lease Term (straight-line)
Total Expense = Interest Expense + Amortization
```

#### Operating Lease Calculations (ASC 842)
```
Total Lease Cost = Sum of all payments + Initial Direct Costs
Straight-line Expense = Total Lease Cost / Lease Term
Amortization = Straight-line Expense - Interest Expense
Interest Expense = Beginning Lease Liability × Periodic Rate
```

#### IFRS 16 Calculations
```
Interest Expense = Beginning Lease Liability × Discount Rate
Depreciation = ROU Asset / Lease Term (straight-line)
Total Expense = Interest Expense + Depreciation
```

## Database Schema

### Tables
1. **leases**: Stores lease contract information
   - Lease terms, payment details, discount rates
   - Classification (operating/finance for ASC 842)
   - Initial costs, prepayments, incentives

2. **asc842_schedules**: Summary data for ASC 842 calculations
   - Initial lease liability and ROU asset
   - Total interest, amortization, and lease cost

3. **ifrs16_schedules**: Summary data for IFRS 16 calculations
   - Initial lease liability and ROU asset
   - Total interest and depreciation

4. **lease_schedule_entries**: Period-by-period detail
   - Monthly/quarterly breakdown of liability, ROU asset
   - Interest expense, principal reduction, amortization/depreciation
   - Running balances for each period

## API Endpoints

### Lease Management
- `POST /api/v1/leases/` - Create new lease
- `GET /api/v1/leases/` - List all leases
- `GET /api/v1/leases/{lease_id}` - Get specific lease
- `PUT /api/v1/leases/{lease_id}` - Update lease
- `DELETE /api/v1/leases/{lease_id}` - Delete lease

### Schedule Generation
- `POST /api/v1/schedules/asc842/{lease_id}` - Generate ASC 842 schedule
- `POST /api/v1/schedules/ifrs16/{lease_id}` - Generate IFRS 16 schedule
- `GET /api/v1/schedules/{standard}/{lease_id}` - Get schedule summary
- `GET /api/v1/schedules/entries/{lease_id}/{standard}` - Get detailed entries
- `DELETE /api/v1/schedules/{standard}/{lease_id}` - Delete schedule

## Development Guidelines

### Code Style
- Follow PEP 8 Python style guidelines
- Use type hints for function parameters and returns
- Keep business logic in service layer, not in API endpoints
- Use Pydantic models for all request/response validation
- Document complex calculations with inline comments

### Testing Approach
- API documentation available at `/docs` (Swagger UI) and `/redoc`
- Test calculations manually using interactive docs
- Verify present value calculations match expected values
- Check period-by-period schedules for accuracy

### Database Migrations
- Use Alembic for all schema changes
- Generate migrations: `alembic revision --autogenerate -m "description"`
- Apply migrations: `alembic upgrade head`
- Rollback migrations: `alembic downgrade -1`

### Environment Setup
- Docker Compose handles PostgreSQL database automatically
- Local development requires manual PostgreSQL setup
- Environment variables configured in `.env` file
- Never commit `.env` file (use `.env.example` as template)

## Common Tasks

### Adding a New Lease Field
1. Update ORM model in `app/models/lease.py`
2. Update Pydantic schema in `app/schemas/lease.py`
3. Generate Alembic migration
4. Update calculation services if field affects calculations
5. Test via API docs

### Adding a New Calculation Standard
1. Create new calculator service in `app/services/`
2. Add ORM models for new schedule type
3. Add Pydantic schemas for new schedule type
4. Create API endpoints in `app/api/v1/schedules.py`
5. Update database schema via Alembic migration

### Debugging Calculations
- Check intermediate values (PV, initial liability, initial ROU asset)
- Verify periodic rates calculated correctly (annual rate / periods per year)
- Ensure running balances decrease properly over lease term
- Confirm total interest + principal equals total payments
- Check that final liability balance approaches zero

## Business Logic Notes

### Payment Frequencies
- Monthly: 12 periods per year
- Quarterly: 4 periods per year
- Annual: 1 period per year
- Periodic rate = annual rate / periods per year

### Lease Classification (ASC 842)
- **Finance lease** if any of:
  - Transfer of ownership at end
  - Purchase option reasonably certain to exercise
  - Lease term ≥ major part of economic life (typically 75%)
  - PV of payments ≥ substantially all of fair value (typically 90%)
  - Asset is specialized with no alternative use
- **Operating lease** if none of above criteria met

### Edge Cases
- Zero or negative ROU asset after adjustments
- Very long lease terms (360+ months)
- Variable payment structures (not yet implemented)
- Lease modifications (not yet implemented)
- Residual value guarantees

## Deployment

### Docker Deployment
```bash
docker-compose up -d
```
- Starts PostgreSQL and FastAPI containers
- Automatically runs migrations on startup
- API accessible at http://localhost:8001

### Local Development
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

## Useful Commands

### Database
```bash
# Generate migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

### Docker
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild containers
docker-compose up -d --build
```

### Development Server
```bash
# Run with auto-reload
uvicorn app.main:app --reload

# Run on specific port
uvicorn app.main:app --port 8080

# Run with specific host
uvicorn app.main:app --host 0.0.0.0
```

## Known Limitations
- Variable lease payments not yet supported
- Lease modifications require deleting and recreating schedules
- No support for short-term lease exemption (<12 months)
- No low-value asset exemption
- Residual value guarantees simplified in calculations
- No support for sale-leaseback transactions
- Payment frequency changes during lease term not supported
