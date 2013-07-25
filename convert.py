#!/usr/bin/python
# -*- coding: utf-8 -*-

''' Converts all '*.xml' files to utf-8 and resolves l10n text references.
'''

import os
import sys
import re

from mabil10n import mabi_gettext


def escape(s):
	return s.replace('\r', '').replace('\\', '\\\\').replace('"', '\\"').replace('\'', '\\\'').replace('\n', '\\n')

def makeit_readable(path):
	try:
		data = open(path).read().decode('utf-16-le').encode('utf-8')
	except UnicodeDecodeError as e:
		print e
		return
	data = re.sub('_LT\\[[^\\]]+\\]', lambda m: escape(mabi_gettext(m.group(0))), data)
	with open(path + '.txt', 'w') as f:
		f.write(data)

def main():
	if len(sys.argv) < 2:
		print 'Usage: %s <unpacked_dir>' % sys.argv[0]
		return
	os.chdir(sys.argv[1])
	for dirpath, dirs, files in os.walk('.'):
		for fname in files:
			if fname.endswith('.xml'):
				path = '%s/%s' % (dirpath, fname)
				print path
				makeit_readable(path)

if __name__ == '__main__':
	main()


