from django.db import models

class Games(models.Model):
    url = models.CharField(max_length=255)
    rawTitle = models.CharField(max_length=255)
    rawText = models.TextField(null=True)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True)
    genre = models.TextField(null=True)
    sysCPU = models.TextField(null=True)
    sysGPU = models.TextField(null=True)
    sysRAM = models.CharField(max_length=255)
    ratingCritics = models.IntegerField(null=True)
    ratingUsers = models.IntegerField(null=True)
    screenshotsFilenames = models.TextField(null=True)
    screenshotsSelected = models.TextField(null=True)
    videoURL = models.CharField(max_length=255)
    videoFilename = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    date = models.DateTimeField(null=True)

    def __str__(self):
        return self.title

    def screenshots_list(self):
        return self.screenshotsFilenames.split(',')

    def selected_screenshots(self):
        return self.screenshotsSelected.split(',')


class Weekly(models.Model):
    owner = models.OneToOneField(Games, on_delete=models.CASCADE)
    messageID = models.IntegerField(null=False)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.owner.title

class Genre(models.Model):
    genre = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.genre

class GenreSynonym(models.Model):
    synonym = models.CharField(max_length=255)
    owner = models.ForeignKey(Genre, on_delete=models.CASCADE)

    def __str__(self):
        return self.synonym

class SteamScore(models.Model):
    appid = models.IntegerField(null=False, unique=True)
    score = models.IntegerField(null=False)
    reviews = models.IntegerField(null=False)
    owner = models.OneToOneField(Games, on_delete=models.CASCADE)

class SteamReview(models.Model):
    good = models.BooleanField(default=True)
    url = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    duration = models.CharField(max_length=255)
    likes = models.IntegerField(null=False)
    text = models.TextField(null=True)
    approved = models.BooleanField(default=False)
    owner = models.ForeignKey(Games, on_delete=models.CASCADE)