from home.models import Comision

def comisions(request):
    return {
        'comi': Comision.objects.all()
    }