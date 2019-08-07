#!/usr/bin/env python
#coding=utf-8
import datetime
from django.shortcuts import HttpResponse
from json import dumps
from django.db.models import Avg
from django.db.models import Q
from R6K import models
from R6K.views.home import JudgeUseage

def totalNodesOfTeam(nodes,line,d):
    fc={'user__line':line}
    ret={'line':line,'high':0,'middle':0,'low':0,'lower':0,'lowest':0,'unused':0,'unreachable':0,'total':0,'lowTotal':0}
    nodes=nodes.filter(**fc)
    nodes = nodes.filter(utilization__day__range=(d[0], d[1]))
    nodes = nodes.annotate(useage_avg=Avg('utilization__useage'))
    ret['total']=nodes.count()
    ret['high'],ret['low'],ret['lower'],ret['lowest'],ret['unused'],ret['unreachable'],ret['middle']=JudgeUseage(nodes)
    ret['lowTotal']=(ret['lowest']+ret['unused']+ret['unreachable'])
    return ret

def totalNodesOfTestbed(nodes,testbed,d):
    if 'SAT' in testbed:
        fc = {'type__contains': 'LEAP'}
    else:
        fc={'type__contains':testbed}
    ret={'testbed':testbed,'high':0,'middle':0,'low':0,'lower':0,'lowest':0,'unused':0,'unreachable':0,'total':0,'lowTotal':0}
    nodes=nodes.filter(**fc)
    nodes = nodes.filter(utilization__day__range=(d[0], d[1]))
    nodes = nodes.annotate(useage_avg=Avg('utilization__useage'))
    ret['total']=nodes.count()
    ret['high'],ret['low'],ret['lower'],ret['lowest'],ret['unused'],ret['unreachable'],ret['middle']=JudgeUseage(nodes)
    ret['lowTotal']=(ret['lowest']+ret['unused']+ret['unreachable'])
    return ret

def lowUTENodesOfTeam(nodes,line,d):
    fc = {'user__line': line}
    ret = {'line':line, '6273':0,'6274':0,'6471/1':0,'6471/2':0,'6371':0,'6675':0,'6672':0,'SAT LEAP':0,'total':0}
    nodes = nodes.filter(**fc)
    nodes = nodes.filter(utilization__day__range=(d[0], d[1]))
    nodes = nodes.annotate(useage_avg=Avg('utilization__useage'))
    nodes = nodes.filter(Q(useage_avg__gt=0.161) & Q(useage_avg__lte=5)).all()
    ret['total'] = nodes.count()
    ret['6371']=nodes.filter(type__contains='6371').count()
    ret['6273']=nodes.filter(type__contains='6273').count()
    ret['6274']=nodes.filter(type__contains='6274').count()
    ret['6471/1']=nodes.filter(type__contains='6471/1').count()
    ret['6471/2']=nodes.filter(type__contains='6471/2').count()
    ret['6675']=nodes.filter(type__contains='6675').count()
    ret['6672']=nodes.filter(type__contains='6672').count()
    ret['SAT LEAP']=nodes.filter(type__contains='LEAP').count()
    return ret

def unusedNodesOfTeam(nodes,line,d):
    fc = {'user__line': line}
    ret = {'line':line, '6273':0,'6274':0,'6471/1':0,'6471/2':0,'6371':0,'6675':0,'6672':0,'total':0}
    nodes = nodes.filter(**fc)
    nodes = nodes.filter(utilization__day__range=(d[0], d[1]))
    nodes = nodes.annotate(useage_avg=Avg('utilization__useage'))
    nodes = nodes.filter(useage_avg__lte=0.161,status__in=(0,1)).all()
    ret['total'] = nodes.count()
    ret['6273']=nodes.filter(type__contains='6273').count()
    ret['6274']=nodes.filter(type__contains='6274').count()
    ret['6471/1']=nodes.filter(type__contains='6471/1').count()
    ret['6471/2']=nodes.filter(type__contains='6471/2').count()
    ret['6675']=nodes.filter(type__contains='6675').count()
    ret['6672']=nodes.filter(type__contains='6672').count()
    return ret

def unreachableNodesOfTeam(nodes,line,d):
    fc = {'user__line': line}
    ret = {'line':line, '6273':0,'6274':0,'6471/1':0,'6471/2':0,'6371':0,'6675':0,'6672':0,'total':0}
    nodes = nodes.filter(**fc)
    nodes = nodes.filter(utilization__day__range=(d[0], d[1]))
    nodes = nodes.annotate(useage_avg=Avg('utilization__useage'))
    nodes = nodes.filter(useage_avg__lte=0.161,status=2).all()
    ret['total'] = nodes.count()
    ret['6273']=nodes.filter(type__contains='6273').count()
    ret['6274']=nodes.filter(type__contains='6274').count()
    ret['6471/1']=nodes.filter(type__contains='6471/1').count()
    ret['6471/2']=nodes.filter(type__contains='6471/2').count()
    ret['6675']=nodes.filter(type__contains='6675').count()
    ret['6672']=nodes.filter(type__contains='6672').count()
    return ret

def getDateList():
    dateList=[]
    curDay = datetime.date.today()
    firstDay = datetime.date(curDay.year, curDay.month - 1, 1)
    lastDay = datetime.date(curDay.year, curDay.month, 1) - datetime.timedelta(days=1)
    dateList.insert(0, [firstDay, lastDay])
    baseDay = datetime.date(2019, 1, 1)
    while dateList[0][0] != baseDay:
        lastDay = dateList[0][0] - datetime.timedelta(days=1)
        firstDay = datetime.date(lastDay.year, lastDay.month, 1)
        dateList.insert(0, [firstDay, lastDay])
    return dateList

def lowUTEOfMonth(nodes,d):
    nodes = nodes.filter(utilization__day__range=(d[0], d[1]))
    nodes = nodes.annotate(useage_avg=Avg('utilization__useage'))
    total=nodes.count()
    low = nodes.filter(useage_avg__lt=5).all().count()
    if total==0:
        return {'year':d[0].year,'month':d[0].month,'rate':0}
    else:
        return {'year':d[0].year,'month':d[0].month,'rate':low/total}

def lowUTEOfTeam(nodes,d):
    line_map = {0:'NT',3:'FDU A',4:'FDU B',5:'FDU C',6:'FDU D',7:'FDU E',8:'FDU F',9:'FDU G',10:'FDU H',11:'PIDS',12:'EOT'}
    ret = {'year':d[0].year,'month':d[0].month,'NT':0,'FDU A':0,'FDU B':0,'FDU C':0,'FDU D':0,'FDU E':0,'FDU F':0,'FDU G':0,'FDU H':0,'PIDS':0,'EOT':0}
    nodes = nodes.filter(utilization__day__range=(d[0], d[1]))
    nodes = nodes.annotate(useage_avg=Avg('utilization__useage'))
    temp = nodes
    for line in line_map.keys():
        nodes=temp
        nodes=nodes.filter(user__line=line).all()
        total=nodes.count()
        low=nodes.filter(useage_avg__lt=5).all().count()
        if total!=0:
            ret[line_map[line]]=low/total
    return ret

def lowUTEOfTestbed(nodes,d):
    testbed = ['6273', '6672', '6675', '6371', '6471/1', '6471/2', '6274', 'SAT LEAP']
    ret = {'year':d[0].year,'month':d[0].month,'6273':0,'6672':0,'6675':0,'6371':0,'6471/1':0,'6471/2':0,'6274':0,'SAT LEAP':0}
    nodes = nodes.filter(utilization__day__range=(d[0], d[1]))
    nodes = nodes.annotate(useage_avg=Avg('utilization__useage'))
    temp = nodes
    for type in testbed:
        nodes = temp
        if 'SAT' in type:
            nodes = nodes.filter(type__contains='LEAP').all()
        else:
            nodes = nodes.filter(type__contains=type).all()
        total = nodes.count()
        low = nodes.filter(useage_avg__lt=5).all().count()
        if total != 0:
            ret[type] = low / total
    return ret

def lowUTEOfInterval(nodes,d):
    ret = {'year':d[0].year,'month': d[0].month,'high':0,'middle':0,'low':0,'lower':0}
    nodes = nodes.filter(utilization__day__range=(d[0], d[1]))
    nodes = nodes.annotate(useage_avg=Avg('utilization__useage'))
    total=nodes.count()
    ret['high'],ret['low'],ret['lower'],t1,t2,t3,ret['middle']=JudgeUseage(nodes)
    if total!=0:
        ret['high'],ret['middle'],ret['low'],ret['lower']=ret['high']/total,ret['middle']/total,ret['low']/total,ret['lower']/total
    return ret

def getData(request,type):
    nodes = models.node_info.objects.filter(status__lt=3, share=False).all()
    # curDay = datetime.date.today()
    if type=='totalNodesOfTeam':
        result=[]
        line_map={0:'NT',3:'FDU A',4:'FDU B',5:'FDU C',6:'FDU D',7:'FDU E',8:'FDU F',9:'FDU G',10:'FDU H',11:'PIDS',12:'EOT'}
        month = request.GET.get('month')
        year=request.GET.get('year')
        if month!=None:
            month = int(month)
        else:
            month = 1
        if year != None:
            year = int(year)
        else:
            year = 2019
        firstDay = datetime.date(year,month,1)
        lastDay = datetime.date(year,month+1,1)-datetime.timedelta(days=1)
        for line in line_map.keys():
            temp=totalNodesOfTeam(nodes,line,[firstDay,lastDay])
            temp['line']=line_map[line]
            result.append(temp)
        # print(result)
        return HttpResponse(dumps(result))
    if type=='totalNodesOfTestbed':
        result=[]
        testbed =['6273','6672','6675','6371','6471/1','6471/2','6274','SAT LEAP']
        month = request.GET.get('month')
        year=request.GET.get('year')
        if month!=None:
            month = int(month)
        else:
            month = 1
        if year != None:
            year = int(year)
        else:
            year = 2019
        firstDay = datetime.date(year, month, 1)
        lastDay = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)
        result = []
        for t in testbed:
            temp = totalNodesOfTestbed(nodes, t, [firstDay, lastDay])
            result.append(temp)
        # print(result)
        return HttpResponse(dumps(result))
    if type=='lowUTENodesOfTeam':
        result = []
        line_map = {0:'NT',3:'FDU A',4:'FDU B',5:'FDU C',6:'FDU D',7:'FDU E',8:'FDU F',9:'FDU G',10:'FDU H',11:'PIDS',12: 'EOT'}
        month = request.GET.get('month')
        year=request.GET.get('year')
        if month!=None:
            month = int(month)
        else:
            month = 1
        if year != None:
            year = int(year)
        else:
            year = 2019
        firstDay = datetime.date(year, month, 1)
        lastDay = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)
        for line in line_map.keys():
            temp=lowUTENodesOfTeam(nodes,line,[firstDay,lastDay])
            temp['line']=line_map[line]
            result.append(temp)
        # print(result)
        return HttpResponse(dumps(result))
    if type=='unusedNodesOfTeam':
        result = []
        line_map = {0:'NT',3:'FDU A',4:'FDU B',5:'FDU C',6:'FDU D',7:'FDU E',8:'FDU F',9:'FDU G',10:'FDU H',11:'PIDS',12: 'EOT'}
        month = request.GET.get('month')
        year=request.GET.get('year')
        if month!=None:
            month = int(month)
        else:
            month = 1
        if year != None:
            year = int(year)
        else:
            year = 2019
        firstDay = datetime.date(year, month, 1)
        lastDay = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)
        for line in line_map.keys():
            temp=unusedNodesOfTeam(nodes,line,[firstDay,lastDay])
            temp['line']=line_map[line]
            result.append(temp)
        # print(result)
        return HttpResponse(dumps(result))
    if type=='unreachableNodesOfTeam':
        result = []
        line_map = {0:'NT',3:'FDU A',4:'FDU B',5:'FDU C',6:'FDU D',7:'FDU E',8:'FDU F',9:'FDU G',10:'FDU H',11:'PIDS',12: 'EOT'}
        month = request.GET.get('month')
        year=request.GET.get('year')
        if month!=None:
            month = int(month)
        else:
            month = 1
        if year != None:
            year = int(year)
        else:
            year = 2019
        firstDay = datetime.date(year, month, 1)
        lastDay = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)
        for line in line_map.keys():
            temp=unreachableNodesOfTeam(nodes,line,[firstDay,lastDay])
            temp['line']=line_map[line]
            result.append(temp)
        # print(result)
        return HttpResponse(dumps(result))
    if type=='lowUTEOfMonth':
        result = []
        dateList = getDateList()
        for d in dateList:
            result.append(lowUTEOfMonth(nodes,d))
        # print(result)
        return HttpResponse(dumps(result))
    if type=='lowUTEOfTeam':
        result = []
        dateList = getDateList()
        for d in dateList:
            result.append(lowUTEOfTeam(nodes,d))
        # print(result)
        return HttpResponse(dumps(result))
    if type=='lowUTEOfTestbed':
        result = []
        dateList = getDateList()
        for d in dateList:
            result.append(lowUTEOfTestbed(nodes, d))
        # print(result)
        return HttpResponse(dumps(result))
    if type=='lowUTEOfInterval':
        result = []
        dateList = getDateList()
        for d in dateList:
            result.append(lowUTEOfInterval(nodes, d))
        # print(result)
        return HttpResponse(dumps(result))