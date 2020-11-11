### This script extracts head-dependent pairs from UD treebanks ###

#usr/bin/env python3

HAPPY = True

import glob, os, io, argparse, csv

### Reading CoNLL formatted file sentence by sentence ###

def conll_read_sentence(file_handle):

	sent = []

	for line in file_handle:
		line = line.strip('\n')
	
		if line.startswith('#') is False :
			toks = line.split("\t")			
		
			if len(toks) == 1:
				return sent 
			else:
				if toks[0].isdigit() == True:
					sent.append(toks)

	return None


def Expelliarmus(file_handle, directory, language):

	pairs = []

	with io.open(directory + '/' + file_handle, encoding = 'utf-8') as f:
		sent = conll_read_sentence(f)

		while sent is not None:
			for tok in sent:
				if tok[7] != 'punct':
					d_tok = tok[2]
					h_idx = tok[6]

					if h_idx != '0':
						h = sent[int(h_idx) - 1]

						if h[7] != 'punct':
							h_tok = h[2]

							pairs.append(str(h_tok + ' ' + str(d_tok)))

			sent = conll_read_sentence(f)

	return pairs

if __name__ == '__main__':

	parser = argparse.ArgumentParser()
	parser.add_argument('--input', type = str, help = 'input path to UD directory')
	parser.add_argument('--output', type = str, help = 'output path')
	parser.add_argument('--language', type = str, help = 'language being computed')


	args = parser.parse_args()

	path = args.input
	os.chdir(path)


	if HAPPY:
	
		language = args.language

		pairs_out = io.open(args.output + language + '_pairs_all.txt', 'w', newline = '', encoding = 'utf-8')

		for file in os.listdir(path):
			if file.endswith('.conllu'):

				all_pairs = Expelliarmus(file, path, language)

				for tok in all_pairs:
					pairs_out.write(tok + '\n')