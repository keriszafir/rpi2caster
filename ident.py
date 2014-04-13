#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import hashlib
import sys
import fileinput

# ścieżka, w której szukać duplikatów

SEARCH_DIR = '.'

# rozmiar pojedynczego odczytu

BUFFER_SIZE = 4096

# słownik z sumami kontrolnymi wszystkich plików

# suma -> [lista, ścieżek, do, plików, z, taką, sumą]

DIGEST_DICT = {}

def gather_digests(search_dir, dig_dict, buf_size):

    for file_name in os.listdir(search_dir):
        full_path = os.path.realpath(os.path.join(search_dir, file_name))
	try:
		if os.path.isdir(full_path):
		# szukamy też w podkatalogach
			gather_digests(full_path, dig_dict, buf_size)
		elif not os.path.isfile(full_path):
			continue
		current_hash = hashlib.sha1()
		with open(full_path) as current_file:
			data = current_file.read(buf_size)
			while data:
				current_hash.update(data)
				data = current_file.read(buf_size)
	except (IOError, OSError):
			continue
    digest = current_hash.hexdigest()
    dig_dict.setdefault(digest, []).append(full_path)

gather_digests(SEARCH_DIR, DIGEST_DICT, BUFFER_SIZE)

# ze słownika z sumami kontrolnymi wybieramy
# te pozycje, które mają wiele wpisów

for digest, paths in DIGEST_DICT.iteritems():
    count = len(paths)
    if count > 1:
        print count, 'identical files:', paths
