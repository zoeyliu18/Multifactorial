from wordfreq import word_frequency
import argparse, os, io
#import opencc

#s2t = opencc.OpenCC('s2t.json')

if __name__ == '__main__':

	parser = argparse.ArgumentParser()
	parser.add_argument('--path', type = str, help = 'path to Language_words.txt file')
	parser.add_argument('--language', type = str, help = 'language being computed')
	parser.add_argument('--code', type = str, help = 'code for language (e.g. zh for Chinese')


	args = parser.parse_args()

	path = args.path
	os.chdir(path)

	language = args.language

	words = []
	with io.open(path + language + '_words.txt', encoding = 'utf-8') as f:
		for line in f:
			toks = line.split()[0]
			words.append(toks)

	c = 0

	word_freq = []
	
	for w in words:
		
		try:
			word_freq.append(word_frequency(w, args.code))
	
		except:
			word_freq.append(1 / (10 ** 10))
			c += 1 
			print(w)				

	print(c)

	outfile = io.open(path + language + '_wc', 'w', encoding = 'utf-8') 
	for i in range(len(words)):
		outfile.write(words[i] + ' ' + str(word_freq[i]) + '\n')