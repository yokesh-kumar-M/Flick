from django.shortcuts import render, redirect
from functools import wraps


def ensure_authenticated(view_func):
    """Decorator to redirect unauthenticated users to the login page."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # We rely on HTTP-only cookies injected by the gateway proxy
        access_token = request.COOKIES.get('access_token')
        refresh_token = request.COOKIES.get('refresh_token')
        
        if not access_token and not refresh_token:
            return redirect('/login/')
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view


@ensure_authenticated
def home(request):
    return render(request, 'pages/home.html')


def login_page(request):
    return render(request, 'pages/login.html')


def register_page(request):
    return render(request, 'pages/register.html')


@ensure_authenticated
def browse(request):
    return render(request, 'pages/browse.html')


@ensure_authenticated
def movie_detail(request, slug):
    return render(request, 'pages/movie_detail.html', {'slug': slug})


@ensure_authenticated
def player(request, slug):
    return render(request, 'pages/player.html', {'slug': slug})


@ensure_authenticated
def profile(request):
    return render(request, 'pages/profile.html')


@ensure_authenticated
def search_page(request):
    return render(request, 'pages/search.html')


@ensure_authenticated
def admin_dashboard(request):
    return render(request, 'pages/admin_dashboard.html')


@ensure_authenticated
def playlist_page(request, slug):
    return render(request, 'pages/playlist.html', {'slug': slug})


@ensure_authenticated
def genre_page(request, slug):
    return render(request, 'pages/genre.html', {'slug': slug})


@ensure_authenticated
def payment_page(request):
    request_id = request.GET.get('request_id', '')
    movie_title = request.GET.get('movie_title', '')
    return render(request, 'pages/payment.html', {
        'request_id': request_id,
        'movie_title': movie_title,
    })


def logout_view(request):
    """Direct logout - clears cookies and redirects to login."""
    response = redirect('/login/')
    response.delete_cookie('access_token', path='/', samesite='Lax')
    response.delete_cookie('refresh_token', path='/', samesite='Lax')
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    return response
