class EmailService:
    def __init__(self, email_client):
        self.email_client = email_client

    def send_email(self, recipient, subject, body):
        self.email_client.send_email(recipient, subject, body)
    
    def send_reservation_confirmation(self, reservation):
        subject = "Reservation Confirmation"
        body = f"Dear {reservation.name},\n\nYour reservation for {reservation.customer_number} people on {reservation.reservation_date} has been confirmed.\n\nThank you!"
        self.send_email(reservation.email, subject, body)