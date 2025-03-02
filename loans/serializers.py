from rest_framework import serializers
from .models import Loan

class LoanSerializer(serializers.ModelSerializer):
    monthly_installment = serializers.SerializerMethodField()
    total_interest = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    payment_schedule = serializers.SerializerMethodField()

    class Meta:
        model = Loan
        fields = ["loan_id", "amount", "tenure", "interest_rate", "monthly_installment", 
                  "total_interest", "total_amount", "payment_schedule"]
        read_only_fields = ["loan_id", "monthly_installment", "total_interest", "total_amount", "payment_schedule"]

    def validate_amount(self, value):
        """Validates loan amount: Must be between ₹1,000 and ₹100,000"""
        if not (1000 <= value <= 100000):
            raise serializers.ValidationError("Amount must be between ₹1,000 and ₹100,000.")
        return value

    def validate_tenure(self, value):
        """Validates tenure: Must be between 3 to 24 months"""
        if not (3 <= value <= 24):
            raise serializers.ValidationError("Tenure must be between 3 to 24 months.")
        return value

    def get_monthly_installment(self, obj):
        return obj.calculate_monthly_installment()

    def get_total_interest(self, obj):
        return obj.calculate_total_interest()

    def get_total_amount(self, obj):
        return obj.amount + obj.calculate_total_interest()

    def get_payment_schedule(self, obj):
        return obj.calculate_payment_schedule()
