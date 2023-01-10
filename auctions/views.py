from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import User, Listing, Bid, Watchlist
from .forms import NewListingForm, NewBidForm, CommentForm

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
    listings = Listing.objects.all()
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
                print(form)
                if form.is_valid():
                    #Saving with commit=False to get model object- and then appending the extra data
                    instance = form.save(commit=False)
                    #add user instance to the form
                    instance.user = request.user
                    #add listing instance to the form
                    instance.listing = Listing.objects.get(pk=listing_id)
                    print(instance)
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
        print(form)
        if form.is_valid():
            #Saving with commit=False, so we can add to the model instance
            instance = form.save(commit=False)
            #add owner and listing to the commentform
            instance.user = request.user
            instance.listing = Listing.objects.get(pk=listing_id)
            #instance.save()
            messages.success(request, "Comment Added")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            messages.error(request, "Error with comment submission")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))




        #extract listing
        #insert into comments database
        #redierecrt
        pass
    else:
        #render auction listings page
        return render(request, "auctions/index.html")

@login_required 
def watchlist(request):
    #extract item id's for that user in the watchlist model
    items = Watchlist.objects.filter(user = request.user).values()
    #loop through the ids -and extract the listing information for each
    listings = []
    for i in range(len(items)):
        input_id = items[i]['listing_id']
        item = Listing.objects.filter(id = items[i]['listing_id']).values()
        listings.append(item[0])
    context = {'listings': listings}
    return render(request, "auctions/watchlist.html", context)  





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
