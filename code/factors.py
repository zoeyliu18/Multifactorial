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

#	total_c = total(wc_dict)

	lf = 1
	length = 0

	for w in toks:
		if w not in punctuation:
			length += 1
		
			if w in wc_dict:
				p = wc_dict[w] 
				if p != '0.0':
					lf = lf * float(p)
				else:
					lf = lf * (1 / (10 ** 10))

			if w not in wc_dict:
				p = 1 / (1 / (10 ** 10))
				lf = lf * p

#	lf = lf ** (-1 / length)

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
	parser.add_argument('--language', type = str, help = 'language being computed')
	parser.add_argument('--size', action='store_true', help = 'whether contextual predictability exists')


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
	PP1 = pp_data['PP1_simple']
	PP2 = pp_data['PP2_simple']
	PP1_len = pp_data['PP1_len']
	PP2_len = pp_data['PP2_len']
	PP1_Pronom = pp_data['PP1_Pronom']
	PP2_Pronom = pp_data['PP2_Pronom']
	position = pp_data['Position']

	#### Calculating semantic closenes ####

	embeddings = {}

	with io.open(path + language + '_em', encoding = 'utf-8') as f:
		for line in f:
			toks = line.split()
			embeddings[toks[0]] = [float(x) for x in toks[1 : ]]

	PP1_SC = []
	PP2_SC = []

	for i in range(len(verbs)):
		v = verbs[i]
		adp1 = Adp1[i]
		adp2 = Adp2[i]
		np1 = NP1[i]
		np2 = NP2[i]

		v_em = 'NONE'
		if v in embeddings:
			v_em = embeddings[v]

		adp1_em = 'NONE'
		if adp1 in embeddings:
			adp1_em = embeddings[adp1]

		np1_em = 'NONE'
		if np1 in embeddings:
			np1_em = embeddings[np1]

		adp2_em = 'NONE'
		if adp2 in embeddings:
			adp2_em = embeddings[adp2]

		np2_em = 'NONE'
		if np2 in embeddings:
			np2_em = embeddings[np2]

		pp1_sc = 'NONE'
		if v_em != 'NONE' and np1_em != 'NONE' and adp1_em != 'NONE':
			pp1_em = [(x + y) / 2 for x, y in zip(np1_em, adp1_em)]
			pp1_sc = cosine_similarity([v_em], [pp1_em])[0][0]

		if v_em != 'NONE' and np1_em != 'NONE' and adp1_em == 'NONE':
			pp1_sc = cosine_similarity([v_em], [np1_em])[0][0]

		if v_em != 'NONE' and np1_em == 'NONE' and adp1_em != 'NONE':
			pp1_sc = cosine_similarity([v_em], [adp1_em])[0][0]
		
		pp2_sc = 'NONE'
		if v_em != 'NONE' and np2_em != 'NONE' and adp2_em != 'NONE':
			pp2_em = [(x + y) / 2 for x, y in zip(np2_em, adp2_em)]
			pp2_sc = cosine_similarity([v_em], [pp2_em])[0][0]

		if v_em != 'NONE' and np2_em != 'NONE' and adp2_em == 'NONE':
			pp2_sc = cosine_similarity([v_em], [np2_em])[0][0]

		if v_em != 'NONE' and np2_em == 'NONE' and adp2_em != 'NONE':
			pp2_sc = cosine_similarity([v_em], [adp2_em])[0][0]

		PP1_SC.append(pp1_sc)
		PP2_SC.append(pp2_sc)

	print(len(PP1_SC))
	print(len(PP2_SC))

	print(PP1_SC)


	#### Calculating lexical frequency ####

	wc = {}
	with io.open(path + language + '_wc', encoding = 'utf-8') as f:
		for line in f:
			toks = line.split()
			if toks[0] not in punctuation:
				wc[toks[0]] = toks[1]

	PP1_LF = []
	PP2_LF = []

	for i in range(len(verbs)):
		pp1_lf = lexical_frequency(PP1[i], wc)
		pp2_lf = lexical_frequency(PP2[i], wc)

		PP1_LF.append(pp1_lf)
		PP2_LF.append(pp2_lf)


	#### Calculating PMI ####

#	joint_c = {}
#	with io.open(path + language + '_jc', encoding = 'utf-8') as f:
#		for line in f:
#			toks = line.split()
#			if toks[1] not in punctuation and toks[2] not in punctuation:
#				joint_c[toks[1] + ' ' + toks[2]] = int(toks[0])

#	PP1_PMI = []
#	PP2_PMI = []

#	for i in range(len(verbs)):
#		pp1_pmi = pmi(NP1[i], verbs[i], joint_c, wc) 
#		pp2_pmi = pmi(NP2[i], verbs[i], joint_c, wc)


	#### Getting predictability ####

	if args.size:
		PP1_simple_Pred = []
		PP2_simple_Pred = []

		PP1_Pred = []
		PP2_Pred = []

		with io.open(path + language + '_pp1_pred', encoding = 'utf-8') as f:
			for line in f:
				toks = line.split()
				PP1_simple_Pred.append(float(toks[0]))
				PP1_Pred.append(float(toks[1]))

		with io.open(path + language + '_pp2_pred', encoding = 'utf-8') as f:
			for line in f:
				toks = line.split()
				PP2_simple_Pred.append(float(toks[0]))
				PP2_Pred.append(float(toks[1]))


	#### Generating data set for regression ####

#	new_data = pp_data.copy()

#	new_data['PP1_SC'] = PP1_SC
#	new_data['PP2_SC'] = PP2_SC
#	new_data['PP1_PMI'] = PP1_PMI
#	new_data['PP2_PMI'] = PP2_PMI
#	new_data['PP1_simple_Pred'] = PP1_simple_Pred
#	new_data['PP2_simple_Pred'] = PP2_simple_Pred
#	new_data['PP1_Pred'] = PP1_Pred
#	new_data['PP2_Pred'] = PP2_Pred

#	print('Generating new PP data')

#	outfile = io.open(path + language + '_regression.csv', 'w', encoding = 'utf-8')
#	outfile.write(new_data.to_csv(index = False, encoding = 'utf-8'))

	pre_features = []
	post_features = []
	a=0

	for i in range(len(verbs)):
		print(PP1_SC[i] - PP2_SC[i])
	for i in range(len(verbs)):
		feature = []

		if position[i] == 'Postverbal':
			len_diff = int(PP2_len[i]) - int(PP1_len[i])
			len_c = ''
			if len_diff > 0:
				len_c = 1
			if len_diff < 0:
				len_c = -1
			if len_diff == 0:
				len_c = 0
			feature.append(len_diff)
			feature.append(len_c)

		#	feature.append(PP1_PMI[i] - PP2_PMI[i])

			sc_diff = ''
			try:
				sc_diff = PP1_SC[i] - PP2_SC[i]
				a += 1
				print(a)
			except:
				sc_diff = 'NONE'
			
			sc_c = ''
			try:
				if sc_diff > 0:
					sc_c = 1
				if sc_diff < 0:
					sc_c = -1
				if sc_diff == 0:
					sc_c = 0
			except:
				sc_c = 'NONE'

			feature.append(sc_diff)
			feature.append(sc_c)

		else:
			len_diff = int(PP1_len[i]) - int(PP2_len[i])
			len_c = ''
			if len_diff > 0:
				len_c = 1
			if len_diff < 0:
				len_c = -1
			if len_diff == 0:
				len_c = 0
			feature.append(len_diff)
			feature.append(len_c)

		#	feature.append(PP2_PMI[i] - PP1_PMI[i])

			sc_diff = ''
			try:
				sc_diff = PP2_SC[i] - PP1_SC[i]
				a+=1
				print(a)
			except:
				sc_diff = 'NONE'
			
			sc_c = ''
			try:
				if sc_diff > 0:
					sc_c = 1
				if sc_diff < 0:
					sc_c = -1
				if sc_diff == 0:
					sc_c = 0
			except:
				sc_c = 'NONE'
				
			feature.append(sc_diff)
			feature.append(sc_c)

	#	lf_diff = PP1_LF[i] - PP2_LF[i]
		lf_diff = PP2_LF[i] - PP1_LF[i]  ## forgot to change this earlier; so in analysis.R, multiply coefficient of lexical frequency by (-1)
		lf_c = ''
		if lf_diff > 0:
			lf_c = 1
		if lf_diff < 0:
			lf_c = -1
		if lf_diff == 0:
			lf_c = 0
		feature.append(lf_diff)
		feature.append(lf_c)
		
		pred_diff = ''
		pred_c = ''
		if args.size:
			pred_diff = PP1_simple_Pred[i] ** (-1 / len(PP1[i].split())) - PP2_simple_Pred[i] ** (-1 / len(PP2[i].split()))
		#	pred_diff = PP2_simple_Pred[i] - PP1_simple_Pred[i]		
			if pred_diff > 0:
				pred_c = 1
			if pred_diff < 0:
				pred_c = -1
			if pred_diff == 0:
				pred_c = 0
		feature.append(pred_diff)
		feature.append(pred_c)

		if PP1_Pronom[i] in ['PRON'] and PP2_Pronom[i] not in ['PRON']:
			feature.append(1)
		if PP1_Pronom[i] in ['PRON'] and PP2_Pronom[i] in ['PRON']:
			feature.append(0)
		if PP1_Pronom[i] not in ['PRON'] and PP2_Pronom[i] not in ['PRON']:
			feature.append(0)
		if PP1_Pronom[i] not in ['PRON'] and PP2_Pronom[i] in ['PRON']:
			feature.append(-1)


		feature.append(verbs[i])
		feature.append(position[i])

		if position[i] == 'Preverbal':
			pre_features.append(feature)

		if position[i] == 'Postverbal':
			post_features.append(feature)

	print('Generating regression data')

	pre_split = round(len(pre_features) / 2) + 1
	post_split = round(len(post_features) / 2) + 1

	c = 0

	
	with io.open(path + language + '_regression.csv', 'w', newline = '', encoding = 'utf-8') as f:
		writer = csv.writer(f)
		writer.writerow(['Order', 'Len', 'Len_c', 'Semantic_closeness', 'Semantic_closeness_c', 'Lexical_frequency', 'Lexical_frequency_c', 'Predictability', 'Predictability_c', 'Pronominality', 'Verb', 'Position'])
	
			#### Preverbal data ####

		if len(pre_features) != 0:

			for i in range(pre_split):
				if pre_features[i][2] != 'NONE':
					c += 1

				writer.writerow([1, pre_features[i][0], pre_features[i][1], pre_features[i][2], pre_features[i][3], pre_features[i][4], pre_features[i][5], pre_features[i][6], pre_features[i][7], pre_features[i][8], pre_features[i][9], pre_features[i][10]])
		
			for i in range(pre_split, len(pre_features)):
				if pre_features[i][2] != 'NONE':
					c += 1

				writer.writerow([0, -1 * pre_features[i][0], -1 * pre_features[i][1], -1 * pre_features[i][2], -1 * pre_features[i][3], -1 * pre_features[i][4], -1 * pre_features[i][5], -1 * pre_features[i][6], -1 * pre_features[i][7], -1 * pre_features[i][8], pre_features[i][9], pre_features[i][10]])

		#### Postverbal data ####

		if len(post_features) != 0:

			for i in range(post_split):
				if post_features[i][2] != 'NONE':
					c += 1

					writer.writerow([1, post_features[i][0], post_features[i][1], post_features[i][2], post_features[i][3], post_features[i][4], post_features[i][5], post_features[i][6], post_features[i][7], post_features[i][8], post_features[i][9], post_features[i][10]])
		
			for i in range(post_split, len(post_features)):
				if post_features[i][2] != 'NONE':
					c += 1

					writer.writerow([0, -1 * post_features[i][0], -1 * post_features[i][1], -1 * post_features[i][2], -1 * post_features[i][3], -1 * post_features[i][4], -1 * post_features[i][5], -1 * post_features[i][6], -1 * post_features[i][7], -1 * post_features[i][8], post_features[i][9], post_features[i][10]])

	
	print(len(verbs))
	print(c)

