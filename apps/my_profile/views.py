from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Profile
from .forms import ProfileForm
from config.menu_config import MENU_ITEMS

@login_required
def index(request):
    # Obtener o crear el perfil del usuario
    profile, created = Profile.objects.get_or_create(user=request.user)
    segment = 'my_profile'  # Para marcar el menú activo

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('my_profile:index')
    else:
        form = ProfileForm(instance=profile)

    context = {
        'form': form,
        'profile': profile,
        'menu_items': MENU_ITEMS,
        'segment': segment,
    }
    return render(request, 'pages/profile.html', context)