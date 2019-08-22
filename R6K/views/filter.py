#!/usr/bin/env python
# -*- coding:utf-8 -*-
import datetime
from django.shortcuts import render
from django.db.models import Avg
from R6K import models
from IXIA import models as ixiam
from django.db.models import Q

def first_filter(request,obj):
    """
    :param request: request请求
    :param obj: nodes信息
    :return: 按request中携带的过滤信息对nodes信息进行过滤
    """
    filter_conditions = {}
    filter_for_css = {}
    for key, val in request.GET.items():
        filter_for_css[key] = val
    #获取开始日期
    val = request.GET.get('s')
    #将字符串按-切割
    val = val.split('-')
    if request.GET.get('s')==request.GET.get('e'):
        date_list=[datetime.date(int(val[0]), int(val[1]), int(val[2]))]
    else:
        #获取开始日期与当前日期差的天数
        s=(datetime.date.today()-datetime.date(int(val[0]), int(val[1]), int(val[2]))).days
        # 获取结束日期
        val = request.GET.get('e')
        # 将字符串按-切割
        val = val.split('-')
        # 获取开始日期与当前日期差的天数，因range不包含最后一个数，所以减1
        e=(datetime.date.today()-datetime.date(int(val[0]), int(val[1]), int(val[2]))).days-1
        try:
            date_list=[datetime.datetime.now().date() - datetime.timedelta(days=i) for i in range(s, e, -1)]
        except Exception as e:
            date_list =[]
            print(e)
    #获取要过滤的line值
    val = request.GET.get('l')
    if val:
        filter_conditions['user__line'] = int(val)
    #获取要过滤的node类型信息
    val = request.GET.get('t')
    if val:
        filter_conditions['type__contains'] = val
    print("filter_conditions,filter_for_css:", filter_conditions, filter_for_css)
    #line和type中任意一个不为空时，进行过滤
    obj = obj.filter(**filter_conditions)
    return obj, filter_conditions, date_list,filter_for_css

def second_filter(request,obj):
    """
    :param request: request请求
    :param obj: nodes信息
    :return: 按request中携带的过滤信息对nodes信息进行过滤
    """
    filter_conditions = {}
    #获取要过滤的topo值
    try:
        val=request.GET.get('_tp')
    except Exception as e:
        val=''
    if val:
        filter_conditions['topo__exact']=val
    #获取要过滤的eid值
    try:
        val=request.GET.get('_u')
    except Exception as e:
        val=''
    if val:
        filter_conditions['user__eid__iexact'] = val
    # 获取要过滤的team信息
    try:
        val = request.GET.get('_p')
    except Exception as e:
        val = ''
    if val:
        filter_conditions['purpose'] = val
    # 获取要过滤的node版本信息
    try:
        val = request.GET.get('_v')
    except Exception as e:
        val = ''
    if val:
        filter_conditions['backplane'] = val
    #获取要过滤的node实验室信息
    try:
        val = request.GET.get('_loc')
    except Exception as e:
        val = ''
    if val:
        filter_conditions['location'] = val
    #获取要过滤的node位置信息
    try:
        val = request.GET.get('_r')
    except Exception as e:
        val = ''
    if val:
        filter_conditions['rack'] = val
    #获取要过滤的node status信息
    try:
        val = request.GET.get('_st')
    except Exception as e:
        val = ''
    if val:
        filter_conditions['status'] = val
    #line和type中任意一个不为空时，进行过滤
    obj = obj.filter(**filter_conditions)
    return obj

def secondFilterIxia(request,obj):
    """
    :param request: request请求
    :param obj: ixias信息
    :return: 按request中携带的过滤信息对ixias信息进行过滤
    """
    filter_conditions = {}
    #获取要过滤的ip
    try:
        val=request.GET.get('_i')
    except Exception as e:
        val=''
    if val:
        filter_conditions['card__ip__ip']=val
    #获取要过滤的card number
    try:
        val=request.GET.get('_c')
    except Exception as e:
        val=''
    if val:
        filter_conditions['card__slot'] = val
    # 获取要过滤的card info
    try:
        val = request.GET.get('_ct')
    except Exception as e:
        val = ''
    if val:
        filter_conditions['card__card_info__icontains'] = val
    # 获取要过滤的user信息
    try:
        val = request.GET.get('_u')
    except Exception as e:
        val = ''
    if val:
        filter_conditions['user__eid__iexact'] = val
    #获取要过滤的purpose信息
    try:
        val = request.GET.get('_p')
    except Exception as e:
        val = ''
    if val:
        filter_conditions['purpose__icontains'] = val
    obj = obj.filter(**filter_conditions)
    return obj

def JudgeUseage(nodes,classify):
    """
    :param nodes: nodes信息
    :param classify: 分类标签
    :return: 按分类标签过滤后的nodes信息
    """
    if classify == 'high':
        nodes=nodes.filter(useage_avg__gt=70)
        return nodes
    elif classify=='middle':
        #使用率处于30%-70%
        nodes = nodes.filter(Q(useage_avg__gt=30) & Q(useage_avg__lte=70))
        return nodes
    elif classify=='low':
        nodes = nodes.filter(Q(useage_avg__gt=15) & Q(useage_avg__lte=30))
        return nodes
    elif classify=='lower':
        nodes = nodes.filter(Q(useage_avg__gt=5) & Q(useage_avg__lte=15))
        return nodes
    elif classify=='lowest':
        #使用率大于0但小于5%
        nodes = nodes.filter(Q(useage_avg__gt=0.161) & Q(useage_avg__lte=5))
        return nodes
    elif classify=='unused':
        #使用率为0，但当前状态为on line/login fail
        nodes = nodes.filter(useage_avg__lte=0.161, status__in=(0,1))
        return nodes
    elif classify=='unreachable':
        #使用率为0，且当前状态不为on line/login fail
        nodes = nodes.filter(useage_avg__lte=0.161, status=2)
        return nodes

def judgeUseageIxia(ixias,classify):
    """
    :param nodes: nodes信息
    :param classify: 分类标签
    :return: 按分类标签过滤后的nodes信息
    """
    if classify == 'high':
        ixias=ixias.filter(useage_avg__gt=70)
        return ixias
    elif classify=='middle':
        #使用率处于30%-70%
        ixias = ixias.filter(Q(useage_avg__gt=30) & Q(useage_avg__lte=70))
        return ixias
    elif classify=='low':
        ixias = ixias.filter(Q(useage_avg__gt=15) & Q(useage_avg__lte=30))
        return ixias
    elif classify=='lower':
        ixias = ixias.filter(Q(useage_avg__gt=5) & Q(useage_avg__lte=15))
        return ixias
    elif classify=='lowest':
        #使用率大于0但小于5%
        ixias = ixias.filter(Q(useage_avg__gt=0) & Q(useage_avg__lte=5))
        return ixias
    elif classify=='unused':
        #使用率为0，但当前状态为on line/login fail
        ixias = ixias.filter(useage_avg=0)
        return ixias

def deal_table(date_list,useages):
    """
    :param date_list: 时间列表
    :param useages: 使用率列表
    :return: 与时间列表个数相等的使用率列表
    """
    i,j=0,0
    new_list=[]
    while i<len(date_list):
        if j<len(useages) and date_list[i]==useages[j][0]:
            new_list.append(useages[j])
            j+=1
        else:
            new_list.append((date_list[i],0))
        i+=1
    return new_list

def classify(request,classify):
    filter_list = {}
    #获取所有node信息
    nodes=models.node_info.objects.filter(share=False,status__lte=2).all()
    print(nodes.count())
    #按跳转过来时条件进行过滤
    nodes,filter_conditions,date_list,filter_for_css=first_filter(request,nodes)
    #如果开始时间与结束时间属于同一个月
    if date_list[0].year==date_list[-1].year and date_list[0].month==date_list[-1].month:
        month_days=date_list[-1].day-date_list[0].day+1
    else:
        import calendar
        # #获取日期列表，包含年份、月份和对应的天数
        monthList=[(date_list[0].year,date_list[0].month,calendar.monthlen(date_list[0].year,date_list[0].month)-date_list[0].day+1)]
        while monthList[-1][0]!=date_list[-1].year or monthList[-1][1]!=date_list[-1].month:
            if monthList[-1][1]==12 and date_list[-1].month==1:
                monthList.append((monthList[-1][0]+1,1,date_list[-1].day))
            elif monthList[-1][1]==12:
                monthList.append((monthList[-1][0]+1,1,31))
            elif monthList[-1][1]+1==date_list[-1].month:
                monthList.append((monthList[-1][0],monthList[-1][1]+1,date_list[-1].day))
            else:
                monthList.append((monthList[-1][0],monthList[-1][1]+1,calendar.monthlen(monthList[-1][0],monthList[-1][1]+1)))
        # print(monthList)
    #如果只获取一天的数据
    if len(date_list)==1:
        nodes=nodes.filter(utilization__day=date_list[0])
        nodes=nodes.annotate(useage_avg=Avg('utilization__useage')).order_by('useage_avg')
    else:
        nodes = nodes.filter(utilization__day__range=(date_list[0],date_list[-1]))
        nodes = nodes.annotate(useage_avg=Avg('utilization__useage')).order_by('useage_avg')
    #对nodes信息按分类标签过滤
    nodes=JudgeUseage(nodes,classify)
    if nodes.count():
        #获取分类项
        filter_list['topo_list'] = nodes.values('topo').distinct().order_by('topo')
        filter_list['line_list'] = nodes.values('user__line').distinct().order_by('user__line')
        #如果line列表第一个值为空或None，进行切片
        if filter_list['line_list'][0]['user__line'] == None:
            filter_list['line_list'] = filter_list['line_list'][1::]
        filter_list['team_list'] = nodes.values('user__team').distinct().order_by('user__team')
        #如果team列表第一个值为空或None，进行切片
        if filter_list['team_list'][0]['user__team'] == None:
            filter_list['team_list'] = filter_list['team_list'][1::]
        filter_list['type_list'] = nodes.values('type').distinct().order_by('type')
        #type列表长度至少为2时
        if len(filter_list['type_list'])>=2:
            #判断type列表第一个值和第二个值不为空或None
            if not filter_list['type_list'][0]['type'] and not filter_list['type_list'][1]['type']:
                filter_list['type_list']=filter_list['type_list'][2::]
            elif not filter_list['type_list'][0]['type']:
                filter_list['type_list'] = filter_list['type_list'][1::]
        #type列表长度为1时
        elif len(filter_list['type_list'])==1:
            if not filter_list['type_list'][0]['type']:
                #如果唯一的元素为空或None，将列表置空
                filter_list['type_list'] = []
        filter_list['version_list'] = nodes.values('backplane').distinct().order_by('backplane')
        filter_list['location_list'] = nodes.values('location').distinct().order_by('location')
        filter_list['rack_list'] = nodes.values('rack').distinct().order_by('rack')
        filter_list['status_list'] = nodes.values('status').distinct().order_by('status')
        filter_list['purpose_list'] = nodes.values('purpose').distinct().order_by('purpose')
        nodes=second_filter(request, nodes)
        total = nodes.count()
        # 遍历每个盒子信息
        for node in nodes:
            # 获取每个盒子最近30天内的数据
            node.useages = list(node.utilization_set.filter(day__range=(date_list[0], date_list[-1])).values_list('day', 'useage'))
            # 如果获取到数据个数不等于日期天数
            if len(date_list) != len(node.useages):
                # 补充缺少的日期和数据
                node.useages = deal_table(date_list, node.useages)
    else:
        # 获取分类项
        filter_list['topo_list'] = []
        filter_list['line_list'] = []
        filter_list['team_list'] = []
        filter_list['type_list'] = []
        filter_list['version_list'] = []
        filter_list['location_list'] = []
        filter_list['rack_list'] = []
        filter_list['status_list'] = []
        filter_list['purpose_list'] = []
    return render(request,'show_filter.html',locals())

def ixiaClassify(request,classify):
    filter_list = {}
    # 获取所有ixia信息
    ixias = ixiam.port.objects.filter(share=False, status=0).all()
    print(ixias.count())
    # 按跳转过来时条件进行过滤
    ixias, filter_conditions, date_list, filter_for_css = first_filter(request, ixias)
    # 如果开始时间与结束时间属于同一个月
    if date_list[0].year == date_list[-1].year and date_list[0].month == date_list[-1].month:
        month_days = date_list[-1].day - date_list[0].day + 1
    else:
        import calendar
        # #获取日期列表，包含年份、月份和对应的天数
        monthList = [(date_list[0].year, date_list[0].month,
                      calendar.monthlen(date_list[0].year, date_list[0].month) - date_list[0].day + 1)]
        while monthList[-1][0] != date_list[-1].year or monthList[-1][1] != date_list[-1].month:
            if monthList[-1][1] == 12 and date_list[-1].month == 1:
                monthList.append((monthList[-1][0] + 1, 1, date_list[-1].day))
            elif monthList[-1][1] == 12:
                monthList.append((monthList[-1][0] + 1, 1, 31))
            elif monthList[-1][1] + 1 == date_list[-1].month:
                monthList.append((monthList[-1][0], monthList[-1][1] + 1, date_list[-1].day))
            else:
                monthList.append(
                    (monthList[-1][0], monthList[-1][1] + 1, calendar.monthlen(monthList[-1][0], monthList[-1][1] + 1)))
        print(monthList)
    # 如果只获取一天的数据
    if len(date_list) == 1:
        ixias = ixias.filter(utilization__day=date_list[0])
        ixias = ixias.annotate(useage_avg=Avg('utilization__useage')).order_by('useage_avg')
    else:
        ixias = ixias.filter(utilization__day__range=(date_list[0], date_list[-1]))
        ixias = ixias.annotate(useage_avg=Avg('utilization__useage')).order_by('useage_avg')
    # 对nodes信息按分类标签过滤
    ixias = judgeUseageIxia(ixias, classify)
    if ixias.count():
        # 获取分类项
        filter_list['ip_list'] = ixias.values('card__ip__ip').distinct().order_by('card__ip__ip')
        filter_list['card_list'] = ixias.values('card__slot').distinct().order_by('card__slot')
        filter_list['line_list'] = ixias.values('user__line').distinct().order_by('user__line')
        # 如果line列表第一个值为空或None，进行切片
        if filter_list['line_list'][0]['user__line'] == None:
            filter_list['line_list'] = filter_list['line_list'][1::]
        #对ixia端口按搜索条件进行二次过滤
        ixias = secondFilterIxia(request, ixias)
        ixias = ixias.distinct().order_by('card__ip__ip', 'card__slot', 'port_num')
        ips = ixias.values('card__ip__ip').distinct().order_by('card__ip__ip')
        cards = ixias.values('card__ip__ip', 'card__slot').distinct().order_by('card__ip__ip', 'card__slot')
        # print('ips,cards:',ips,cards)
        # 存储每个ip及卡号对应的port数量
        count = [[], []]
        for ip in ips:
            count[0].append(ixias.filter(card__ip__ip=ip['card__ip__ip']).count())
        for card in cards:
            count[1].append(ixias.filter(card__ip__ip=card['card__ip__ip'], card__slot=card['card__slot']).count())
        print(count)
        total = ixias.count()
        # 遍历每个盒子信息
        for ixia in ixias:
            # 获取每个盒子最近30天内的数据
            ixia.useages=list(ixia.utilization_set.filter(day__range=(date_list[0],date_list[-1])).values_list('day','useage'))
            # 如果获取到数据个数不等于日期天数
            if len(date_list) != len(ixia.useages):
                # 补充缺少的日期和数据
                ixia.useages = deal_table(date_list, ixia.useages)
    else:
        filter_list['ip_list'] = []
        filter_list['card_list'] = []
        filter_list['line_list'] = []
    return render(request, 'show_ixia_filter.html', locals())