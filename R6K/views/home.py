#!/usr/bin/env python
# coding=utf-8
import datetime
from django.shortcuts import render,redirect,HttpResponse
from django.db.models import Avg
from django.db.models import Q
from django.http import JsonResponse
from RMDB.settings import BASE_DIR
from django.views.decorators.csrf import csrf_protect
from R6K import models
from IXIA import models as ixia
from .account import check_login
from django.core.paginator import Paginator,EmptyPage
from R6K.views import api
from django.core.mail import send_mail
from django.conf import settings

log=api.log
def get_filter_result(request,obj):
    """
    按过滤条件对node进行过滤
    :param request:
    :param obj:
    :return:
    """
    filter_conditions = {}
    filter_for_css={}
    for key,val in request.GET.items():
        filter_for_css[key] = val
    try:
        val=request.GET.get('_s')
    except Exception as e:
        val=10
    try:
        val=request.GET.get('_tp')
    except Exception as e:
        val=''
    if val:
        filter_conditions['topo__exact'] = val
    try:
        val = request.GET.get('_u')
    except Exception as e:
        val = ''
    if val:
        filter_conditions['user__eid__iexact'] = val.lower()
    try:
        val = request.GET.getlist('_l')[0]
    except Exception as e:
        val = ''
    if val:
        filter_conditions['user__line'] = val
    try:
        val = request.GET.get('_t')
    except Exception as e:
        val = ''
    if val:
        filter_conditions['user__team'] = val
    try:
        val = request.GET.get('_ty')
    except Exception as e:
        val = ''
    if val:
        filter_conditions['type__contains'] = val
    try:
        val = request.GET.get('_v')
    except Exception as e:
        val = ''
    if val:
        filter_conditions['backplane'] = val
    try:
        val = request.GET.get('_loc')
    except Exception as e:
        val = ''
    if val:
        filter_conditions['location'] = val
    try:
        val = request.GET.get('_r')
    except Exception as e:
        val = ''
    if val:
        filter_conditions['rack'] = val
    try:
        val = request.GET.get('_b')
    except Exception as e:
        val = ''
    if val:
        filter_conditions['bams__icontains']=val
    try:
        val = request.GET.get('_st')
    except Exception as e:
        val = ''
    if val:
        filter_conditions['status'] = val
    try:
        val = request.GET.get('_m')
    except Exception as e:
        val = ''
    if val:
        filter_conditions['mode'] = val
    try:
        val = request.GET.get('_q')
    except Exception as e:
        val = ''
    if val:
        filter_conditions['hardware_info__iregex'] = val
    try:
        filter_for_css.pop('page')
    except Exception as e:
        pass
    # print("filter_conditions",filter_conditions,filter_for_css)
    obj=obj.filter(**filter_conditions)
    return obj,filter_conditions,filter_for_css

def filter_icon(request,obj,obj1):
    """
    按时间,line,type进行过滤
    :param request:
    :param obj:
    :return:
    """
    filter_conditions = {}
    filter_for_css={}
    for key,val in request.GET.items():
        filter_for_css[key] = val
    try:
        val=request.GET.get('startdate')
    except Exception as e:
        val=''
    if not val:
        filter_for_css['startdate']=datetime.date.today()-datetime.timedelta(30)
    else:
        val=val.split('-')
        filter_for_css['startdate']=datetime.date(int(val[0]),int(val[1]),int(val[2]))
    try:
        val = request.GET.get('enddate')
    except Exception as e:
        val = ''
    if not val:
        filter_for_css['enddate'] = datetime.date.today()-datetime.timedelta(1)
    else:
        val = val.split('-')
        filter_for_css['enddate']=datetime.date(int(val[0]), int(val[1]), int(val[2]))
    try:
        val = request.GET.getlist('line')[0]
    except Exception as e:
        val = ''
    if val:
        filter_conditions['user__line'] = val
    obj1=obj1.filter(**filter_conditions)
    try:
        val = request.GET.get('duttype')
    except Exception as e:
        val = ''
    if val:
        filter_conditions['type__contains'] = val
    print("filter_conditions,filter_for_css:",filter_conditions,filter_for_css)
    obj=obj.filter(**filter_conditions)
    return obj,obj1,filter_conditions,filter_for_css

def JudgeUseage(nodes):
    """
    按条件获取node个数
    :param nodes:
    :return:
    """
    HighUsage=nodes.filter(useage_avg__gt=70).count()
    Other = nodes.filter(Q(useage_avg__gt=30) & Q(useage_avg__lte=70)).count()
    LowUsage = nodes.filter(Q(useage_avg__gt=15) & Q(useage_avg__lte=30)).count()
    LowerUsage = nodes.filter(Q(useage_avg__gt=5) & Q(useage_avg__lte=15)).count()
    LowestUsage = nodes.filter(Q(useage_avg__gt=0.161) & Q(useage_avg__lte=5)).count()
    Unused = nodes.filter(useage_avg__lte=0.161, status__in=(0,1)).count()
    Unreachable = nodes.filter(useage_avg__lte=0.161, status=2).count()
    return HighUsage,LowUsage,LowerUsage,LowestUsage,Unused,Unreachable,Other

def JudgeIxiaUseage(ixias):
    """
    按条件获取ixia port个数
    :param ixias:
    :return:
    """
    HighUsage=ixias.filter(useage_avg__gt=70).count()
    Other = ixias.filter(Q(useage_avg__gt=30) & Q(useage_avg__lte=70)).count()
    LowUsage = ixias.filter(Q(useage_avg__gt=15) & Q(useage_avg__lte=30)).count()
    LowerUsage = ixias.filter(Q(useage_avg__gt=5) & Q(useage_avg__lte=15)).count()
    LowestUsage = ixias.filter(Q(useage_avg__gt=0) & Q(useage_avg__lte=5)).count()
    Unused = ixias.filter(useage_avg__lte=0, status=0).count()
    return HighUsage,LowUsage,LowerUsage,LowestUsage,Unused,Other

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
            new_list.append((date_list[i],0.16))
        i+=1
    return new_list

@check_login
@csrf_protect
def add_node(request):
    ret={'status':1,'message':None}
    if request.method=='POST':
        #获取当前用户的信息
        user_obj = models.user_info.objects.filter(nid=request.session.get('user_info')['nid']).first()
        #获取用户填写的信息
        ip,console,username,password,location,rack,bams,topo=request.POST['ip'],request.POST['console'],request.POST['username'],request.POST['password'],request.POST['location'].replace(" ", ""),request.POST['rack'].replace(" ", ""),request.POST['bams'],request.POST['topo']
        #bams id不正确时，仅提示，但不强制
        if len(bams)<10 or not str(bams).startswith('1001'):
            ret['status'] = 0
            ret['message'] = 'bams id was incorrect,it should be 10 digits start with 1001\r\n'
        try:
            node_obj=models.node_info.objects.create(ip=ip,console=console,username=username,password=password,location=location,rack=rack,bams=bams,topo=topo)
            models.node2user.objects.create(uid=user_obj,nid=node_obj)
            log.log('add node %s and assign to user %s success' % (ip, request.session.get('user_info')['eid']), node_obj.nid)
        except Exception as e:
            log.log('add node %s and assign to user %s fail reason:%s' % (ip, request.session.get('user_info')['eid'],e), False)
            ret['status']=0
            ret['message']='node '+ip+' create failed, ip address or bams number conflict, please check.\r\n'
    return HttpResponse(JsonResponse(ret))

@check_login
@csrf_protect
def edit_node(request):
    ret={'status':1,'message':None}
    if request.method=='POST':
        print(request.POST)
        #获取修改设计的user和node信息
        user = models.user_info.objects.filter(eid=request.POST['user'].lower()).values('nid','eid','username').first()
        node=models.node_info.objects.filter(nid=request.POST['node_nid']).values('ip','console','username','password','location','rack','topo','bams','node2user__uid__eid','status').first()
        # print(node)
        #获取post请求中携带的信息
        nid,ip,console,username,password,location,rack,topo,bams=request.POST['node_nid'],request.POST['ip'],request.POST['console'],request.POST['username'],request.POST['password'],request.POST['location'].replace(" ", ""),request.POST['rack'].replace(" ", ""),request.POST['topo'],request.POST['bams']
        #获取status信息
        try:
            status=request.POST['status']
        except Exception as e:
            status=''
        # print(status,type(status))
        try:
            if ip!=node['ip'] or username!=node['username'] or password!=node['password'] or location!=node['location'] or rack!=node['rack'] or topo!=node['topo'] or console!=node['console']:
                #有任意信息修改时，更新node相关信息
                models.node_info.objects.filter(nid=nid).update(ip=ip,username=username,password=password,location=location.replace(" ", ""),rack=rack,topo=topo,console=console)
                log.log('edit node info from %s to %s success by %s' % ([node['ip'],node['location'],node['rack'],node['topo']], [ip,location,rack,topo],request.session.get('user_info')['eid']), nid)
            # else:
            #     models.node_info.objects.filter(nid=nid).update(deleted=False)
            # print(user_nid,nid)
            #如果获取的user不为当前node的所有者,且node当前所有者不为空
            # print(user['eid'],node['node2user__uid__eid'])
            if not user:
                pass
            elif user['eid']!=node['node2user__uid__eid']:
                # print(22222)
                #判断数据库中是否已存在node与user的映射关系，若存在进行更新
                if models.node2user.objects.filter(nid=nid).count():
                    models.node2user.objects.filter(nid=nid).update(uid=user['nid'])
                    models.node_info.objects.filter(nid=nid).update(share=False,status=0)
                else:
                    #若不存在则创建
                    models.node2user.objects.create(nid_id=nid,uid_id=user['nid'])
                    models.node_info.objects.filter(nid=nid).update(share=False,status=0)
                try:
                    send_mail('Node assign',
                              'Hi %s,\nNode %s was assigned to you by %s.\n\n\n\n\nhttp://10.185.57.124:8888/r6k' %(user['eid'],node['ip'],request.session.get('user_info')['eid']),
                              settings.EMAIL_HOST_USER,
                              [user['username'],request.session.get('user_info')['username']],
                              fail_silently=False)
                except Exception as e:
                    print(e)
                log.log('assign node %s from %s to %s success by %s' % (node['ip'],node['node2user__uid__eid'],user['eid'],request.session.get('user_info')['eid']), nid)
            if node['bams'] != bams:
                if len(bams)>10:
                    bams=bams[:10]
                #如果bams号有变更则进行更新
                models.node_info.objects.filter(nid=nid).update(bams=bams)
                log.log('modify node %s bams from %s to %s success by %s' % (node['ip'], node['bams'], bams,request.session.get('user_info')['eid']),nid)
            if status and status != '0':
                #node的状态有更改且不为on line，进行更新，并删除node与user的映射关系
                # print(555555,status,type(status))
                models.node_info.objects.filter(nid=nid).update(status=status,share=True)
                models.node2user.objects.filter(nid=nid).delete()
                try:
                    models.event.objects.filter(node_id=nid).delete()
                except Exception as e:
                    print('event delete fail',e)
                send_mail('Node release',
                          'Hi %s,\nYour node %s was released by %s.\n\n\n\n\nhttp://10.185.57.124:8888/r6k' % (node['node2user__uid__eid'], node['ip'], request.session.get('user_info')['eid']),
                          settings.EMAIL_HOST_USER,[user['username'], request.session.get('user_info')['username']],fail_silently=False)
                log.log('node %s status from %s to %s success by %s' % (node['ip'],models.node_info.status_choice[int(node['status'])][1], models.node_info.status_choice[int(status)][1], request.session.get('user_info')['eid']), nid)
            elif status:
                #否则修改node的status
                # print(11111111)
                models.node_info.objects.filter(nid=nid).update(status=status,share=False)
                log.log('modify node %s status from %s to %s success by %s' % (node['ip'],models.node_info.status_choice[int(node['status'])][1], models.node_info.status_choice[int(status)][1],request.session.get('user_info')['eid']), nid)
            if status=='3':
                #如果status的值为3，代表将盒子release，盒子变为共享
                models.node_info.objects.filter(nid=nid).update(share=True)
        except Exception as e:
            #记录node编辑失败的原因
            log.log('edit node info from %s to %s fail reason %s' % (node, [ip,console,username,password,location,rack,topo,bams,status],e), False)
            ret['status']=0
            ret['message']='node '+ip+' update failed\r\n'
    return HttpResponse(JsonResponse(ret))

@check_login
def upload(request):
    ret={'status':True,'message':''}
    if request.method == 'POST':
        #获取导入的文件信息，获取失败时返回None
        file_obj = request.FILES.get('myfile',None)
        # print(request.session.get('user_info'))
        user_obj = models.user_info.objects.filter(nid=request.session.get('user_info')['nid']).first()
        # print(user_obj.superuser,type(user_obj))
        # print(file_obj, type(file_obj))
        if file_obj:
            import os
            #定义导入文件的存放路径
            destination = open(os.path.join(BASE_DIR,'upload',file_obj.name), 'wb+')
            for chunk in file_obj.chunks():  # 分块写入文件
                destination.write(chunk)
            destination.close()
            import xlrd
            #读取导入excel的第一个sheet的内容
            datas=xlrd.open_workbook(destination.name).sheet_by_index(0)
            #获取sheet的行数和列数
            nrows = datas.nrows
            ncols = datas.ncols
            #定义空列表
            nu_list=[]
            #遍历sheet中每一行的内容
            if ncols>2 and ncols<9:
                for r in range(0, nrows):
                    data={'ip':None,'location':None,'bams':None,'rack':None,'topo':None,'username':'cde','password':'Spitfire_12345','console':''}
                    #遍历某一行中每一列的值
                    for c in range(0, ncols):
                        #如果数据为空，结束本次循环
                        if datas.cell(r, c).value=='':
                            continue
                        # print(datas.cell(r, c).value, type(datas.cell(r, c).value))
                        elif c==0:
                            #获取topo
                            data['topo'] = str(datas.cell(r, c).value)
                        elif c==1:
                            #获取IP
                            data['ip']=datas.cell(r, c).value.replace(" ", "")
                        elif c==2:
                            #获取location信息,并去掉空格
                            data['location']=datas.cell(r, c).value.replace(" ", "")
                        elif c==3:
                            #获取rack信息
                            data['rack']=datas.cell(r, c).value.replace(" ", "")
                        elif c==4 and str(datas.cell(r, c).value).startswith('1001'):
                            # print(str(datas.cell(r, c).value))
                            #获取bams id,且必须以1001开头
                            data['bams']=str(datas.cell(r, c).value).split('.')[0]
                        elif c==5:
                            data['username']=str(datas.cell(r, c).value)
                        elif c==6:
                            data['password']=str(datas.cell(r, c).value)
                        elif c==7:
                            data['console']=str(datas.cell(r, c).value)
                    # print(data)
                    if data['ip'] and data['rack'] and data['bams'] and data['location'] and data['topo'] and data['username'] and data['password']:
                        try:
                            #创建node表
                            obj=models.node_info.objects.create(ip=data['ip'],rack=data['rack'],bams=data['bams'],location=data['location'],topo=data['topo'],username=data['username'],password=data['password'],console=data['console'])
                            # print('obj:',obj,type(obj),request.session.get('user_info'))
                            log.log('create node %s success by %s,detail info:%s' % (data['ip'], [data['ip'],data['rack'],data['bams'],data['location'],data['topo'],data['username'],data['password'],data['console']],request.session.get('user_info')['eid']),obj.nid)
                            #创建node与user的对应关系
                            # print(user_obj)
                            nu_list.append(models.node2user(nid=obj, uid=user_obj))
                            log.log('assign node %s to user %s' % (data['ip'], request.session.get('user_info')['eid']), obj.nid)
                        except Exception as e:
                            log.log('create node %s fail reason:%s by %s' % (data['ip'],e,request.session.get('user_info')['eid']), False)
                            #创建失败时，提供提示信息
                            ret['status'] = False
                            ret['message'] += 'node '+data['ip']+' create failed, ip address or bams number conflict, please check.\r\n'
                    else:
                        ret['status'] = False
                        if not data['ip']:
                            ret['message'] +='ip is null\r\n'
                        else:
                            ret['message'] += 'incomplete information'+'node ' + data['ip'] + ' create failed\r\n'
                if nu_list:
                    #将node与user的对应关系写入数据库
                    models.node2user.objects.bulk_create(nu_list)
            elif ncols==2:
                for r in range(0, nrows):
                    try:
                        models.node_info.objects.filter(ip=datas.cell(r, 0).value.replace(" ", "")).update(console=datas.cell(r, 1).value)
                        log.log('update node %s console %s' % (datas.cell(r, 0).value.replace(" ", ""),datas.cell(r, 1).value),True)
                    except Exception as e:
                        ret['status'] = False
                        ret['message'] = "There's no record for ip %s in database" %datas.cell(r, 0).value.replace(" ", "")
            elif ncols>=9 and user_obj.superuser:
                comments=''
                temp=datas.cell(0,0).value.split('\n')
                try:
                    chassis=ixia.chassis.objects.create(ip=temp[0],chassis_info='\nLocation:%s\nRack:%s\nBams:%s\n' %(temp[1],temp[2],temp[3]))
                    # print(chassis)
                    log.log('create ixia %s success by %s' % (temp,request.session.get('user_info')['eid']),True)
                except Exception as e:
                    ret['status'] = False
                    ret['message'] = 'ixia %s create fail\r\n' %temp[0]
                    log.log('create ixia %s fail reason:%s by %s' % (temp[0], e, request.session.get('user_info')['eid']), False)
                    return HttpResponse(ret['message'])
                for r in range(0, nrows):
                    # 遍历某一行中每一列的值
                    for c in range(1, ncols):
                        # 如果数据为空，结束本次循环
                        if c == 1 and datas.cell(r, 1).value:
                            temp = str(datas.cell(r, 1).value).split('\n')
                            if len(temp)==2:
                                try:
                                    card=ixia.card.objects.create(ip=chassis,slot=int(temp[0]),card_info='Bams:%s\n' %temp[1])
                                    log.log('create ixia %s card %s success' % (chassis.ip, temp[0]),True)
                                except Exception as e:
                                    print(e)
                            else:
                                try:
                                    card = ixia.card.objects.create(ip=chassis, slot=int(temp[0].split('.')[0]))
                                    log.log('create ixia %s card %s success' % (chassis.ip, temp[0]),True)
                                except Exception as e:
                                    print(e)
                        elif c==2:
                            port=int(datas.cell(r, 2).value)
                        elif c == 3:
                            broken=int(datas.cell(r, 3).value)
                        elif c == 4:
                            switch=datas.cell(r, 4).value
                        elif c == 5:
                            line=datas.cell(r, 5).value
                        elif c == 6:
                            user=datas.cell(r, 6).value
                        elif c == 7:
                            purpose=datas.cell(r, 7).value
                        elif c == 8:
                            usecycle=datas.cell(r, 8).value
                        elif c == 9:
                            comments=datas.cell(r, 9).value
                    try:
                        card.port_set.create(port_num=port,status=broken,switch=switch,line=line,user=user,purpose=purpose,usecycle=usecycle,comments=comments)
                    except Exception as e:
                        print(e)
            #删除上传的文件
            os.remove(os.path.join(BASE_DIR,'upload',file_obj.name))
        else:
            #导入文件获取失败时的提示信息
            ret['status']=False
            ret['message']='File not found'
    if ret['status']:
        return redirect('/r6k/nodes')
    else:
        return HttpResponse(ret['message'])

def nodes_info(request):
    #获取session中的user信息
    user=request.session.get('user_info')
    filter_list={}
    #定义最近30天的日期列表
    date_list = [datetime.datetime.now().date() - datetime.timedelta(days=i) for i in range(30, 0, -1)]
    #获取所有正常使用的node信息
    nodes = models.node_info.objects.filter(status__lte=2,share=False).all()
    #按过滤条件对node进行筛选
    nodes, filter_conditon, filter_for_css = get_filter_result(request, nodes)
    #如果用户已登录
    if user:
        #将属于当前用户的node放到最前面展示
        nodes=list(nodes.filter(user__nid=request.session.get('user_info')['nid']).all().order_by('nid')) + list(nodes.exclude(user__nid=request.session.get('user_info')['nid']).all().order_by('nid'))
    #获取数据库中存储的node关联的所有topo信息并排序
    filter_list['topo_list'] = models.node_info.objects.values('topo').distinct().order_by('topo')
    #获取数据库中存储的node关联的所有line信息并排序
    filter_list['line_list']=models.node_info.objects.values('user__line').distinct().order_by('user__line')
    # print(filter_list['line_list'])
    #如果列表的第一个元素为空/None,则切片取后面的所有元素
    if filter_list['line_list'][0]['user__line']=='' or filter_list['line_list'][0]['user__line']==None:
        filter_list['line_list']=filter_list['line_list'][1::]
    # 获取数据库中存储的node关联的所有team信息并排序
    filter_list['team_list']=models.node_info.objects.values('user__team').distinct().order_by('user__team')
    if not filter_list['team_list'][0]['user__team']:
        filter_list['team_list']=filter_list['team_list'][1::]
    # 获取数据库中存储的node所有type信息并排序
    filter_list['type_list']=models.node_info.objects.values('type').distinct().order_by('type')
    if not filter_list['type_list'][0]['type'] and not filter_list['type_list'][1]['type']:
        filter_list['type_list']=filter_list['type_list'][2::]
    elif not filter_list['type_list'][0]['type']:
        filter_list['type_list'] = filter_list['type_list'][1::]
    # print(filter_list['type_list'])
    # 获取数据库中存储的node机框版本信息并排序
    filter_list['version_list']=models.node_info.objects.values('backplane').distinct().order_by('backplane')
    # 获取数据库中存储的node所在实验室信息并排序
    filter_list['location_list']=models.node_info.objects.values('location').distinct().order_by('location')
    # 获取数据库中存储的node所在位置信息并排序
    filter_list['rack_list']=models.node_info.objects.values('rack').distinct().order_by('rack')
    # 获取数据库中存储的node状态信息并排序
    filter_list['status_list']=models.node_info.objects.values('status').distinct().order_by('status')
    # print(filter_list)
    #遍历每个盒子信息
    for node in nodes:
        #获取每个盒子最近30天内的数据
        node.useages=list(node.utilization_set.filter(day__range=(date_list[0],date_list[-1])).values_list('day', 'useage'))
        #如果获取到数据不足30天
        # print(node.useages)
        if len(date_list)!=len(node.useages):
            #补充缺少的日期和数据
            node.useages=deal_table(date_list,node.useages)
    #计算上个月天数
    pre_month_days=30-datetime.datetime.now().day+1
    #获取node数量
    try:
        total=nodes.count()
    except Exception as e:
        total=len(nodes)
    #获取每页展示的数量
    try:
        show=filter_for_css['_s']
    except Exception as e:
        show =10
    if show == '-1':
        show=total
    # print(show)
    #如果node数不为0
    if total:
        paginator = Paginator(nodes, show)
        # print(paginator)
        try:
            current_num = int(request.GET.get('page', 1))  # 当你在url内输入的?page = 页码数  显示你输入的页面数目 默认为第1页
            nodes = paginator.page(current_num)
        except EmptyPage:
            nodes = paginator.page(4)
            nodes.next_page_number()
        if paginator.num_pages > 11:  # 如果分页的数目大于11
            if current_num - 5 < 1:  # 你输入的值
                pageRange = range(1, 11)  # 按钮数
            elif current_num + 5 > paginator.num_pages:  # 按钮数加5大于分页数
                pageRange = range(current_num - 5, paginator.num_pages + 1)  # 显示的按钮数
            else:
                pageRange = range(current_num - 5, current_num + 6)  # range求的是按钮数   如果你的按钮数小于分页数 那么就按照正常的分页数目来显示
        else:
            pageRange = paginator.page_range # 正常分配

    return render(request,'nodes_info.html',locals())

def index(request,*args,**kwargs):
    """
    :param request:
    :return:
    """
    line_list = models.node_info.objects.values('user__line').distinct().order_by('user__line')
    if line_list[0]['user__line']==None:
        line_list=line_list[1::]
    # print(line_list)
    #获取所有node信息
    nodes = models.node_info.objects.filter(status__in=(0,1,2),share=False).all()
    ixias = ixia.port.objects.filter(status=0, share=False).all()
    #根据过滤条件进行过滤
    nodes, ixias, filter_conditon, filter_for_css = filter_icon(request, nodes, ixias)
    # print(filter_for_css)
    # print(ixias)
    #若起止时间相同
    if filter_for_css['startdate'] == filter_for_css['enddate']:
        date_list=[filter_for_css['enddate']]
    else:
        date_list = [filter_for_css['startdate'],filter_for_css['enddate']]
    print(date_list)
    if len(date_list)==1:
        #时间只选择了一天
        nodes = nodes.filter(utilization__day=date_list[0])
        nodes = nodes.annotate(useage_avg=Avg('utilization__useage'))
        ixias = ixias.filter(utilization__day=date_list[0])
        ixias = ixias.annotate(useage_avg=Avg('utilization__useage'))
    elif date_list[0]>date_list[1]:
        #时间选择不正确
        return HttpResponse('Date selection error, please re - select.')
    else:
        # print(date_list[0], date_list[-1],date_list)
        nodes = nodes.filter(utilization__day__range=(date_list[0], date_list[-1]))
        nodes = nodes.annotate(useage_avg=Avg('utilization__useage'))
        ixias = ixias.filter(utilization__day__range=(date_list[0], date_list[-1]))
        ixias = ixias.annotate(useage_avg=Avg('utilization__useage'))
    #获取盒子分类后的数量
    HighUsage, LowUsage, LowerUsage, LowestUsage, Unused, Unreachable, Other=JudgeUseage(nodes)
    HighIxia, LowIxia, LowerIxia, LowestIxia, UnusedIxia, OtherIxia=JudgeIxiaUseage(ixias)
    # print(HighIxia, LowIxia, LowerIxia, LowestIxia, UnusedIxia, OtherIxia)
    return render(request,'icon.html',locals())

def pageNotFound(request):
    return render(request,'404.html')