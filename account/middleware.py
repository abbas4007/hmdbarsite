# account/middleware.py
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.http import HttpResponse

User = get_user_model()


class LoginAttemptsMiddleware :
    def __init__(self, get_response) :
        self.get_response = get_response

    def __call__(self, request) :
        if request.method == 'POST' and 'username' in request.POST :
            username = request.POST['username']
            cache_key = f'login_attempts_{username}'
            attempts = cache.get(cache_key, 0)

            if attempts >= 3 :  # بعد از ۳ بار تلاش ناموفق
                user = User.objects.filter(username = username).first()
                if user :
                    user.is_active = False
                    user.save()
                return HttpResponse("حساب شما موقتاً قفل شده است. لطفاً پس از ۵ دقیقه مجدداً تلاش کنید.", status = 403)

            response = self.get_response(request)

            if hasattr(response, 'status_code') and response.status_code == 200 :
                cache.set(cache_key, attempts + 1, timeout = 300)  # ۵ دقیقه
            return response

        return self.get_response(request)