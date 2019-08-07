from django.db import models
from R6K.models import user_info
class chassis(models.Model):
    ip=models.GenericIPAddressField(null=False,blank=False,unique=True)
    chassis_info=models.CharField(null=True,blank=True,default='',max_length=255)
    def __str__(self):
        return self.ip

class card(models.Model):
    ip=models.ForeignKey(to='chassis',to_field='id',on_delete=models.CASCADE)
    slot=models.SmallIntegerField()
    card_info=models.CharField(null=True,blank=True,default='',max_length=255)
    status_choice = ((0, 'normal'),
                     (1, 'broken'),
                     (2, 'return to factory'),
                     (3, 'borrow'),
                     )
    status = models.SmallIntegerField(choices=status_choice, default=0)
    def __str__(self):
        return '%s-%s' %(self.ip.ip,str(self.slot))
        # return str(self.slot)

class port(models.Model):
    card=models.ManyToManyField(to='card')
    port_num=models.SmallIntegerField()
    purpose=models.CharField(null=True,blank=True,max_length=64,default='')
    users=models.CharField(null=True,blank=True,max_length=48,default='')
    user = models.ForeignKey(user_info,on_delete=models.CASCADE,null=True,blank=True)
    # line = models.CharField(null=True, blank=True, max_length=8, default='')
    switch=models.CharField(null=True,blank=True,max_length=16,default='')
    share=models.BooleanField(default=False)
    usecycle=models.CharField(null=True,blank=True,max_length=16,default='')
    comments=models.CharField(null=True,blank=True,max_length=255,default='')
    status_choice = ((0, 'booked'),
                     (1, 'broken'),
                     (2, 'release'),
                     )
    status = models.SmallIntegerField(choices=status_choice, default=2)
    def __str__(self):
        return '%s-%s-%s' %(self.card.first().ip.ip,str(self.card.first().slot),str(self.port_num))
        # return str(self.port_num)

class utilization(models.Model):
    port=models.ForeignKey(port,on_delete=models.DO_NOTHING)
    day = models.DateField(null=True, blank=True)
    useage = models.FloatField(default=0)
    def __str__(self):
        return '%s-%s-%s-%s-%s' %(self.port.card.first().ip)