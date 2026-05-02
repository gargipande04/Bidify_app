from rest_framework import serializers
from .models import Question, User, Bid, FavoriteBid, Category


class QuestionSerializer(serializers.ModelSerializer):
    asked_by = serializers.CharField(source="asked_by.username", read_only=True)
    answered_by = serializers.CharField(source="answered_by.username", read_only=True)

    class Meta:
        model = Question
        fields = [
            "id",
            "text",
            "asked_by",
            "created_at",
            "answer_text",
            "answered_by",
            "answered_at",
        ]


class UserProfileSerializer(serializers.ModelSerializer):
    interests = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        many=True,
        required=False,
    )
    interests_detail = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "profile_picture",
            "date_of_birth",
            "interests",
            "interests_detail",
        ]
        read_only_fields = ["id", "username"]

    def get_interests_detail(self, obj):
        return [
            {
                "id": category.id,
                "name": category.name,
                "parent_id": category.parent_id,
                "parent_name": category.parent.name if category.parent else None,
            }
            for category in obj.interests.select_related("parent").all()
        ]


class BidSerializer(serializers.ModelSerializer):
    bidder_username = serializers.CharField(source="bidder.username", read_only=True)
    item_id = serializers.IntegerField(source="item.id", read_only=True)
    item_title = serializers.CharField(source="item.title", read_only=True)
    item_image = serializers.ImageField(source="item.image", read_only=True)

    class Meta:
        model = Bid
        fields = [
            "id",
            "amount",
            "created_at",
            "bidder_username",
            "item_id",
            "item_title",
            "item_image",
        ]


class FavoriteBidSerializer(serializers.ModelSerializer):
    bid = BidSerializer(read_only=True)

    class Meta:
        model = FavoriteBid
        fields = ["id", "created_at", "bid"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "parent"]
