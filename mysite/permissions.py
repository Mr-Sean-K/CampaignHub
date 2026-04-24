from django.contrib.auth.decorators import user_passes_test

# decorator to confirm user is authenticated to access certain views

def role_required(*allowed_roles):

    def check(user):
        return user.is_authenticated and (user.is_superuser or user.role in allowed_roles)

    return user_passes_test(check)
