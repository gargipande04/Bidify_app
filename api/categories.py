"""Static category definitions for the auction site."""

CATEGORY_TREE = [
    {
        "name": "Kids",
        "children": [
            "Boys' Clothes",
            "Girls' Clothes",
            "Footwear",
            "Outerwear",
        ],
    },
    {
        "name": "All",
        "children": [
            "Accessories",
            "Art",
            "Beauty",
            "Books and magazines",
            "Cameras and film",
            "Designer",
            "Gaming",
            "Garden",
            "Pets",
            "Automobiles",
            "Tickets",
            "Home",
            "Music",
            "Sports equipment",
            "Electronics",
            "Toys",
        ],
    },
    {
        "name": "Women",
        "children": [
            "Clothing",
            "Footwear",
            "Bags",
            "Jewellery",
            "Outerwear",
        ],
    },
    {
        "name": "Men",
        "children": [
            "Clothing",
            "Footwear",
            "Accessories",
            "Outerwear",
        ],
    },
]


def ensure_categories() -> None:
    """Ensure hard-coded categories exist in the database."""
    from .models import Category

    for group in CATEGORY_TREE:
        parent, _ = Category.objects.get_or_create(name=group["name"], parent=None)
        for child_name in group["children"]:
            Category.objects.get_or_create(name=child_name, parent=parent)
