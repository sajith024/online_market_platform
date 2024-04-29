from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from online_market_app.models import OnlineMarketUser


# Create your views here.
@login_required
def customer_support(request):
    
    if request.user.role.name == "Customer Support":
        users = OnlineMarketUser.objects.filter(Q(role__name="Buyer") | Q(role__name="Seller"))
    else:
        users = OnlineMarketUser.objects.filter(role__name="Customer Support")
    return render(request, "chat/customer_support.html", {"users": users})


@login_required
def community(request):
    return render(request, "chat/community.html")
