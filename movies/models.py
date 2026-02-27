from django.db import models
from django.contrib.auth.models import User 
from django.utils import timezone
import datetime

class Movie(models.Model):
    # Existing fields
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="movies/")
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    cast = models.TextField()
    description = models.TextField(blank=True, null=True)

    # --- NEW FIELDS ---
    GENRE_CHOICES = [
        ('Action', 'Action'),
        ('Comedy', 'Comedy'),
        ('Romance', 'Romance'),
        ('Drama', 'Drama'),
        ('Horror', 'Horror'),
    ]
    LANGUAGE_CHOICES = [
        ('Hindi', 'Hindi'),
        ('English', 'English'),
        ('Marathi', 'Marathi'),
        ('Tamil', 'Tamil'),
        ('Telugu', 'Telugu'),
    ]

    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="movies/")
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    cast = models.TextField()
    description = models.TextField(blank=True, null=True)

    language = models.CharField(max_length=50, choices=LANGUAGE_CHOICES, default='Hindi')
    genre = models.CharField(max_length=100, choices=GENRE_CHOICES, default="Action")
    trailer_url = models.URLField(blank=True, null=True, help_text="YouTube Embed Link")
    # ------------------

    def __str__(self):
        return self.name

class Theater(models.Model):
    name = models.CharField(max_length=255)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='theaters')
    time = models.DateTimeField()

    def __str__(self):
        return f'{self.name} - {self.movie.name} at {self.time}'

class Seat(models.Model):
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE, related_name='seats')
    seat_number = models.CharField(max_length=10)
    is_booked = models.BooleanField(default=False)
    
    
    is_reserved = models.BooleanField(default=False)
    reserved_at = models.DateTimeField(null=True, blank=True)
    reserved_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    # ------------------------------

    def is_expired(self):
        """Check if the 5-minute reservation has timed out"""
        if self.is_reserved and self.reserved_at:
            return timezone.now() > self.reserved_at + datetime.timedelta(minutes=5)
        return False

    def __str__(self):
        return f'{self.seat_number} in {self.theater.name}'

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    seat = models.OneToOneField(Seat, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE)
    booked_at = models.DateTimeField(auto_now_add=True)
    # Added amount for Analytics later
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) 

    def __str__(self):
        return f'Booking by {self.user.username} for {self.seat.seat_number}'