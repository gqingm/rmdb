#!/usr/bin/env python
#coding=utf-8
import datetime
import xlwt
from django.db.models import Q

def BulidR6KExcel(download_url,obj):
    #定义字段名(列表)
    field_name_list = ['ip','topo','user','line','team','type','version','location','rack','bams id','sn','status','mode','haradware info']
    #定义格式
    style0 = xlwt.easyxf('font: name Times New Roman, color-index red, bold on')
    #获取每个设备的信息
    mylist=[]
    for i in obj:
        mylist.append([i.ip,i.topo,i.node2user_set.first().uid.eid,i.node2user_set.first().uid.get_line_display(),i.node2user_set.first().uid.team,i.type,i.backplane,i.location,i.rack,i.bams,i.sn,i.get_status_display(),i.get_mode_display(),i.hardware_info])
    #创建excel表格和sheet页
    wb = xlwt.Workbook()
    ws = wb.add_sheet('Sheet')
    num = 0
    #添加时间及对应的设备使用率
    for i in obj:
        for u in i.useages:
            if num==0:
                field_name_list.append(u[0].strftime("%Y-%m-%d"))
            mylist[num].append(u[1])
        # print(mylist[num])
        num+=1
    #写入excel的首行的信息
    for i in range(len(field_name_list)):
        # print(0,i,field_name_list[i])
        ws.write(0,i,field_name_list[i],style0)
    #写入每台设备的信息
    # print('count:',obj.count(),len(field_name_list))
    for i in range(0,obj.count()):
        for j in range(len(field_name_list)):
            # print(i+1,j,mylist[i][j])
            ws.write(i+1,j,mylist[i][j])
    timestr=datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    # print(download_url,timestr)
    # print(wb)
    #将信息保存到本地
    wb.save(download_url+'/'+'R6K_'+timestr+'.xls')
    return 'R6K_'+timestr

def BulidIxiaExcel(download_url,obj):
    #定义字段名(列表)
    field_name_list = ['ip','chassisinfo','card','cardinfo','cardstatus','port','status','switch','line','user','purpose','usecycle','comments']
    #定义格式
    style0 = xlwt.easyxf('font: name Times New Roman, color-index red, bold on')
    #获取每个端口的信息
    mylist=[]
    for i in obj:
        if i.user:
            mylist.append([i.card.first().ip.ip,i.card.first().ip.chassis_info,i.card.first().slot,i.card.first().card_info,i.card.first().get_status_display(),i.port_num,i.get_status_display(),i.switch,i.user.eid,i.user.get_line_display(),i.purpose,i.usecycle,i.comments])
        else:
            mylist.append([i.card.first().ip.ip,i.card.first().ip.chassis_info,i.card.first().slot,i.card.first().card_info,i.card.first().get_status_display(),i.port_num,i.get_status_display(),i.switch,'','',i.purpose,i.usecycle,i.comments])
    #创建excel表格和sheet页
    wb = xlwt.Workbook()
    ws = wb.add_sheet('Sheet')
    num = 0
    #添加时间及对应的设备使用率
    for i in obj:
        for u in i.useages:
            if num==0:
                field_name_list.append(u[0].strftime("%Y-%m-%d"))
            mylist[num].append(u[1])
        # print(mylist[num])
        num+=1
    #写入excel的首行的信息
    for i in range(len(field_name_list)):
        # print(0,i,field_name_list[i])
        ws.write(0,i,field_name_list[i],style0)
    #写入每台设备的信息
    # print('count:',obj.count(),len(field_name_list))
    for i in range(0,obj.count()):
        for j in range(len(field_name_list)):
            # print(i+1,j,mylist[i][j])
            ws.write(i+1,j,mylist[i][j])
    timestr=datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    # print(download_url,timestr)
    # print(wb)
    #将信息保存到本地
    wb.save(download_url+'/'+'IXIA_'+timestr+'.xls')
    return 'IXIA_'+timestr

def JudgeUseage(nodes):
    """
    按条件获取node
    :param nodes:
    :return:
    """
    HighUsage=nodes.filter(useage_avg__gt=70)
    Other = nodes.filter(Q(useage_avg__gt=30) & Q(useage_avg__lte=70))
    LowUsage = nodes.filter(Q(useage_avg__gt=15) & Q(useage_avg__lte=30))
    LowerUsage = nodes.filter(Q(useage_avg__gt=5) & Q(useage_avg__lte=15))
    LowestUsage = nodes.filter(Q(useage_avg__gt=0.161) & Q(useage_avg__lte=5))
    Unused = nodes.filter(useage_avg__lte=0.161, status__in=(0,1))
    Unreachable = nodes.filter(useage_avg__lte=0.161, status=2)
    return HighUsage,LowUsage,LowerUsage,LowestUsage,Unused,Unreachable,Other

def JudgeIxiaUseage(ixias):
    """
    按条件获取port
    :param ixias:
    :return:
    """
    HighUsage=ixias.filter(useage_avg__gt=70)
    Middle = ixias.filter(Q(useage_avg__gt=30) & Q(useage_avg__lte=70))
    LowUsage = ixias.filter(Q(useage_avg__gt=15) & Q(useage_avg__lte=30))
    LowerUsage = ixias.filter(Q(useage_avg__gt=5) & Q(useage_avg__lte=15))
    LowestUsage = ixias.filter(Q(useage_avg__gt=0) & Q(useage_avg__lte=5))
    Unused = ixias.filter(useage_avg=0)
    return HighUsage,Middle,LowUsage,LowerUsage,LowestUsage,Unused

def deal_table(date_list,useages):
    """
    补全node 30天的使用率数据
    :param date_list:
    :param useages:
    :return:
    """
    i,j=0,0
    new_list=[]
    while i<len(date_list):
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

def WriteSheet(obj,sheet,datelist):
    field_name_list = ['ip','topo','user','line','team','type','version','location','rack','status']
    mylist = []
    #定义格式
    style0 = xlwt.easyxf('font: name Times New Roman, color-index red, bold on')
    for i in obj:
        mylist.append([i.ip, i.topo, i.node2user_set.first().uid.eid, i.node2user_set.first().uid.get_line_display(),i.node2user_set.first().uid.team, i.type, i.backplane, i.location, i.rack,i.get_status_display()])
    for d in datelist:
        field_name_list.append(d.strftime("%Y-%m-%d"))
    field_name_list.append('Avg')
    # 写入excel的首行的信息
    for i in range(len(field_name_list)):
        # print(0,i,field_name_list[i])
        sheet.write(0, i, field_name_list[i], style0)
    if obj.count():
        for node in obj:
            # 获取每个盒子最近30天内的数据
            node.useages = list(node.utilization_set.filter(day__range=(datelist[0], datelist[-1])).values_list('day', 'useage'))
            # 如果获取到数据个数不等于日期天数
            node.useages = deal_table(datelist, node.useages)
        num = 0
        # 添加时间及对应的设备使用率
        for i in obj:
            for u in i.useages:
                mylist[num].append(u[1])
            if i.useage_avg<0.161:
                mylist[num].append(0)
            else:
                mylist[num].append(i.useage_avg)
            # print(mylist[num])
            num += 1
        # 写入每台设备的信息
        # print('count:',obj.count(),len(field_name_list))
        for i in range(0, obj.count()):
            for j in range(len(field_name_list)):
                # print(i+1,j,mylist[i][j])
                sheet.write(i + 1, j, mylist[i][j])

def WriteIxiaSheet(obj,sheet,datelist):
    field_name_list = ['ip','card','card info','port','line','user','purpose','usecycle','comments']
    mylist = []
    #定义格式
    style0 = xlwt.easyxf('font: name Times New Roman, color-index red, bold on')
    for i in obj:
        mylist.append([i.card.first().ip.ip,i.card.first().slot,i.card.first().card_info,i.port_num,i.user.get_line_display(),i.user.eid,i.purpose,i.usecycle,i.comments])
    for d in datelist:
        field_name_list.append(d.strftime("%Y-%m-%d"))
    field_name_list.append('Avg')
    # 写入excel的首行的信息
    for i in range(len(field_name_list)):
        # print(0,i,field_name_list[i])
        sheet.write(0, i, field_name_list[i], style0)
    if obj.count():
        for ixia in obj:
            # 获取每个盒子最近30天内的数据
            ixia.useages = list(ixia.utilization_set.filter(day__range=(datelist[0], datelist[-1])).values_list('day', 'useage'))
            # 如果获取到数据个数不等于日期天数
            ixia.useages = deal_table(datelist, ixia.useages)
        num = 0
        # 添加时间及对应的设备使用率
        for i in obj:
            for u in i.useages:
                mylist[num].append(u[1])
            mylist[num].append(i.useage_avg)
            # print(mylist[num])
            num += 1
        # 写入每台设备的信息
        # print('count:',obj.count(),len(field_name_list))
        for i in range(0, obj.count()):
            for j in range(len(field_name_list)):
                # print(i+1,j,mylist[i][j])
                sheet.write(i + 1, j, mylist[i][j])

def IconR6KExcel(download_url,obj,datelist):
    #定义字段名(列表)
    #获取每个设备的信息
    HighUsage, LowUsage, LowerUsage, LowestUsage, Unused, Unreachable, Other=JudgeUseage(obj)
    #创建excel表格和sheet页
    wb = xlwt.Workbook()
    ws1 = wb.add_sheet('>70%')
    WriteSheet(HighUsage,ws1,datelist)
    ws2 = wb.add_sheet('30%~70%')
    WriteSheet(Other,ws2,datelist)
    ws3 = wb.add_sheet('15%~30%')
    WriteSheet(LowUsage,ws3,datelist)
    ws4 = wb.add_sheet('5%~15%')
    WriteSheet(LowerUsage,ws4,datelist)
    ws5 = wb.add_sheet('0~5%')
    WriteSheet(LowestUsage,ws5,datelist)
    ws6 = wb.add_sheet('unused')
    WriteSheet(Unused,ws6,datelist)
    ws7 = wb.add_sheet('unreachable')
    WriteSheet(Unreachable,ws7,datelist)
    timestr=datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    # print(download_url,timestr)
    # print(wb)
    #将信息保存到本地
    wb.save(download_url+'/'+'R6K_'+timestr+'.xls')
    return 'R6K_'+timestr

def IconIXIAExcel(download_url,obj,datelist):
    #定义字段名(列表)
    #获取每个设备的信息
    HighUsage, Middle, LowUsage, LowerUsage, LowestUsage, Unused=JudgeIxiaUseage(obj)
    #创建excel表格和sheet页
    wb = xlwt.Workbook()
    ws1 = wb.add_sheet('>70%')
    WriteIxiaSheet(HighUsage,ws1,datelist)
    ws2 = wb.add_sheet('30%~70%')
    WriteIxiaSheet(Middle,ws2,datelist)
    ws3 = wb.add_sheet('15%~30%')
    WriteIxiaSheet(LowUsage,ws3,datelist)
    ws4 = wb.add_sheet('5%~15%')
    WriteIxiaSheet(LowerUsage,ws4,datelist)
    ws5 = wb.add_sheet('0~5%')
    WriteIxiaSheet(LowestUsage,ws5,datelist)
    ws6 = wb.add_sheet('unused')
    WriteIxiaSheet(Unused,ws6,datelist)
    timestr=datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    # print(download_url,timestr)
    # print(wb)
    #将信息保存到本地
    wb.save(download_url+'/'+'IXIA_'+timestr+'.xls')
    return 'IXIA_'+timestr