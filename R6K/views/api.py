from django.shortcuts import HttpResponse
import json,queue
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F
from R6K import models
from IXIA import models as ixia
import time,datetime
from django.core.mail import send_mail,EmailMessage
from django.conf import settings
from django.utils import timezone
from R6K.views.log import Logger

q=queue.Queue()
log=Logger()
def get_request_ip(request):
    try:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]  # 所以这里是真实的ip
        else:
            ip = request.META.get('REMOTE_ADDR')  # 这里获得代理ip
    except:
        ip = None
    return ip

def client_config(request,eid):
    if request.method=='GET' and eid=='rootnt':
        node_obj = list(models.node_info.objects.filter(status__in=(0,1,2,3)).values_list('nid','ip','username','password').all())
        return HttpResponse(json.dumps(node_obj))
    elif request.method=='GET' and eid=='ixia':
        ixia_obj=list(ixia.chassis.objects.values_list('id','ip').all())
        return HttpResponse(json.dumps(ixia_obj))
    else:
        return HttpResponse('你大爷的，滚蛋！！！')

@csrf_exempt
def service_report(request,choice):
    ip=get_request_ip(request)
    print(ip)
    if ip != "127.0.0.1":
        return HttpResponse(json.dumps('你大爷的，滚蛋！！！'))
    if request.method == 'POST':
        datas = json.loads(request.body,encoding='utf-8')
        status=200
        # 把数据存下来，判断是否是更新使用率
        if choice == 'should':
            for data in datas:
                # print(data)
                node = models.node_info.objects.filter(nid=data['id']).values('ip', 'status', 'share').first()
                # 判断最新的node的状态是否跟原值一致
                if data['status'] != node['status']:
                    try:
                        models.node_info.objects.filter(nid=data['id']).update(status=data['status'])
                        log.log('report node status %s for node %s success' % (data, node['ip']), True)
                    except Exception as e:
                        log.log('report node status %s for node %s,fail reason %s' % (data, node['ip'], e), False)
                if not node['share']:
                    dealEvent(data['id'], data['status'])
                  # 判断是否已创建今天的记录
                    if models.utilization.objects.filter(node_id=data['id'], day=time.strftime('%Y-%m-%d')).count():
                        if not int(data['should']):
                            # return HttpResponse(json.dumps("---no change---"))
                            continue
                        useage=models.utilization.objects.filter(node_id=data['id'],day=time.strftime('%Y-%m-%d')).values('useage').first()['useage']+1.04
                        # print(useage)
                        try:
                            models.utilization.objects.filter(node_id=data['id'],day=time.strftime('%Y-%m-%d')).update(useage=float('%.2f' % useage))
                            log.log('report node useage to %s for node %s success' % (data['should'], node['ip']), True)
                        except Exception as e:
                            log.log('report node useage %s for node %s,fail reason %s' % (data, node['ip'], e), False)
                            # return HttpResponse(json.dumps("----database modify fail----"), status=400)
                            status=400
                    else:
                        useage=0.16+1.04*int(data['should'])
                        try:
                            models.utilization.objects.create(node_id=data['id'], day=time.strftime('%Y-%m-%d'),useage=float('%.2f' % useage))
                            log.log('create and report node useage to %s for node %s' % (data['should'], node['ip']), True)
                        except Exception as e:
                            log.log('create and report node useage %s for node %s,fail reason %s' % (data, node['ip'], e),False)
                            # return HttpResponse(json.dumps("----database modify fail----"), status=400)
                            status=400
            start_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '10:35', '%Y-%m-%d%H:%M')
            end_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '11:45', '%Y-%m-%d%H:%M')
            cur_time = datetime.datetime.now()
            #只在规定时间内进行邮件通知
            if cur_time > start_time and cur_time < end_time:
                mailForNode()
        #判断是否是更新硬件信息
        elif choice=='type':
            for data in datas:
                node = models.node_info.objects.filter(nid=data['id']).values('ip', 'status', 'share').first()
                # 判断最新的node的状态是否跟原值一致
                if data['status'] != node['status']:
                    try:
                        models.node_info.objects.filter(nid=data['id']).update(status=data['status'])
                        log.log('report node status to %s for node %s' % (data['status'], node['ip']), True)
                    except Exception as e:
                        log.log('report data %s for node %s,fail reason %s' % (data, node['ip'], e), False)
                if not node['share']:
                    dealEvent(data['id'], data['status'])
                if data['status']!=0:
                    #如果status不为0，其他信息必然没有获取到，直接结束
                    # return HttpResponse(json.dumps("----invalid data----"))
                    continue
                #判断新获取的盒子类型不同于数据库中存储的盒子类型
                original = models.node_info.objects.filter(nid=data['id']).values('mode','type', 'sn', 'backplane', 'hardware_info').first()
                # print(original['hardware_info'])
                #只要其中一个值不一样就进行更新
                if data['type'] != original['type'] or data['sn'] != original['sn'] or data['rev'] != original['backplane'] or data['hardware'] != original['hardware_info'] or data['mode'] != original['mode']:
                    try:
                        models.node_info.objects.filter(nid=data['id']).update(type=data['type'],sn=data['sn'], backplane=data['rev'],hardware_info=data['hardware'],mode=data['mode'])
                        log.log('report node info from %s to %s for node %s' % (original, data, node['ip']), data['id'])
                    except Exception as e:
                        log.log('report data %s for node %s,fail reason %s' % (data, node['ip'], e),False)
                        # return HttpResponse(json.dumps("----database modify fail----"),status=400)
                        status=400
        return HttpResponse(json.dumps("---report success---"),status=status)
    else:
        return HttpResponse(json.dumps("There's no action."))

@csrf_exempt
def report_ixia(request,id):
    ip = get_request_ip(request)
    if ip != "10.185.57.245":
        return HttpResponse(json.dumps('你大爷的，滚蛋！！！'))
    if request.method == 'POST':
        data = json.loads(request.body, encoding='utf-8')
        # print(data)
        #当status为False时，无需任何操作
        if not data['status']:
            return HttpResponse(json.dumps("---no change---"))
        ip=ixia.chassis.objects.filter(id=id).all().first()
        if 'useage' in data.keys():
            # print(type(data['useage']),data['useage'])
            for u in data['useage']:
                u=u.split(' ')
                port=ixia.port.objects.filter(card__ip_id=id,card__slot=int(u[0]),port_num=int(u[1])).first()
                if not port:
                    continue
                # print(u,port.id,port.status)
                if not port.status:
                    # 判断是否已创建今天的记录
                    if ixia.utilization.objects.filter(port=port, day=time.strftime('%Y-%m-%d')).count():
                        if int(u[2]):
                            try:
                                ixia.utilization.objects.filter(port=port, day=time.strftime('%Y-%m-%d')).update(useage=F('useage')+1.04)
                            except Exception as e:
                                print(11111111,e)
                    else:
                        try:
                            ixia.utilization.objects.create(port=port,day=time.strftime('%Y-%m-%d'),useage=1.04*int(u[2]))
                        except Exception as e:
                            print(222222222,e)
        elif 'chassis' in data.keys():
            # 更新chassis信息
            original = ip.chassis_info
            # print(original,type(original))
            if len(original.split('\n'))<=4:
                for k,v in data['chassis'].items():
                    original+='\n%s:%s' %(k,v)
                ixia.chassis.objects.filter(id=id).update(chassis_info=original)
            else:
                new=''
                for k,v in data['chassis'].items():
                    new+='\n%s:%s' %(k,v)
                if new not in original:
                    original=original.split('\n')
                    ixia.chassis.objects.filter(id=id).update(chassis_info='\n'+original[1]+'\n'+original[2]+'\n'+original[3]+new)
            # 更新card信息
            cards=ixia.card.objects.filter(ip_id=id).all()
            # print(data['card'])
            for card in cards:
                if str(card.slot) not in data['card']:
                    continue
                else:
                    original = card.card_info
                    new = ''
                    for k,v in data['card'][str(card.slot)].items():
                        new += '%s:%s\n' % (k, v)
                    # print(card,original,new)
                    # original = original.split('\n')
                    if len(original.split('\n')) < 2:
                        ixia.card.objects.filter(ip_id=id,id=card.id).update(card_info=original+new)
                    elif new not in original:
                        original=original.split('\n')
                        ixia.card.objects.filter(ip_id=id,id=card.id).update(card_info=original[0]+'\n'+new)
    return HttpResponse(json.dumps("---report success---"))

def dealEvent(id,status):
    """
    :param node:
    :param status:
    :return:
    """
    #如果node可正常访问且存在event记录，则删除
    if status==0 and models.event.objects.filter(node_id=id).count():
        models.event.objects.filter(node_id=id).delete()
    #如果node不能正常访问，且event没有记录，则生成新的记录，否则不处理
    elif status in [1,2] and (not models.event.objects.filter(node_id=id).count()):
        # print(timezone.localtime())
        models.event.objects.create(node_id=id,time=timezone.localtime())
    return None

def mailForNode():
    mailInfo = {'subject': [], 'to': [], 'content': []}
    cur_time=timezone.localtime()
    # print(cur_time-timezone.timedelta(hours=23,days=6))
    events=models.event.objects.filter(time__range=(timezone.localtime()-timezone.timedelta(hours=23,days=6),timezone.localtime()-timezone.timedelta(hours=23)))
    for event in events:
        temp = {'subject': '', 'to': '', 'content': ''}
        # print(event.node.user.first().username)
        temp['subject'] = 'Nodes were in abnormal condition for more than one day.'
        # 对同一收件人的邮件进行合并
        try:
            temp['to'] = event.node.user.first().username
        except Exception as e:
            print(event.node,event.node.user.first())
        temp['content'] ='%14s %7s %10s %10s %13s  %s\n' %(event.node.ip,event.node.type,event.node.bams,event.node.sn,event.node.get_status_display(),cur_time - event.time)
        try:
            index = mailInfo['to'].index(temp['to'])
        except Exception as e:
            index = -1
        if index == -1:
            mailInfo['subject'].append(temp['subject'])
            mailInfo['to'].append(temp['to'])
            mailInfo['content'].append('Hi %s,\nThe nodes under your signum were in abnormal condition for more than one day. The details are as follows:\n      Ip       Type   Bams-id      SN      Latest status  Duration\n' %(event.node.user.first().eid)+temp['content'])
        else:
            mailInfo['content'][index] +=temp['content']
    # print(mailInfo)
    endContent='\n\nhttp://10.185.57.124:8888/r6k/nodes'
    if len(mailInfo['to']):
        # print(mailInfo)
        # 发送邮件
        index = 0
        for t in mailInfo['to']:
            send_mail(mailInfo['subject'][index],mailInfo['content'][index]+endContent,settings.EMAIL_HOST_USER, [t],fail_silently=False)
            index += 1
    mailInfo = {'subject': [], 'to': [], 'content': [], 'cc': []}
    events = models.event.objects.filter(time__lt=timezone.localtime()-timezone.timedelta(hours=23,days=6))
    for event in events:
        temp = {'subject': '', 'to': '', 'content': '', 'cc': ''}
        temp['subject'] = 'Nodes were in abnormal condition for more than one week.'
        # 对同一收件人的邮件进行合并
        temp['to'] = event.node.user.first().username
        temp['content']='%14s %7s %10s %10s %13s  %s\n' %(event.node.ip,event.node.type,event.node.bams,event.node.sn,event.node.get_status_display(),cur_time-event.time)
        # print(event.node.user.first().line,type(event.node.user.first().line))
        temp['cc']=models.line_manager.objects.filter(id=event.node.user.first().line+1).values('manager_email').first()['manager_email']
        try:
            index = mailInfo['to'].index(temp['to'])
        except Exception as e:
            index = -1
        if index == -1:
            mailInfo['subject'].append(temp['subject'])
            mailInfo['to'].append(temp['to'])
            mailInfo['content'].append('Hi %s,\nThe nodes under your signum were in abnormal condition for more than one week. The details are as follows:\n      Ip       Type   Bams-id      SN      Latest status  Duration\n' % (event.node.user.first().eid)+temp['content'])
            mailInfo['cc'].append(temp['cc'])
        else:
            mailInfo['content'][index] +=temp['content']
    print(mailInfo)
    if len(mailInfo['to']):
        # 发送邮件
        index = 0
        for t in mailInfo['to']:
            EmailMessage(mailInfo['subject'][index],mailInfo['content'][index]+endContent,settings.EMAIL_HOST_USER,[t],cc=[mailInfo['cc'][index]]).send()
            index += 1