from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_listing", views.new_listing, name="new_listing"),
    path("listing/<listing_id>", views.listing, name="listing"),
    path("watch/<listing_id>", views.watch, name="watch"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("comments/<listing_id>", views.comments, name="comments"),
    path("user_listings", views.user_listings, name="user_listings"),
    path("end_auction/<listing_id>", views.end_auction, name="end_auction"),
    path("bought_items", views.bought_items, name="bought_items"),
    path("past_listings", views.past_listings, name="past_listings"),
    #path("categories", views.categories, name="categories"),
    path("categories/<category>", views.categories, name="categories")
]
