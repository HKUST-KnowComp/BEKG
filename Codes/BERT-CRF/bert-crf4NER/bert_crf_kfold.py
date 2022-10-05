#!/usr/bin/env python
# coding: utf-8
__author__ = 'Dhanachandra N.'

#from __future__ import unicode_literals, print_function, division
from io import open, StringIO
import unicodedata
import string
import re
import random
import pickle 
import torch
import torch.nn as nn
from torch import optim
import torch.nn.functional as F
from torch.utils import data 
from torch.utils.data import ConcatDataset
from sklearn.model_selection import KFold
from transformers import BertTokenizer
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
torch.cuda.set_device(2)
import numpy as np
import os
from transformers import BertPreTrainedModel, BertModel
from transformers import AutoTokenizer, AutoModel
#from pytorch_pretrained_bert import BertModel
from torchcrf import CRF
import timeit
import subprocess
from tqdm import tqdm, trange
from transformers import AdamW, get_linear_schedule_with_warmup
from matplotlib import pyplot as plt 
import datetime
from config import Config as config
import spacy
tokenizer = spacy.load("en_core_web_sm", disable=["tagger", "parser", "ner"])
log_soft = F.log_softmax
import sys
from optparse import OptionParser
import pdb
import nltk
import time
#to initialize the network weight with fix seed. 
def seed_torch(seed=12345):
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed) # if you are using multi-GPU.
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
seed_torch()

from collections import OrderedDict
# read the corpus and return them into list of sentences of list of tokens
def corpus_reader(path, delim='\t', word_idx=0, label_idx=-1):
    tokens, labels = [], []
    tmp_tok, tmp_lab = [], []
    label_set = []
    with open(path, 'r') as reader:
        for line in reader:
            line = line.strip()
            cols = line.split(delim)
            if len(cols) < 2:
                if len(tmp_tok) > 0:
                    #pdb.set_trace()
                    tokens.append(tmp_tok); labels.append(tmp_lab)
                tmp_tok = []
                tmp_lab = []
            else:
                tmp_tok.append(cols[word_idx])
                tmp_lab.append(cols[label_idx])
                label_set.append(cols[label_idx])
    '''                       
    t_map = {}
    count = 0
    write_count = 0
    savepath = '/data/pldu/corpus/eng_test_building.txt'
    fw = open(savepath, 'w')
    for idx, (token, label) in enumerate(zip(tokens, labels)):
        #pdb.set_trace()
        sent = ' '.join(token)
        if sent in t_map.keys():
            count += 1
            continue
            #tokens.pop(idx)
            #labels.pop(idx)
        else:
            t_map[sent] = True
            for t, l in zip(token, label):
                line = [t, l]
                data_line = StringIO(' '.join(l for l in line) + '\n')
                fw.write(''.join(data_line))
            write_count += 1
            fw.write('\n')
    print(count)
    print(write_count)
    fw.close()
    pdb.set_trace()'''
    return tokens, labels, list(OrderedDict.fromkeys(label_set))

class NER_Dataset(data.Dataset):
    def __init__(self, tag2idx, sentences, labels, tokenizer_path = '', do_lower_case=True):
        self.tag2idx = tag2idx
        self.sentences = sentences
        self.labels = labels
        self.tokenizer = BertTokenizer.from_pretrained(tokenizer_path, do_lower_case=do_lower_case)

    def __len__(self):
        return len(self.sentences)

    def __getitem__(self, idx):
        sentence = self.sentences[idx]
        label = []
        for x in self.labels[idx]:
            if x in self.tag2idx.keys():
                label.append(self.tag2idx[x])
            else:
                label.append(self.tag2idx['O'])
        bert_tokens = []
        orig_to_tok_map = []
        bert_tokens.append('[CLS]')
        #append dummy label 'X' for subtokens
        modified_labels = [self.tag2idx['X']]
        for i, token in enumerate(sentence):
            if len(bert_tokens) >= 512:
                break
            orig_to_tok_map.append(len(bert_tokens))
            modified_labels.append(label[i])
            new_token = self.tokenizer.tokenize(token)
            bert_tokens.extend(new_token)
            modified_labels.extend([self.tag2idx['X']] * (len(new_token) -1))

        bert_tokens.append('[SEP]')
        modified_labels.append(self.tag2idx['X'])
        token_ids = self.tokenizer.convert_tokens_to_ids(bert_tokens)
        if len(token_ids) > 511:
            token_ids = token_ids[:512]
            modified_labels = modified_labels[:512]
        return token_ids, len(token_ids), orig_to_tok_map, modified_labels, self.sentences[idx]

def pad(batch):
    '''Pads to the longest sample'''
    get_element = lambda x: [sample[x] for sample in batch]
    seq_len = get_element(1)
    maxlen = np.array(seq_len).max()
    do_pad = lambda x, seqlen: [sample[x] + [0] * (seqlen - len(sample[x])) for sample in batch] # 0: <pad>
    tok_ids = do_pad(0, maxlen)
    attn_mask = [[(i>0) for i in ids] for ids in tok_ids] 
    LT = torch.LongTensor
    label = do_pad(3, maxlen)
    
    # sort the index, attn mask and labels on token length
    token_ids = get_element(0)
    token_ids_len = torch.LongTensor(list(map(len, token_ids)))
    _, sorted_idx = token_ids_len.sort(0, descending=True)
    #print(sorted_idx, label)
    tok_ids = LT(tok_ids)[sorted_idx]
    attn_mask = LT(attn_mask)[sorted_idx]
    #pdb.set_trace()
    for idx, l in enumerate(label):
        if len(l) != maxlen:
            print("This sentence has wrong length of labels: \n{:s}".format(str(get_element(-1)[idx])))  
    labels = LT(label)[sorted_idx]
    org_tok_map = get_element(2)
    sents = get_element(-1)

    return tok_ids, attn_mask, org_tok_map, labels, sents, list(sorted_idx.cpu().numpy())


class Bert_CRF(BertPreTrainedModel):
    def __init__(self, config):
        super(Bert_CRF, self).__init__(config)
        self.num_labels = config.num_labels
        self.bert = BertModel(config)
        #for p in self.bert.parameters():
           # p.requires_grad = False
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
        self.classifier = nn.Linear(config.hidden_size, self.num_labels)
        #pdb.set_trace()
        self.init_weights()
        self.crf = CRF(self.num_labels, batch_first=True)    
    
    def forward(self, input_ids, attn_masks, labels=None):  # dont confuse this with _forward_alg above.
        #self.bert.eval()
        #with torch.no_grad():
        outputs = self.bert(input_ids, attn_masks)
            #pdb.set_trace()
        sequence_output = outputs[0]
        sequence_output = self.dropout(sequence_output)
        emission = self.classifier(sequence_output)        
        attn_masks = attn_masks.type(torch.uint8)
        if labels is not None:
            # loss_fct = nn.CrossEntropyLoss(ignore_index=0)
            # active_loss = attn_masks.view(-1) == 1
            # active_logits = emission.view(-1, self.num_labels)[active_loss]
            # active_labels = labels.view(-1)[active_loss]
            # loss = loss_fct(active_logits, active_labels) 
            #pdb.set_trace()
            loss = -self.crf(log_soft(emission, 2), labels, mask=attn_masks, reduction='mean')
            return loss
        else:
            prediction = self.crf.decode(emission, mask=attn_masks)
            return prediction


class SpanBert_CRF(AutoModel):
    def __init__(self, config):
        super(SpanBert_CRF, self).__init__(config)
        #pdb.set_trace()
        self.num_labels = config.num_labels
        self.spanbert = AutoModel.from_pretrained("SpanBERT/spanbert-base-cased")
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
        self.classifier = nn.Linear(config.hidden_size, self.num_labels)
        #self.init_weights()
        self.crf = CRF(self.num_labels, batch_first=True)    
    
    def forward(self, input_ids, attn_masks, labels=None):  # dont confuse this with _forward_alg above.
        #self.bert.eval()
        #with torch.no_grad():
        outputs = self.spanbert(input_ids, attn_masks)
        sequence_output = outputs[0]
        sequence_output = self.dropout(sequence_output)
        emission = self.classifier(sequence_output)        
        attn_masks = attn_masks.type(torch.uint8)
        if labels is not None:
            # loss_fct = nn.CrossEntropyLoss(ignore_index=0)
            # active_loss = attn_masks.view(-1) == 1
            # active_logits = emission.view(-1, self.num_labels)[active_loss]
            # active_labels = labels.view(-1)[active_loss]
            # loss = loss_fct(active_logits, active_labels) 
            #pdb.set_trace()
            loss = -self.crf(log_soft(emission, 2), labels, mask=attn_masks, reduction='mean')
            return loss
        else:
            prediction = self.crf.decode(emission, mask=attn_masks)
            return prediction

def generate_training_data(config, bert_tokenizer="bert-base", do_lower_case=True):
    training_data, validation_data = config.data_dir+config.training_data, config.data_dir+config.val_data 
    train_sentences, train_labels, label_set = corpus_reader(training_data, delim=' ')
    #pdb.set_trace()
    label_set.append('X')
    tag2idx = {t:i for i, t in enumerate(label_set)}
    #print('Training datas: ', len(train_sentences))
    train_dataset = NER_Dataset(tag2idx, train_sentences, train_labels, tokenizer_path = bert_tokenizer, do_lower_case=do_lower_case)
    # save the tag2indx dictionary. Will be used while prediction
    with open(config.apr_dir + 'tag2idx.pkl', 'wb') as f:
        pickle.dump(tag2idx, f, pickle.HIGHEST_PROTOCOL)
    dev_sentences, dev_labels, _ = corpus_reader(validation_data, delim=' ')
    dev_dataset = NER_Dataset(tag2idx, dev_sentences, dev_labels, tokenizer_path = bert_tokenizer, do_lower_case=do_lower_case)

    #print(len(train_dataset))
    '''
    train_iter = data.DataLoader(dataset=train_dataset,
                                batch_size=config.batch_size,
                                shuffle=True,
                                num_workers=4,
                                collate_fn=pad)
    eval_iter = data.DataLoader(dataset=dev_dataset,
                                batch_size=config.batch_size,
                                shuffle=False,
                                num_workers=1,
                                collate_fn=pad)'''
    return train_dataset, dev_dataset, tag2idx

def generate_test_data(config, tag2idx, bert_tokenizer="bert-base", do_lower_case=True):
    test_data = config.data_dir+config.test_data
    test_sentences, test_labels, _ = corpus_reader(test_data, delim=' ')
    test_dataset = NER_Dataset(tag2idx, test_sentences, test_labels, tokenizer_path = bert_tokenizer, do_lower_case=do_lower_case)
    test_iter = data.DataLoader(dataset=test_dataset,
                                batch_size=config.batch_size,
                                shuffle=False,
                                num_workers=1,
                                collate_fn=pad)
    #pdb.set_trace()
    return test_iter

def train(train_iter, eval_iter, tag2idx, config, bert_model="bert-base-uncased"):
    #print('#Tags: ', len(tag2idx))
    unique_labels = list(tag2idx.keys())
    model = Bert_CRF.from_pretrained(bert_model, num_labels = len(tag2idx))
    model.train()
    if torch.cuda.is_available():
      model.cuda()
    num_epoch = config.epoch
    gradient_acc_steps = 1
    t_total = len(train_iter) // gradient_acc_steps * num_epoch
    no_decay = ['bias', 'LayerNorm.weight']
    optimizer_grouped_parameters = [
        {
            "params": [p for n, p in model.named_parameters() if not any(nd in n for nd in no_decay)],
            "weight_decay": 0.0,
        },
        {"params": [p for n, p in model.named_parameters() if any(nd in n for nd in no_decay)], "weight_decay": 0.0},
    ]
    optimizer = AdamW(optimizer_grouped_parameters, lr=config.lr, eps=config.eps)
    scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=0, num_training_steps=t_total)
    global_step = 0
    model.zero_grad()
    model.train()
    training_loss = []
    validation_loss = []
    train_iterator = trange(num_epoch, desc="Epoch", disable=0)
    start_time = timeit.default_timer()

    for epoch in (train_iterator):
        epoch_iterator = tqdm(train_iter, desc="Iteration", disable=-1)
        tr_loss = 0.0
        tmp_loss = 0.0
        model.train()
        for step, batch in enumerate(epoch_iterator):
            s = timeit.default_timer()
            token_ids, attn_mask, _, labels, _, _= batch
            #print(labels)
            inputs = {'input_ids' : token_ids.to(device),
                     'attn_masks' : attn_mask.to(device),
                     'labels' : labels.to(device)
                     }  
            loss= model(**inputs) 
            loss.backward()
            tmp_loss += loss.item()
            tr_loss += loss.item()
            if (step + 1) % 1 == 0:
                optimizer.step()
                scheduler.step()  # Update learning rate schedule
                model.zero_grad()
                global_step += 1
            if step == 0:
                print('\n%s Step: %d of %d Loss: %f' %(str(datetime.datetime.now()), (step+1), len(epoch_iterator), loss.item()))
            if (step+1) % 100 == 0:
                print('%s Step: %d of %d Loss: %f' %(str(datetime.datetime.now()), (step+1), len(epoch_iterator), tmp_loss/1000))
                tmp_loss = 0.0
      
        print("Training Loss: %f for epoch %d" %(tr_loss/len(train_iter), epoch))
        #pdb.set_trace()
        training_loss.append(tr_loss/len(train_iter))
        #'''
        #Y_pred = []
        #Y_true = []
        val_loss = 0.0
        model.eval()
        writer = open(config.apr_dir + 'prediction_'+str(epoch)+'.csv', 'w')
        for i, batch in enumerate(eval_iter):
            token_ids, attn_mask, org_tok_map, labels, original_token, sorted_idx = batch
            #attn_mask.dt
            inputs = {'input_ids': token_ids.to(device),
                      'attn_masks' : attn_mask.to(device)
                     }  
            
            dev_inputs = {'input_ids' : token_ids.to(device),
                         'attn_masks' : attn_mask.to(device),
                         'labels' : labels.to(device)
                         } 
            with torch.torch.no_grad():
                #pdb.set_trace()
                tag_seqs = model(**inputs)
                tmp_eval_loss = model(**dev_inputs)
            val_loss += tmp_eval_loss.item()
            #print(labels.numpy())
            y_true = list(labels.cpu().numpy())
            for i in range(len(sorted_idx)):
                o2m = org_tok_map[i]
                pos = sorted_idx.index(i)
                for j, orig_tok_idx in enumerate(o2m):
                    writer.write(original_token[i][j] + '\t')
                    writer.write(unique_labels[y_true[pos][orig_tok_idx]] + '\t')
                    pred_tag = unique_labels[tag_seqs[pos][orig_tok_idx]]
                    if pred_tag == 'X':
                        pred_tag = 'O'
                    writer.write(pred_tag + '\n')
                writer.write('\n')
                
        validation_loss.append(val_loss/len(eval_iter))
        writer.flush()
        print('Epoch: ', epoch)
        command = "python conlleval.py < " + config.apr_dir + "prediction_"+str(epoch)+".csv"
        process = subprocess.Popen(command,stdout=subprocess.PIPE, shell=True)
        result = process.communicate()[0].decode("utf-8")
        print(result)
        torch.save({
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'loss': tr_loss/len(train_iter),
        }, config.apr_dir + 'model_' + str(epoch) + '.pt')

    total_time = timeit.default_timer() - start_time
    print('Total training time: ',   total_time)
    return training_loss, validation_loss

'''
    raw_text should pad data in raw data prediction
'''
def test(config, test_iter, model, unique_labels, test_output):
    model.eval()
    writer = open(config.apr_dir + test_output, 'w')
    for i, batch in enumerate(test_iter):
        token_ids, attn_mask, org_tok_map, labels, original_token, sorted_idx = batch
        #attn_mask.dt
        inputs = {'input_ids': token_ids.to(device),
                  'attn_masks' : attn_mask.to(device)
                 }  
        with torch.torch.no_grad():
            tag_seqs = model(**inputs)
        y_true = list(labels.cpu().numpy())
        for i in range(len(sorted_idx)):
            #pdb.set_trace()
            o2m = org_tok_map[i]
            pos = sorted_idx.index(i)
            for j, orig_tok_idx in enumerate(o2m):
                writer.write(original_token[i][j] + '\t')
                writer.write(unique_labels[y_true[pos][orig_tok_idx]] + '\t')
                pred_tag = unique_labels[tag_seqs[pos][orig_tok_idx]]
                if pred_tag == 'X':
                    pred_tag = 'O'
                writer.write(pred_tag + '\n')
            #pdb.set_trace()
            writer.write('\n')
    writer.flush()
    command = "python conlleval.py < " + config.apr_dir + test_output
    process = subprocess.Popen(command,stdout=subprocess.PIPE, shell=True)
    result = process.communicate()[0].decode("utf-8")
    print(result)
def parse_raw_data(padded_raw_data, model, unique_labels, out_file_name='raw_prediction.csv'):
    model.eval()
    token_ids, attn_mask, org_tok_map, labels, original_token, sorted_idx = padded_raw_data
    #attn_mask.dt
    writer = open(out_file_name, 'w')
    inputs = {'input_ids': token_ids.to(device),
              'attn_masks' : attn_mask.to(device)
             }  
    with torch.torch.no_grad():
        tag_seqs = model(**inputs)
    y_true = list(labels.cpu().numpy())
    for i in range(len(sorted_idx)):
        o2m = org_tok_map[i]
        pos = sorted_idx.index(i)
        for j, orig_tok_idx in enumerate(o2m):
            writer.write(original_token[i][j] + '\t')
            writer.write(unique_labels[y_true[pos][orig_tok_idx]] + '\t')
            pred_tag = unique_labels[tag_seqs[pos][orig_tok_idx]]
            if pred_tag == 'X':
                pred_tag = 'O'
            writer.write(pred_tag + '\n')
        writer.write('\n')
    print("Raw data prediction done!")

def show_graph(training_loss, validation_loss, resource_dir):
    plt.plot(range(1,len(training_loss)+1), training_loss, label='Training Loss')
    plt.plot(range(1,len(training_loss)+1), validation_loss, label='Testing Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title("Training Loss Vs Testing Loss")
    plt.legend()
    plt.show()
    plt.savefig(resource_dir + 'Loss.png')

def load_model(config, do_lower_case=True):
    f = open(config.apr_dir +'tag2idx.pkl', 'rb')
    tag2idx = pickle.load(f)
    unique_labels = list(tag2idx.keys())
    model = Bert_CRF.from_pretrained(config.bert_model, num_labels=len(tag2idx))
    checkpoint = torch.load(config.apr_dir + config.model_name, map_location='cpu')
    model.load_state_dict(checkpoint['model_state_dict'])
    global bert_tokenizer
    bert_tokenizer = BertTokenizer.from_pretrained(config.bert_model, do_lower_case=do_lower_case)
    if torch.cuda.is_available():
        model.cuda()
    model.eval()
    return model, bert_tokenizer, unique_labels, tag2idx

def raw_processing(doc, bert_tokenizer, word_tokenizer=nltk.tokenize.word_tokenize):
    tic = time.time()
    spans = re.split("[\n\r]", doc)
    offset = 0
    batch = []
    for span in spans:
        sentences = sentence_segmenter(span)
        for s_idx, sentence in enumerate(sentences.sents):
            bert_tokens = []
            orig_to_tok_map = []
            bert_tokens.append('[CLS]')
            begins = []
            ends = []
            for tok in tokenzer(word):
                token = tok.text
                offset = doc.find(token, offset)
                current_begins.append(offset)
                ends.append(offset + len(token))
                offset += len(token)
                orig_to_tok_map.append(len(bert_tokens))
                new_token = bert_tokenizer.tokenize(token)
                bert_tokens.extend(new_token)
            bert_tokens.append('[SEP]')
            token_id = bert_tokenizer.convert_tokens_to_ids(bert_tokens)
            if len(token_id) > 511:
                token_id = token_id[:512]
            dummy_labels = ['X'] * len(token_id)
            dummy_f_names = ['f_names'] * len(token_id)
            sample = (token_id, len(token_id), orig_to_tok_map, dummy_labels, original_token)
            batch.append(sample)
    pad_data = pad(batch)
    return pad_data    

def usage(parameter):
    parameter.print_help()
    print("Example usage (training):\n", \
        "\t python bert_crf.py --mode train ")

    print("Example usage (testing):\n", \
        "\t python bert_crf.py --mode test ")


if __name__ == "__main__":
    user_input = OptionParser()
    user_input.add_option("--mode", dest="model_mode", metavar="string", default='traning',
                      help="mode of the model (required)")
    (options, args) = user_input.parse_args()

    if options.model_mode == "train":
        train_dataset, eval_dataset, tag2idx = generate_training_data(config=config, bert_tokenizer=config.bert_model, do_lower_case=True)
        #pdb.set_trace()
        #### Modifying k-fold
        dataset = ConcatDataset([train_dataset, eval_dataset])
        kfold = KFold(n_splits=5, shuffle=True)
        for fold, (train_ids, test_ids) in enumerate(kfold.split(dataset)):
            # Print
            print(f'FOLD {fold}')
            print('--------------------------------')
            # Sample elements randomly from a given list of ids, no replacement.
            train_subsampler = torch.utils.data.SubsetRandomSampler(train_ids)
            test_subsampler = torch.utils.data.SubsetRandomSampler(test_ids)
            #pdb.set_trace()
            # Define data loaders for training and testing data in this fold
            trainloader = data.DataLoader(dataset=dataset,
                                batch_size=config.batch_size,
                                num_workers=4,
                                collate_fn=pad,
                                sampler=train_subsampler
                                )
            testloader = data.DataLoader(dataset=dataset,
                                batch_size=config.batch_size,
                                num_workers=1,
                                collate_fn=pad,
                                sampler=test_subsampler
                                )
            #pdb.set_trace()
            t_loss, v_loss = train(trainloader, testloader, tag2idx, config=config, bert_model=config.bert_model)
            show_graph(t_loss, v_loss, config.apr_dir)
    elif options.model_mode == "test":
        model, bert_tokenizer, unique_labels, tag2idx = load_model(config=config, do_lower_case=True)
        test_iter = generate_test_data(config, tag2idx, bert_tokenizer=config.bert_model, do_lower_case=True)
        print('test len: ', len(test_iter))
        test(config, test_iter, model, unique_labels, config.test_out)
    elif options.model_mode == "raw_text":
        if config.raw_text == None:
            print('Please provide the raw text path on config.raw_text')
            import sys
            sys.exit(1)
        model, bert_tokenizer, unique_labels, tag2idx= load_model(config=config, do_lower_case=True)
        doc = open(config.raw_text).read()
        pad_data = raw_processing(doc, bert_tokenizer)
        parse_raw_data(pad_data, model, unique_labels, out_file_name=config.raw_prediction_output)
    else:
        usage(user_input)