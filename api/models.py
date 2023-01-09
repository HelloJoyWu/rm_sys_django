from django.db import models

# Create your models here.


class DayGameStatusModel(models.Model):
    # readonly daSystem.interval_game_status
    objects = models.Manager()

    class Meta:
        managed = False
        abstract = True
        db_table = 'day_game_status'
        app_label = 'default_read'


class DayGameStatus(DayGameStatusModel):
    date = models.DateField()
    game_name = models.CharField(max_length=50)
    game_code = models.CharField(max_length=50, primary_key=True)
    game_type = models.CharField(max_length=50)
    bets = models.DecimalField(max_digits=20, decimal_places=2)
    incomes = models.DecimalField(max_digits=20, decimal_places=2)
    rounds = models.IntegerField()
    players = models.IntegerField()


class IntervalGameStatusModel(models.Model):
    # readonly daSystem.interval_game_status
    objects = models.Manager()

    class Meta:
        managed = False
        abstract = True
        db_table = 'interval_game_status'
        app_label = 'default_read'


class IntervalGameStatus(IntervalGameStatusModel):
    date = models.DateTimeField()
    interval_len = models.IntegerField()
    game_name = models.CharField(max_length=50)
    game_code = models.CharField(max_length=50, primary_key=True)
    game_type = models.CharField(max_length=50)
    bets = models.DecimalField(max_digits=20, decimal_places=2)
    incomes = models.DecimalField(max_digits=20, decimal_places=2)
    rounds = models.IntegerField()
    players = models.IntegerField()


class GameInfoModel(models.Model):
    # readonly MaReport.game_info
    objects = models.Manager()

    class Meta:
        managed = False
        abstract = True
        db_table = 'game_info'
        app_label = 'mareport_read'


class GameInfo(GameInfoModel):
    gid = models.IntegerField(primary_key=True)
    game_code = models.CharField(max_length=50)
    game_type = models.CharField(max_length=50)
    game_name_en = models.CharField(max_length=50)
    game_name_tw = models.CharField(max_length=50)
    game_name_cn = models.CharField(max_length=50)
    status = models.IntegerField()
    onlinetime = models.DateField()
    onlinetime_t = models.DateTimeField()
    game_team = models.CharField(max_length=36)
    brand = models.CharField(max_length=10)
