from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Loan
from .serializers import LoanSerializer
from django.contrib.auth.models import User

class LoanAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, loan_id=None):
        """Users see their own loans, Admins see all loans"""
        if request.user.role == 'admin':
            loan = Loan.objects.all() if not loan_id else Loan.objects.filter(loan_id=loan_id).first()
        else:  # Normal User
            loan = Loan.objects.filter(user=request.user) if not loan_id else Loan.objects.filter(loan_id=loan_id, user=request.user).first()

        if not loan:
            return Response({"status": "error", "message": "Loan not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = LoanSerializer(loan, many=not loan_id)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        """Only Users can create a loan"""
        if request.user.role != 'user':
            return Response({"status": "error", "message": "Only Users can create loans"}, status=status.HTTP_403_FORBIDDEN)

        serializer = LoanSerializer(data=request.data)
        if serializer.is_valid():
            loan = serializer.save(user=request.user)

            return Response({
                "status": "success",
                "data": {
                    "loan_id": loan.loan_id,
                    "amount": loan.amount,
                    "tenure": loan.tenure,
                    "interest_rate": f"{loan.interest_rate}% yearly",
                    "monthly_installment": loan.calculate_monthly_installment(),
                    "total_interest": loan.calculate_total_interest(),
                    "total_amount": loan.amount + loan.calculate_total_interest(),
                    "payment_schedule": loan.calculate_payment_schedule()
                }
            }, status=status.HTTP_201_CREATED)

        return Response({"status": "error", "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, loan_id):
        """Only Admins can delete loans"""
        if request.user.role != 'admin':
            return Response({"status": "error", "message": "Only Admins can delete loans"}, status=status.HTTP_403_FORBIDDEN)

        loan = Loan.objects.filter(loan_id=loan_id).first()
        if not loan:
            return Response({"status": "error", "message": "Loan not found"}, status=status.HTTP_404_NOT_FOUND)

        loan.delete()
        return Response({"status": "success", "message": "Loan deleted successfully"}, status=status.HTTP_200_OK)


class ForeclosureAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, loan_id):
        """Calculate foreclosure amount if the user wants to pay early"""
        loan = Loan.objects.filter(loan_id=loan_id, user=request.user).first()

        if not loan:
            return Response({"status": "error", "message": "Loan not found"}, status=status.HTTP_404_NOT_FOUND)

        months_paid = request.data.get("months_paid", 0)

        if months_paid < 0 or months_paid > loan.tenure:
            return Response({"status": "error", "message": "Invalid months paid"}, status=status.HTTP_400_BAD_REQUEST)

        foreclosure_amount = loan.calculate_foreclosure_amount(months_paid)

        return Response({
            "status": "success",
            "data": {
                "loan_id": loan.loan_id,
                "months_paid": months_paid,
                "foreclosure_amount": foreclosure_amount
            }
        }, status=status.HTTP_200_OK)
