import json
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views import generic
from django_q.tasks import async_task

from telegramClient.models import TelegramChannels as telegram

from .models import Games, Weekly

"""
Await games
"""
class AwaitView(LoginRequiredMixin, generic.ListView):
    template_name = "games/index.html"
    context_object_name = "await_games"
    navigation_select = ['games', 'await']

    def get_queryset(self):
        return Games.objects.filter(status='await').order_by('date')

# Send game to TG
@login_required
def send(request, game_id):

    # Generate game new info
    game = {
        'title': request.POST['title'],
        'genre': request.POST['genre'],
        'description': request.POST['description'],
        'sysCPU': request.POST['cpu'],
        'sysGPU': request.POST['gpu'],
        'sysRAM': request.POST['ram'],
        'ratingUsers': request.POST['ratingGamers'] or None,
        'ratingCritics': request.POST['ratingCritics'] or None,
        'screenshotsSelected': ','.join(request.POST.getlist('screenshots')),
        'videoFilename': request.POST['videoFilename'],
        'status': 'queued',
    }

    # Prepare Telegram message
    message_text = '<b>{title}</b>\n'.format(**game)

    # Genres
    list_of_genres = []
    for genre in game['genre'].split(', '):
        list_of_genres.append('#' + genre.replace(' ', '_').replace('-', '_'))

    message_text += ', '.join(list_of_genres)

    # Description
    message_text += '\n\n{description}\n\n'.format(**game)

    # System requirements
    message_text += '<b>Минимум:</b> {sysCPU} • {sysGPU} • {sysRAM} Гб ОЗУ'.format(**game)

    # Metacritic
    message_text += '\n\n<b>Метакритик:</b> '
    if not game['ratingUsers'] and not game['ratingCritics']:
        message_text += 'нет оценок'
    else:
        if game['ratingUsers']:
            message_text += 'геймеры {ratingUsers}%, '.format(**game)
        else:
            message_text += 'геймеры –, '

        if game['ratingCritics']:
            message_text += 'критики {ratingCritics}%'.format(**game)
        else:
            message_text += 'критики –'

    # Files
    message_files = [settings.MEDIA_ROOT + '/video/' + game['videoFilename']]
    for image in request.POST.getlist('screenshots'):
        message_files.append(settings.MEDIA_ROOT + '/images/' + image)

    # Update game in DB
    Games.objects.filter(id=game_id).update(**game)
    
    # Send TG message
    async_task(
        telegram.send_message,
        'games',
        message_text,
        message_files,
        kwargs={'id': game_id},
        task_name='Telegram Games: ' + game['title'],
        hook='games.views.change_status_after_send')

    # Return
    return HttpResponseRedirect(reverse("games:index"))

# Change game status after send Telegram message
def change_status_after_send(task):

    if task.success:
        status = 'approved'
    else:
        status = 'await'

    Games.objects.filter(id=task.kwargs['kwargs']['id']).update(status=status)


"""
Weekly games
"""
class WeeklyView(LoginRequiredMixin, generic.ListView):
    template_name = "games/weekly.html"
    context_object_name = "weekly_games"
    navigation_select = ['games', 'weekly']

    def get_queryset(self):
        # Calc last friday date
        now_date = timezone.now()

        last_friday = now_date - timedelta(days=(now_date.weekday() - 4) % 7)
        
        # Check if today is friday
        if now_date.weekday() == 4:
            last_friday = last_friday - timedelta(weeks=1)

        last_friday = last_friday.replace(hour=18,minute=0,second=0,microsecond=0)

        # HOTFIX today on friday
        now_date = now_date + timedelta(days=1)

        # Select games from last friday 18:00
        return Games.objects.filter(status='approved').filter(date__range=[last_friday,now_date]).order_by('date')

@login_required
def sendWeekly(request):
    weekly_games = json.loads(request.POST.get('data', ''))

    # Generate telegram message text and screenshots filenames
    message_text = '<b>Новые ПК игры в сети за неделю</b>'
    data = []

    # Generate games info
    for game in weekly_games[0]:
        # Get origin from DB
        origin = Weekly.objects.get(id=game['id'])

        # Update weekly description
        origin.description = game['description']
        origin.save()

        # Generate game description
        description = f"<b><a href='https://t.me/flint_games/{origin.messageID}'>{origin.owner.title}</a></b>\n{game['description']}"
        
        # Save to list
        data.append(description)

    message_text = '<b>Новые ПК игры в сети за неделю</b>\n\n' + '\n\n'.join(data)
    message_files = []
    for image in weekly_games[1]:
        message_files.append(settings.MEDIA_ROOT + '/images/' + image)

    # Send TG message
    async_task(
        telegram.send_message,
        'main',
        message_text,
        message_files,
        allowSendTomorrow=False,
        kwargs={'id': 'none'},
        task_name=f"Telegram Main: Weekly games")

    return JsonResponse({'success':1})

"""
Rejected games
"""
class RejectedView(LoginRequiredMixin, generic.ListView):
    template_name = "games/rejected.html"
    context_object_name = "rejected_games"
    navigation_select = ['games', 'rejected']

    def get_queryset(self):
        return Games.objects.filter(status='rejected').order_by('date')

# Reject game
@login_required
def reject(request, game_id):
    Games.objects.get(id=game_id).update(status='rejected')
    return HttpResponseRedirect(reverse("games:index"))