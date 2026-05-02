from django.contrib import admin
from .models import Item, Question, PageView, User, Bid, FavoriteBid, FavoriteItem


admin.site.register(User)
admin.site.register(Item)
admin.site.register(Question)
admin.site.register(PageView)
admin.site.register(Bid)
admin.site.register(FavoriteBid)
admin.site.register(FavoriteItem)
