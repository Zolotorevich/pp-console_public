import asyncio
import os
from datetime import datetime, time, timedelta

import shortuuid
from django.conf import settings
from django.db import models
from django.utils import timezone
from django_q.tasks import async_task
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from moviepy.editor import VideoFileClip, concatenate_videoclips
from telethon import TelegramClient
from telethon.tl.types import DocumentAttributeVideo

api_id = 000000
api_hash = 'SECRET'
session_file = settings.BASE_DIR / 'flint.session'
client = TelegramClient(str(session_file), api_id, api_hash)
client.parse_mode = 'html'

def get_or_create_eventloop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return asyncio.get_event_loop()

async def telegram_message(channel, message, files, time, disableSound):
    if files:
        video_metadata = None
        
        # Find video in files
        for file in files:
            if '/video/' in file:
                metadata = extractMetadata(createParser(file))
                video_metadata = (
                    (0, metadata.get('duration').seconds)[metadata.has('duration')],
                    (0, metadata.get('width'))[metadata.has('width')],
                    (0, metadata.get('height'))[metadata.has('height')]
                )
                await client.send_file(channel, files, caption=message, silent=disableSound, 
                               attributes=(DocumentAttributeVideo(*video_metadata)),
                               schedule=time)
                
                break
        else:
            await client.send_file(channel, files, caption=message, silent=disableSound,
                               schedule=time)

    else:
        await client.send_message(channel, message, silent=disableSound, schedule=time, link_preview=False)

# Create your models here.
class TelegramChannels(models.Model):
    name = models.CharField(max_length=255)
    link = models.CharField(max_length=255)
    defaultTime = models.CharField(max_length=255)
    lastMessageDate = models.DateTimeField(null=True)

    def send_message(channelName,
                     message,
                     files=False,
                     delayMinutes=0,
                     disableSound=True,
                     allowSendTomorrow=True,
                     **kwargs):

        # kwargs is not used, hack for Django Q complete hook
        
        # If debug -> send to dev channel
        if settings.DEBUG:
            channelName = 'dev'
            delayMinutes = -1

        # Find channel in DB and get current time
        channel = TelegramChannels.objects.get(name=channelName)
        nowTime = timezone.now()

        # Check delay or set time of sending
        if delayMinutes:
            messageTime = nowTime + timedelta(minutes=delayMinutes)
        else:
            # Construct message time
            newTime = time(int(channel.defaultTime[:2]), int(channel.defaultTime[2:]))
            messageTime = datetime.combine(nowTime.date(), newTime)
            messageTime = timezone.make_aware(messageTime)

            # Check if message time alredy past and shift to tomorrow
            if nowTime > messageTime and allowSendTomorrow:
                messageTime = messageTime + timedelta(days=1)

            # Check for first messages of today
            if channel.lastMessageDate.day != messageTime.day:
                disableSound = False
                TelegramChannels.objects.filter(name=channelName).update(lastMessageDate=messageTime)

        # Prepare async and send message
        get_or_create_eventloop()
        with client:
            client.loop.run_until_complete(
                telegram_message(channel.link, message, files, messageTime, disableSound))

    def send_weekly_message(channelName,
                            messageTitle,
                            itemsdata,
                            **kwargs):

        # kwargs is not used, hack for Django Q complete hook

        # Init
        clips = []
        message_text = f"<b>{messageTitle}</b>"
        duration_sec = 0

        # Prepage message and video files
        for item in itemsdata:

            # Calc duration for link in message
            if duration_sec:
                minutes = duration_sec // 60
                if not minutes:
                    minutes = '00'
                elif minutes < 10:
                    minutes = '0' + str(minutes)

                seconds = duration_sec % 60
                if not seconds:
                    seconds = '00'
                elif seconds < 10:
                    seconds = '0' + str(seconds)
                
                duration = f" • {minutes}:{seconds}"
            else:
                duration = ''

            # Append message
            message_text += f"\n\n<b>{item['title']}</b>{duration}\n{item['description']}"

            # Prepage videofile
            video_file = item['videoFilename']
            clips.append(VideoFileClip(video_file))

            # Update video duration
            metadata = extractMetadata(createParser(video_file))
            duration_sec += metadata.get('duration').seconds

        # Generate uniq filename for output
        output_file = settings.MEDIA_ROOT + '/video/weekly/' + shortuuid.uuid() + '.mp4'
        while os.path.isfile(output_file):
            output_file = settings.MEDIA_ROOT + '/video/weekly/' + shortuuid.uuid() + '.mp4'
        
        # Make video
        final_clip = concatenate_videoclips(clips, method="compose")
        final_clip.write_videofile(output_file, audio_codec="aac")

        # Send TG message
        async_task(
            TelegramChannels.send_message,
            channelName,
            message_text,
            [output_file],
            allowSendTomorrow=False,
            kwargs={'id': 'none'},
            task_name=f"Telegram Main: {messageTitle}")