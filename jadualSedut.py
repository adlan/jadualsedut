#!/usr/bin/env python
# Bagi mereka yang malas memasuki iCress.
# Penggunaan skrip ini adalah atas tanggungan anda sendiri.
# Adlan, adlanism {at} gmail {dot} com
#
# Changelog
# + Jumaat, 20 Jun
#	- Tambah opsyen kod kumpulan
#	- Tambah gui option, bagi pengguna gnome
# + Rabu, 18 Jun
#	- Perubahan kecil, menangkap exception yang tertinggal
# + Selasa, 30 Dec 2008
#	- Terlupa nak cek ade ke tak BeautifulSoup, jadi telah tambah kod itu
#
# ------------------------------------------------------------------------
#
#  This program is free software. It comes without any warranty, to
#  the extent permitted by applicable law. You can redistribute it
#  and/or modify it under the terms of the Do What The Fuck You Want
#  To Public License, Version 2, as published by Sam Hocevar. See
#  http://sam.zoy.org/wtfpl/COPYING for more details.
#
# ------------------------------------------------------------------------

import re
import urllib2
import sys
import getopt
import string
import os.path

try:
	from BeautifulSoup import BeautifulSoup
except:
	print "Maap, BeautifulSoup tiada. Sila install atau download sebentar di http://crummy.com/software/BeautifulSoup"
	exit(1)

class CourseClass:
	def __init__(self, group, timeStart, timeEnd, day, room, course):
		self.group = group
		self.timeStart = timeStart
		self.timeEnd = timeEnd
		self.day = day
		self.room = room
		self.course = course

	def view(self):
		return '[%s] %8s - %-8s %-10s %s' % (
				self.group, 
				self.timeStart, 
				self.timeEnd, 
				self.day, 
				self.room
			)

	def text(self):
		return '%s %s %s %s "%s"' % (
				self.group, 
				self.timeStart, 
				self.timeEnd, 
				self.day,
				self.room
			)

def listFaculty():
	sys.stdout.write(
		'AC - FAKULTI PERAKAUNAN\n'
		'AD - FAKULTI SENILUKIS DAN SENIREKA\n'
		'AM - FAKULTI SAINS PENTADBIRAN DAN PENGAJIAN POLISI\n'
		'AP - FAKULTI SENIBINA PERANCANGAN & UKUR\n'
		'AS - FAKULTI SAINS GUNAAN\n'
		'BM - FAKULTI PENGURUSAN PERNIAGAAN SHAH ALAM\n'
		'CS - FAKULTI TEKNOLOGI MAKLUMAT DAN SAINS KUANTITATIF\n'
		'CT - FAKULTI TEKNOLOGI KREATIF & ARTISTIK\n'
		'EC - FAKULTI KEJURUTERAAN AWAM\n'
		'ED - FAKULTI PENDIDIKAN, UiTM KAMPUS SEKSYEN 17, SHAH ALAM\n'
		'EE - FAKULTI KEJURUTERAAN ELEKTRIKAL\n'
		'EH - FAKULTI KEJURUTERAAN KIMIA\n'
		'EM - FAKULTI KEJURUTERAAN MEKANIKAL\n'
		'HM - FAKULTI PENGURUSAN HOTEL DAN PELANCONGAN\n'
		'HS - FAKULTI SAINS KESIHATAN\n'
		'IS - FAKULTI PENGURUSAN MAKLUMAT\n'
		'LW - FAKULTI UNDANG-UNDANG\n'
		'MC - FAKULTI KOMUNIKASI DAN PENGAJIAN MEDIA\n'
		'MU - FAKULTI MUZIK\n'
		'OM - FAKULTI PENGURUSAN DAN TEKNOLOGI PEJABAT\n'
		'PB - AKADEMI PENGAJIAN BAHASA - KAMPUS SHAH ALAM\n'
		'PH - FAKULTI FARMASI\n'
		'SR - FAKULTI SAINS SUKAN DAN REKREASI\n'
		'PI - PUSAT PEMIKIRAN DAN KEFAHAMAN ISLAM (CITU)\n'
		'AG - KAMPUS MELAKA\n'
		'AR - KAMPUS PERLIS\n'
		'BT - KAMPUS PULAU PINANG\n'
		'DU - KAMPUS TERENGGANU\n'
		'JK - KAMPUS PAHANG\n'
		'KK - KAMPUS SABAH\n'
		'KP - KAMPUS NEGERI SEMBILAN\n'
		'MA - KAMPUS KELANTAN\n'
		'SA - KAMPUS KOTA SAMARAHAN, SARAWAK\n'
		'SG - KAMPUS JOHOR\n'
		'SI - KAMPUS PERAK\n'
		'SP - KAMPUS KEDAH\n'
	)

# gui ini memerlukan zenity
def gui(data, course):
	string = ' \\\n'.join([i.text() for i in data]) 
	zenity = 'zenity --list --width=500 --height=250 --title="Jadual" --text="' + course + '" --column="Kumpulan" --column="Mula" --column="Tamat" --column="Hari" --column="Bilik" ' + string
	timeTable = os.system(zenity)

def usage():
	sys.stderr.write(
		'Usage:\n'
		'   jadualSedut.py -f FACULTYCODE -c COURSECODE [-o FILENAME]\n'
		'Optons:\n'
		'   -f, --faculty <faculty/campus code> Faculty code to fetch from.\n'
		'   -c, --course <course code>          Time table for course to fetch.\n'
		'   -g, --group <group code>            Filter by group code.\n'
		'   -o, --output <filename>             Output to file.\n'
		'   -l, --list                          List all campus/faculty code.\n'
		'   -h, --help                          Print this message.\n'
	)

# nyum2, segale maklumat akan diratah oleh fungsi ini
# dan diberakkan dalam bentuk daftar yang mengandungi objek CourseClass
def process(faculty, course, group=None):
	url = 'http://icress.uitm.edu.my/jadual/' + faculty + '/' + course + '.html'
	headers = {
		'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)'
	}
	request = urllib2.Request(url, None, headers)
	
	list = []

	try:
		document = urllib2.urlopen(request)
	except urllib2.HTTPError:
		return list

	soup = BeautifulSoup(document)
	removeSpaceTime = re.compile('\s+')
	row = soup('tr')
	for i in row[1:]:
		coursegroup = i.contents[0].contents[0]
		if group != None and coursegroup != group:
			continue
		timeStart = removeSpaceTime.sub('', i.contents[1].contents[0])  
		timeEnd = removeSpaceTime.sub('', i.contents[2].contents[0])
		day = i.contents[3].contents[0].strip()
		try:
			room = removeSpaceTime.sub(' ', i.contents[6].contents[0])
		except IndexError:
			room = "Not yet determined"
		list.append(CourseClass(coursegroup, timeStart, timeEnd, day, room, course))

	return list

# write to file
def save(filename, data, course):
	append = os.path.exists(filename)

	if append:
		file = open(filename, 'a')
	else:
		file = open(filename, 'w')
	
	file.write(course + '\n')
	for line in data:
		file.write(line.view())
		file.write('\n')

def main():
	if len(sys.argv) == 1:
		sys.argv.append('-h')
	try:
		opts, args = getopt.getopt(sys.argv[1:], 'f:c:o:g:ulh', 
				['faculty=', 'course=', 'group=', 'output=', 'gui', 'list', 'help'])
	except getopt.GetoptError, err:
		print 'Error: %s' % str(err)
		print 'For options: jadualSedut.py --help'
		return 1

	saveToFile = False
	guiMode = False
	faculty = None
	course = None
	group = None

	for opt, arg in opts:
		if opt in ('-f', '--faculty'):
			faculty = string.upper(arg)
		elif opt in ('-c', '--course'):
			course = string.upper(arg)
		elif opt in ('-o', '--output'):
			filename = arg
			saveToFile = True
		elif opt in ('-g', '--group'):
			group = string.upper(arg)
		elif opt in('-u', '--gui'):
			guiMode = True
		elif opt in ('-l', '--list'):
			listFaculty()
			return 0
		elif opt in ('-h', '--help'):
			usage()
			return 0
	
	if faculty == None or course == None:
		usage()
		return 1
	
	item = process(faculty, course, group)
	
	if item:
		if guiMode:
			gui(item, course)
		else:
			print course
			for i in item:
				print i.view()
		if saveToFile:
			save(filename, item, course)
	else:
		print "Uh!, something wrong, please check your faculty/campus code or course code."
		return 1

if __name__ == '__main__':
	sys.exit(main() or 0)
