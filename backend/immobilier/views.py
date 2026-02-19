from django.shortcuts import render


def page_placeholder(request, title, description, pk=None):
    context = {
        "title": title,
        "description": description,
        "pk": pk,
    }
    return render(request, "immobilier/page_placeholder.html", context)
