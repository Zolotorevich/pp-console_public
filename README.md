# Сайт с инфой об играх на трекерах
Показывает информацию об играх на торрент трекерах, которую собрал pp-harvester (www.github.com/Zolotorevich/pp-harvester_public), и отправляет её в Телеграм-канал. Последнее делает через клиент, а не бота. По пятницам склеивает трейлеры игр за неделю в одно видео.

Внутри: Django + Q2, Telethon, moviepy, Ubuntu + MySQL + Apache.

Зачем: zolotorevich.com/works/pirate-parrot/crawler/

## games
Показывает информацию об играх и список игра за неделю

## telegramClient
Отправляет информацю в Телеграм

## telegram_auth.py
Авторизация в Телеграме. Запустить один раз на сервере для создания файла сессии.