from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import User, Listing, Bid, Watchlist, Comment, Category
from .forms import NewListingForm, NewBidForm, CommentForm
from django.db.models import Q


@login_required
def new_listing(request):
    if request.method == "POST":
        #extract form submitted by user
        form = NewListingForm(request.POST)
        if form.is_valid():
            #Saving with commit=False gets you a model object, then you can add your extra data and save it.
            instance = form.save(commit=False)
            #add owner_id to the form
            instance.owner_id = request.user
            #save form to database
            instance.save()
            return render(request, "auctions/index.html") 
        else:
            return new_listing(request)
    else:
        form = NewListingForm()
        context = {'form': form}
        return render(request, "auctions/new_listing.html", context)

def index(request):
    #extract all listings
    listings = list(Listing.objects.filter(is_active = True).values())
    #loop over listings, find and append current price
    for listing in listings:
        #find last bid, if there is one
        current_bid = Bid.objects.filter(listing = listing['id']).values().last()
        if current_bid:
            listing['current_bid'] = current_bid['bid_amount']
        #if there's not we'll use the starting price
        if not current_bid:
            starting_bid = Listing.objects.filter(pk=listing['id']).values()
            listing['starting_bid'] = starting_bid = starting_bid[0]['starting_bid']
    context = {'listings': listings}
    return render(request, "auctions/index.html", context)

@login_required
def listing(request, listing_id):
    if request.method == "POST":
        #check that bid is above the start price:
        starting_price = Listing.objects.get(pk=listing_id).starting_bid
        new_bid = float(request.POST['bid_amount'])
        if new_bid <= 0:
            messages.error(request, "Bid Must be Higher Than 0")
            return HttpResponseRedirect('/listing/' + listing_id)
        if starting_price > new_bid:
            messages.error(request, "Bid Cannot Be Less Than Starting Price")
            return HttpResponseRedirect('/listing/' + listing_id)
        #check if already any bids for that listing
        last_bid = Bid.objects.filter(listing = Listing.objects.get(pk=listing_id))
        if last_bid:
            #if there is, extract the latest bit - to check new bid is greater than that
            last_bid = last_bid.latest('Timestamp').bid_amount
            #if new bid is too low - return error meesage
            if last_bid >= new_bid:
                messages.error(request, "Bid Must be Higher Than Current Bid")
                return HttpResponseRedirect('/listing/' + listing_id)
            #else add new bid to the listing
            else:
                #extract users bid as a new bid form
                form = NewBidForm(request.POST)
                if form.is_valid():
                    #Saving with commit=False to get model object- and then appending the extra data
                    instance = form.save(commit=False)
                    #add user instance to the form
                    instance.user = request.user
                    #add listing instance to the form
                    instance.listing = Listing.objects.get(pk=listing_id)
                    #save form to database
                    instance.save()
                    messages.success(request, "Successfully Bid")
                    return HttpResponseRedirect('/listing/' + listing_id)
                else:
                    messages.error(request, "Form Not Entered Correctly")
                    return HttpResponseRedirect('/listing/' + listing_id)
        #if there hasnt been any bids so far, and users bid is higher than startign price - add the bid
        else:
            #extract users bid as a new bid form
            form = NewBidForm(request.POST)
            if form.is_valid():
                #Saving with commit=False to get model object- and then appending the extra data
                instance = form.save(commit=False)
                #add user instance to the form
                instance.user = request.user
                #add listing instance to the form
                instance.listing = Listing.objects.get(pk=listing_id)
                #save form to database
                instance.save()
                messages.success(request, "Successfully Bid")
                return HttpResponseRedirect('/listing/' + listing_id)
    #get request
    else:
        #filter the listings model for the specific listing required with the id, use distinct to get the values as a dict
        listed_item = Listing.objects.filter(id=listing_id).values().distinct()
        listed_item = listed_item[0]
        context = {'listing': listed_item}
        #extract the current bid for the listing from the database
        current_bid = Bid.objects.filter(listing = Listing.objects.get(pk=listing_id)).last()
        if current_bid:
            current_bid = current_bid.bid_amount
        #if there isnt any bids, extract the minimum price 
        if not current_bid:
            minimum_bid =  listed_item['starting_bid']
            context['minimum_bid'] = minimum_bid
        context['current_bid'] = current_bid
        #check if item is on users watch list, if it is add to context
        watched = Watchlist.objects.filter(listing = Listing.objects.get(pk=listing_id), user = request.user)
        if watched:
            context['watched'] = watched
        #add the user bid form to the context
        form = NewBidForm()
        comment_form = CommentForm()
        context['form'] = form
        context['comment_form'] = comment_form
        #extract the comments for the listing so we can render on the page
        comments = Comment.objects.filter(listing = Listing.objects.get(pk=listing_id)).values().distinct()
        # loop over the comments and add the username on it 
        for i in range(len(comments)):
            #extract username where user_id = x
            username = User.objects.get(id=comments[i]['user_id'])
            comments[i]['username'] = username
        context['comments'] = comments
        #check if user is the owner of the listing. If none returns - we can use that as logic on page
        is_owner = Listing.objects.filter(id = listing_id, owner_id = request.user).values()
        context['is_owner'] = is_owner
        #check if listing is complete -so we can dictate logic on the page
        #context['has_ended'] = 
        #check if user is the highest bidder/ winner? of the auction 
        return render(request, "auctions/listing.html", context)



@login_required
def watch(request, listing_id):
    if request.method == "POST":
        #is it a watch submission:
        if 'watch' in request.POST:
            watched = Watchlist.objects.create(listing = Listing.objects.get(pk=listing_id), user = request.user)
            watched.save()
            messages.success(request, "Added to watch list")
            return HttpResponseRedirect('/listing/' + listing_id) 
        #is it an unwatch submission
        if 'unwatch' in request.POST:
            unwatched = Watchlist.objects.filter(listing = Listing.objects.get(pk=listing_id), user = request.user)
            unwatched.delete()
            messages.info(request, "Removed from watch list")
            #take user back to page they were on:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            
    else:
        #render auction listings page
        return render(request, "auctions/index.html") 


@login_required
def comments(request, listing_id):
    if request.method == "POST":
        #extract comment form submitted by user
        form = CommentForm(request.POST)
        if form.is_valid():
            #Saving with commit=False, so we can add to the model instance
            instance = form.save(commit=False)
            #add owner and listing to the commentform
            instance.user = request.user
            instance.listing = Listing.objects.get(pk=listing_id)
            instance.save()
            messages.success(request, "Comment Added")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            messages.error(request, "Error with comment submission")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def end_auction(request, listing_id):
    # check user is the owner
    is_owner = Listing.objects.filter(id = listing_id, owner_id = request.user)
    if not is_owner:
        messages.error(request, "You don't have permission to do that")
        return HttpResponseRedirect('/listing/' + listing_id)
    finished_auction = Listing.objects.get(id = listing_id)
    #extract last bid (if there is one) - and who was the bidder
    try:
        last_bid = Bid.objects.filter(listing = Listing.objects.get(pk=listing_id)).latest('Timestamp')
    except:
        messages.info(request, "Completed Listing as unsold")
    else:
        #add winner id and winning bid to the listing
        finished_auction.winning_bid = last_bid.bid_amount
        finished_auction.winner_id = last_bid.user_id
        messages.success(request, "Auction complete")
    finally:
        # change the listing to inactive and save
        finished_auction.is_active = False
        finished_auction.save()
        return HttpResponseRedirect('/listing/' + listing_id)


@login_required
def bought_items(request):
    #look in listing for items where winner id = x
    bought_items = Listing.objects.filter(winner_id = request.user.id)
    context = {'listings': bought_items}
    #pull info together and render to page
    return render(request, "auctions/bought_items.html", context) 


@login_required
def past_listings(request):
    #look in listings for items where is_active is false, and listing owner is the current user
    unsold_listings = Listing.objects.filter(is_active = False, owner_id = request.user, winning_bid = None)
    #for sold items i use a Q object - which returns all entries except those with a winning bid of None
    sold_listings = Listing.objects.filter(is_active = False, owner_id = request.user).filter(~Q (winning_bid = None))
    context = {'unsold_listings': unsold_listings}
    context['sold_listings'] = sold_listings
    #pull info together and render to page
    return render(request, "auctions/past_listings.html", context) 

@login_required 
def watchlist(request):
    #extract item id's for that user in the watchlist model
    items = Watchlist.objects.filter(user = request.user).values()
    #loop through the ids -and extract the listing information for each
    listings = []
    for i in range(len(items)):
        input_id = items[i]['listing_id']
        item = Listing.objects.filter(id = items[i]['listing_id']).filter(is_active = True).values()
        if item:
            listings.append(item[0])
    context = {'listings': listings}
    return render(request, "auctions/watchlist.html", context)  

@login_required
def user_listings(request):
    #extract what listings belong to the user logged in
    listings = Listing.objects.filter(owner_id = request.user).filter(is_active = True).values()
    #loop over listings, find and append current price
    for listing in listings:
        #find last bid, if there is one
        current_bid = Bid.objects.filter(listing = listing['id']).values().last()
        if current_bid:
            listing['current_bid'] = current_bid['bid_amount']
        #if there's not we'll use the starting price
        if not current_bid:
            starting_bid = Listing.objects.filter(pk=listing['id']).values()
            listing['starting_bid'] = starting_bid = starting_bid[0]['starting_bid']
    context = {'listings': listings}
    return render(request, "auctions/user_listings.html", context)


def categories(request, category):
    if category == 'all':
        categories = Category.objects.all()
        context = { 'categories': categories}
        return render(request, "auctions/categories.html", context)
    else:
        category = Category.objects.filter(name = category)
        category = category[0]
        items = Listing.objects.filter(category = category).filter(is_active = True)
        context = { 'listings': items}
        context['category'] = category
    return render(request, "auctions/categories.html", context)





def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


