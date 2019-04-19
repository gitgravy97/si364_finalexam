from django.shortcuts import render
from django.views import View
from django.conf import settings

from autos.models import Auto, Comment

from django.views import View
from django.views import generic
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse

from autos.util import OwnerListView, OwnerDetailView, OwnerCreateView, OwnerUpdateView, OwnerDeleteView

from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from autos.forms import CreateForm, CommentForm

class AutoListView(OwnerListView):
    model = Auto
    template_name = "auto_list.html"

class AutoDetailView(OwnerDetailView):
    model = Auto
    template_name = "auto_detail.html"
    def get(self, request, pk) :
        auto = Auto.objects.get(id=pk)
        comments = Comment.objects.filter(auto=auto).order_by('-updated_at')
        comment_form = CommentForm()
        context = { 'auto' : auto, 'comments': comments, 'comment_form': comment_form,}
        return render(request, self.template_name, context)

class AutoCreateView(OwnerCreateView):
    model = Auto
    fields = ['name', 'detail', 'mileage']
    template_name = "auto_form.html"

class AutoUpdateView(OwnerUpdateView):
    model = Auto
    fields = ['name', 'detail', 'mileage']
    template_name = "auto_form.html"

class AutoDeleteView(OwnerDeleteView):
    model = Auto
    template_name = "auto_delete.html"

class AutoFormView(LoginRequiredMixin, View):
    template = 'autos/form.html'
    success_url = reverse_lazy('autos')
    def get(self, request, pk=None) :
        if not pk : 
            form = CreateForm()
        else: 
            auto = get_object_or_404(Auto, id=pk, owner=self.request.user)
            form = CreateForm(instance=auto)
        ctx = { 'form': form }
        return render(request, self.template, ctx)

    def post(self, request, pk=None) :
        if not pk:
            form = CreateForm(request.POST, request.FILES or None)
        else:
            auto = get_object_or_404(Auto, id=pk, owner=self.request.user)
            form = CreateForm(request.POST, request.FILES or None, instance=auto)

        if not form.is_valid() :
            ctx = {'form' : form}
            return render(request, self.template, ctx)

        # Adjust the model owner before saving
        auto = form.save(commit=False)
        auto.owner = self.request.user
        auto.save()
        return redirect(self.success_url)

class CommentCreateView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        f = get_object_or_404(Auto, id=pk)
        comment_form = CommentForm(request.POST)

        comment = Comment(text=request.POST['comment'], owner=request.user, auto=f)
        comment.save()
        return redirect(reverse_lazy('auto_detail', args=[pk]))

class CommentDeleteView(OwnerDeleteView):
    model = Comment
    template_name = "auto_comment_delete.html"

    # https://stackoverflow.com/questions/26290415/deleteview-with-a-dynamic-success-url-dependent-on-id
    def get_success_url(self):
        auto = self.object.auto
        return reverse_lazy('auto_detail', args=[auto.id])