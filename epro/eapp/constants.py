# eapp/constants.py
# from enum import Enum

class PaymentStatus:
    PENDING = 'Pending'
    SUCCESS = 'Success'
    FAILED = 'Failed'

    CHOICES = [
        (PENDING, 'Pending'),
        (SUCCESS, 'Success'),
        (FAILED, 'Failed'),
    ]
