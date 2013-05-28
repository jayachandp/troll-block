from django.db import models

# Create your models here.

share_choices = (
    ('public', 'private'),
    ('private', 'private'),
    ('no', 'no')
    )

class Blocked_List(models.Model):
    user_id = models.CharField(max_length=10)
    share = models.CharField(max_length=10)
    blocked_users = models.TextField()
    
    def __unicode__(self):
        return "User Id: %s, Blocked Users: %s" %(self.user_id,
                                                  self.blocked_users)


class Subscribed_List(models.Model):
    user_id = models.ForeignKey(Blocked_List)
    subscribed_users = models.TextField()
    
    def __unicode__(self):
        return "User Id: %s, Subscribed Users: %s" %(self.user_id,
                                                     self.subscribed_users)
