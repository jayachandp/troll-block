from django.db import models

# Create your models here.

class Blocked_List(models.Model):
    user_id = models.CharField(max_length=30)
    share = models.CharField(max_length=10)
    blocked_users = models.TextField()
    subscribed_users = models.TextField()
    #def save(self, *args, **kwargs):
    #    pass
    
    def __unicode__(self):
        return "User Id: %s, Shared: %s" %(self.user_id, self.share)