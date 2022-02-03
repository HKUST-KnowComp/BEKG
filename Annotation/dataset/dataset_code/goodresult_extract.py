import pandas as pd
import os.path as osp
import os
from CoreNLP import coreference_resolution
from CoreNLP import word_tokenize
from utils import *

import json


def main():
    source_path = '/home/pigd/Documents/Projects/knowledge_graph/brat/brat-v1.3_Crunchy_Frog/data/dataset_annotation/' \
                  'train_data/'
    dataset_path = '/home/pigd/Documents/Projects/knowledge_graph/data/train_demo.json'
    all_ann_path = get_paths_from_anns(source_path)    # get all the ann path from the folder
    data_dict = {}
    ann_count = 0
    total_rel = 0
    for ann_path in all_ann_path:
        txt_path = ann_path.replace('.ann', '.txt')    # original text path
        f = open(ann_path, "r")
        ann_count += 1
        rel_count = 0
        sents_list = get_sent_list(txt_path)
        ent_dict = get_ent_dict(ann_path)
        lines = f.readlines()
        Relation = ann_path.split('/')[-2]
        print('Processing Relation: {:s} \n'.format(Relation))
        for idx, line in enumerate(lines):
            if rel_count == 50:
                break
            if line[0] == 'R':
                relation = line.split(' ')[0].split()[-1]
                if relation == 'good_result':
                    inst_dict = {}
                    ent1_text, ent2_text, sentence = extract_good(line, ent_dict, sents_list)
                    #print('Processing Relation: {:s} \n Sentence: \n {:s} \n'.format(Relation, sentence))
                    #sent_split = word_tokenize(sentence)  #use for debug
                    sent_split, title = coreference_resolution(sentence, ent1_text, ent2_text)
                    if sent_split is None:
                        print(None)
                    dataset(data_dict, inst_dict, sent_split, ent1_text, ent2_text, Relation, title)
                    rel_count += 1
                    total_rel += 1

        '''if rel_count != 50:
            print('{:d} instances for {:s} relation have been written into dataset'.format(rel_count, Relation))'''
        print('{:d} instances for {:s} relation have been written into dataset'.format(rel_count, Relation))

    print('{:d} kinds of relations, {:d} instances have been written into dataset'.format(ann_count, total_rel))
    # Write the data into json
    with open(dataset_path, "w") as f:
        json.dump(data_dict, f)

def extract_good(line, ent_dict, sents_list):
    ent1_ID = line.split(' ')[1].split(':')[-1]
    ent1_text = ent_dict[ent1_ID.strip()]
    ent2_ID = line.split(' ')[2].split(':')[-1].split('\t')[0]
    ent2_text = ent_dict[ent2_ID.strip()]
    for sent in sents_list:
        if ent1_text in sent and ent2_text in sent:
            return ent1_text, ent2_text, sent.strip().replace('；', ';')
    print('Entity:{:s}: "{:s}" ,{:s} "{:s}" are not in the sentence.'.format(ent1_ID,  ent1_text, ent2_ID, ent2_text))


def dataset(data_dict, inst_dict, sent, token1, token2, rel, title):
    inst_dict['tokens'] = sent  # 已经将句子拆分为tokens了
    h_pos = get_token_pos(word_tokenize(replace_people_pronoun_ent(token1)), sent)
    t_pos = get_token_pos(word_tokenize(replace_people_pronoun_ent(token2)), sent)
    inst_dict['h'] = [token1, h_pos]
    inst_dict['t'] = [token2, t_pos]
    inst_dict['title'] = title
    if rel not in data_dict.keys():
        data_dict[rel] = []
        data_dict[rel].append(inst_dict)
    else:
        data_dict[rel].append(inst_dict)



if __name__ == '__main__':
    main()
