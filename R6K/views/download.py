#!/usr/bin/env python
# coding=utf-8
import datetime,os
from django.shortcuts import HttpResponse
from django.db.models import Avg
from utils import FileHandle
from django.views.decorators.csrf import csrf_exempt
from R6K import models
from IXIA import models as ixia
from RMDB.settings import BASE_DIR

def filter_r6k(request,obj):
    """
    按过滤条件对node进行过滤
    :param request:
    :param obj:
    :return:
    """
    filter_conditions = {}
    try:
        val=request.POST.get('_tp')
    except Exception as e:
        val=''
    if val:
        filter_conditions['topo__exact'] = val
    try:
        val = request.POST.get('_u')
    except Exception as e:
        val = ''
    if val:
        filter_conditions['user__eid__iexact'] = val.lower()
    try:
        val = request.POST.get('_l')
    except Exception as e:
        val = ''
    if val:
        filter_conditions['user__line'] = val
    try:
        val = request.POST.get('_t')
    except Exception as e:
        val = ''
    if val:
        filter_conditions['user__team'] = val
    try:
        val = request.POST.get('_ty')
    except Exception as e:
        val = ''
    if val:
        filter_conditions['type__contains'] = val
    try:
        val = request.POST.get('_v')
    except Exception as e:
        val = ''
    if val:
        filter_conditions['backplane'] = val
    try:
        val = request.POST.get('_loc')
    except Exception as e:
        val = ''
    if val:
        filter_conditions['location'] = val
    try:
        val = request.POST.get('_r')
    except Exception as e:
        val = ''
    if val:
        filter_conditions['rack'] = val
    try:
        val = request.POST.get('_b')
    except Exception as e:
        val = ''
    if val:
        filter_conditions['bams__icontains']=val
    try:
        val = request.POST.get('_st')
    except Exception as e:
        val = ''
    if val:
        filter_conditions['status'] = val
    try:
        val = request.POST.get('_m')
    except Exception as e:
        val = ''
    if val:
        filter_conditions['mode'] = val
    try:
        val = request.POST.get('_q')
    except Exception as e:
        val = ''
    if val:
        filter_conditions['hardware_info__iregex'] = val
    # print("filter_conditions",filter_conditions)
    obj=obj.filter(**filter_conditions)
    return obj

def filter_ixia(request,obj):
    """
    按过滤条件对node进行过滤
    :param request:
    :param obj:
    :return:
    """
    filter_conditions = {}
    try:
        val=request.POST.get('_i')
    except Exception as e:
        val=''
    if val:
        filter_conditions['card__ip__ip'] = val
    try:
        val = request.POST.get('_c')
    except Exception as e:
        val = ''
    if val:
        filter_conditions['card__slot'] = val.lower()
    try:
        val = request.POST.get('_ct')
    except Exception as e:
        val = ''
    if val:
        filter_conditions['card__card_info__icontains'] = val
    try:
        val = request.POST.get('_s')
    except Exception as e:
        val = ''
    if val:
        filter_conditions['status'] = val
    try:
        val = request.POST.get('_sw')
    except Exception as e:
        val = ''
    if val:
        filter_conditions['switch__icontains'] = val
    try:
        val = request.POST.get('_l')
    except Exception as e:
        val = ''
    if val:
        filter_conditions['user__line'] = val
    try:
        val = request.POST.get('_u')
    except Exception as e:
        val = ''
    if val:
        filter_conditions['user__eid__iexact'] = val
    try:
        val = request.POST.get('_p')
    except Exception as e:
        val = ''
    if val:
        filter_conditions['purpose__icontains'] = val
    print("filter_conditions",filter_conditions)
    obj=obj.filter(**filter_conditions)
    return obj

def icon_r6k(request,obj):
    """
    按过滤条件对node进行过滤
    :param request:
    :param obj:
    :return:
    """
    filter_conditions = {}
    val = request.POST.get('sd')
    # 将字符串按-切割
    val = val.split('-')
    if request.POST.get('sd') == request.POST.get('ed'):
        date_list = [datetime.date(int(val[0]), int(val[1]), int(val[2]))]
    else:
        # 获取开始日期与当前日期差的天数
        s = (datetime.date.today() - datetime.date(int(val[0]), int(val[1]), int(val[2]))).days
        # 获取结束日期
        val = request.POST.get('ed')
        # 将字符串按-切割
        val = val.split('-')
        # 获取开始日期与当前日期差的天数，因range不包含最后一个数，所以减1
        e = (datetime.date.today() - datetime.date(int(val[0]), int(val[1]), int(val[2]))).days - 1
        try:
            date_list = [datetime.datetime.now().date() - datetime.timedelta(days=i) for i in range(s, e, -1)]
        except Exception as e:
            date_list = []
            print(e)
    # 获取要过滤的topo值
    # 获取要过滤的line值
    val = request.POST.get('l')
    if val:
        filter_conditions['user__line'] = int(val)
    # 获取要过滤的node类型信息
    val = request.POST.get('t')
    if val:
        filter_conditions['type__contains'] = val
    # line和type中任意一个不为空时，进行过滤
    obj = obj.filter(**filter_conditions)
    return obj,date_list

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
            if useages[j][1]==0.16:
                new_list.append((useages[j][0],0))
            else:
                new_list.append(useages[j])
            j+=1
        else:
            new_list.append((date_list[i],'-'))
        i+=1
    return new_list

@csrf_exempt
def BulidData(request):
    ret=''
    db = request.POST['type']
    if db=='r6k':
        nodes=models.node_info.objects.filter(share=False,status__lte=2).all()
        date_list = [datetime.datetime.now().date() - datetime.timedelta(days=i) for i in range(30, 0, -1)]
        nodes=filter_r6k(request,nodes)
        for node in nodes:
            #获取每个盒子最近30天内的数据
            node.useages=list(node.utilization_set.filter(day__range=(date_list[0],date_list[-1])).values_list('day','useage'))
            node.useages=deal_table(date_list,node.useages)
        ret = FileHandle.BulidR6KExcel(os.path.join(BASE_DIR,'upload'),nodes)
    elif db=='icon_r6k':
        nodes = models.node_info.objects.filter(share=False, status__lte=2).all()
        nodes,date_list= icon_r6k(request, nodes)
        if len(date_list) == 1:
            nodes = nodes.filter(utilization__day=date_list[0])
            nodes = nodes.annotate(useage_avg=Avg('utilization__useage')).order_by('useage_avg')
        else:
            nodes = nodes.filter(utilization__day__range=(date_list[0], date_list[-1]))
            nodes = nodes.annotate(useage_avg=Avg('utilization__useage')).order_by('useage_avg')
        ret=FileHandle.IconR6KExcel(os.path.join(BASE_DIR,'upload'),nodes,date_list)
    elif db=='ixia':
        ixias = ixia.port.objects.all().order_by('card__ip__ip','card__slot','port_num')
        date_list = [datetime.datetime.now().date() - datetime.timedelta(days=i) for i in range(30, 0, -1)]
        ixias = filter_ixia(request, ixias)
        for ix in ixias:
            # 获取每个盒子最近30天内的数据
            ix.useages = list(ix.utilization_set.filter(day__range=(date_list[0], date_list[-1])).values_list('day', 'useage'))
            ix.useages = deal_table(date_list, ix.useages)
        ret = FileHandle.BulidIxiaExcel(os.path.join(BASE_DIR, 'upload'), ixias)
    elif db=='icon_ixia':
        ixias = ixia.port.objects.filter(share=False, status=0).all().order_by('card__ip__ip','card__slot','port_num')
        ixias,date_list= icon_r6k(request, ixias)
        if len(date_list) == 1:
            ixias = ixias.filter(utilization__day=date_list[0])
            ixias = ixias.annotate(useage_avg=Avg('utilization__useage')).order_by('useage_avg')
        else:
            ixias = ixias.filter(utilization__day__range=(date_list[0], date_list[-1]))
            ixias = ixias.annotate(useage_avg=Avg('utilization__useage')).order_by('useage_avg')
        ret=FileHandle.IconIXIAExcel(os.path.join(BASE_DIR,'upload'),ixias,date_list)
    return HttpResponse(ret)

def download(request,offset):
    # print('offset',offset)
    from django.http import StreamingHttpResponse
    def file_iterator(file_name,chunk_size=512):
        # print(file_name)
        with open(file_name,'rb') as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break
        os.remove(os.path.join(BASE_DIR,'upload',offset+'.xls'))
    the_file_name =offset+'.xls'
    response = StreamingHttpResponse(file_iterator(os.path.join(BASE_DIR,'upload',offset+'.xls')))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(the_file_name)
    return response