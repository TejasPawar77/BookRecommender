from rest_framework import serializers

from .models import AuthorProfile, BookSummary, Order, OrderItem


class AuthorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthorProfile
        fields = ["id", "display_name", "bio", "is_approved"]
        read_only_fields = ["id", "is_approved"]


class PublicSummarySerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(
        source="author.display_name",
        read_only=True,
    )

    class Meta:
        model = BookSummary
        fields = [
            "id",
            "book_title",
            "book_author",
            "description",
            "cover_image_url",
            "preview",
            "price",
            "author_name",
            "created_at",
        ]


class AuthorSummarySerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(
        source="author.display_name",
        read_only=True,
    )

    class Meta:
        model = BookSummary
        fields = [
            "id",
            "book_title",
            "book_author",
            "description",
            "cover_image_url",
            "preview",
            "full_content",
            "price",
            "status",
            "rights_confirmed",
            "author_name",
            "created_at",
        ]
        read_only_fields = ["id", "status", "author_name", "created_at"]

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "The summary price must be greater than zero."
            )
        return value

    def validate_rights_confirmed(self, value):
        if not value:
            raise serializers.ValidationError(
                "Confirm that you have the rights to sell this content."
            )
        return value

    def validate(self, attrs):
        request = self.context.get("request")
        if request and request.method == "POST":
            if not request.user.author_profile.is_approved:
                raise serializers.ValidationError(
                    "Your author account is not approved yet."
                )
        return attrs


class OrderItemSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(
        source="summary.book_title",
        read_only=True,
    )

    class Meta:
        model = OrderItem
        fields = ["id", "book_title", "unit_price", "author"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "total_amount",
            "currency",
            "status",
            "created_at",
            "items",
        ]