from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from dateutil.relativedelta import relativedelta
from typing import List, Dict, Tuple
from sqlalchemy.orm import Session

from app.models.lease import Lease, LeaseScheduleEntry
from app.models.schedule import IFRS16Schedule
from app.models.journals import Payments
from .utils import make_json_safe


class IFRS16Calculator:
    """
    IFRS 16 Lease Accounting Calculator

    IFRS 16 eliminates the operating vs finance lease distinction for lessees.
    All leases are treated similarly to finance leases under ASC 842.

    Recognition:
    - Right-of-Use Asset (depreciated on straight-line basis)
    - Lease Liability (amortized using effective interest method)

    Expense Recognition:
    - Interest expense on lease liability (front-loaded)
    - Depreciation expense on ROU asset (straight-line)
    """

    def __init__(self, lease: Lease):
        self.lease = lease

    def fetch_payments_from_db(self, db: Session) -> List[Dict]:
        """
        Fetch payments from database for this lease
        Returns list of payment dictionaries with amount and due_date
        """
        payments = db.query(Payments).filter(
            Payments.contract_id == str(self.lease.id)
        ).order_by(Payments.due_date).all()
        
        if not payments:
            raise ValueError(f"No payments found for lease ID {self.lease.id}")
        
        payment_schedule = []
        for payment in payments:
            payment_schedule.append({
                "amount": Decimal(str(payment.amount)),
                "due_date": payment.due_date.date() if hasattr(payment.due_date, 'date') else payment.due_date,
                "payment_id": payment.id
            })
        
        print("payment schedule: ", payment_schedule)
        return payment_schedule
    
    def calculate_period_rate_from_payments(self) -> Decimal:
        """Calculate periodic interest rate from annual IBR"""
        annual_rate = self.lease.incremental_borrowing_rate / 100
        frequency_map = {
            "monthly": Decimal("12"),
            "quarterly": Decimal("4"),
            "annual": Decimal("1"),
        }
        periods = frequency_map.get(self.lease.payment_frequency, Decimal("12"))
        print("period_rate: ",  annual_rate / periods)
        return annual_rate / periods

    def calculate_payment_periods(self) -> int:
        """Calculate number of payment periods based on frequency"""
        frequency_map = {
            "monthly": self.lease.lease_term_months,
            "quarterly": self.lease.lease_term_months // 3,
            "annual": self.lease.lease_term_months // 12,
        }
        return frequency_map.get(self.lease.payment_frequency, self.lease.lease_term_months)

    # def calculate_period_rate(self) -> Decimal:
    #     """Calculate periodic interest rate from annual discount rate"""
    #     annual_rate = self.lease.discount_rate
    #     frequency_map = {
    #         "monthly": Decimal("12"),
    #         "quarterly": Decimal("4"),
    #         "annual": Decimal("1"),
    #     }
    #     periods = frequency_map.get(self.lease.payment_frequency, Decimal("12"))
    #     return annual_rate / periods

    # def calculate_present_value(self) -> Decimal:
    #     """Calculate present value of lease payments"""
    #     n_periods = self.calculate_payment_periods()
    #     period_rate = float(self.calculate_period_rate())
    #     payment = float(self.lease.periodic_payment)

    #     # Present value of annuity formula
    #     if period_rate == 0:
    #         pv = Decimal(str(payment * n_periods))
    #     else:
    #         pv_factor = (1 - (1 + period_rate) ** -n_periods) / period_rate
    #         pv = Decimal(str(payment * pv_factor))

    #     # Add present value of residual value
    #     if self.lease.residual_value > 0:
    #         residual_pv = float(self.lease.residual_value) / ((1 + period_rate) ** n_periods)
    #         pv += Decimal(str(residual_pv))

    #     return pv.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)

    def calculate_present_value_from_payments(
        self, payment_schedule: List[Dict], period_rate: Decimal
    ) -> Decimal:
        """
        Calculate present value of lease payments
        Uses beginning-of-period timing (annuity due)
        
        For annuity due (payment at beginning of period):
        PV = PMT + PMT × [(1 - (1 + r)^-(n-1)) / r]
        
        Or for individual payments:
        PV = Sum of [Payment_i / (1 + r)^(i-1)] for i = 1 to n
        """
        pv = Decimal("0")
        rate = float(period_rate)
        
        # Calculate PV for each payment (beginning of period)
        for period_num, payment in enumerate(payment_schedule, start=1):
            payment_amount = float(payment["amount"])
            
            if rate == 0:
                discount_factor = 1.0
            else:
                # Beginning of period: discount by (period - 1)
                # Period 1 payment has no discount, period 2 discounted by 1 period, etc.
                discount_factor = 1.0 / ((1.0 + rate) ** period_num)
            
            payment_pv = Decimal(str(payment_amount * discount_factor))
            pv += payment_pv
        
        # Add present value of residual value if applicable
        if self.lease.residual_value > 0:
            n_periods = len(payment_schedule)
            if rate > 0:
                residual_pv = float(self.lease.residual_value) / ((1.0 + rate) ** n_periods)
                pv += Decimal(str(residual_pv))
            else:
                pv += self.lease.residual_value
        
        return pv.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # def calculate_initial_measurements(self) -> Tuple[Decimal, Decimal]:
    #     """
    #     Calculate initial ROU asset and lease liability under IFRS 16

    #     Lease Liability = PV of lease payments
    #     ROU Asset = Lease Liability + Initial Direct Costs + Prepaid Rent - Lease Incentives

    #     Note: IFRS 16 includes initial direct costs in ROU asset
    #     """
    #     lease_liability = self.calculate_present_value()

    #     rou_asset = (
    #         lease_liability
    #         + self.lease.initial_direct_costs
    #         + self.lease.prepaid_rent
    #         - self.lease.lease_incentives
    #     )

    #     return rou_asset, lease_liability

    def calculate_initial_measurements(
        self, payment_schedule: List[Dict], period_rate: Decimal
    ) -> Tuple[Decimal, Decimal]:
        """
        Calculate initial ROU asset and lease liability under IFRS 16
        
        Lease Liability = PV of lease payments
        ROU Asset = Lease Liability + Initial Direct Costs + Prepaid Rent - Lease Incentives

        Note: IFRS 16 includes initial direct costs in ROU asset
        """
        print("per rate: ", period_rate)
        lease_liability = self.calculate_present_value_from_payments(
            payment_schedule, period_rate
        )
        
        rou_asset = (
            lease_liability
            + self.lease.initial_direct_costs
            + self.lease.prepaid_rent
            - self.lease.lease_incentives
        )
        print("lease, rou : ", lease_liability, rou_asset)
        return rou_asset, lease_liability

    def generate_schedule(self, db: Session) -> IFRS16Schedule:
        """Generate complete IFRS 16 lease schedule"""

        # Fetch payments from database
        payment_schedule = self.fetch_payments_from_db(db)
        print("payment schedule from db: ", payment_schedule)
        
        # Calculate period rate based on payment frequency
        period_rate = self.calculate_period_rate_from_payments()
        print("period rate from db: ", period_rate)

        # Calculate initial measurements
        rou_asset, lease_liability = self.calculate_initial_measurements(
            payment_schedule, period_rate
        )
        print("rou_lease: ",rou_asset, lease_liability)

        # rou_asset, lease_liability = self.calculate_initial_measurements()
        # n_periods = self.calculate_payment_periods()
        # period_rate = self.calculate_period_rate()

        # entries = self._generate_ifrs16_schedule(
        #     rou_asset, lease_liability, n_periods, period_rate
        # )
        entries = self._generate_ifrs16_schedule(
                rou_asset, lease_liability, payment_schedule, period_rate
            )

        # Calculate totals from entries (skip period 0)
        actual_entries = [e for e in entries if e["period"] > 0]
        total_payments = sum(e["lease_payment"] for e in actual_entries)
        total_interest = sum(e["interest_expense"] for e in actual_entries)
        total_depreciation = sum(e["amortization"] for e in actual_entries)

         # Safe JSON Serializer
        entries = make_json_safe(entries)

        # Create schedule record
        schedule = IFRS16Schedule(
            lease_id=self.lease.id,
            initial_rou_asset=rou_asset,
            initial_lease_liability=lease_liability,
            total_payments=total_payments,
            total_interest=total_interest,
            total_depreciation=total_depreciation,
            schedule_data={"entries": entries,"payment_count": len(payment_schedule)},
        )
        db.add(schedule)

        # Create schedule entries (skip period 0 for database storage)
        for entry_data in entries:
            if entry_data["period"] > 0:
                entry = LeaseScheduleEntry(
                    lease_id=self.lease.id,
                    schedule_type="IFRS16",
                    **entry_data
                )
                db.add(entry)

        db.commit()
        db.refresh(schedule)
        return schedule

    def _generate_ifrs16_schedule(
        self, rou_asset: Decimal, lease_liability: Decimal, payment_schedule: List[Dict], period_rate: Decimal
    ) -> List[Dict]:
        """
        Generate IFRS 16 lease schedule

        Key differences from ASC 842:
        - No operating vs finance lease distinction
        - Depreciation is always straight-line
        - Interest expense calculated on liability balance (front-loaded)
        - Total expense is higher in early periods, lower in later periods
        """
        entries = []
        n_periods = len(payment_schedule)

        # remaining_liability = lease_liability
        # remaining_asset = rou_asset

        # Straight-line depreciation
        total_payments = sum(p["amount"] for p in payment_schedule)
        total_lease_cost = total_payments + self.lease.initial_direct_costs
        depreciation_per_period = (rou_asset / Decimal(str(n_periods))).quantize(
            Decimal("0.001"), rounding=ROUND_HALF_UP
        )

        print("total_payment: ", total_payments)
        print("total_lease_cost: ", total_lease_cost)

        # Period 0: Initial measurement
        entries.append({
            "period": 0,
            "period_date": self.lease.commencement_date,
            "lease_payment": Decimal("0"),
            "interest_expense": Decimal("0"),
            "principal_reduction": Decimal("0"),
            "lease_liability_beginning": lease_liability,
            "lease_liability_ending": lease_liability,
            "rou_asset_beginning": rou_asset,
            "amortization": Decimal("0"),
            "rou_asset_ending": rou_asset,
            "total_expense": Decimal("0"),
        })

          # Track running balances
        liability_balance = lease_liability
        asset_balance = rou_asset
        
        for period_num, payment_info in enumerate(payment_schedule, start=1):
            print("period num, payment_info: ", period_num, payment_info)
            payment_amount = payment_info["amount"]
            period_date = payment_info["due_date"]
            
            # Beginning balances
            liability_beginning = liability_balance
            asset_beginning = asset_balance
            
            # interest_expense = (liability_beginning * period_rate).quantize(
            #     Decimal("0.01"), rounding=ROUND_HALF_UP
            # )

            # Step 1: Make payment (principal reduction)
            principal_reduction = payment_amount
            liability_after_payment = liability_beginning - principal_reduction
            
            # Step 2: Accrue interest on remaining liability
            interest_expense = (liability_beginning * period_rate).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            print("liability beginning: ", liability_beginning)
            # Step 3: Add accrued interest to liability
            liability_ending = liability_after_payment + interest_expense
            print("liability ending: ", liability_ending)

            # Depreciation (straight-line)
            if period_num == n_periods:
                # Last period: depreciate remaining balance to ensure ROU asset reaches zero
                depreciation = asset_balance
            else:
                depreciation = depreciation_per_period

            asset_ending = asset_balance - depreciation

            # Total expense = Interest + Depreciation
            total_expense = interest_expense + depreciation

            entries.append({
                "period": period_num,
                "period_date": period_date,
                "lease_payment": payment_amount,
                "interest_expense": interest_expense,
                "principal_reduction": principal_reduction,
                "lease_liability_beginning": liability_beginning,
                "lease_liability_ending": max(liability_ending, Decimal("0")),
                "rou_asset_beginning": asset_beginning,
                "amortization": depreciation,  # Called depreciation in IFRS 16
                "rou_asset_ending": max(asset_ending, Decimal("0")),
                "total_expense": total_expense,
            })
            print("entries: ", entries[-1])
            # Update balances
            liability_balance = max(liability_ending, Decimal("0"))
            asset_balance = max(asset_ending, Decimal("0"))

        return entries

    # def _calculate_period_date(self, period: int) -> date:
    #     """Calculate the date for a given period"""
    #     frequency_map = {
    #         "monthly": relativedelta(months=period),
    #         "quarterly": relativedelta(months=period * 3),
    #         "annual": relativedelta(years=period),
    #     }
    #     delta = frequency_map.get(self.lease.payment_frequency, relativedelta(months=period))
    #     return self.lease.commencement_date + delta
