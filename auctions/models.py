from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, DecimalValidator, RegexValidator

class User(AbstractUser):
    pass
    def __str__(self):
        return self.username


class Category(models.Model):
    name = models.CharField(max_length=30)
    def __str__(self):
        return f"{self.name}"


class Listing(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=300)
    image = models.CharField(max_length=200, validators=[RegexValidator(regex="([^\\s]+(\\.(?i)(jpe?g|png|gif|bmp))$)")], blank=True)
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2 , default=0, validators=[MinValueValidator(0)])
    date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    winner_id = models.IntegerField(blank=True, null=True)
    winning_bid = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    owner_id = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="sellerListings")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True, related_name="categoryListings")
    def __str__(self):
        return f"{self.title} (id:{self.id})"

class Bid(models.Model):
    bid_amount =  models.DecimalField(max_digits=10, decimal_places=2 , default=0, validators=[MinValueValidator(0.01)])
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userBid")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listingBid")
    Timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.bid_amount} by {self.user_id} on {self.listing_id}"

class Comment(models.Model):
    comment = models.TextField(max_length=300)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userComments")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listingComments")
    Timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Comment:{self.comment} by {self.user_id} on {self.listing_id}"


class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userWatching")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listingWatchers")
    def __str__(self):
        return f"{self.user_id} watching {self.listing_id}"