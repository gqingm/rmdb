from django.db import models

class user_info(models.Model):
    nid = models.BigAutoField(primary_key=True)
    username = models.EmailField(max_length=32,null=False,blank=False,default=None,unique=True)
    password=models.CharField(max_length=32,default=None)
    eid=models.CharField(max_length=7,unique=True)
    team=models.CharField(max_length=32)
    line_choice = ((0, 'NT'),
                   (1, 'HW'),
                   (2, 'FPGA'),
                   (3, 'FDU A'),
                   (4, 'FDU B'),
                   (5, 'FDU C'),
                   (6, 'FDU D'),
                   (7, 'FDU E'),
                   (8, 'FDU F'),
                   (9, 'FDU G'),
                   (10, 'FDU H'),
                   (11, 'PIDS'),
                   (12, 'EOT'),)
    line = models.PositiveSmallIntegerField(choices=line_choice, default=None)
    superuser=models.BooleanField(default=False)
    def __str__(self):
        return self.eid

class line_manager(models.Model):
    manager_email=models.EmailField(max_length=32)
    def __str__(self):
        return self.manager_email

class node_info(models.Model):
    nid = models.BigAutoField(primary_key=True)
    user=models.ManyToManyField(to='user_info',through='node2user',through_fields=('nid','uid'))
    ip=models.GenericIPAddressField(null=False,blank=False,unique=True)
    username=models.CharField(default='cde',max_length=16)
    password=models.CharField(default='Spitfire_12345',max_length=32)
    console=models.CharField(null=True,blank=True,max_length=48)
    sn=models.CharField(null=True,blank=True,max_length=12)
    bams=models.CharField(null=True,blank=True,unique=True,max_length=10)
    rack=models.CharField(null=True,blank=True,max_length=8)
    location=models.CharField(null=True,blank=True,max_length=24)
    deleted=models.BooleanField(default=False)
    status_choice=((0,'on line'),
                   (1,'login fail'),
                   (2,'telnet fail'),
                   (3,'release'),
                   (4,'unavailable'),
                   (5,'return to factory'),
                   (6,'abandoned'),
                   )
    status=models.SmallIntegerField(choices=status_choice,default=0)
    type=models.CharField(null=True,blank=True,default=None,max_length=8)
    hardware_info=models.CharField(null=True,blank=True,max_length=256)
    topo=models.CharField(null=True,blank=True,default=None,max_length=64)
    backplane=models.CharField(null=True,blank=True,default=None,max_length=8)
    mode_choice = ((0, 'D'),(1, 'C'))
    mode=models.SmallIntegerField(choices=mode_choice,default=0)
    share=models.BooleanField(default=False)
    comments=models.CharField(null=True,blank=True,max_length=255)
    purpose_choice = ((0, 'None'),
                      (1, 'Centralized regression-FT'),
                      (2, 'Centralized regression-ST'),
                      (3, 'Centralized regression-1D-KPI'),
                      (4, 'Centralized regression-IoT'),
                      (5, 'Maintain'),
                      (6, 'E2E'),
                      (7, 'Manual Test'),
                      )
    purpose = models.SmallIntegerField(choices=purpose_choice,default=0)
    def __str__(self):
        return self.ip

class node2user(models.Model):
    nid=models.ForeignKey(to='node_info',to_field='nid',on_delete=models.CASCADE)
    uid=models.ForeignKey(to='user_info',to_field='nid',on_delete=models.CASCADE)

class utilization(models.Model):
    node=models.ForeignKey(node_info,on_delete=models.DO_NOTHING)
    day=models.DateField(null=True,blank=True)
    useage=models.FloatField(default=0.16)
    def __str__(self):
        return "%s-%s-%s" %(self.node.ip,self.day,self.useage)

class event(models.Model):
    node=models.ForeignKey(node_info,on_delete=models.DO_NOTHING)
    time=models.DateTimeField(null=True,blank=True)
    def __str__(self):
        return "%s-%s" %(self.node.ip,self.time.strftime('%Y-%m-%d'))