#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import urllib
import cookielib
import re
import rsa
import binascii
import requests

class WeiBo:
	def __init__(self):
		self.pre_login_url = 'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=MjYwNzI0MTE5JTQwcXEuY29t&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.18)&_=1470731779603'
		self.retcode = 0
		self.pubkey = 'EB2A38568661887FA180BDDB5CABD5F21C7BFD59C090CB2D245A87AC253062882729293E5506350508E7F9AA3BB77F4333231490F915F6D63C55FE2F08A49B353F444AD3993CACC02DB784ABBB8E42A9B1BBFFFB38BE18D78E87A0E41B9B8F73A928EE0CCEE1F6739884B9777E4FE9E88A1BBE495927AC4A799B3181D6442443'
		self.rsakv = '1330428213'
		self.is_openlock = 0
		self.showpin = 0
		self.username = 'MjYwNzI0MTE5JTQwcXEuY29t'
		self.passwd = 'password'


	def prelogin(self):
		pre_request = urllib2.Request(self.pre_login_url)
		self.cookies = cookielib.CookieJar()
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookies))
		response_page = opener.open(pre_request)
		result = response_page.read()
		result = result.replace('sinaSSOController.preloginCallBack', '')
		result = eval(result)
		self.servertime = result['servertime']
		self.nonce = result['nonce']

	def password(self):
		rsaPublicKey = rsa.PublicKey(int(self.pubkey, 16), 65537)
		self.password = rsa.encrypt(str(self.servertime) + '\t' + str(self.nonce) + "\n" + str(self.passwd), rsaPublicKey)
		self.password =  binascii.b2a_hex(self.password)

	def login(self):
		post_data = { 
			'entry' : 'weibo',
			'gateway' : '1',
			'from' : '',
			'savestate' : '7',
			'useticket' : '1',
			'pageerfer' : 'http://login.sina.com.cn/sso/logout.php?entry=miniblog&r=http%3A%2Fweibo.com%2Flogout.php%3Fbackurl',
			'vsnf' : '1',
			'su' : self.username ,
			'service' : 'miniblog',
			'servertime' : self.servertime,
			'nonce' : self.nonce,
			'pwencode' : 'rsa2',
			'rsakv' : self.rsakv,
			'sp' : self.password,
			'sr' : '1366*768',
			'encoding' : 'UTF-8',
			'prelt' : '115',
			'url' : 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
			'returntype' : 'META'
		}
		post_data = urllib.urlencode(post_data)
		login_url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)'
		self.user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36'
		headers = {'User-Agent' : self.user_agent}
		request = urllib2.Request(login_url, data=post_data)
		request.add_header('User-Agent', self.user_agent)
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookies))
		response = opener.open(request)
		self.return_page = response.read().decode('GBK')
		pattern = re.compile(r'location\.replace\([\'"](.*?)[\'"]\)', re.S)
		self.login_url = pattern.findall(self.return_page)[0]

	def loginWeiBo(self):
		request = urllib2.Request(self.login_url)
		request.add_header('User-Agent', self.user_agent)
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookies))
		response = opener.open(request)
		result = response.read()
		pattern = re.compile('"uniqueid":"(.*?)"', re.S)
		self.uniqueid = pattern.findall(result)[0]
		#print uniqueid
		self.final_url = 'http://weibo.com/%s/profile?topnav=1&wvr=6&is_all=1' % self.uniqueid
	
	def module_test(self):
		page_num = 1
		self.dict = {}
		pattern = re.compile(r'nick-name=\\"(.*?)\\"', re.S)
		for page_num in range(1, 100):
			self.final_url = 'http://weibo.com/u/%s/home?end_id=4006640628435333&pre_page=%d&page=%d' % (self.uniqueid, page_num, page_num+1)
			self.loginFinal()
			page_list = pattern.findall(self.data_page)
			for item in page_list:
				if item in self.dict:
					self.dict[item] = self.dict[item] + 1
				else:
					self.dict[item] = 1


	def loginFinal(self):
		request = urllib2.Request(self.final_url)
		request.add_header('User-Agent', self.user_agent)
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookies))
		response_page = opener.open(request)
		self.data_page = response_page.read().decode('utf-8')

	def calculate(self):
		for item in self.dict:
			print "%s = %d" % (item, self.dict[item])
	
if __name__ == '__main__':
	
	weiBo = WeiBo()
	weiBo.prelogin()
	weiBo.password()
	weiBo.login()
	weiBo.loginWeiBo()
	weiBo.module_test()
	weiBo.calculate()
