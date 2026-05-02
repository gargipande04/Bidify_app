from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError



class Category(models.Model):
    name = models.CharField(max_length=80)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )

    class Meta:
        unique_together = ("name", "parent")

    def clean(self):
        # Prevent parent = self
        if self.parent_id and self.parent_id == self.id:
            raise ValidationError({"parent": "A category cannot be its own parent."})

    def save(self, *args, **kwargs):
        # Run validation before saving
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        """Return a label for the category."""
        if self.parent:
            return f"{self.parent} / {self.name}"
        return self.name


class User(AbstractUser):
    profile_picture = models.ImageField(upload_to="profile_pictures/", null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    interests = models.ManyToManyField(Category, related_name="interested_users", blank=True)


class Item(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="items")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="items")
    title = models.CharField(max_length=200)
    description = models.TextField()
    starting_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    image = models.ImageField(upload_to="item_images/", null=True, blank=True)
    end_time = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)
    email_sent = models.BooleanField(default=False)

    def __str__(self):
        """Return a item label."""
        return self.title


class Question(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="questions")
    asked_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    answer_text = models.TextField(blank=True)
    answered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="answers",
    )
    answered_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        """Return a summary of the question and author."""
        return f"Question on {self.item.title} by {self.asked_by}"


class Bid(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="bids")
    bidder = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bids")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        """Return a summary of the bid."""
        return f"{self.bidder} bid {self.amount} on {self.item.title}"


class FavoriteBid(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favorite_bids")
    bid = models.ForeignKey(Bid, on_delete=models.CASCADE, related_name="favorites")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("user", "bid")

    def __str__(self):
        """Return a summary of the favorite bid entry."""
        return f"{self.user} favorited bid {self.bid_id}"


class FavoriteItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favorite_items")
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="favorites")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("user", "item")

    def __str__(self):
        """Return a summary of the favorite item entry."""
        return f"{self.user} favorited item {self.item_id}"


class PageView(models.Model):
    count = models.IntegerField(default=0)

    def __str__(self):
        """Return a label for the page view counter."""
        return f"Page view count: {self.count}"