from django.shortcuts import render, redirect


def home(request):
    return render(request, 'pages/home.html')


def login_page(request):
    return render(request, 'pages/login.html')


def register_page(request):
    return render(request, 'pages/register.html')


def browse(request):
    return render(request, 'pages/browse.html')


def movie_detail(request, slug):
    return render(request, 'pages/movie_detail.html', {'slug': slug})


def player(request, slug):
    return render(request, 'pages/player.html', {'slug': slug})


def profile(request):
    return render(request, 'pages/profile.html')


def search_page(request):
    return render(request, 'pages/search.html')


def admin_dashboard(request):
    return render(request, 'pages/admin_dashboard.html')


def playlist_page(request, slug):
    return render(request, 'pages/playlist.html', {'slug': slug})


def genre_page(request, slug):
    return render(request, 'pages/genre.html', {'slug': slug})


def payment_page(request):
    request_id = request.GET.get('request_id', '')
    movie_title = request.GET.get('movie_title', '')
    return render(request, 'pages/payment.html', {
        'request_id': request_id,
        'movie_title': movie_title,
    })


def logout_view(request):
    """Direct logout - clears cookies and redirects to home."""
    response = redirect('/')
    response.delete_cookie('access_token', path='/', samesite='Lax')
    response.delete_cookie('refresh_token', path='/', samesite='Lax')
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    return response
