# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
'''
	libmabinogi/mabi/mabidb/common/mabil10n.py

	Loads and formats mabinogi l10n texts.
	See mabipack:local/<type>/<name>.<lang>.txt
'''

import re
try:
	import korean
	_USE_KOREAN = True
except ImportError:
	_USE_KOREAN = False

g_current_locale = 'korea'
def mabidata_open(path, mode='rt'):
	# strip 'data/'
	path = path[5:]
	try:
		return open(path, mode)
	except IOError:
		return None


g_localtextdbs = {}

_re_convert_formatstr = re.compile('{(\\d+)}{(은|는|이|가|을|를|과|와|아|야|이|으)}')
def _convert_formatstr(s):
	''' Converts mabinogi's format string to python style.
		TODO: handle mabi's {1:param}, {1:스탯} style formats.
	'''
	if _USE_KOREAN:
		return _re_convert_formatstr.sub('{\\1:\\2}', s)
	else:
		return _re_convert_formatstr.sub('{\\1}\\2', s)

def mabi_formattext(fmt, *args):
	if _USE_KOREAN:
		args = [korean.Noun(arg.decode('utf8')) if isinstance(arg, str) else korean.NumberWord(arg) for arg in args]
		return fmt.decode('utf8').format(*args).encode('utf8')
	else:
		return fmt.format(*args)

def _load_localtextdb(name):
	path = 'data/local/%s.%s.txt' % (name, g_current_locale)
	fh = mabidata_open(path, 'rt')
	if not fh:
		return None

	data = fh.read().decode('utf-16-le').replace(u'\r', u'')
	if data[:1] == u'\ufeff':
		# strip BOM
		data = data[1:]
	lines = data.encode('utf-8').split('\n')

	res = {}
	for line in lines:
		line = line.strip()
		if line == '':
			continue
		ss = line.split('\t', 1)
		subid = ss[0]
		try:
			text = ss[1]
		except IndexError:
			text = ''
		# Convert mabi's format string to python style.
		text = _convert_formatstr(text.decode('string_escape'))
		res[subid] = text
	return res

def load_localtext(textid):
	# textid samples:
	# > xml.itemdb.2000
	# > world.uladh_dunbarton.field_dunbarton_00.prop.note3
	if textid.find('/') >= 0 or textid.find('..') >= 0:
		print('mabidb.common.mabil10n: ERROR: invalid textid: "%s"' % textid)
		return textid

	pathelems = textid.split('.')
	if pathelems[0] == 'world':
		# textid: 'world.uladh_dunbarton.field_dunbarton_00.prop.note3'
		name = pathelems[0]
		subid = '.'.join(pathelems[1:])
	elif pathelems[0] == 'code':
		# textid: 'code.standard.Mabinogi_Talent.1'
		name = pathelems[0] + '/' + pathelems[1]
		subid = '.'.join(pathelems[2:])
	else: # 'xml'
		# textid: 'xml.itemdb.2000'
		name = '/'.join(pathelems[:-1])
		subid = pathelems[-1]

	try:
		db = g_localtextdbs[name]
	except KeyError:
		db = _load_localtextdb(name)
		if db:
			g_localtextdbs[name] = db
		else:
			print('mabidb.common.mabil10n: ERROR: no such text for textid: %s' % textid)
			return textid

	try:
		return db[subid]
	except KeyError:
		return textid

def mabi_gettext(s):
	try:
		if s[0:4] == '_LT[' and s[-1] == ']':
			textid = s[4:-1]
			return load_localtext(textid)
	except IndexError:
		pass
	return s


