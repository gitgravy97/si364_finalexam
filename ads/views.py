from django.shortcuts import render
from django.views import View
from django.conf import settings

"""
# Create your views here.
class HomeView(View):
    def get(self, request) :
        cleanup()
        print(request.get_host())
        host = request.get_host()
        islocal = host.find('localhost') >= 0 or host.find('127.0.0.1') >= 0
        context = {
            'installed' : settings.INSTALLED_APPS,
            'islocal' : islocal
        }
        return render(request, 'main_home.html', context)

# Remove ads > 30 minutes old
from ads.models import Ad
from datetime import timedelta
from django.utils import timezone

# https://stackoverflow.com/questions/37607411/django-runtimewarning-datetimefield-received-a-naive-datetime-while-time-zon/37607525
def cleanup() :
    time_threshold = timezone.now() - timedelta(minutes=30)
    count = Ad.objects.filter(created_at__lt=time_threshold).count()
    if count > 0 :
        Ad.objects.filter(created_at__lt=time_threshold).delete()
        print('Deleted',count,' expired ads')
"""

from ads.models import Ad, Comment, Fav

from django.views import View
from django.views import generic
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse

from ads.util import OwnerListView, OwnerDetailView, OwnerCreateView, OwnerUpdateView, OwnerDeleteView

from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from ads.forms import CreateForm, CommentForm

class AdListView(OwnerListView):
    model = Ad
    template_name = "ad_list.html"

class AdDetailView(OwnerDetailView):
    model = Ad
    template_name = "ad_detail.html"
    def get(self, request, pk) :
        ad = Ad.objects.get(id=pk)
        comments = Comment.objects.filter(ad=ad).order_by('-updated_at')
        comment_form = CommentForm()

        favorites = list()
        if request.user.is_authenticated:
            rows = request.user.favorite_ads.values('id')
            favorites = [ row['id'] for row in rows ]            

        context = { 'ad' : ad, 'comments': comments, 'comment_form': comment_form,
            'favorites': favorites }
        return render(request, self.template_name, context)

"""
    def get(self, request) :
        thing_list = Thing.objects.all()
        favorites = list()
        if request.user.is_authenticated:
            rows = request.user.favorite_things.values('id')
            favorites = [ row['id'] for row in rows ]
        ctx = {'thing_list' : thing_list, 'favorites': favorites}
        return render(request, self.template_name, ctx)
"""
####################################################################################################
"""
class ThingListView(OwnerListView):
    model = Thing
    template_name = "favs/list.html"

    def get(self, request) :
        thing_list = Thing.objects.all()
        favorites = list()
        if request.user.is_authenticated:
            # rows = [{'id': 2}]  (A list of rows)
            rows = request.user.favorite_things.values('id')
            favorites = [ row['id'] for row in rows ]
        ctx = {'thing_list' : thing_list, 'favorites': favorites}
        return render(request, self.template_name, ctx)
"""

class AdCreateView(OwnerCreateView):
    model = Ad
    fields = ['title', 'price', 'text']
    template_name = "ad_form.html"

class AdUpdateView(OwnerUpdateView):
    model = Ad
    fields = ['title', 'price', 'text']
    template_name = "ad_form.html"

class AdDeleteView(OwnerDeleteView):
    model = Ad
    template_name = "ad_delete.html"

class AdFormView(LoginRequiredMixin, View):
    template = 'ads/form.html'
    success_url = reverse_lazy('ads')
    def get(self, request, pk=None) :
        if not pk : 
            form = CreateForm()
        else: 
            ad = get_object_or_404(Ad, id=pk, owner=self.request.user)
            form = CreateForm(instance=ad)
        ctx = { 'form': form }
        return render(request, self.template, ctx)

    def post(self, request, pk=None) :
        if not pk:
            form = CreateForm(request.POST, request.FILES or None)
        else:
            ad = get_object_or_404(Ad, id=pk, owner=self.request.user)
            form = CreateForm(request.POST, request.FILES or None, instance=ad)

        if not form.is_valid() :
            ctx = {'form' : form}
            return render(request, self.template, ctx)

        # Adjust the model owner before saving
        ad = form.save(commit=False)
        ad.owner = self.request.user
        ad.save()
        return redirect(self.success_url)

def stream_file(request, pk) :
    ad = get_object_or_404(Ad, id=pk)
    response = HttpResponse()
    response['Content-Type'] = ad.content_type
    response['Content-Length'] = len(ad.picture)
    response.write(ad.picture)
    return response

class CommentCreateView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        f = get_object_or_404(Ad, id=pk)
        comment_form = CommentForm(request.POST)

        comment = Comment(text=request.POST['comment'], owner=request.user, ad=f)
        comment.save()
        return redirect(reverse_lazy('ad_detail', args=[pk]))

class CommentDeleteView(OwnerDeleteView):
    model = Comment
    template_name = "comment_delete.html"

    # https://stackoverflow.com/questions/26290415/deleteview-with-a-dynamic-success-url-dependent-on-id
    def get_success_url(self):
        ad = self.object.ad
        return reverse_lazy('ad_detail', args=[ad.id])

# Homework "ChucksList #3" Content
# https://stackoverflow.com/questions/16458166/how-to-disable-djangos-csrf-validation
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.utils import IntegrityError

@method_decorator(csrf_exempt, name='dispatch')
class AddFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        print("Add PK",pk)
        t = get_object_or_404(Ad, id=pk)
        fav = Fav(user=request.user, ad=t)
        print()
        print("Add Favorite - Attempting . . .")
        try:
            fav.save()  # In case of duplicate key
            print("AddFave Successful, Saved")
        except IntegrityError as e:
            print("AddFave Failing")
            pass
        return HttpResponse()

@method_decorator(csrf_exempt, name='dispatch')
class DeleteFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        print("Delete PK",pk)
        t = get_object_or_404(Ad, id=pk)
        print()
        print("Delete Favorite - Attempting . . .")
        try:
            fav = Fav.objects.get(user=request.user, ad=t).delete()
            print("DelFave Executed")
        except Fav.DoesNotExist as e:
            print("DelFave Failing")
            pass

        return HttpResponse()
