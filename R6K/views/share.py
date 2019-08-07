#!/usr/bin/env python
#coding=utf-8
import datetime
from django.shortcuts import render,HttpResponse
from django.db.models import Q
from R6K import models
from IXIA import models as ixia

def filter_r6k(request,obj):
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
        val=request.GET.get('_tp')
    except Exception as e:
        val=''
    if val:
        filter_conditions['topo__exact'] = val
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
    print("filter_conditions",filter_conditions,filter_for_css)
    obj=obj.filter(**filter_conditions)
    return obj,filter_for_css

def filterIxia(request,obj):
    """
    按过滤条件对ixia进行过滤
    :param request:
    :param obj:
    :return:
    """
    filter_conditions = {}
    filter_for_css={}
    for key,val in request.GET.items():
        filter_for_css[key] = val
    try:
        val=request.GET.get('_tp')
    except Exception as e:
        val=''
    if val:
        filter_conditions['topo__exact'] = val
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
    print("filter_conditions",filter_conditions,filter_for_css)
    obj=obj.filter(**filter_conditions)
    return obj,filter_for_css

def share_nodes(request):
    #获取session中的user信息
    user=request.session.get('user_info')
    filter_list={}
    #获取所有的node信息
    nodes = models.node_info.objects.filter(Q(status__gt=3)|Q(share=True)).all().order_by('status')
    #按过滤条件对node进行筛选
    #获取数据库中存储的node关联的所有topo信息并排序
    filter_list['topo_list'] = nodes.values('topo').distinct().order_by('topo')
    # 获取数据库中存储的node所有type信息并排序
    filter_list['type_list']=nodes.values('type').distinct().order_by('type')
    if not filter_list['type_list'][0]['type'] and not filter_list['type_list'][1]['type']:
        filter_list['type_list']=filter_list['type_list'][2::]
    elif not filter_list['type_list'][0]['type']:
        filter_list['type_list'] = filter_list['type_list'][1::]
    # print(filter_list['type_list'])
    # 获取数据库中存储的node机框版本信息并排序
    filter_list['version_list']=nodes.values('backplane').distinct().order_by('backplane')
    if not filter_list['version_list'][0]['backplane']:
        filter_list['version_list'] = filter_list['version_list'][1::]
    # 获取数据库中存储的node所在实验室信息并排序
    filter_list['location_list']=nodes.values('location').distinct().order_by('location')
    # 获取数据库中存储的node所在位置信息并排序
    filter_list['rack_list']=nodes.values('rack').distinct().order_by('rack')
    # 获取数据库中存储的node状态信息并排序
    filter_list['status_list']=nodes.values('status').distinct().order_by('status')
    # print(filter_list)
    nodes,filter_for_css=filter_r6k(request,nodes)
    #获取node数量
    total=nodes.count()
    return render(request, 'share_r6k.html', locals())

def share_ixia(request):
    # 获取session中的user信息
    user = request.session.get('user_info')
    filter_list = {}
    # 获取所有的node信息
    ixias = ixia.port.objects.filter(Q(status=2)|Q(share=True)).all().order_by('card__ip__ip','card__slot','port_num')
    if ixias.count():
        #对ixia端口按ip,card,port依次进行排序
        ixias = ixias.distinct().order_by('card__ip__ip', 'card__slot', 'port_num')
    # 获取node数量
    total = ixias.count()
    ips = ixias.values('card__ip__ip').distinct().order_by('card__ip__ip')
    cards = ixias.values('card__ip__ip', 'card__slot').distinct().order_by('card__ip__ip', 'card__slot')
    # print('ips,cards:',ips,cards)
    # 存储每个ip及卡号对应的port数量
    count = [[], []]
    for ip in ips:
        count[0].append(ixias.filter(card__ip__ip=ip['card__ip__ip']).count())
    for card in cards:
        count[1].append(ixias.filter(card__ip__ip=card['card__ip__ip'], card__slot=card['card__slot']).count())
    return render(request, 'share_ixia.html', locals())

def share_others(request):
    pass
    return HttpResponse('Waiting to build')