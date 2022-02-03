from io import StringIO
import re
import os.path as osp
import os
import json
import shutil
from utils import abstract2sent, _get_paths_from_files
import nltk

class brat():
    def __init__(self, result_path: str, rel_name: str, root_path: str):
        self.result_path = result_path
        self.root_path = root_path #'/home/pigd/Documents/Projects/knowledge_graph/brat-v1.3_Crunchy_Frog'
        self.rel_name = rel_name
        self.rel_path = (osp.join(self.root_path, rel_name))
        if not osp.exists(self.root_path):
            os.mkdir(self.root_path)
        if not osp.exists(self.rel_path):
            os.mkdir(self.rel_path)
            if self.result_path.endswith('.txt'):
                self.cleantxt_path = self.result_path.replace('.txt', '_clean.txt')
            elif self.result_path.endswith('.json'):
                self.cleantxt_path = self.rel_path + '/' + self.rel_name + '_clean.txt'
        self.conf_path = './annotation.conf'
        self.TOKENIZATION_REGEX = re.compile(r'([0-9a-zA-Z]+|[^0-9a-zA-Z])')
        self.ENTITY_REGEX = re.compile(r'[(](.*)[)]', re.S)
        self.NEWLINE_TERM_REGEX = re.compile(r'(.*?\n)')
        self.ent_info = {}

    def parse_result(self):
        # txt_path = '/home/windlbl/Documents/knowledge_graph/brat/brat-v1.3_Crunchy_Frog/data/ollie_result_01/ollie_result_01_clean.txt'
        f = open(self.result_path, "r")
        lines = f.readlines()
        txt_path = self.cleantxt_path
        EREs = []
        with open(txt_path, 'w') as w:
            for idx, line in enumerate(lines):
                if line.find('.') > 20 and idx != len(lines) - 1 and lines[idx + 1] not in \
                        ("No extractions found.\n", "No extractions found."):
                    if line.find(';') > 0:  # and line[line.find('C. ') + 2:line.find('C. ') + 3].istitle():
                        line = line.replace(';', '；')
                    if line.find('. it') > 0:  # and line[line.find('C. ') + 2:line.find('C. ') + 3].istitle():
                        line = line.replace('. it', '.\nIt')
                    if line.find('. ') > 0 and line[line.find('. ') + 2:line.find('. ') + 3].istitle():
                        line = line.replace('. ', '.\n')
                    w.write(line)

                    ## Extract the result
                    split = lines[idx + 1].split(':')
                    if len(split) == 2:
                        ent_rel_ent = split[-1]
                    elif len(lines[idx + 1].split(':')) > 2:
                        ent_rel_ent = split[1]
                        for s in split[2:]:
                            ent_rel_ent = ent_rel_ent + ':' + s
                    if ent_rel_ent.count(')') > 1:
                        ent_rel_ent.replace('(', '((')
                    ERE = self.ENTITY_REGEX.split(ent_rel_ent.strip())[1]
                    if len(ERE.split(';')) != 3:
                        print(None)
                    EREs.append(ERE)
        f.close()
        return EREs

    def parse_FewRel_results(self, abstract_path: str = None):
        EREs = []
        total, ere_count = 0, 0
        f_w = open(self.cleantxt_path, 'a')
        f_re = open(self.result_path, 'r')
        result = json.load(f_re)
        if abstract_path:
            f_ab = open(abstract_path, 'r')
            abstract = json.load(f_ab)
            sents = abstract2sent(abstract, 300)
            rel_name = self.rel_name[-3:]
            for inst in result[rel_name]:
                buf = 0
                flag = False
                t_h, t_t, r = inst['token_h'].replace(' \' ', '\' '), inst['token_t'].replace(' \' ', '\' '), inst['relation']
                for sent_abs in sents:
                    for sent in sent_abs:
                        buf += 1
                        if t_h in sent and t_t in sent:
                            if buf > total:
                                total = buf
                            flag = True
                            ere_count += 1
                            f_w.write(sent+'\n')
                            EREs.append(';'.join([t_h, r, t_t]))
                            break
                    if flag:
                        break
                if not flag:
                    print('\'{:s}\', \'{:s}\' can not be found in sents'.format(t_h, t_t))
            f_w.close()
            print('Extracting {:d} EREs from {:d} sentences'.format(ere_count, total))
        else:
            batch_idx = int(self.rel_name[-2:]) - 1
            for inst in result[batch_idx]:
                f_w.write(inst['sent'] + '\n')
                t_h, r, t_t = inst['token_h'], inst['relation'], inst['token_t']
                EREs.append(';'.join([t_h, r, t_t]))
                ere_count += 1
            assert ere_count == 100
            print('Extracting {:d} EREs sentences from {:d} batch'.format(ere_count, batch_idx))
        return EREs


    def parse_dataset(self):
        f_re = open(self.result_path, 'r')
        result = json.load(f_re)[self.rel_name]
        EREs = []
        ere_count = 0
        f_w = open(self.cleantxt_path, 'a')
        for inst in result:
            f_w.write(' '.join(inst['tokens']) + '\n')
            t_h, r, t_t = inst['h'][0], self.rel_name, inst['t'][0]
            EREs.append(';'.join([t_h, r, t_t]))
            ere_count += 1
            print('Extracting {:d} EREs sentences from {:s} relation'.format(ere_count, self.rel_name))
        return EREs

    def annotator(self, EREs, plain_txt_path):
        f_s = open(plain_txt_path, "r", encoding="utf-8")
        lines = f_s.readlines()
        entity_num = 0
        relation_num = 0
        fail_count = 0
        sentence_dict = self.get_sentence_dict(lines)
        assert len(EREs) == len(lines)
        for line, ERE in zip(lines, EREs):
            sentence = line.strip()
            ent1, relation, ent2 = ERE.split(';')
            entity1 = Entity(sentence_dict, sentence, ent1, entity_num)
            if entity1.pos is None:
                fail_count += 1
                print(sentence)
                continue
            entity_num, token1_idx = entity1.writer(entity1.pos, entity1.ent, entity_num, plain_txt_path, self.ent_info)
            entity2 = Entity(sentence_dict, sentence, ent2, entity_num)
            if entity2.pos is None:
                fail_count += 1
                print(sentence)
                continue
            entity_num, token2_idx = entity2.writer(entity2.pos, entity2.ent, entity_num, plain_txt_path, self.ent_info)
            relation_num += 1
            self.write_rel(relation, token1_idx, token2_idx, relation_num, plain_txt_path)
        f_s.close()
        print(fail_count)
        print('Successfully annotate {:d}/{:d} relations'.format(relation_num, len(EREs)))

    def get_sentence_dict(self, sentences):
        """Convert plain text into CoNLL format."""

        sent_dict = {}
        #sentences = []
        '''
        for l in f:
            sent_split = l.split('\n')
            for sent in sent_split:
                if sent != '':
                    sentences.append(sent+'\n')'''
        offset = 0
        for s in sentences:
            offset += len(s)
            sent_dict[s.strip()] = [offset - len(s), offset - 1]
        return sent_dict

    def conf_writer(self, file, rel: str):
        f = open(file, "r")
        lines = f.readlines()
        for idx, line in enumerate(lines):
            if '[relations]' in line:
                line_idx = idx
                break
        rel = rel.strip()
        rel = rel.replace(' ', '_')
        conf = rel + '\t' + 'Arg1:Entity, Arg2:Entity\n'
        with open(file, "r") as f:
            lines = f.readlines()
            lines.insert(line_idx+1, conf)
            f.close()
        with open(file, 'w') as cw:
            for line in lines:
                cw.write(line)
            cw.close()
        return rel

    def new_conf(self, file):
        with open(file, 'w') as fw:
            fw.write('[entities]\nEntity\n\n')
            fw.write('[relations]\n\n')
            fw.write('[events]\n\n')
            fw.write('[attributes]\n\n')
        fw.close()

    def write_rel(self, rel, ent1_num, ent2_num, rel_num, path):
        conf_path = osp.split(path)[0] + '/annotation.conf'
        if not osp.exists(conf_path):
            self.new_conf(conf_path)
        rel = self.conf_writer(conf_path, rel)
        ann_path = path.replace('.txt', '.ann')

        line = ['R' + str(rel_num), rel + ' Arg1:T' + str(ent1_num) + ' Arg2:T' + str(ent2_num), '']
        rel_annotation = StringIO('\t'.join(l for l in line) + '\n')
        with open(ann_path, 'at') as of:
            of.write(''.join(rel_annotation))



class Entity(object):
    def __init__(self, sent_dict, sent, ent, num):
        self.sent_dict = sent_dict
        self.sent = sent
        self.num = num
        self.ent = self.entity_collecition(self.sent, ent)
        self.pos = self.get_pos(self.sent_dict, self.sent, self.ent)

    def entity_collecition(self, sent, tokens):
        tokens = self.post_process(tokens, sent)
        if sent.find(tokens) >= 0:
            return [tokens]
        elif sent.find(tokens) == -1:
            entities = []
            new_tokens = ""
            word = ""
            for idx, alpha in enumerate(tokens):
                word = word + alpha
                if alpha == ' ' or idx == len(tokens)-1:
                    if sent.find(new_tokens + word) >= 0:
                        new_tokens = new_tokens + word
                        word = ""
                        continue

                    elif sent.find(new_tokens + word.replace(' ', ', ')) >= 0:
                        new_tokens = new_tokens + word.replace(' ', '')
                        word = ""
                        continue
                    elif sent.find(new_tokens + word.strip()) >= 0: #Here is pretty important, solve many problems
                        new_tokens = new_tokens + word.strip()
                        word = ""
                        continue
                    elif sent.find(new_tokens.strip() + word) >= 0:
                        new_tokens = new_tokens.strip() + word
                        word = ""
                        continue
                    else:
                        #if new_tokens != "":
                        entities.append(new_tokens)
                        new_tokens = ""

            if sent.find(new_tokens + word) >= 0:
                entities.append(new_tokens)
            if len(entities) > 5:
                print("Sentence: {:s} \n  Entity: {:s} \n".format(sent, tokens))
            return entities



    def get_pos(self, sent_dict:dict, sent, tokens):
        if sent not in sent_dict.keys():
            return None
        pos = []
        for t in tokens:
            token_pos = sent_dict[sent][0] + sent.find(t)
            pos.append(str(token_pos) + " " + str(token_pos + len(t)))
        return pos


    def writer(self, pos, tokens, num, path, ent_info):
        #token = post_process(token)
        #pos = get_pos(sent_dict, sent, token)
        ann_path = path.replace('.txt', '.ann')
        if pos[0] in ent_info.keys():
            ent_num = ent_info[pos[0]]
        else:
            num += 1
            ent_num = ent_info[pos[0]] = num
            positon = ';'.join(p for p in pos)
            entity = ' '.join(t for t in tokens)
            line = ['T'+str(ent_num), 'Entity ' + positon, entity]
            annotation = StringIO('\t'.join(l for l in line)+'\n')
            with open(ann_path, 'at') as of:
                of.write(''.join(annotation))
        return num, ent_num

    def post_process(self, token:str, sent:str):
        token = token.strip()
        #token = token.replace(" '", "'")
        if token.find(")[e"):
            token = token.split(")[e")[0]
        if token.find("\'") > 0:
            if sent[sent.find("\'") - 2] == token[token.find("\'") - 1] and sent[sent.find("\'") - 1] == " ":
                token = token.replace("\'", " \'")
        if token.find("- ") > 0:
            if sent[sent.find("- ") - 2] == token[token.find("- ") - 1] and sent[sent.find("- ") - 1] == " ":
                token = token.replace("- ", " - ")
        if token.find(" which") > 0:
            if sent[sent.find(" which") - 2] == token[token.find(" which") -1 ] and sent[sent.find(" which") - 1] == ",":
                token = token.replace(" which", ", which")
        return token




def mkdir(path):
    folder = os.path.exists(path)

    if not folder:  # 判断是否存在文件夹如果不存在则创建为文件夹
        os.makedirs(path)  # makedirs 创建文件时如果路径不存在会创建这个路径
        print("Creating the {:s} folder".format(path))
    else:
        print("The folder is already existed".format(path))


if __name__ == '__main__':
    #Brat = brat(result_path='/home/pigd/Documents/Projects/knowledge_graph/brat-v1.3_Crunchy_Frog/data/ollie_test/ollie_result_01.txt', rel_name='ollie_result_01')
    #EREs = Brat.parse_result()
    #for idx in range(1, 30):
    result_path = '/Users/pigd/入口/知识图谱/data/FewRel/dataset/train_building_v1_modified.json'
    f_re = open(result_path, 'r')
    dataset = json.load(f_re)
    for rel in dataset.keys():
        Brat = brat(
                result_path='/Users/pigd/入口/知识图谱/data/FewRel/dataset/train_building_v1_modified.json',
                rel_name=rel, root_path='/Users/pigd/入口/知识图谱/data/brat')
        EREs = Brat.parse_dataset()
        Brat.annotator(EREs, Brat.cleantxt_path)
    #Brat.get_sentence_dict(file)