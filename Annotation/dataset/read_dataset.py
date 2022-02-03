#AMiner数据转换成JSON数据格式
import fileinput
import json
import csv
import numpy.random as rand
from utils import *
#from CoreNLP import word_tokenize
import numpy as np
import matplotlib.pyplot as plt

#处理数据文件
class dataset():
    def __init__(self):
        #super(dataset, self).__init__()
        self.dataset_rel = ['play', 'make', 'made', 'offer', 'suggest', 'require', 'propose', 'present', 'include',
                       'explore', 'examine', 'employ',
                       'draw on', 'discuss', 'develop', 'identify', 'focus', 'describe', 'consider', 'represent',
                       'show', 'investigate', 'demonstrate',
                       'contribute', 'conclude', 'relate', 'associat', 'lead to', 'result in', 'depend']
        self.data_path = '/home/pigd/Documents/Projects/knowledge_graph/data/train_building_v1_modified.json'  # FewRel/dataset/train_wiki.json
        self.csv_path = '/home/pigd/Documents/Projects/knowledge_graph/data/RelationCluster.csv'
        self.save_path = '/home/pigd/Documents/Projects/knowledge_graph/data/final/train_building_v1.json'
        self.rel_idx = []

    def load_json(self, path):
        f = open(path, 'r')
        return json.load(f)

    def check(self, data:dict):
        #f = open(path, 'r')
        #data = json.load(f)
        for key in data.keys():
            for idx, item in enumerate(data[key]):
                if item['h'][1] is None:
                    print('key {:s} : {:d} item is none'.format(key, idx))
                    pos = get_token_pos(word_tokenize(item['h'][0]), item['tokens'])
                    if pos is not None:
                        data[key][idx]['h'][1] = pos
                        print('key {:s} : {:d} item modified successfully'.format(key, idx))
                if item['t'][1] is None:
                    print('key {:s} : {:d} item is none'.format(key, idx))
                    pos = get_token_pos(word_tokenize(item['t'][0]), item['tokens'])
                    if pos is not None:
                        data[key][idx]['t'][1] = pos
                        print('key {:s} : {:d} item modified successfully'.format(key, idx))

    def split(self,data:dict):
        train_count, val_count, test_count = [18, 5, 6]
        train_data = {}
        val_data = {}
        test_data = {}
        for idx, key in enumerate(data.keys()):
            if idx < train_count:
                train_data[key] = data[key]
            if train_count <= idx < train_count+val_count:
                val_data[key] = data[key]
            if train_count+val_count <= idx < 29:
                test_data[key] = data[key]
        return train_data, val_data, test_data





    def merge_rel(self):
        data_merge_dict = self.load_json(self.data_path)
        merge_relation = [['inside', 'have', 'include'], ['explore', 'investigate'], ['require', 'based_on'],
                          ['used_as', 'play_role_in'], ['demonstrate', 'show', 'suggest', 'present', 'propose'],
                          ['related_to', 'contribute_to', 'provide']]
        rename_relation = ['include', 'explore', 'require', 'used_as', 'reveal', 'related_to']
        assert len(merge_relation) == len(rename_relation)
        for rel_group, rel_name in zip(merge_relation, rename_relation):
            inst_group = []
            inst_merge = []
            for rel in rel_group:
                inst_group.extend(data_merge_dict[rel])
                del data_merge_dict[rel]
            for idx in range(50):
                rand_num = rand.randint(0, len(inst_group))
                inst_merge.append(inst_group[rand_num])
            data_merge_dict[rel_name] = inst_merge
        return data_merge_dict

    def read_dataset(self):
        with open(self.csv_path, 'w') as csvfile:
            csvwriter = csv.writer(csvfile)
            with open(self.data_path, 'r', encoding='utf8')as fp:
                data = json.load(fp)
                #print(data)
                csvwriter.writerow([])
                rel_num = 0
                for rel in data:
                    if rel[-1] != rel_num:
                        csvwriter.writerow([])
                    entity_h = rel[0][0].strip()
                    entity_t = rel[0][2].strip()
                    relation = rel[0][1].strip()
                    ann_flag = False
                    for idx, d_rel in enumerate(self.dataset_rel):
                        if d_rel in relation:
                            ann_flag = True
                            break
                    if ann_flag:
                        csvwriter.writerow([entity_h, relation, entity_t, 'yes', idx+1])
                        self.rel_idx.append(idx+1)
                    else:
                        csvwriter.writerow([entity_h, relation, entity_t])
                    rel_num = rel[-1]
                for idx, d_rel in enumerate(self.dataset_rel):
                    if idx + 1 not in self.rel_idx:
                        csvwriter.writerow([d_rel, idx+1])
                    else:
                        csvwriter.writerow([d_rel, idx + 1, 'yes'])
        '''for rel_key in data.keys():
            for inst_dict in data[rel_key]:
                sent = ''
                for token in inst_dict['tokens']:
                    sent += token + ' '
                token1 = inst_dict['h'][0]
                token2 = inst_dict['t'][0]
                rel = rel_key
                print('{:s}\n'.format(sent))
                print('Relation is: {:s}\n'.format(rel))
                print('Head token is: {:s}, tail token is: {:s}\n\n'.format(token1, token2))'''

    def modify_result(self, data: list):
        for batch in data:
            record = {}
            for inst in batch:
                for token in (inst['token_h'], inst['token_t']):
                    if len(token) <= 2 and not token.isalnum():
                        print('Finding bad token: {:s}'.format(token))
                        if inst['relation'] in record.keys():
                            record[inst['relation']] += 1
                        else:
                            record[inst['relation']] = 1
                        batch.remove(inst)
            for rel in record.keys():
                new_data = self.match_inst(self.load_json(self.data_path), record[rel], [rel])
                for new_inst in new_data[rel]:
                    new_inst['relation'] = rel
                    print('Replacing bad token with new inst: {:s}--{:s}--{:s}'.
                          format(new_inst['token_h'], new_inst['relation'], new_inst['token_t']))
                    batch.append(new_inst)
        return data

    def match_inst(self, result_data: dict, sample_count, relations):
        samp_dict = {}
        #sample_count = 100
        abstract_path = '/home/pigd/Documents/Projects/knowledge_graph/data/Raw/Abstract_80k_sent.json'
        print('Loading abstract data...\n')
        sents = self.load_json(abstract_path)
        print('Loading successfully.')
        for rel in relations:
            instances = []
            idx_flag = 0
            for inst in result_data[rel]:
                flag = False
                t_h, t_t = inst['token_h'].replace(' \' ', '\' '), inst['token_t'].replace(' \' ', '\' ')
                for t in (t_h, t_t):
                    if t in ['the', 'a', 'this'] or (len(t) <= 2 and not t.isalnum()):
                        continue
                for sents_in_abs in sents[idx_flag:]:
                    for sent in sents_in_abs:
                        if t_h in sent and t_t in sent:
                            inst['sent'] = sent
                            inst.pop('score')
                            instances.append(inst)
                            idx_flag = sents.index(sents_in_abs)
                            flag = True
                            print('Sampling No{:d}: {:s}--{:s}--{:s}'.format(len(instances), t_h, rel, t_t))
                            break
                    if flag:
                        break
                if len(instances) == sample_count:
                    break
            samp_dict[rel] = instances
            print('\n')
        return samp_dict

    def random_split(self, data: dict):
        rel_all = list(data.keys())
        split_all = []
        for _ in range(29):
            single_insts = []
            while len(single_insts) < 100:
                random_idx = np.random.randint(0, 29)
                rel = rel_all[random_idx]
                if data[rel]:
                    inst = data[rel].pop()
                    inst['relation'] = rel
                    single_insts.append(inst)
                else:
                    continue
            split_all.append(single_insts)
        return split_all

    def clean_data(self, data: dict):
        print('Scaning data...')
        remove_count = 0
        rest_count = 0
        failed_count =0
        for rel in data.keys():
            for inst in data[rel][::1]:
                t_h, t_t = inst['token_h'], inst['token_t']
                for t in (t_h, t_t):
                    if t in ['the', 'a'] or (len(t) <= 2 and not t.isalnum()):
                        if inst not in data[rel]:
                            failed_count += 1
                            break
                        data[rel].remove(inst)
                        remove_count += 1
                        print('Deleting NO.{:d} data:{:s} {:s}'.format(remove_count, t_h, t_t))
            rest_count += len(data[rel])
        print('{:d} instances were remained, failed: {:d}'.format(rest_count, failed_count))
        return data


    def write(self, data, path:str):
        f = open(path, 'w')
        json.dump(data, f)
####inference data processing scripts

def make_dataset(token_entity: list):
    count = 0
    dataset_dict = {'raw': []}
    for instance in token_entity:
        tokens, entities = instance
        for idx_h in range(len(entities)):
            for idx_t in range(idx_h + 1, len(entities)):
                inst_dict = {'tokens': tokens}
                inst_dict['h'] = extract_entity_pos(entities[idx_h])
                inst_dict['t'] = extract_entity_pos(entities[idx_t])
                dataset_dict['raw'].append(inst_dict)
                count += 1
                print('Processing No.{:d} sentence: {:s}\n Entity_h:{:s}, Entity_t:{:s}'\
                      .format(count, str(tokens), inst_dict['h'][0], inst_dict['t'][0]))

    return dataset_dict


def extract_entity_pos(entity: list):
    entity_tok = []
    entity_pos = []
    for tokens, pos in entity:
        entity_tok.append(tokens)
        entity_pos.append(pos)
    assert nltk.tokenwrap(entity_tok, width=150) == ' '.join(t for t in entity_tok)

    return [nltk.tokenwrap(entity_tok, width=150), [entity_pos]]


def relation_filter(data:dict, thres):
    total_count = 0
    filtered_count = 0
    ent_set = set()
    for rel in data.keys():
        ent_sum = len(ent_set)
        filtered_inst = []
        for inst in data[rel]:
            if inst['score'] >= thres and inst['token_h'] not in ['a', 'A', 'The', 'the']:
                filtered_inst.append(inst)
                ent_set.add(inst['token_h'])
                ent_set.add(inst['token_t'])
        filtered_count += len(filtered_inst)
        total_count += len(data[rel])
        print('Relation {:s} has filtered {:d} instances, remaining {:d} instances, {:d} entities.'.
              format(rel, len(data[rel])-len(filtered_inst), len(filtered_inst), len(ent_set)-ent_sum))
        data[rel] = filtered_inst

    print('Totally filtered {:d} instances, remaining {:d} instances, {:d} entities.'.format(total_count - filtered_count, filtered_count, len(ent_set)))
    return data, 'rel_building_s{:.1f}_{:d}.json'.format(thres, filtered_count)

def sample_relation(data: list, path: str):
    thresholds = [7.7]
    output = {}
    for thres in thresholds:
        count = 0
        inst_count = 0
        output[thres] = []
        for inst in data:
            inst_count += 1
            if inst['score'] > thres:
                count += 1
                output[thres].append(inst)
            if count == 300:
                print('Scanning {:d} instances getting 300 result at {:f} threshold'.format(inst_count, thres))
                break

    return output, path.replace('s0.0', 'score7to8')


def record_score(data):
    scores = {}
    for rel in data.keys():
        for inst in data[rel]:
            score = int(inst['score'])
            if score in scores.keys():
                scores[score] += 1
            else:
                scores[score] = 1
    for s in sorted(scores.keys()):
        for s1 in sorted(scores.keys()):
            if s1 > s:
                scores[s] += scores[s1]
    return scores


def plot_resutl(x, y):
    fig, ax = plt.subplots()
    ax.plot(x, y, linewidth=2.0)
    plt.show()
if __name__ == "__main__":

   # add_data_path = '/home/pigd/Documents/Projects/knowledge_graph/data/train_add.json'
    Dataset = dataset()


    #data = Dataset.load_json(Dataset.data_path)
    Dataset.data_path = '/Users/pigd/入口/知识图谱/data/Raw/Abstract_80K.json'
    #split_path = '/home/pigd/Documents/Projects/knowledge_graph/data/FewRel/rel_building_s7.7_2900_split.json'
    data = Dataset.load_json(Dataset.data_path)
    score_statics = record_score(data)
    sum = []
    for score in sorted(score_statics.keys()):
        sum.append(score_statics[score])
    plot_resutl(sorted(score_statics.keys()), sum)
    #cleaned_data = Dataset.clean_data(data)
    #Dataset.write(cleaned_data, Dataset.data_path.replace('.json', '_new.json'))

    '''
    Dataset.check(Orig_data)
    train_data, val_data, test_data = Dataset.split(Orig_data)
    Dataset.write(train_data, Dataset.save_path)
    Dataset.write(val_data, Dataset.save_path.replace('train', 'val'))
    Dataset.write(test_data, Dataset.save_path.replace('train', 'test'))'''
    #Dataset.read_dataset()
    #merge_data = Dataset.merge_rel()
    #add_data = Dataset.load_json(add_data_path)
    #merge_data.update(add_data)
    #Dataset.write(merge_data)

