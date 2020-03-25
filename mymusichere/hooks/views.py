from django.shortcuts import render
from django.http import HttpResponse, Http404

import os

def build(request):
    exitcode = os.system('$VIRTUAL_ENV/../build')
    return HttpResponse("Rebuild is finished with exitcode %d." % exitcode)
