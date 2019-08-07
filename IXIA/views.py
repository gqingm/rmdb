#!/usr/bin/env python
#coding=utf-8
import datetime,os,shutil,time
from django.shortcuts import HttpResponse,render
from RMDB.settings import BASE_DIR
from IXIA import models
from R6K.models import user_info
from django.http import JsonResponse
from R6K.views.account import check_login
from R6K.views import api
from django.core.mail import EmailMessage
from django.conf import settings

log=api.log
def filter_ixia(request,obj):
    filter_conditions = {}
    filter_for_css = {}
    if obj:
        for key, val in request.GET.items():
            filter_for_css[key] = val
        val = request.GET.get('_i')
        if val==None:
            # val=obj[0].card.values('ip__ip').first()['ip__ip']
            val=obj[0].card.values('ip__ip').first()['ip__ip']
        if val:
            filter_conditions['card__ip__ip'] =val
            filter_for_css['_i']=val
        val = request.GET.get('_c')
        if val:
            filter_conditions['card__slot'] = val
        val = request.GET.get('_ct')
        if val:
            filter_conditions['card__card_info__icontains'] = val
        val = request.GET.get('_s')
        if val not in [None,'']:
            filter_conditions['status'] = val
        val = request.GET.get('_sw')
        if val:
            filter_conditions['switch__icontains'] = val
        val = request.GET.get('_l')
        if val:
            filter_conditions['user__line'] = val
        val = request.GET.get('_u')
        if val:
            filter_conditions['user__eid__iexact'] = val
        val = request.GET.get('_p')
        if val:
            filter_conditions['purpose__icontains'] = val
        # print("filter_conditions,filter_for_css:",filter_conditions,filter_for_css)
        obj = obj.filter(**filter_conditions)
    return obj,filter_for_css

def deal_table(date_list,useages):
    """
    补全node 30天的使用率数据
    :param date_list:
    :param useages:
    :return:
    """
    i,j=0,0
    new_list=[]
    while i<=29:
        if j<len(useages) and date_list[i]==useages[j][0]:
            new_list.append(useages[j])
            j+=1
        else:
            new_list.append((date_list[i],0))
        i+=1
    return new_list

@check_login
def add_ixia(request):
    """
    :param request:
    :return:
    """
    ret={'status':True,'message':None}
    if request.method=='POST':
        # print(request.POST)
        #获取当前用户的信息
        user_obj = user_info.objects.filter(nid=request.session.get('user_info')['nid']).first()
        #判断是否有权限
        if user_obj.superuser:
            #获取用户填写的信息
            ip,chassisinfo,slots,sbams,ports=request.POST['ip'],request.POST['cinfo'],request.POST['slot'],request.POST['slotbams'],request.POST['ports']
            # print(ip,chassisinfo,slots,sbams,ports)
            try:
                #查询或创建chassis
                if not models.chassis.objects.filter(ip=ip).count():
                    chassisinfo=chassisinfo.split(',')
                    # print(chassisinfo)
                    ch=models.chassis.objects.create(ip=ip,chassis_info='\nLocation:%s\nRack:%s\nBams:%s\n' %(chassisinfo[0],chassisinfo[1],chassisinfo[2]))
                else:
                    ch=models.chassis.objects.filter(ip=ip).first()
                #字符串切割
                slots=slots.replace(' ','').split(',')
                sbams=sbams.replace(' ','').split(',')
                ports=ports.replace(' ','').split(',')
                for slot,bams,port in zip(slots,sbams,ports):
                    # print(slot,bams,port)
                    # 创建对应的card
                    if not models.card.objects.filter(ip=ch,slot=int(slot)).count():
                        card=models.card.objects.create(ip=ch,slot=int(slot),card_info='Bams:%s\n' %bams)
                    else:
                        models.card.objects.filter(ip=ch, slot=int(slot)).update(card_info='Bams:%s\n' % bams)
                        card=models.card.objects.filter(ip=ch,slot=int(slot)).all().first()
                    # print(card,type(card))
                    # 创建对应的port
                    port_count=models.port.objects.filter(card__ip=ch,card__slot=int(slot)).count()
                    if not port_count:
                        for i in range(1,int(port)+1):
                            card.port_set.create(port_num=i)
                    elif port_count < int(port):
                        for i in range(port_count+1,int(port)+1):
                            card.port_set.create(port_num=i)
                    elif port_count > int(port):
                        for i in range(int(port)+1,port_count+1):
                            pobj=models.port.objects.filter(card__ip=ch,card__slot=int(slot),port_num=i).all().first()
                            # print(pobj,pobj.id)
                            models.utilization.objects.filter(port=pobj).delete()
                            pobj.delete()
            except Exception as e:
                print(e)
                ret['status']=False
                ret['message']='%s create fail' %ip
    return HttpResponse(JsonResponse(ret))

@check_login
def delete_chassis(request):
    """
    :param request:
    :return:
    """
    ret={'status':True,'message':None}
    if request.method=='POST':
        # print(request.POST)
        #获取当前用户的信息
        user_obj = user_info.objects.filter(nid=request.session.get('user_info')['nid']).first()
        #判断是否有权限
        if user_obj.superuser:
            #获取用户填写的信息
            ports=models.port.objects.filter(card__ip_id=request.POST['ip_id']).all()
            #备份数据库
            backupData()
            try:
                for port in ports:
                    # print(port)
                    models.utilization.objects.filter(port=port).delete()
                    port.delete()
                models.card.objects.filter(ip_id=request.POST['ip_id']).delete()
                models.chassis.objects.filter(id=request.POST['ip_id']).delete()
                log.log('Ixia chassis %s was deleted by %s' %(request.POST['ip_id'], request.session.get('user_info')['eid']), 1)
            except Exception as e:
                ret['status']=False
                ret['message']='delete fail'
    return JsonResponse(ret)

@check_login
def edit_chassis(request):
    """
    :param request:
    :return:
    """
    ret={'status':True,'message':None}
    if request.method=='POST':
        # print(request.POST)
        #获取当前用户的信息
        user_obj = user_info.objects.filter(nid=request.session.get('user_info')['nid']).first()
        #判断是否有权限
        if user_obj.superuser:
            #获取用户填写的信息
            try:
                ch_obj=models.chassis.objects.filter(id=request.POST['ip_id']).all().first()
                if ch_obj.ip != request.POST['ip']:
                    # print(ch_obj.ip,request.POST['ip'],type(request.POST['ip']))
                    models.chassis.objects.filter(id=request.POST['ip_id']).update(ip=request.POST['ip'])
                    log.log('Ixia chassis %s info update,ip:%s->%s by %s' %(request.POST['ip_id'], ch_obj.ip, request.POST['ip'],request.session.get('user_info')['eid']), 1)
                models.chassis.objects.filter(id=request.POST['ip_id']).update(chassis_info='\nLocation:%s\nRack:%s\nBams:%s\n' % (request.POST['location'], request.POST['rack'], request.POST['chbams']))
                log.log('Ixia chassis %s info update: %s->\nLocation:%s\nRack:%s\nBams:%s by %s' %(request.POST['ip_id'],ch_obj.chassis_info,request.POST['location'], request.POST['rack'], request.POST['chbams'],request.session.get('user_info')['eid']), 1)
            except Exception as e:
                ret['status']=False
                ret['message']='chassis info update fail'
    return JsonResponse(ret)

@check_login
def edit_card(request):
    """
    :param request:
    :return:
    """
    ret={'status':True,'message':None}
    if request.method=='POST':
        print(request.POST)
        #获取当前用户的信息
        user_obj = user_info.objects.filter(nid=request.session.get('user_info')['nid']).first()
        #判断是否有权限
        if user_obj.superuser:
            #获取用户填写的信息
            try:
                card_obj=models.card.objects.filter(id=request.POST['card_id']).all().first()
                if card_obj.slot != int(request.POST['slot']) and not models.card.objects.filter(ip__ip=request.POST['ip'],slot=int(request.POST['slot'])).count():
                    # print(ch_obj.ip,request.POST['ip'],type(request.POST['ip']))
                    models.card.objects.filter(id=request.POST['card_id']).update(ip__ip=request.POST['ip'],slot=int(request.POST['slot']))
                    log.log('Ixia card %s info update, ip:%s->%s, slot:%s->%s by %s' %(card_obj.id,card_obj.ip__ip,request.POST['ip'],card_obj.slot,request.POST['slot'],request.session.get('user_info')['eid']), 1)
                else:
                    # ret['status'] = False
                    ret['message'] = 'The slot %s has already exists' %request.POST['slot']
                models.card.objects.filter(id=request.POST['card_id']).update(status=int(request.POST['status']),card_info='Bams:%s\n' % (request.POST['cardbams']))
                log.log('Ixia card %s info update, status:%s->%s, cardinfo:%s->Bams:%s by %s' %(
                    card_obj.id,card_obj.status,request.POST['status'],card_obj.card_info,request.POST['cardbams'],
                    request.session.get('user_info')['eid']), 1)
            except Exception as e:
                ret['status']=False
                ret['message']='card info update fail'
    return JsonResponse(ret)

@check_login
def delete_card(request):
    """
    :param request:
    :return:
    """
    ret={'status':True,'message':None}
    if request.method=='POST':
        # print(request.POST)
        #获取当前用户的信息
        user_obj = user_info.objects.filter(nid=request.session.get('user_info')['nid']).first()
        #判断是否有权限
        if user_obj.superuser:
            #获取用户填写的信息
            ports=models.port.objects.filter(card__id=request.POST['card_id']).all()
            #备份数据库
            backupData()
            try:
                for port in ports:
                    models.utilization.objects.filter(port=port).delete()
                    port.delete()
                models.card.objects.filter(id=request.POST['card_id']).delete()
                log.log('Ixia card %s was deleted by %s' % (request.POST['card_id'], request.session.get('user_info')['eid']), 1)
            except Exception as e:
                ret['status']=False
                ret['message']='delete fail'
    return JsonResponse(ret)

@check_login
def edit_ports(request):
    """
    :param request:
    :return:
    """
    ret={'status':True,'message':''}
    if request.method=='POST':
        datas=eval(request.POST['data'])
        statusmap={'booked':0,'broken':1,'release':2}
        mailInfo={'subject':[],'to':[],'content':[],'cc':[]}
        # print(datas)
        for data in datas:
            temp={'subject':'','to':'','content':'','cc':''}
            port=models.port.objects.filter(id=int(data['id'])).values('card__ip__ip','card__slot','user__eid','port_num','status','purpose','switch','usecycle','comments').first()
            print(port['purpose'],data['purpose'][1],port['user__eid'],data['user'][1],port['switch'],data['switch'][1],port['usecycle'],data['usecycle'][1],port['comments'],data['comments'][1],port['status'],statusmap[data['portstatus'][1]])
            if port['purpose']!=data['purpose'][1] or (port['user__eid'] and port['user__eid']!=data['user'][1]) or (port['switch']!=data['switch'][1] and port['switch']) or port['usecycle']!=data['usecycle'][1] or (port['comments']!=data['comments'][1] and port['comments']) or port['status']!=statusmap[data['portstatus'][1]]:
                ret['status'] = False
                ret['message'] += 'For port %s-%s-%s, the original data was not latest, please refresh and try to modify again.' % (port['card__ip__ip'],port['card__slot'],port['port_num'])
            else:
                try:
                    old_user=user_info.objects.filter(eid=port['user__eid']).all().first()
                    # print(data,port)
                    if statusmap[data['portstatus'][0]]==0:
                        models.port.objects.filter(id=int(data['id'])).update(status=statusmap[data['portstatus'][0]],purpose=data['purpose'][0],switch=data['switch'][0],usecycle=data['usecycle'][0],comments=data['comments'][0],share=False)
                        log.log('Ixia port %s-%s-%s info update, status:%s->%s,purpose:%s->%s, switch:%s->%s, usecycle:%s->%s, comments:%s->%s by %s'
                                %(port['card__ip__ip'],port['card__slot'],port['port_num'],port['status'],statusmap[data['portstatus'][0]],
                                  port['purpose'],data['purpose'][0],port['switch'],data['switch'][0],port['usecycle'],data['usecycle'][0],port['comments'],data['comments'][0],request.session.get('user_info')['eid']),1)
                        user = user_info.objects.filter(eid=data['user'][0].lower()).all().first()
                        if not user:
                            ret['status'] = False
                            ret['message'] += 'user %s was not registered' %data['user'][0]
                        else:
                            models.port.objects.filter(id=int(data['id'])).update(user=user)
                            log.log('Ixia port %s-%s-%s assigned from %s to %s by %s' % (port['card__ip__ip'], port['card__slot'], port['port_num'],
                                    port['user__eid'],data['user'][0],request.session.get('user_info')['eid']), 1)
                            # print(user, user['username'])
                            if not old_user:
                                temp['cc']=''
                            else:
                                temp['cc']=old_user.username
                            temp['subject'] = 'assign'
                            #对同一收件人的邮件进行合并
                            temp['to']=user.username
                            temp['content']='%s-%s-%s' %(port['card__ip__ip'],port['card__slot'], port['port_num'])
                    else:
                        if statusmap[data['portstatus'][0]]==2:
                            models.port.objects.filter(id=int(data['id'])).update(user='',status=2,purpose='',usecycle='',comments='',share=True)
                        else:
                            models.port.objects.filter(id=int(data['id'])).update(user='',status=1,purpose='',usecycle='',comments='')
                        log.log('Ixia port %s-%s-%s info update, status:%s->%s by %s'%(port['card__ip__ip'], port['card__slot'], port['port_num'], port['status'],statusmap[data['portstatus'][0]],request.session.get('user_info')['eid']), 1)
                        if old_user:
                            temp['subject'] = 'releas'
                            temp['to'] = old_user.username
                            temp['content'] = '%s-%s-%s' % (port['card__ip__ip'], port['card__slot'], port['port_num'])
                            temp['cc'] = ''
                    if temp['to']:
                        try:
                            index = mailInfo['to'].index(temp['to'])
                        except Exception as e:
                            index = -1
                        # print(index)
                        # 如果在收件人列表里没有该用户，创建，否则，只更新邮件内容
                        #bug:当assign和release给同一人时，邮件不会被合并
                        if index == -1 or mailInfo['subject'][index]!=temp['subject']:
                            mailInfo['subject'].append(temp['subject'])
                            mailInfo['to'].append(temp['to'])
                            mailInfo['content'].append('Hi %s,\n%s %sed ixia port ' %(data['user'][0].lower(), request.session.get('user_info')['eid'],temp['subject']) + temp['content'])
                            mailInfo['cc'].append([temp['cc']])
                        else:
                            mailInfo['content'][index] += ', ' + temp['content']
                            mailInfo['cc'][index].append(temp['cc'])
                except Exception as e:
                    print(e)
                    ret['status']=False
                    ret['message']+='port update fail\r\n'
        if len(mailInfo['to']) and ret['status']:
            # print(mailInfo)
            #发送邮件
            index=0
            endContent={'assign':' to you.\n\n\n\n\nhttp://10.185.57.124:8888/r6k/ixia',
                        'releas':' which used by you in the past.\n\n\n\n\nhttp://10.185.57.124:8888/r6k/ixia'}
            for t in mailInfo['to']:
                #抄送人去重
                cc=list(set(mailInfo['cc'][index]+[request.session.get('user_info')['username']]))
                # print(cc)
                EmailMessage('Ixia ports %sed' %(mailInfo['subject'][index]),mailInfo['content'][index]+endContent[mailInfo['subject'][index]],
                             settings.EMAIL_HOST_USER, [t],cc=cc).send()
                index+=1
    return JsonResponse(ret)

@check_login
def del_ports(request):
    """
    :param request:
    :return:
    """
    ret={'status':True,'message':None}
    if request.method=='POST':
        # print(request.POST)
        #获取当前用户的信息
        user_obj = user_info.objects.filter(nid=request.session.get('user_info')['nid']).first()
        #判断是否有权限
        if user_obj.superuser:
            #获取用户填写的信息
            port_list=request.POST.getlist('data')
            # print(port_list,type(port_list))
            #备份数据库
            backupData()
            for port in port_list:
                try:
                    models.utilization.objects.filter(port_id=int(port)).delete()
                    # card=models.card.objects.filter(port)
                    models.port.objects.filter(id=int(port)).delete()
                    log.log('Ixia port %s was deleted by %s' % (port,request.session.get('user_info')['eid']), 1)
                except Exception as e:
                    print(e)
                    ret['status']=False
                    ret['message']='port delete fail'
    return JsonResponse(ret)

def ixia(request):
    """
    :param request:
    :return:
    """
    # 获取session中的user信息
    user = request.session.get('user_info')
    filter_list = {}
    judge={'ip':'','slot':0}
    # 定义最近30天的日期列表
    date_list = [datetime.datetime.now().date() - datetime.timedelta(days=i) for i in range(30, 0, -1)]
    pre_month_days=30-date_list[-1].day
    # print(pre_month_days)
    #获取所有的port，并按ip，slot，port进行排序
    port_objs=models.port.objects.filter(share=False).all()
    # port_objs=models.port.objects.all()
    filter_list['status']=port_objs.values('status').distinct().order_by('status')
    #按过滤条件进行过滤
    port_objs,filter_for_css=filter_ixia(request,port_objs)
    #过滤后按ip，card，port依次进行排序
    port_objs=port_objs.distinct().order_by('card__ip__ip','card__slot','port_num')
    # print(port_objs)
    #获取对应的ip及卡号
    ips=port_objs.values('card__ip__ip').distinct().order_by('card__ip__ip')
    cards=port_objs.values('card__ip__ip','card__slot').distinct().order_by('card__ip__ip','card__slot')
    # print('ips,cards:',ips,cards)
    #存储每个ip及卡号对应的port数量
    count=[[],[]]
    for ip in ips:
        count[0].append(port_objs.filter(card__ip__ip=ip['card__ip__ip']).count())
    for card in cards:
        count[1].append(port_objs.filter(card__ip__ip=card['card__ip__ip'],card__slot=card['card__slot']).count())
    # print(count)
    #获取port总数量
    total=port_objs.count()
    # print('port_count:',total)
    #筛选过滤条件
    filter_list['ip']=models.chassis.objects.values('ip').distinct().order_by('ip')
    filter_list['card']=models.card.objects.values('slot').distinct().order_by('slot')
    filter_list['port']=models.port.objects.values('port_num').distinct().order_by('port_num')
    filter_list['switch']=models.port.objects.values('switch').distinct().order_by('switch')
    filter_list['line']=models.port.objects.values('user__line').distinct().order_by('user__line')
    #如果列表的第一个元素为空/None,则切片取后面的所有元素
    if filter_list['line'][0]['user__line'] == '' or filter_list['line'][0]['user__line'] == None:
        filter_list['line'] = filter_list['line'][1::]
    # filter_list['line']=[]
    # users=models.port.objects.values('user').distinct().order_by('user')
    # for u in users:
    #     print(u)
    print(filter_list)
    # 遍历每个盒子信息
    for port in port_objs:
        # 获取每个盒子最近30天内的数据
        port.useages = list(port.utilization_set.filter(day__range=(date_list[0], date_list[-1])).values_list('day', 'useage'))
        # 如果获取到数据不足30天
        # print(node.useages)
        if len(date_list) != len(port.useages):
            # 补充缺少的日期和数据
            port.useages = deal_table(date_list, port.useages)
    return render(request,'ixia_info.html',locals())

def backupData():
    file=os.path.join(BASE_DIR,'db.sqlite3')
    backupfile=os.path.join(BASE_DIR,'db_%s.sqlite3' %time.strftime('%Y%m%d%H%M%S',time.localtime()))
    shutil.copy(file,backupfile)