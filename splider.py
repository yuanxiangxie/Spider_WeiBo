#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2
from bs4 import BeautifulSoup
import cookielib
#import MySQLdb
#import sys
#import csv
#import codecs

#reload(sys)
#sys.setdefaultencoding('utf-8')

class Spider:

    url = 'https://movie.douban.com/top250'
    url_top250_head = 'https://movie.douban.com/top250?start='
    url_top250_tail = '&filter='

    def __init__(self):
        self.cookies = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookies))

    def __getWebPage(self, url):
        self.request = urllib2.Request(url)
        response = self.opener.open(self.request)
        return response

    def __getMovieInfo(self, url):
        response = self.__getWebPage(url)
        soup = BeautifulSoup(response, 'html.parser')
        for movie in soup.find_all('div', class_='item'):
            info = []
            movie_name = movie.find_all('span', class_='title')[0].get_text()
            print movie_name
            info.append(movie_name)
            movie_introduce = movie.find_all('a')[0].get('href')
            print movie_introduce
            info.append(movie_introduce)
            movie_img = movie.find_all('img')[0].get('src')
            print movie_img
            info.append(movie_img)
            movie_star_list = movie.find_all('div', class_='star')[0]
            movie_star = movie_star_list.find_all('span', class_='rating_num')[0].get_text()
            print movie_star
            info.append(movie_star)
            movie_comment = movie_star_list.find_all('span', attrs={'property': 'v:best'})[0].find_next_sibling().get_text()
            print movie_comment
            info.append(movie_comment)

    def printContent(self):
        try:
            connect = MySQLdb.connect(host='127.0.0.1', user='root', passwd='root', port=3306)
            cur = connect.cursor()
            connect.select_db('DouBan')
            count = cur.execute('select * from Movie')
            print 'there are %s rows record' % count
            result = cur.fetchone()
            print result
            print 'ID: %s info %s' % result

            results = cur.fetchmany(5)
            for r in results:
                print r

            print '=='*10

            results = cur.fetchall()
            for r in results:
                print r[1]

            connect.commit()
            cur.close()
            connect.close()
        except MySQLdb.Error, e:
            print "MySQL error %d: %s" % (e.args[0], e.args[1])

    def insertMySQL(self):
        try:
            self.connect = MySQLdb.connect(host='127.0.0.1', user='root', passwd='root', db='DouBan', port = 3306, charset="utf8")
            self.cur = self.connect.cursor()
            self.cur.execute('create database if not exists DouBan')
            self.connect.select_db('DouBan')
            self.cur.execute('drop table if exists Movie')
            self.cur.execute('create table if not exists Movie(Movie_Name varchar(20), Movie_Introduce varchar(200), Movie_Img varchar(200), Movie_Star VARCHAR(20), Movie_Comment VARCHAR(20))')
            self.__getMovieInfo()
            self.connect.commit()
            self.cur.close()
            self.connect.close()

        except MySQLdb.Error, e:
            print 'MySQL error %d: %s' %(e.args[0], e.args[1])


    def writeCSV(self):
        csvfile = file('movie.csv', 'wb')
        writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        self.__getMovieInfo(writer)
        csvfile.close()

    def printAll(self):
        self.__getMovieInfo(Spider.url)
        for num in xrange(25, 250, 25):
            url = ''.join([Spider.url_top250_head, str(num)])
            self.__getMovieInfo(url)

if __name__ == '__main__':

    s = Spider()
    #s.insertMySQL()
    #s.printContent()
    #s.writeCSV()
    s.printAll()

