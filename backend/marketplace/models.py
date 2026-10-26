
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Q


class AuthorProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="author_profile",
    )
    display_name = models.CharField(max_length=120)
    bio = models.TextField(blank=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.display_name


class BookSummary(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PENDING = "pending", "Pending Review"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        ARCHIVED = "archived", "Archived"

    author = models.ForeignKey(
        AuthorProfile,
        on_delete=models.PROTECT,
        related_name="summaries",
    )
    book_title = models.CharField(max_length=250)
    book_author = models.CharField(max_length=200)
    description = models.TextField()
    cover_image_url = models.URLField(blank=True)
    preview = models.TextField()
    full_content = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )
    rights_confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.book_title} - {self.author.display_name}"

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=Q(price__gte=Decimal("0.00")),
                name="summary_price_nonnegative",
            ),
        ]


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"
        REFUNDED = "refunded", "Refunded"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="marketplace_orders",
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="INR")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    razorpay_order_id = models.CharField(
        max_length=100, unique=True, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.pk} - {self.status}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name="items",
    )
    summary = models.ForeignKey(
        BookSummary,
        on_delete=models.PROTECT,
        related_name="order_items",
    )
    # Snapshot the seller and price when the order is created.
    author = models.ForeignKey(
        AuthorProfile,
        on_delete=models.PROTECT,
        related_name="sales",
    )
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    commission_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("10.00"),
    )

    def __str__(self):
        return f"Order #{self.order_id} - {self.summary.book_title}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["order", "summary"],
                name="unique_summary_per_order",
            ),
        ]


class Payment(models.Model):
    class Status(models.TextChoices):
        CREATED = "created", "Created"
        AUTHORIZED = "authorized", "Authorized"
        CAPTURED = "captured", "Captured"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"

    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name="payments",
    )
    razorpay_payment_id = models.CharField(
        max_length=100, unique=True, null=True, blank=True
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.CREATED,
        db_index=True,
    )
    signature_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Payment for order #{self.order_id}"


class LibraryAccess(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="purchased_summaries",
    )
    summary = models.ForeignKey(
        BookSummary,
        on_delete=models.PROTECT,
        related_name="library_entries",
    )
    order_item = models.OneToOneField(
        OrderItem,
        on_delete=models.PROTECT,
        related_name="library_access",
    )
    granted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "summary"],
                name="unique_user_summary_access",
            ),
        ]