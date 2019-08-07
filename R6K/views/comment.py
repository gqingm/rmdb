#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
from django.shortcuts import render,HttpResponse
from django.http import JsonResponse
from RMDB.settings import BASE_DIR
from R6K import models
import json
from .account import check_login
from R6K.views import api

log=api.log
@check_login
def add(request,nid):
    """
    只有superuser可以添加
    :param request:
    :param nid:
    :return:
    """
    # if not request.session.get('user_info')['superuser']:
    #     return HttpResponse(JsonResponse('滚蛋'))
    if request.method=='POST':
        print(request.POST)
        node=models.node_info.objects.filter(nid=nid).all()
        node.update(comments=request.POST['comment'])
        # log.log(request.POST['comment'],nid)
    return HttpResponse(JsonResponse({'status':True}))

def show(request,nid):
    message=[]
    file=os.path.join(BASE_DIR,'log','%s.log' %nid)
    if not os.path.exists(file):
        message.append("There's no any record.")
    else:
        with open(file, "r") as f:
            while True:
                tlines = f.readline()
                if not tlines:
                    break
                else:
                    message.append(tlines)
    return render(request,'comment.html',{'message':message})

def getLastLine(nid):
    file = os.path.join(BASE_DIR, 'log', '%s.log' % nid)
    if not os.path.exists(file):
        return ''
    else:
        with open(file, 'rb') as f:  # 打开文件
            offset = -50  # 设置偏移量
            while True:
                """
                file.seek(off, whence=0)：从文件中移动off个操作标记（文件指针），正往结束方向移动，负往开始方向移动。
                如果设定了whence参数，就以whence设定的起始位为准，0代表从头开始，1代表当前位置，2代表文件最末尾位置。 
                """
                try:
                    f.seek(offset, 2)  # seek(offset, 2)表示文件指针：从文件末尾(2)开始向前50个字符(-50)
                except Exception as e:
                    f.seek(0,0)
                    lines = f.readlines()
                    lines=lines[-1].decode('utf-8')
                    if len(lines) > 50:
                        lines = lines[:50]
                    return lines+'...'
                lines = f.readlines()  # 读取文件指针范围内所有行
                if len(lines) >= 2:  # 判断是否最后至少有两行，这样保证了最后一行是完整的
                    last_line = lines[-1]  # 取最后一行
                    break
                offset *= 2
        last_line=last_line.decode('utf-8')
        if len(last_line)>50:
            last_line=last_line[:50]
        return last_line+'...'

def get(request):
    message=[]
    if request.method=='POST':
        nids=request.POST.getlist('nids')
        for nid in nids:
            # print(nid,getLastLine(nid).split('\r\n')[0])
            message.append(getLastLine(nid).split('\r\n')[0])
    return HttpResponse(json.dumps(message))