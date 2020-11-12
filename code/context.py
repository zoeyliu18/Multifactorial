import torch, argparse, io, os
import torch.nn as nn

import pandas as pd

from dictionary_corpus import Corpus
from utils import repackage_hidden, get_batch, batchify
from dictionary_corpus import Dictionary

import opencc

s2t = opencc.OpenCC('s2t.json')

torch.cuda.manual_seed(1)

parser = argparse.ArgumentParser()
parser.add_argument('--data', type=str, help='train/dev/test data file path')
parser.add_argument('--model', type=str, help='model path')
parser.add_argument('--pp', type=str, help='pp data path')
parser.add_argument('--language', type=str, help='language being computed')


args = parser.parse_args()

dictionary = Dictionary(args.data + args.language + '/')

ntokens = 50001
eval_batch_size = 1

with open(args.data + args.language + '/' + args.model,'rb') as f:
	model = torch.load(f)
	model.cuda()

def evaluate(data_source):
    # Turn on evaluation mode which disables dropout.
    model.eval()
    total_loss = 0
    hidden = model.init_hidden(eval_batch_size)
   
    with torch.no_grad():
        for i in range(0, data_source.size(0) - 1, 35):#args.bptt):
            data, targets = get_batch(data_source, i, 35, evaluation = True) #args.bptt, evaluation=True)
            output, hidden = model(data, hidden)
            output_flat = output.view(-1, ntokens)
            total_loss += len(data) * nn.CrossEntropyLoss()(output_flat, targets).data
            hidden = repackage_hidden(hidden)
    
    return total_loss.item() /len(data_source)


path = args.pp
os.chdir(path)

language = args.language

pp_data = pd.read_csv(path + language + '_pp.csv', encoding = 'utf-8')
Context_PP1 = pp_data['Context_PP1']
Context_PP2 = pp_data['Context_PP2']


PP1_PPL = []

for i in range(len(Context_PP1)):
	pp = Context_PP1[i]
	if args.language == 'Chinese':
		pp = s2t.convert(pp)

	token = 0
	idx = torch.LongTensor(len(pp))
	for word in pp:
		if word in dictionary.word2idx:
			idx[token] = dictionary.word2idx[word]
		else:
			idx[token] = dictionary.word2idx["<unk>"]
		token += 1
	pp_batch = batchify(idx, 1, True)            
	PP1_PPL.append(evaluate(pp_batch))

#args.cuda)


PP2_PPL = []

for i in range(len(Context_PP2)):
	pp = Context_PP2[i]
	if args.language == 'Chinese':
		pp = s2t.convert(pp)
		
	token = 0
	idx = torch.LongTensor(len(pp))
	for word in pp:
		if word in dictionary.word2idx:
			idx[token] = dictionary.word2idx[word]
		else:
			idx[token] = dictionary.word2idx["<unk>"]
		token += 1
	pp_batch = batchify(idx, 1, True)            
	PP2_PPL.append(evaluate(pp_batch))


with io.open(path + language + '_pp1_pred', 'w', encoding = 'utf-8') as f:
	for tok in PP1_PPL:
		f.write(str(tok) + '\n')

f.close()

with io.open(path + language + '_pp2_pred', 'w', encoding = 'utf-8') as f:
	for tok in PP2_PPL:
		f.write(str(tok) + '\n')

f.close()
