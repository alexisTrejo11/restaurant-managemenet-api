from django.db import models
from django.utils import timezone

class Reservation(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('BOOKED', 'Booked'),
        ('ATTENDED', 'Attended'),
        ('NOT_ATTENDED', 'Not Attended'),
        ('CANCELLED', 'Cancelled'),
    ]

    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255)
    customer_number = models.IntegerField()
    email = models.CharField(max_length=255)
    table = models.ForeignKey('tables.Table', on_delete=models.PROTECT, related_name='reservations')
    reservation_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    @staticmethod
    def from_dict(dict_data):
        return Reservation(
            name = dict_data.get('name'),
            email = dict_data.get('email'),
            phone_number = dict_data.get('phone_number'),
            customer_number = dict_data.get('customer_number'),
            reservation_date = dict_data.get('reservation_date'),
        )

    def update_status(self, new_status):
        if new_status == "PENDING":
            self.set_as_pending()
        elif new_status == "CANCELLED":
            self.set_as_cancelled()
        elif new_status == "BOOKED":
            self.set_as_booked()
        elif new_status == "NOT_ATTENDED":
            self.set_as_not_attended()


    def set_as_pending(self):
        self.status = self.STATUS_CHOICES[0][0]

    def set_as_cancelled(self):
        self.status = self.STATUS_CHOICES[4][0]
        self.cancelled_at = timezone.now()

    def set_as_booked(self):
        self.status = self.STATUS_CHOICES[1][0]

    def set_as_attended(self):
        self.status = self.STATUS_CHOICES[2][0]

    def set_as_not_attended(self):
        self.status = self.STATUS_CHOICES[3][0]

    class Meta:
        db_table = 'reservations'
        verbose_name = 'Reservation'
        verbose_name_plural = 'Reservations'

    def __str__(self):
        return f'{self.name} - {self.reservation_date}'
