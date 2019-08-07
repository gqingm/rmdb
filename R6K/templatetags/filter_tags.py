from django.template import Library
from django.utils.safestring import mark_safe
from R6K.models import node_info,user_info
from IXIA.models import port
register = Library()

@register.simple_tag
def lineselect(line):
    if line == None:
        return
    else:
        ele='<option value="%s">%s</option>' %(line,dict(user_info.line_choice)[line])
    return mark_safe(ele)

@register.simple_tag
def statusselect(status):
    ele='<option value="%s">%s</option>' %(status,dict(node_info.status_choice)[status])
    return mark_safe(ele)

@register.simple_tag
def build_table_row(filter_column,filter_list):
    filter_ele = '<th width="115px">Show<select name="_s" id="show">'
    if filter_column['_s'] == '10':
        filter_ele+='<option value="10" selected>10</option><option value="50">50</option><option value="100">100</option><option value="200">200</option><option value="500">500</option><option value="-1">All</option></select></th>'
    elif filter_column['_s'] == '50':
        filter_ele += '<option value="10">10</option><option value="50" selected>50</option><option value="100">100</option><option value="200">200</option><option value="500">500</option><option value="-1">All</option></select></th>'
    elif filter_column['_s'] == '100':
        filter_ele += '<option value="10">10</option><option value="50">50</option><option value="100" selected>100</option><option value="200">200</option><option value="500">500</option><option value="-1">All</option></select></th>'
    elif filter_column['_s'] == '200':
        filter_ele += '<option value="10">10</option><option value="50">50</option><option value="100">100</option><option value="200" selected>200</option><option value="500">500</option><option value="-1">All</option></select></th>'
    elif filter_column['_s'] == '500':
        filter_ele += '<option value="10">10</option><option value="50">50</option><option value="100">100</option><option value="200">200</option><option value="500" selected>500</option><option value="-1">All</option></select></th>'
    else:
        filter_ele += '<option value="10">10</option><option value="50">50</option><option value="100">100</option><option value="200">200</option><option value="500">500</option><option value="-1" selected>All</option></select></th>'
    #topo
    filter_ele+='<th width="92px"><select name="_tp" id="topo" style="width: 80px"><option></option>'
    for f in filter_list['topo_list']:
        if f['topo']==filter_column['_tp']:
            filter_ele += '<option value="%s" selected>%s</option>' % (f['topo'], f['topo'])
        else:
            filter_ele +='<option value="%s">%s</option>' %(f['topo'],f['topo'])
    #user
    filter_ele+='</select></th><th width="67px"><input type="text" name="_u" id="user" value="%s" style="width: 55px;height: 19px"></th><th width="59px"><select name="_l" id="line" style="width: 47px;"><option></option>' %filter_column['_u']
    #line
    for f in filter_list['line_list']:
        if f['user__line'] == None:
            continue
        elif str(f['user__line'])==filter_column['_l']:
            filter_ele += '<option value="%s" selected>%s</option>' %(f['user__line'],dict(user_info.line_choice)[f['user__line']])
        else:
            filter_ele += '<option value="%s">%s</option>' %(f['user__line'],dict(user_info.line_choice)[f['user__line']])
    filter_ele += '</select></th><th width="102px"><select name="_t" id="team" style="width: 90px;"><option></option>'
    #team
    for f in filter_list['team_list']:
        if f['user__team'] == None:
            continue
        elif f['user__team']==filter_column['_t']:
            filter_ele += '<option value="%s" selected>%s</option>' % (f['user__team'], f['user__team'])
        else:
            filter_ele +='<option value="%s">%s</option>' %(f['user__team'],f['user__team'])
    filter_ele += '</select></th><th width="67px"><select name="_ty" id="type" style="width: 55px;"><option></option>'
    #type
    for f in filter_list['type_list']:
        if f['type']==filter_column['_ty']:
            filter_ele += '<option value="%s" selected>%s</option>' % (f['type'], f['type'])
        else:
            filter_ele +='<option value="%s">%s</option>' %(f['type'],f['type'])
    filter_ele += '</select></th><th width="78px"><select name="_v" id="version" style="width: 66px;"><option></option>'
    #version
    for f in filter_list['version_list']:
        if f['backplane']==filter_column['_v']:
            filter_ele += '<option value="%s" selected>%s</option>' % (f['backplane'], f['backplane'])
        else:
            filter_ele +='<option value="%s">%s</option>' %(f['backplane'],f['backplane'])
    filter_ele += '</select></th><th width="92px"><select name="_loc" id="location" style="width: 80px;"><option></option>'
    #location
    for f in filter_list['location_list']:
        if f['location']==filter_column['_loc']:
            filter_ele += '<option value="%s" selected>%s</option>' % (f['location'], f['location'])
        else:
            filter_ele +='<option value="%s">%s</option>' %(f['location'],f['location'])
    filter_ele += '</select></th><th width="77px"><select name="_r" id="rack" style="width: 65px;"><option></option>'
    #rack
    for f in filter_list['rack_list']:
        if f['rack']==filter_column['_r']:
            filter_ele += '<option value="%s" selected>%s</option>' % (f['rack'], f['rack'])
        else:
            filter_ele +='<option value="%s">%s</option>' %(f['rack'],f['rack'])
    #search for bams
    filter_ele += '</select></th><th width="102px"><input type="text" name="_b" id="bams" value="%s" placeholder="search for bamsid" style="width: 90px;height: 19px"></th>' %filter_column['_b']
    #button for filter
    filter_ele+='<th width="112px"><input type="submit" style="height: 19px;text-align: center;font-size: smaller" value="filter"></th><th width="67px"><select name="_st" id="status" style="width: 55px;"><option></option>'
    #status
    for f in filter_list['status_list']:
        if str(f['status'])==filter_column['_st']:
            filter_ele += '<option value="%s" selected>%s</option>' %(f['status'],dict(node_info.status_choice)[f['status']])
        else:
            filter_ele += '<option value="%s">%s</option>' %(f['status'],dict(node_info.status_choice)[f['status']])
    #mode
    filter_ele += '</select></th><th width="52px"><select name="_m" id="status" style="width:40px;"><option></option>'
    if filter_column['_m'] == '0':
        filter_ele+='<option value="0" selected>D</option><option value="1">C</option>'
    elif filter_column['_m'] == '1':
        filter_ele += '<option value="0">D</option><option value="1" selected>C</option>'
    else:
        filter_ele += '<option value="0">D</option><option value="1">C</option>'
    #search for hardware
    filter_ele += '</select></th><th width="352px"><input type="text" name="_q" value="%s" placeholder="search for hardware" id="hardware" style="height: 19px;width: 340px"></th>' %filter_column['_q']

    return mark_safe(filter_ele)

@register.simple_tag
def render_paginator(filter_column,nodes,paginator,range,cur_num):
    if cur_num:
        strf=''
        for k,v in filter_column.items():
            if k=='page':continue
            strf+='&'+k+'='+v
        ele='<li><a href="?page=1%s" class="active"><span aria-hidden="true">First</span></a></li>' %strf
        if nodes.has_previous():
            ele+='<li><a href="?page=%s%s" aria-label="Previous"><span aria-hidden="true">&laquo;</span></a></li>' %(nodes.previous_page_number(),strf)
        else:
            ele+='<li class="disabled"><a href="" aria-label="Previous"><span aria-hidden="true">&laquo;</span></a></li>'
        for i in range:
            if cur_num==i:
                ele+='<li class="active"><a href="?page=%s%s">%s</a></li>' %(i,strf,i)
            else:
                ele+='<li><a href="?page=%s%s">%s</a></li>' %(i,strf,i)
        if nodes.has_next():
            ele+='<li><a href="?page=%s%s" aria-label="Next"><span aria-hidden="true">&raquo;</span></a></li>' %(nodes.next_page_number(),strf)
        else:
            ele+='<li class="disabled"><a href="" aria-label="Next"><span aria-hidden="true">&raquo;</span></a></li>'
        ele+='<li><a href="?page=%s%s" class="active"><span aria-hidden="true">Last</span></a></li>' %(paginator.num_pages,strf)
        return mark_safe(ele)
    else:
        return mark_safe('')

@register.simple_tag
def build_icon_line(filter_column,line_list):
    filter_ele = '<select name="line" id="line" style="height: 26px; width: 80px;"><option value="">All</option>'
    #line
    for l in line_list:
        if l['user__line'] == None:
            continue
        elif str(l['user__line'])==filter_column['user__line']:
            filter_ele += '<option value="%s" selected>%s</option>' %(l['user__line'],dict(user_info.line_choice)[l['user__line']])
        else:
            filter_ele += '<option value="%s">%s</option>' %(l['user__line'],dict(user_info.line_choice)[l['user__line']])
    filter_ele += '</select>'
    return mark_safe(filter_ele)

@register.simple_tag
def build_icon_type(filter_column):
    filter_ele = '<select name="duttype" id="dutType" style="height: 26px; width: 80px;"><option value="">All</option>'
    # type
    if filter_column['type__contains']=='6672':
        filter_ele += '<option value="6672" selected>6672</option><option value="6675">6675</option><option value="6371">6371</option><option value="6471/1">6471/1</option><option value="6471/2">6471/2</option><option value="6274">6274</option>'
    elif filter_column['type__contains']=='6675':
        filter_ele += '<option value="6672">6672</option><option value="6675" selected>6675</option><option value="6371">6371</option><option value="6471/1">6471/1</option><option value="6471/2">6471/2</option><option value="6274">6274</option>'
    elif filter_column['type__contains']=='6371':
        filter_ele += '<option value="6672">6672</option><option value="6675">6675</option><option value="6371" selected>6371</option><option value="6471/1">6471/1</option><option value="6471/2">6471/2</option><option value="6274">6274</option>'
    elif filter_column['type__contains']=='6471/1':
        filter_ele += '<option value="6672">6672</option><option value="6675">6675</option><option value="6371">6371</option><option value="6471/1" selected>6471/1</option><option value="6471/2">6471/2</option><option value="6274">6274</option>'
    elif filter_column['type__contains']=='6471/2':
        filter_ele += '<option value="6672">6672</option><option value="6675">6675</option><option value="6371">6371</option><option value="6471/1">6471/1</option><option value="6471/2" selected>6471/2</option><option value="6274">6274</option>'
    elif filter_column['type__contains']=='6274':
        filter_ele += '<option value="6672">6672</option><option value="6675">6675</option><option value="6371">6371</option><option value="6471/1">6471/1</option><option value="6471/2">6471/2</option><option value="6274" selected>6274</option>'
    filter_ele += '</select>'
    return mark_safe(filter_ele)

@register.simple_tag
def build_filter_table(filter_for_css,filter_list):
    filter_ele = '<th><select name="_tp" id="topo" style="width: 160px;vertical-align: middle"><option></option>'
    for f in filter_list['topo_list']:
        if '_tp' in filter_for_css and f['topo'] == filter_for_css['_tp']:
            filter_ele += '<option value="%s" selected>%s</option>' % (f['topo'], f['topo'])
        else:
            filter_ele += '<option value="%s">%s</option>' % (f['topo'], f['topo'])
    #user
    if '_u' in filter_for_css:
        filter_ele += '</select></th><th><input type="text" name="_u" id="user" value="%s" style="width: 55px;height: 19px;vertical-align: middle"></th><th><select name="l" id="line" style="width: 44px;"><option></option>' % filter_for_css['_u']
    else:
        filter_ele += '</select></th><th><input type="text" name="_u" id="user" value="" style="width: 55px;height: 19px;vertical-align: middle"></th><th><select name="l" id="line" style="width: 47px;"><option></option>'
    #line
    for f in filter_list['line_list']:
        if str(f['user__line']) == filter_for_css['l']:
            filter_ele += '<option value="%s" selected>%s</option>' %(f['user__line'], dict(user_info.line_choice)[f['user__line']])
        else:
            filter_ele += '<option value="%s">%s</option>' % (f['user__line'], dict(user_info.line_choice)[f['user__line']])
    filter_ele += '</select></th><th><select name="_t" id="team" style="width: 90px;vertical-align: middle"><option></option>'
    # team
    for f in filter_list['team_list']:
        if '_t' in filter_for_css and f['user__team'] == filter_for_css['_t']:
            filter_ele += '<option value="%s" selected>%s</option>' % (f['user__team'], f['user__team'])
        else:
            filter_ele += '<option value="%s">%s</option>' % (f['user__team'], f['user__team'])
    filter_ele += '</select></th><th><select name="t" id="type" style="width: 55px;vertical-align: middle"><option></option>'
    # type
    if filter_for_css['t']=='6672':
        filter_ele += '<option value="6672" selected>6672</option><option value="6675">6675</option><option value="6371">6371</option><option value="6471/1">6471/1</option><option value="6471/2">6471/2</option><option value="6274">6274</option>'
    elif filter_for_css['t']=='6675':
        filter_ele += '<option value="6672">6672</option><option value="6675" selected>6675</option><option value="6371">6371</option><option value="6471/1">6471/1</option><option value="6471/2">6471/2</option><option value="6274">6274</option>'
    elif filter_for_css['t']=='6371':
        filter_ele += '<option value="6672">6672</option><option value="6675">6675</option><option value="6371" selected>6371</option><option value="6471/1">6471/1</option><option value="6471/2">6471/2</option><option value="6274">6274</option>'
    elif filter_for_css['t']=='6471/1':
        filter_ele += '<option value="6672">6672</option><option value="6675">6675</option><option value="6371">6371</option><option value="6471/1" selected>6471/1</option><option value="6471/2">6471/2</option><option value="6274">6274</option>'
    elif filter_for_css['t']=='6471/2':
        filter_ele += '<option value="6672">6672</option><option value="6675">6675</option><option value="6371">6371</option><option value="6471/1">6471/1</option><option value="6471/2" selected>6471/2</option><option value="6274">6274</option>'
    elif filter_for_css['t']=='6274':
        filter_ele += '<option value="6672">6672</option><option value="6675">6675</option><option value="6371">6371</option><option value="6471/1">6471/1</option><option value="6471/2">6471/2</option><option value="6274" selected>6274</option>'
    else:
        filter_ele += '<option value="6672">6672</option><option value="6675">6675</option><option value="6371">6371</option><option value="6471/1">6471/1</option><option value="6471/2">6471/2</option><option value="6274">6274</option>'
    filter_ele += '</select></th><th><select name="_v" id="version" style="width: 66px;vertical-align: middle"><option></option>'
    # version
    for f in filter_list['version_list']:
        if '_v' in filter_for_css and f['backplane'] == filter_for_css['_v']:
            filter_ele += '<option value="%s" selected>%s</option>' % (f['backplane'], f['backplane'])
        else:
            filter_ele += '<option value="%s">%s</option>' % (f['backplane'], f['backplane'])
    filter_ele += '</select></th><th><select name="_loc" id="location" style="width: 80px;vertical-align: middle"><option></option>'
    # location
    for f in filter_list['location_list']:
        if '_loc' in filter_for_css and f['location'] == filter_for_css['_loc']:
            filter_ele += '<option value="%s" selected>%s</option>' % (f['location'], f['location'])
        else:
            filter_ele += '<option value="%s">%s</option>' % (f['location'], f['location'])
    filter_ele += '</select></th><th><select name="_r" id="rack" style="width: 65px;vertical-align: middle"><option></option>'
    # rack
    for f in filter_list['rack_list']:
        if '_r' in filter_for_css and f['rack'] == filter_for_css['_r']:
            filter_ele += '<option value="%s" selected>%s</option>' % (f['rack'], f['rack'])
        else:
            filter_ele += '<option value="%s">%s</option>' % (f['rack'], f['rack'])
    filter_ele += '</select></th><th><select name="_st" id="status" style="width: 55px;vertical-align: middle"><option></option>'
    #status
    for f in filter_list['status_list']:
        if '_st' in filter_for_css and str(f['status']) == filter_for_css['_st']:
            filter_ele += '<option value="%s" selected>%s</option>' % (f['status'], dict(node_info.status_choice)[f['status']])
        else:
            filter_ele += '<option value="%s">%s</option>' % (f['status'], dict(node_info.status_choice)[f['status']])
    filter_ele += '</select></th>'
    return mark_safe(filter_ele)

@register.simple_tag
def build_share_r6k(filter_column,filter_list):
    filter_ele = '<th></th>'
    #topo
    filter_ele+='<th><select name="_tp" id="topo" style="width: 80px"><option></option>'
    for f in filter_list['topo_list']:
        if f['topo']==filter_column['_tp']:
            filter_ele += '<option value="%s" selected>%s</option>' % (f['topo'], f['topo'])
        else:
            filter_ele +='<option value="%s">%s</option>' %(f['topo'],f['topo'])
    filter_ele+='</select></th><th></th><th></th><th></th><th><select name="_ty" id="type" style="width: 55px;"><option></option>'
    #type
    for f in filter_list['type_list']:
        if f['type']==filter_column['_ty']:
            filter_ele += '<option value="%s" selected>%s</option>' % (f['type'], f['type'])
        else:
            filter_ele +='<option value="%s">%s</option>' %(f['type'],f['type'])
    filter_ele += '</select></th><th><select name="_v" id="version" style="width: 66px;"><option></option>'
    #version
    for f in filter_list['version_list']:
        if f['backplane']==filter_column['_v']:
            filter_ele += '<option value="%s" selected>%s</option>' % (f['backplane'], f['backplane'])
        else:
            filter_ele +='<option value="%s">%s</option>' %(f['backplane'],f['backplane'])
    filter_ele += '</select></th><th><select name="_loc" id="location" style="width: 80px;"><option></option>'
    #location
    for f in filter_list['location_list']:
        if f['location']==filter_column['_loc']:
            filter_ele += '<option value="%s" selected>%s</option>' % (f['location'], f['location'])
        else:
            filter_ele +='<option value="%s">%s</option>' %(f['location'],f['location'])
    filter_ele += '</select></th><th><select name="_r" id="rack" style="width: 65px;"><option></option>'
    #rack
    for f in filter_list['rack_list']:
        if f['rack']==filter_column['_r']:
            filter_ele += '<option value="%s" selected>%s</option>' % (f['rack'], f['rack'])
        else:
            filter_ele +='<option value="%s">%s</option>' %(f['rack'],f['rack'])
    #search for bams
    filter_ele += '</select></th><th><input type="text" name="_b" id="bams" value="%s" placeholder="search for bamsid" style="width: 90px;height: 19px"></th>' %filter_column['_b']
    #button for filter
    filter_ele+='<th><input type="submit" style="height: 19px;text-align: center;font-size: smaller" value="filter"></th><th><select name="_st" id="status" style="width: 55px;"><option></option>'
    #status
    for f in filter_list['status_list']:
        if str(f['status'])==filter_column['_st']:
            filter_ele += '<option value="%s" selected>%s</option>' %(f['status'],dict(node_info.status_choice)[f['status']])
        else:
            filter_ele += '<option value="%s">%s</option>' %(f['status'],dict(node_info.status_choice)[f['status']])
    #mode
    filter_ele += '</select></th><th><select name="_m" id="status" style="width:40px;"><option></option>'
    if filter_column['_m'] == '0':
        filter_ele+='<option value="0" selected>D</option><option value="1">C</option>'
    elif filter_column['_m'] == '1':
        filter_ele += '<option value="0">D</option><option value="1" selected>C</option>'
    #search for hardware
    filter_ele += '</select></th><th><input type="text" name="_q" value="%s" placeholder="search for hardware" id="hardware" style="height: 19px;width: 340px"></th>' %filter_column['_q']
    return mark_safe(filter_ele)

@register.simple_tag
def ixiastatus(status):
    ele='<option value="%s">%s</option>' %(status,dict(port.status_choice)[status])
    return mark_safe(ele)

@register.simple_tag
def build_ixia_filter(filter_column,filter_list):
    if len(filter_column)==1 and '_i' in filter_column.keys():
        #IP
        filter_ele = '<th style="width:150px;"><select name="_i" id="ip" style="width: 120px"><option></option>'
        for f in filter_list['ip']:
            if f['ip'] == filter_column['_i']:
                filter_ele += '<option value="%s" selected>%s</option>' % (f['ip'], f['ip'])
            else:
                filter_ele += '<option value="%s">%s</option>' % (f['ip'], f['ip'])
        # card
        filter_ele += '</select></th><th style="width:40px;"><select name="_c" id="card" style="width: 32px;"><option></option>'
        for f in filter_list['card']:
            filter_ele += '<option value=%s>%s</option>' % (f['slot'], f['slot'])
        # cardinfo
        filter_ele += '</select></th><th style="width: 175px;"><input type="text" name="_ct" placeholder="search for card info" id="cardinfo" style="height: 19px;width: 157px;"></th><th></th><th style="width:59px;"><select name="_s" id="status" style="width: 46px;"><option></option>'
        # status
        for f in filter_list['status']:
            filter_ele += '<option value=%s>%s</option>' % (f['status'], dict(port.status_choice)[f['status']])
        # switch
        filter_ele += '</select></th><th style="width:86px;"><select name="_sw" id="switch" style="width: 66px;"><option></option>'
        for f in filter_list['switch']:
            if f['switch']:
                filter_ele += '<option value="%s">%s</option>' % (f['switch'], f['switch'])
        # line
        filter_ele += '</select></th><th style="width:59px;"><select name="_l" id="line" style="width: 47px;"><option></option>'
        for f in filter_list['line']:
            if f['user__line'] in range(13):
                filter_ele += '<option value="%s">%s</option>' % (f['user__line'], dict(user_info.line_choice)[f['user__line']])
        # user
        filter_ele += '</select></th><th style="width:83px;"><input type="text" name="_u" id="user" placeholder="search for user" style="width: 70px;height: 19px"></th>'
        # purpose
        filter_ele += '<th style="width:154px;"><input type="text" name="_p" id="purpose" placeholder="search for purpose" style="width: 138px;height: 19px"></th>'
    else:
        #IP
        filter_ele='<th style="width: 150px;"><select name="_i" id="ip" style="width: 120px"><option></option>'
        for f in filter_list['ip']:
            if f['ip']==filter_column['_i']:
                filter_ele += '<option value="%s" selected>%s</option>' % (f['ip'], f['ip'])
            else:
                filter_ele +='<option value="%s">%s</option>' %(f['ip'],f['ip'])
        #card
        filter_ele += '</select></th><th style="width:40px;"><select name="_c" id="card" style="width: 32px;"><option></option>'
        for f in filter_list['card']:
            if str(f['slot'])==filter_column['_c']:
                filter_ele += '<option value="%s" selected>%s</option>' % (f['slot'], f['slot'])
            else:
                filter_ele +='<option value="%s">%s</option>' %(f['slot'],f['slot'])
        #cardinfo
        filter_ele+='</select></th><th style="width: 175px;"><input type="text" name="_ct" value="%s" placeholder="search for card info" id="cardinfo" style="height: 19px;width: 157px;"></th><th></th><th style="width:59px;"><select name="_s" id="status" style="width: 46px;"><option></option>' %filter_column['_ct']
        #status
        for f in filter_list['status']:
            if str(f['status'])==filter_column['_s']:
                filter_ele += '<option value="%s" selected>%s</option>' %(f['status'],dict(port.status_choice)[f['status']])
            else:
                filter_ele += '<option value="%s">%s</option>' %(f['status'],dict(port.status_choice)[f['status']])
        #switch
        filter_ele += '</select></th><th style="width:86px;"><select name="_sw" id="switch" style="width: 66px;"><option></option>'
        for f in filter_list['switch']:
            if f['switch'] and f['switch'] == filter_column['_sw']:
                filter_ele += '<option value="%s" selected>%s</option>' % (f['switch'], f['switch'])
            elif f['switch']:
                filter_ele += '<option value="%s">%s</option>' % (f['switch'], f['switch'])
        #line
        filter_ele += '</select></th><th style="width:59px;"><select name="_l" id="line" style="width: 39px;"><option></option>'
        for f in filter_list['line']:
            if str(f['user__line']) and str(f['user__line']) == filter_column['_l']:
                filter_ele += '<option value="%s" selected>%s</option>' % (f['user__line'], dict(user_info.line_choice)[f['user__line']])
            elif f['user__line'] in range(13):
                filter_ele += '<option value="%s">%s</option>' % (f['user__line'], dict(user_info.line_choice)[f['user__line']])
        #user
        filter_ele += '</select></th><th style="width:83px;"><input type="text" value="%s" name="_u" id="user" placeholder="search for user" style="width: 70px;height: 19px"></th>' %filter_column['_u']
        #purpose
        filter_ele+='<th style="width:154px;"><input type="text" value="%s" name="_p" id="purpose" placeholder="search for purpose" style="width: 138px;height: 19px"></th>' %filter_column['_p']
    return mark_safe(filter_ele)

@register.simple_tag
def buildIxiaFilterTable(filter_for_css,filter_list):
    filter_ele = '<th width="150px"><select name="_i" id="ip" style="width: 120px"><option></option>'
    #ip
    for f in filter_list['ip_list']:
        if '_i' in filter_for_css and f['card__ip__ip'] == filter_for_css['_i']:
            filter_ele += '<option value="%s" selected>%s</option>' % (f['card__ip__ip'], f['card__ip__ip'])
        else:
            filter_ele += '<option value="%s">%s</option>' % (f['card__ip__ip'], f['card__ip__ip'])
    filter_ele += '</select></th><th width="40px"><select name="_c" id="card" style="width: 32px;"><option></option>'
    #card
    for f in filter_list['card_list']:
        if '_c' in filter_for_css and f['card__slot'] == filter_for_css['_c']:
            filter_ele += '<option value="%s" selected>%s</option>' % (f['card__slot'], f['card__slot'])
        else:
            filter_ele += '<option value="%s">%s</option>' % (f['card__slot'], f['card__slot'])
    #card info
    if '_c' in filter_for_css:
        filter_ele += '</select></th><th width="175px"><input type="text" name="_ct" value="%s" placeholder="search for card info" id="cardinfo" style="height: 19px;width: 156px;"></th><th></th><th><select name="_l" id="line" style="width: 47px;"><option></option>' % filter_for_css['_c']
    else:
        filter_ele += '</select></th><th width="175px"><input type="text" name="_ct" placeholder="search for card info" id="cardinfo" style="height: 19px;width: 117px;"></th><th></th><th><select name="l" id="line" style="width: 47px;"><option></option>'
    #line
    for f in filter_list['line_list']:
        if str(f['user__line']) == filter_for_css['l']:
            filter_ele += '<option value="%s" selected>%s</option>' %(f['user__line'], dict(user_info.line_choice)[f['user__line']])
        else:
            filter_ele += '<option value="%s">%s</option>' % (f['user__line'], dict(user_info.line_choice)[f['user__line']])
    #user
    if '_c' in filter_for_css:
        filter_ele += '</select></th><th><input type="text" name="_u" value="%s" id="user" placeholder="search for user" style="width: 70px;height: 19px"></th>' %filter_for_css['_u']
    else:
        filter_ele += '</select></th><th><input type="text" name="_u" id="user" placeholder="search for user" style="width: 70px;height: 19px"></th>'
    #purpose
    if '_c' in filter_for_css:
        filter_ele += '<th><input type="text" name="_p" value="%s" id="purpose" placeholder="search for purpose" style="width: 138px;height: 19px"></th>' %filter_for_css['_u']
    else:
        filter_ele += '<th><input type="text" name="_p" id="purpose" placeholder="search for purpose" style="width: 151px;height: 19px"></th>'
    return mark_safe(filter_ele)