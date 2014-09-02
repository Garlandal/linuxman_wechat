# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.encoding import smart_str, smart_unicode

import xml.etree.ElementTree as ET
import time,hashlib
import datetime
import urllib
import urllib2
import json
import re

TOKEN = "Your Token"

TURING_API = "Your Turing API"

WELCOME = ""
INTRODUCE = ""
ACTIVITY = ""

SOURCES = ""


@csrf_exempt
def handleRequest(request):
    if request.method == 'GET':
        response = HttpResponse(checkSignature(request),content_type="text/plain")
        return response
    elif request.method == 'POST':
        response = HttpResponse(responseMsg(request),content_type="application/xml")
        return response
    else:
        return None

def checkSignature(request):
    global TOKEN
    signature = request.GET.get("signature", None)
    timestamp = request.GET.get("timestamp", None)
    nonce = request.GET.get("nonce", None)
    echoStr = request.GET.get("echostr",None)

    token = TOKEN
    tmpList = [token,timestamp,nonce]
    tmpList.sort()
    tmpstr = "%s%s%s" % tuple(tmpList)
    tmpstr = hashlib.sha1(tmpstr).hexdigest()
    if tmpstr == signature:
        return echoStr
    else:
        return None

def responseMsg(request):
    rawStr = smart_str(request.raw_post_data)
    msg = paraseMsgXml(ET.fromstring(rawStr))

    global WELCOME,INTRODUCE,ACTIVITY,SOURCES
    if msg.get('MsgType') == 'event':
		event = msg.get('Event')
		if event == 'subscribe':
			return getReplyXml(msg,WELCOME)
    info = msg['Content']
    if info == '1':
		return getReplyXml(msg,INTRODUCE)
    if info == '2':
		return getReplyXml(msg,ACTIVITY)
    if info == '3':
		return getReplyXml(msg,SOURCES)
    if info[:4] == 'man ':
		return getReplyXml(msg,man(info[4:]))
    else:
		url = ' http://www.tuling123.com/openapi/api?key=8970e526edc1e26dfd71b2ef68296d9f&info=' + info
		content = urllib.urlopen(url).read()
		myjson = json.loads(content)
		return getReplyXml(msg,myjson['text'])

def paraseMsgXml(rootElem):
    msg = {}
    if rootElem.tag == 'xml':
        for child in rootElem:
            msg[child.tag] = smart_str(child.text)
    return msg

def getReplyXml(msg,replyContent):
    TextReply = "<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s</CreateTime><MsgType><![CDATA[%s]]></MsgType><Content><![CDATA[%s]]></Content><FuncFlag>0</FuncFlag></xml>"
    TextReply = TextReply % (msg['FromUserName'],msg['ToUserName'],str(int(time.time())),'text',replyContent)
    return TextReply

def man(com):
		if type(com) == int or type(com) == float:
			res0 = '请按照正确格式输入(man command)'
			return res0
		else:
			url = 'http://l.51yip.com/search/%s' % com
			content = urllib.urlopen(url).read()
			if len(content) < 10000:
				res1 = '暂时还没有发现相应的中文man'
				return res1
			else:
				pat0 = re.compile(r'<pre>(.+?)</pre>',re.DOTALL)
				html0 = re.findall(pat0, content)
				html1 = re.sub(r'<br.{0,5}>','\n',html0[0])
				html2 = re.sub(r'&nbsp;',' ',html1)
				html3 = re.sub(r'<.*p>',' ',html2)
				html4 = html3.replace('&lt;','<')
				html5 = html4.replace('&gt;','>')
				html6 = html5.replace('&quot;','"')
				zh = html6.replace('&amp','&')
				if len(zh) < 2047:
					return zh
				else: 
					return zh[0:2047]
