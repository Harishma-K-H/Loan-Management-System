from django.urls import path
from .views import LoanAPIView,LoanForeclosureAPIView

urlpatterns = [
    path('loans/', LoanAPIView.as_view()),  # Get all loans & Create loan
    path('loans/<str:loan_id>/', LoanAPIView.as_view()),  # Get or Delete a loan by loan_id
    path('loans/<int:loan_id>/foreclose/', LoanForeclosureAPIView.as_view()),
]