from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

import settings


class Genre(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Actor(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    actors = models.ManyToManyField(to=Actor)
    genres = models.ManyToManyField(to=Genre)

    class Meta:
        indexes = [
            models.Index(fields=["title"])
        ]

    def __str__(self):
        return self.title


class CinemaHall(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()

    def capacity(self):
        return self.rows * self.seats_in_row

    def __str__(self):
        return self.name


class MovieSession(models.Model):
    show_time = models.DateTimeField()
    cinema_hall = models.ForeignKey(to=CinemaHall, on_delete=models.CASCADE)
    movie = models.ForeignKey(to=Movie, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.movie.title} {str(self.show_time)}"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.created_at}"


class Ticket(models.Model):
    movie_session = models.ForeignKey(MovieSession,
                                      on_delete=models.CASCADE,
                                      related_name="tickets")
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    row = models.IntegerField()
    seat = models.IntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["row", "seat", "movie_session"],
                                    name="unique_ticket")
        ]

    def __str__(self):
        return f"{self.movie_session} " \
               f"(row: {self.row}, seat: {self.seat})"

    def clean(self):
        if not (1 <= self.row <= self.movie_session.cinema_hall.rows):
            raise ValidationError({
                "row": (f"row number must be in available range:"
                        f" (1, rows):"
                        f" (1, {self.movie_session.cinema_hall.rows})")})
        if not (1 <= self.seat <= self.movie_session.cinema_hall.seats_in_row):
            raise ValidationError({
                "seat": (f"seat number must be in available range:"
                         f" (1, seats_in_row): "
                         f"(1, {self.movie_session.cinema_hall.seats_in_row})")
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(Ticket, self).save(*args, **kwargs)


class User(AbstractUser):
    pass
