from django.views import generic

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

# Work in progress
class IndexView(LoginRequiredMixin, generic.ListView):
    template_name = "harvesterStatus/index.html"
    context_object_name = "index_harvesterStatus"

    def get_queryset(self):
        return True