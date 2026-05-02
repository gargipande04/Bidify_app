from django.urls import path
from . import views

urlpatterns = [
    # User / auth
    path("me/", views.me),
    path("signup/", views.signup),
    path("login/", views.login),
    path("logout/", views.logout),
    path("profile/", views.profile),
    path("csrf-token/", views.csrf_token),

    # Items
    path("items/", views.items_list),
    path("items/create/", views.create_item),
    path("items/<int:item_id>/", views.item_detail),
    path("items/<int:item_id>/delete/", views.delete_item),
    path("items/<int:item_id>/favorite/", views.toggle_favorite_item),
    path("items/<int:item_id>/questions/", views.item_questions),
    path("items/<int:item_id>/bids/", views.item_bids),

    # Bids / wishlist
    path("bids/<int:bid_id>/favorite/", views.toggle_favorite_bid),
    path("wishlist/", views.wishlist),
    path("wishlist/items/", views.wishlist_items),

    # Misc
    path("categories/", views.categories_list),
    path("recommendations/", views.recommendations),
    path("profile/items/", views.profile_items),
    path("profile/bids/", views.profile_bids),
    path("questions/<int:question_id>/answer/", views.answer_question),
]
