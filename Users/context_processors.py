from .models import Matches

def count_matches(request):
    if request.user.is_authenticated:
        count = Matches.objects.filter(
            second_user__exact=request.user,
            first_status=True,
            second_status__isnull=True
        ).count()
        return {'matches_count': count}
    return {}