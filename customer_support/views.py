from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def customer_support(request):
    token = ""
    return render(request, "chat/customer_support.html", {"token": token})
