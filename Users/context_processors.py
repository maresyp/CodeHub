from .models import Matches

def count_matches(request):
    """
    Function to count the number of matches for the authenticated user where `first_status` is True and `second_status` is null.

    Parameters:
    request (WSGIRequest): An HttpRequest instance.

    Returns:
    dict: A dictionary containing `matches_count` key with the count of matches as value. Returns an empty dictionary if user is not authenticated.
    """
    if request.user.is_authenticated:
        count = Matches.objects.filter(
            second_user__exact=request.user,
            first_status=True,
            second_status__isnull=True
        ).count()
        return {'matches_count': count}
    return {}