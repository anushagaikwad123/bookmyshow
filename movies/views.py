from django.shortcuts import render, get_object_or_404, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from .models import Movie, Theater, Seat, Booking  
from django.utils import timezone
from datetime import timedelta 

# HELPER FUNCTION: Releases seats that were reserved > 5 minutes ago but not booked
def release_expired_seats():
    expiration_time = timezone.now() - timedelta(minutes=5)
    expired_seats = Seat.objects.filter(
        is_reserved=True, 
        is_booked=False, 
        reserved_at__lt=expiration_time
    )
    for seat in expired_seats:
        seat.is_reserved = False
        seat.reserved_at = None
        seat.save()

def index(request):
    movies = Movie.objects.all()
    
    # TASK 1: MULTIPLE FILTERS
    genre_query = request.GET.get('genre')
    lang_query = request.GET.get('language')

    if genre_query:
        movies = movies.filter(genre=genre_query)
    if lang_query:
        movies = movies.filter(language=lang_query)

    return render(request, 'movies/movie_list.html', {'movies': movies})

def theater_list(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    theaters = Theater.objects.filter(movie=movie)
    return render(request, 'movies/theater_list.html', {'movie': movie, 'theaters': theaters})

@login_required(login_url='/login/')
def book_seats(request, theater_id):
    # Call the cleanup function first
    release_expired_seats()

    theaters = get_object_or_404(Theater, id=theater_id)
    seats = Seat.objects.filter(theater=theaters)
    
    if request.method == 'POST':
        selected_Seats = request.POST.getlist('seats')
        error_seats = []
        booked_seat_numbers = []

        if not selected_Seats:
            return render(request, "movies/seat_selection.html", {'theaters': theaters, "seats": seats, 'error': "No seat selected"})

        for seat_id in selected_Seats:
            seat = get_object_or_404(Seat, id=seat_id, theater=theaters)
            
            # Check if seat is permanently booked or temporarily reserved by someone else
            if seat.is_booked or (seat.is_reserved and seat.reserved_at > timezone.now() - timedelta(minutes=5)):
                error_seats.append(seat.seat_number)
                continue
            
            try:
                # MARK AS BOOKED (In a real app, you might do this after payment)
                Booking.objects.create(
                    user=request.user,
                    seat=seat,
                    movie=theaters.movie,
                    theater=theaters
                )
                seat.is_booked = True
                seat.is_reserved = False # Clear reservation once fully booked
                seat.save()
                booked_seat_numbers.append(seat.seat_number)
            except IntegrityError:
                error_seats.append(seat.seat_number)

        if error_seats:
            error_message = f"Unavailable/Already booked: {', '.join(error_seats)}"
            return render(request, 'movies/seat_selection.html', {'theaters': theaters, "seats": seats, 'error': error_message})
        
        # TASK 2: EMAIL
        if booked_seat_numbers:
            subject = f"Booking Confirmed: {theaters.movie.name}"
            message = f"Hi {request.user.username}, your booking for {theaters.movie.name} is successful! Seats: {', '.join(booked_seat_numbers)}"
            send_mail(subject, message, settings.EMAIL_HOST_USER, [request.user.email])

        return redirect('profile')
            
    return render(request, 'movies/seat_selection.html', {'theaters': theaters, "seats": seats})