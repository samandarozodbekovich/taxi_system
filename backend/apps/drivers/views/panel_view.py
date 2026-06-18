from django.shortcuts import render

def driver_index(request):
    return render(request, 'driver_webapp/index.html')