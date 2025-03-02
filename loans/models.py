from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import math

class Loan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    loan_id = models.AutoField(primary_key=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)  # Principal Amount
    tenure = models.IntegerField()  # Tenure in months
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)  # Annual interest rate (in %)
    start_date = models.DateField(auto_now_add=True)
    is_closed = models.BooleanField(default=False)

    def calculate_monthly_installment(self):
        """
        Calculate EMI (Equated Monthly Installment) using compound interest formula:
        EMI = P * r * (1 + r)^n / ((1 + r)^n - 1)
        where:
        - P = loan amount (principal)
        - r = monthly interest rate (annual_rate / 12 / 100)
        - n = tenure in months
        """
        P = float(self.amount)
        r = float(self.interest_rate) / 12 / 100
        n = self.tenure

        if r == 0:  # If interest rate is 0%
            return round(P / n, 2)

        emi = P * r * (math.pow(1 + r, n)) / (math.pow(1 + r, n) - 1)
        return round(emi, 2)

    def calculate_total_interest(self):
        """ Total interest = (Monthly Installment * tenure) - Principal """
        total_payment = self.calculate_monthly_installment() * self.tenure
        total_interest = total_payment - float(self.amount)
        return round(total_interest, 2)

    def calculate_foreclosure_amount(self, months_paid):
        """
        Calculate foreclosure amount if the user wants to pay off the loan early.
        Formula: Remaining Principal = P * ((1 + r)^n - (1 + r)^m) / ((1 + r)^n - 1)
        where:
        - m = months already paid
        """
        P = float(self.amount)
        r = float(self.interest_rate) / 12 / 100
        n = self.tenure
        m = months_paid

        if r == 0:
            return round(P * (1 - (m / n)), 2)

        remaining_principal = P * (math.pow(1 + r, n) - math.pow(1 + r, m)) / (math.pow(1 + r, n) - 1)
        return round(remaining_principal, 2)

    def calculate_payment_schedule(self):
        """
        Generate a list of monthly payment details, including:
        - Month
        - EMI
        - Principal Paid
        - Interest Paid
        - Remaining Balance
        """
        schedule = []
        remaining_balance = float(self.amount)
        emi = self.calculate_monthly_installment()
        r = float(self.interest_rate) / 12 / 100

        for month in range(1, self.tenure + 1):
            interest_paid = round(remaining_balance * r, 2)
            principal_paid = round(emi - interest_paid, 2)
            remaining_balance = round(remaining_balance - principal_paid, 2)

            schedule.append({
                "month": month,
                "emi": emi,
                "principal_paid": principal_paid,
                "interest_paid": interest_paid,
                "remaining_balance": max(remaining_balance, 0)
            })

        return schedule
