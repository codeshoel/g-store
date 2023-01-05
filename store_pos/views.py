from django.shortcuts import render
from .forms import AdminLoginForm

templates = ("login.html", "index.html", "customers.html", "store.html", "orders.html")


def login(request):
    template = "admin/pages/{:s}".format(templates[0])
    form = AdminLoginForm()
    return render(request, template_name=template, context={"loginForm": form})


def dashboard(request):
    template = "admin/pages/{:s}".format(templates[1])
    return render(request, template_name=template, context={})


def customers(request):
    template = "admin/pages/{:s}".format(templates[2])
    return render(request, template_name=template, context={})


def store_product(request):
    template = "admin/pages/{:s}".format(templates[3])
    return render(request, template_name=template, context={})


def orders(request):
    template = "admin/pages/{:s}".format(templates[4])
    return render(request, template_name=template, context={})


