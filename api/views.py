from __future__ import annotations

from datetime import datetime

from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.db.models import Q
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .categories import CATEGORY_TREE, ensure_categories
from .models import Bid, Category, FavoriteBid, FavoriteItem, Item, Question, User
from .serializers import BidSerializer, FavoriteBidSerializer, QuestionSerializer, UserProfileSerializer


def get_item_image_url(item: Item, request: HttpRequest) -> str | None:
    """Build an absolute image URL for an item if present."""
    if item.image:
        return request.build_absolute_uri(item.image.url)
    return None


def serialize_item(item: Item, request: HttpRequest) -> dict[str, object | None]:
    """Serialize an item for profile summary lists."""
    category = item.category
    return {
        "id": item.id,
        "title": item.title,
        "description": item.description,
        "end_time": item.end_time.isoformat(),
        "owner_username": item.owner.username,
        "starting_price": str(item.starting_price),
        "image": get_item_image_url(item, request),
        "category_id": category.id if category else None,
        "category_name": category.name if category else None,
        "category_parent": category.parent.name if category and category.parent else None,
    }


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def item_questions(request: HttpRequest, item_id: int) -> Response:
    """List or create questions for a specific item."""
    item = get_object_or_404(Item, pk=item_id)

    if request.method == "GET":
        qs = item.questions.order_by("created_at")
        serializer = QuestionSerializer(qs, many=True)
        return Response({"questions": serializer.data})

    if not request.user.is_authenticated:
        return Response(
            {"error": "Authentication required"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    serializer = QuestionSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    serializer.save(item=item, asked_by=request.user)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def answer_question(request: HttpRequest, question_id: int) -> Response:
    """Allow an item owner to answer a question."""
    q = get_object_or_404(Question, pk=question_id)
    if q.item.owner != request.user:
        return Response(
            {"error": "Only item owner can answer"},
            status=status.HTTP_403_FORBIDDEN,
        )

    answer_text: str = str(request.data.get("answer_text", "")).strip()
    if not answer_text:
        return Response(
            {"error": "answer_text is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    q.answer_text = answer_text
    q.answered_by = request.user
    q.answered_at = timezone.now()
    q.save()

    serializer = QuestionSerializer(q)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def items_list(request: HttpRequest) -> Response:
    """List active items with optional search query.

    Args:
        request: Incoming HTTP request.
    """
    q: str = str(request.GET.get("q", "")).strip()
    category_id = request.GET.get("category_id")
    now = timezone.now()

    qs = (
        Item.objects.filter(end_time__gt=now)
        .select_related("owner", "category", "category__parent")
        .order_by("end_time")
    )

    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))
    if category_id:
        qs = qs.filter(category_id=category_id)

    data = []
    for item in qs:
        category = item.category
        data.append(
            {
                "id": item.id,
                "title": item.title,
                "description": item.description,
                "end_time": item.end_time.isoformat(),
                "owner_username": item.owner.username,
                "starting_price": str(item.starting_price),
                "image": get_item_image_url(item, request),
                "category_id": category.id if category else None,
                "category_name": category.name if category else None,
                "category_parent": category.parent.name if category and category.parent else None,
            }
        )

    return Response({"items": data})


@api_view(["GET"])
@permission_classes([AllowAny])
def item_detail(request: HttpRequest, item_id: int) -> Response:
    """Return a single item's details.

    Args:
        request: Incoming HTTP request.
        item_id: Primary key of the item to fetch.
    """
    item = get_object_or_404(Item.objects.select_related("owner", "category", "category__parent"), pk=item_id)
    highest_bid = item.bids.select_related("bidder").order_by("-amount").first()
    bid_count = item.bids.count()
    category = item.category

    return Response(
        {
            "id": item.id,
            "title": item.title,
            "description": item.description,
            "end_time": item.end_time.isoformat(),
            "owner_username": item.owner.username,
            "starting_price": str(item.starting_price),
            "image": get_item_image_url(item, request),
            "highest_bid": str(highest_bid.amount) if highest_bid else None,
            "highest_bidder": highest_bid.bidder.username if highest_bid else None,
            "bid_count": bid_count,
            "category_id": category.id if category else None,
            "category_name": category.name if category else None,
            "category_parent": category.parent.name if category and category.parent else None,
        }
    )


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def item_bids(request: HttpRequest, item_id: int) -> Response:
    """List bids or place a new bid on an item."""
    item = get_object_or_404(Item.objects.select_related("owner"), pk=item_id)

    if request.method == "GET":
        bids = (
            Bid.objects.select_related("bidder", "item")
            .filter(item_id=item_id)
            .order_by("-amount", "created_at")
        )
        serializer = BidSerializer(bids, many=True, context={"request": request})
        return Response({"bids": serializer.data})

    # POST - place a bid
    if not request.user.is_authenticated:
        return Response(
            {"error": "You must be logged in to bid"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    # Check if user is the owner
    if item.owner == request.user:
        return Response(
            {"error": "You cannot bid on your own item"},
            status=status.HTTP_403_FORBIDDEN,
        )

    # Check if auction has ended
    if item.end_time <= timezone.now():
        return Response(
            {"error": "This auction has ended"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    amount = request.data.get("amount")
    if not amount:
        return Response(
            {"error": "Bid amount is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        amount_f = float(amount)
        if amount_f <= 0:
            return Response(
                {"error": "Bid amount must be positive"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    except (ValueError, TypeError):
        return Response(
            {"error": "Invalid bid amount"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Check if bid is higher than starting price
    if amount_f < float(item.starting_price):
        return Response(
            {"error": f"Bid must be at least £{item.starting_price}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Check if bid is higher than current highest bid
    highest_bid = item.bids.order_by("-amount").first()
    if highest_bid and amount_f <= float(highest_bid.amount):
        return Response(
            {"error": f"Bid must be higher than current highest bid (£{highest_bid.amount})"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    bid = Bid.objects.create(
        item=item,
        bidder=request.user,
        amount=amount_f,
    )

    serializer = BidSerializer(bid, context={"request": request})
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def toggle_favorite_bid(request: HttpRequest, bid_id: int) -> Response:
    """Add or remove a bid from the user's wishlist.

    Args:
        request: Incoming HTTP request.
        bid_id: Primary key of the bid to toggle.
    """
    bid = get_object_or_404(Bid, pk=bid_id)
    favorite, created = FavoriteBid.objects.get_or_create(user=request.user, bid=bid)
    if not created:
        favorite.delete()
        return Response({"favorited": False}, status=status.HTTP_200_OK)
    return Response({"favorited": True}, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def wishlist(request: HttpRequest) -> Response:
    """Return the current user's favorite bids.

    Args:
        request: Incoming HTTP request.
    """
    favorites = (
        FavoriteBid.objects.select_related("bid", "bid__item", "bid__bidder")
        .filter(user=request.user)
        .order_by("-created_at")
    )
    serializer = FavoriteBidSerializer(favorites, many=True, context={"request": request})
    return Response({"favorites": serializer.data})


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def toggle_favorite_item(request: HttpRequest, item_id: int) -> Response:
    """Toggle the current user's favorite status for an item.

    Args:
        request: Incoming HTTP request.
        item_id: Primary key of the item to toggle.
    """
    item = get_object_or_404(Item, pk=item_id)
    if request.method == "GET":
        is_favorited = FavoriteItem.objects.filter(user=request.user, item=item).exists()
        return Response({"favorited": is_favorited}, status=status.HTTP_200_OK)

    favorite, created = FavoriteItem.objects.get_or_create(user=request.user, item=item)
    if not created:
        favorite.delete()
        return Response({"favorited": False}, status=status.HTTP_200_OK)
    return Response({"favorited": True}, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def wishlist_items(request: HttpRequest) -> Response:
    """Return the current user's favorite items.

    Args:
        request: Incoming HTTP request.
    """
    favorites = (
        FavoriteItem.objects.select_related("item", "item__owner", "item__category", "item__category__parent")
        .filter(user=request.user)
        .order_by("-created_at")
    )
    items = [serialize_item(favorite.item, request) for favorite in favorites]
    return Response({"items": items}, status=status.HTTP_200_OK)


def main_spa(request: HttpRequest) -> HttpResponse:
    """Serve the single-page app shell."""
    return render(request, "api/spa/index.html", {})


def csrf_token(request: HttpRequest) -> JsonResponse:
    """Return a CSRF token for subsequent requests."""
    return JsonResponse({"csrfToken": get_token(request)})


@api_view(["POST"])
@permission_classes([AllowAny])
def signup(request: HttpRequest) -> Response:
    """Register a new user account."""
    username = request.data.get("username", "").strip()
    email = request.data.get("email", "").strip()
    password = request.data.get("password", "")
    interests = request.data.get("interests", [])

    if not username or not email or not password:
        return Response(
            {"error": "username, email, and password are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {"error": "Username already taken"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if User.objects.filter(email=email).exists():
        return Response(
            {"error": "Email already registered"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if isinstance(interests, list) and len(interests) > 5:
        return Response(
            {"error": "You can choose up to 5 interests."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = User.objects.create_user(username=username, email=email, password=password)
    if isinstance(interests, list) and interests:
        valid_ids = Category.objects.filter(id__in=interests).values_list("id", flat=True)
        user.interests.set(list(valid_ids))
    return Response(
        {"id": user.id, "username": user.username, "email": user.email},
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request: HttpRequest) -> Response:
    """Authenticate a user and start a session."""
    username = request.data.get("username", "").strip()
    password = request.data.get("password", "")

    if not username or not password:
        return Response(
            {"error": "username and password are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = authenticate(username=username, password=password)
    if not user:
        return Response(
            {"error": "Invalid username or password"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    auth_login(request, user)
    return Response({"success": "Login successful"}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([AllowAny])
def logout(request: HttpRequest) -> Response:
    """Log out the current user and clear the session."""
    auth_logout(request)
    return Response({"success": "Logged out successfully"}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request: HttpRequest) -> Response:
    """Return the current user's username.

    Args:
        request: Incoming HTTP request.
    """
    return Response({"username": request.user.username})


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def profile(request: HttpRequest) -> Response:
    """Retrieve or update the authenticated user's profile."""
    if request.method == "GET":
        serializer = UserProfileSerializer(request.user, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    serializer = UserProfileSerializer(
        request.user,
        data=request.data,
        partial=True,
        context={"request": request},
    )
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([AllowAny])
def categories_list(request: HttpRequest) -> Response:
    """Return a nested category tree for selection UIs.

    Args:
        request: Incoming HTTP request.
    """
    ensure_categories()
    data = []
    for group in CATEGORY_TREE:
        parent = Category.objects.filter(parent__isnull=True, name=group["name"]).first()
        if not parent:
            continue
        children = []
        for child_name in group["children"]:
            child = Category.objects.filter(parent=parent, name=child_name).first()
            if child:
                children.append({"id": child.id, "name": child.name, "parent_id": parent.id})
        data.append({"id": parent.id, "name": parent.name, "children": children})
    return Response({"categories": data})


@api_view(["GET"])
@permission_classes([AllowAny])
def recommendations(request: HttpRequest) -> Response:
    """Return items filtered by the authenticated user's interests.

    Args:
        request: Incoming HTTP request.
    """
    if not request.user.is_authenticated:
        return Response({"items": []}, status=status.HTTP_200_OK)

    interests = request.user.interests.all()
    if not interests.exists():
        return Response({"items": []}, status=status.HTTP_200_OK)

    now = timezone.now()
    qs = (
        Item.objects.filter(end_time__gt=now, category__in=interests)
        .select_related("owner", "category", "category__parent")
        .order_by("end_time")[:12]
    )
    data = []
    for item in qs:
        category = item.category
        data.append(
            {
                "id": item.id,
                "title": item.title,
                "description": item.description,
                "end_time": item.end_time.isoformat(),
                "owner_username": item.owner.username,
                "starting_price": str(item.starting_price),
                "image": get_item_image_url(item, request),
                "category_id": category.id if category else None,
                "category_name": category.name if category else None,
                "category_parent": category.parent.name if category and category.parent else None,
            }
        )
    return Response({"items": data}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def profile_items(request: HttpRequest) -> Response:
    """Return current and past items created by the user.

    Args:
        request: Incoming HTTP request.
    """
    now = timezone.now()
    qs = (
        Item.objects.filter(owner=request.user)
        .select_related("owner", "category", "category__parent")
        .order_by("-end_time")
    )
    current_items = [serialize_item(item, request) for item in qs.filter(end_time__gt=now)]
    past_items = [serialize_item(item, request) for item in qs.filter(end_time__lte=now)]
    return Response({"current": current_items, "past": past_items}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def profile_bids(request: HttpRequest) -> Response:
    """Return current and past bids made by the user.

    Args:
        request: Incoming HTTP request.
    """
    now = timezone.now()
    bids = (
        Bid.objects.filter(bidder=request.user)
        .select_related("item", "item__owner", "item__category", "item__category__parent")
        .order_by("-created_at")
    )
    current_bids = []
    past_bids = []
    for bid in bids:
        item_data = serialize_item(bid.item, request)
        bid_data = {
            "id": bid.id,
            "amount": str(bid.amount),
            "created_at": bid.created_at.isoformat(),
            "item": item_data,
        }
        if bid.item.end_time > now:
            current_bids.append(bid_data)
        else:
            past_bids.append(bid_data)
    return Response({"current": current_bids, "past": past_bids}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_item(request: HttpRequest) -> Response:
    """Create a new auction item for the authenticated user."""
    title = request.data.get("title", "").strip()
    description = request.data.get("description", "").strip()
    starting_price = request.data.get("starting_price")
    end_time = request.data.get("end_time")
    category_id = request.data.get("category_id")

    if not title:
        return Response({"error": "Title is required"}, status=status.HTTP_400_BAD_REQUEST)
    if not description:
        return Response({"error": "Description is required"}, status=status.HTTP_400_BAD_REQUEST)
    if not starting_price:
        return Response({"error": "Starting price is required"}, status=status.HTTP_400_BAD_REQUEST)
    if not end_time:
        return Response({"error": "End time is required"}, status=status.HTTP_400_BAD_REQUEST)
    if not category_id:
        return Response({"error": "Category is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        starting_price_f = float(starting_price)
        if starting_price_f < 0:
            return Response({"error": "Starting price must be positive"}, status=status.HTTP_400_BAD_REQUEST)
    except (ValueError, TypeError):
        return Response({"error": "Invalid starting price"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        end_time_dt = datetime.fromisoformat(str(end_time).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return Response({"error": "Invalid end time format"}, status=status.HTTP_400_BAD_REQUEST)

    category = get_object_or_404(Category, pk=category_id)

    item = Item.objects.create(
        owner=request.user,
        category=category,
        title=title,
        description=description,
        starting_price=starting_price_f,
        end_time=end_time_dt,
    )

    if "image" in request.FILES:
        item.image = request.FILES["image"]
        item.save()

    return Response(
        {
            "id": item.id,
            "title": item.title,
            "description": item.description,
            "starting_price": str(item.starting_price),
            "image": get_item_image_url(item, request),
            "end_time": item.end_time.isoformat(),
            "created_at": item.created_at.isoformat(),
            "category_id": category.id,
            "category_name": category.name,
            "category_parent": category.parent.name if category.parent else None,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_item(request: HttpRequest, item_id: int) -> Response:
    """Delete an item listing owned by the current user.

    Args:
        request: Incoming HTTP request.
        item_id: Primary key of the item to delete.
    """
    item = get_object_or_404(Item, pk=item_id)
    if item.owner != request.user:
        return Response({"error": "You can only delete your own listings."}, status=status.HTTP_403_FORBIDDEN)
    item.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
