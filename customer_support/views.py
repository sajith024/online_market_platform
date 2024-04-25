from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from online_market_app.models import OnlineMarketUser


# Create your views here.
@login_required
def customer_support(request):
    users = OnlineMarketUser.objects.exclude(id=request.user.id).exclude(
        role__name="Admin"
    )
    return render(request, "chat/customer_support.html", {"users": users})

@login_required
def community(request):
    return render(request, "chat/community.html")