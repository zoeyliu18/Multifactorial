### This script calculates semantic closeness ###

#usr/bin/env python3

HAPPY = True

import glob, os, io, argparse, csv, pandas, string, math
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

punctuation = list(string.punctuation)


def total(wc_dict):

	total_c = 0

	for w, c in wc_dict.items():
		total_c += int(c)

	return total_c


def lexical_frequency(phrase, wc_dict):

	toks = phrase.split()

	total_c = total(wc_dict)

	lf = 1
	length = 0

	for w in toks:
		if w not in punctuation:
			length += 1
		
			if w in wc_dict:
				p = wc_dict[w] / total_c
				lf = lf * p

			if w not in wc_dict:
				p = 1 / total_c
				lf = lf * p

	lf = lf ** (-1 / length)

	return lf


def pmi(np, v, jc_dict, wc_dict):

	wc_total = total(wc_dict)

	total_c = 0
	for p, c in jc_dict.items():
		total_c += int(c)

	v_p = 1 / wc_total
	if v in wc_dict:
		v_p = wc_dict[v] / wc_total

	np_p = 1 / wc_total
	if np in wc_dict:
		np_p = wc_dict[np] / wc_total

	pmi_v = math.log2((jc_dict[v + ' ' + np] / total_c) / (v_p * np_p))

	return pmi_v



if __name__ == '__main__':

	parser = argparse.ArgumentParser()
	parser.add_argument('--pp', type = str, help = 'input path to initial *_pp.csv data')
	parser.add_argument('--em', type = str, help = 'input path to fastText embeddings')
	parser.add_argument('--new', type = str, help = 'output path to new pp data')
	parser.add_argument('--language', type = str, help = 'language being computed')


	args = parser.parse_args()

	path = args.pp
	os.chdir(path)

	language = args.language

	pp_data = pd.read_csv(path + language + '_pp.csv', encoding = 'utf-8')

	verbs = pp_data['Verb']
	Adp1 = pp_data['Adp1']
	Adp2 = pp_data['Adp2']
	NP1 = pp_data['NP1']
	NP2 = pp_data['NP2']
	PP1 = pp_data['PP1']
	PP2 = pp_data['PP2']
	PP1_len = pp_data['PP1_len']
	PP2_len = pp_data['PP2_len']
	PP1_Pronom = pp_data['PP1_Pronom']
	PP2_Pronom = pp_data['PP2_Pronom']
	position = pp_data['Position']

	#### Calculating semantic closenes ####

	embeddings = {}

	with io.open(args.em, encoding = 'utf-8') as f:
		for line in f:
			toks = line.split()
			embeddings[toks[0]] = [float(x) for x in toks[1 : ]]

	PP1_SC = []
	PP2_SC = []

	for i in range(len(verbs)):
		v = verbs[i]
		np1 = NP1[i]
		np2 = NP2[i]

		v_em = 'NONE'
		if v in embeddings:
			v_em = embeddings[v]

		np1_em = 'NONE'
		if np1 in embeddings:
			np1_em = embeddings[np1]

		np2_em = 'NONE'
		if np2 in embeddings:
			np2_em = embeddings[np2]

		pp1_sc = 'NONE'
		if v_em != 'NONE' and np1_em != 'NONE':
			pp1_sc = cosine_similarity([v_em], [np1_em])[0][0]
		
		pp2_sc = 'NONE'
		if v_em != 'NONE' and np2_em != 'NONE':
			pp2_sc = cosine_similarity([v_em], [np2_em])[0][0]

		PP1_SC.append(pp1_sc)
		PP2_SC.append(pp2_sc)


	#### Calculating lexical frequency ####

	wc = {}
	with io.open(path + language + '_wc', encoding = 'utf-8') as f:
		for line in f:
			toks = line.split()
			if toks[1] not in punctuation:
				wc[toks[1]] == int(toks[0])

	PP1_LF = []
	PP2_LF = []

	for i in range(len(verbs)):
		pp1_lf = lexical_frequency(PP1[i], wc)
		pp2_lf = lexical_frequency(PP2[i], wc)


	#### Calculating PMI ####

	joint_c = {}
	with io.open(path + language + '_jc', encoding = 'utf-8') as f:
		for line in f:
			toks = line.split()
			if toks[1] not in punctuation and toks[2] not in punctuation:
				joint_c[toks[1] + ' ' + toks[2]] = int(toks[0])

	PP1_PMI = []
	PP2_PMI = []

	for i in range(len(verbs)):
		pp1_pmi = pmi(NP1[i], verbs[i], joint_c, wc) 
		pp2_pmi = pmi(NP2[i], verbs[i], joint_c, wc)


	#### Getting predictability ####

	PP1_Pred = []
	PP2_Pred = []

	with io.open(path + language + '_pp1_pred', encoding = 'utf-8') as f:
		for line in f:
			pp1_pred = float(line)
			PP1_Pred.append(pp1_pred)

	with io.open(path + language + '_pp2_pred', encoding = 'utf-8') as f:
		for line in f:
			pp2_pred = float(line)
			PP2_Pred.append(pp2_pred)



	#### Generating data set for regression ####

	new_data = pp_data.copy()

	new_data['PP1_SC'] = PP1_SC
	new_data['PP2_SC'] = PP2_SC
	new_data['PP1_PMI'] = PP1_PMI
	new_data['PP2_PMI'] = PP2_PMI
	new_data['PP1_Pred'] = PP1_Pred
	new_data['PP2_Pred'] = PP2_Pred


	print('Generating new PP data')

	outfile = io.open(args.new + language + '_pp.csv', 'w', encoding = 'utf-8')
	outfile.write(new_data.to_csv(index = False, encoding = 'utf-8'))

	features = []
	
	for i in range(len(verbs)):
		feature = []

		if position == 'Postverbal':
			feature.append(int(PP2_len[i]) - int(PP1_len[i]))
			feature.append(PP1_PMI[i] - PP2_PMI[i])
			feature.append(PP1_SC[i] - PP2_SC[i])

		else:
			feature.append(int(PP1_len[i]) - int(PP2_len[i]))
			feature.append(PP2_PMI[i] - PP1_PMI[i])
			feature.append(PP2_SC[i] - PP1_SC[i])

		feature.append(PP2_LF[i] - PP1_LF[i])
		feature.append(PP2_Pred[i] - PP1_Pred[i])

		if PP1_Pronom[i] in ['PRON'] and PP2_Pronom[i] not in ['PRON']:
			feature.append(1)
		if PP1_Pronom[i] in ['PRON'] and PP2_Pronom[i] in ['PRON']:
			feature.append(0)
		if PP1_Pronom[i] not in ['PRON'] and PP2_Pronom[i] not in ['PRON']:
			feature.append(0)
		if PP1_Pronom[i] not in ['PRON'] and PP2_Pronom[i] in ['PRON']:
			feature.append(-1)


		feature.append(verbs[i])
		features.append(feature)

		print('Generating regression data')

		split = round(len(verbs) / 2) + 1

		with io.open(args.new + language + '_regression.csv', 'w', newline = '', encoding = 'utf-8') as f:
			writer = csv.writer(f)
			writer.writerow(['Order', 'Len', 'PMI', 'Semantic_closeness', 'Lexical_frequency', 'Predictability', 'Pronominality', 'Verb'])
			for i in range(split):
				writer.writerow([1, features[i][0], features[i][1], features[i][2], features[i][3], features[i][4], features[i][5], features[i][6]])
			for i in range(split, len(pp1_len)):
				writer.writerow([0, -1 * features[i][0], -1 * features[i][1], -1 * features[i][2], -1 * features[i][3], -1 * features[i][4], -1 * features[i][5], features[i][6]])

	


