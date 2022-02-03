from stanfordcorenlp import StanfordCoreNLP
import corenlp
from utils import get_token_pos
from utils import replace_people_pronoun_split
import csv

'''
def main():
    # corenlp.StanfordCoreNLP()
    get_abstract_list()
    sentence = 'A new type of small-molecule phosphate superplasticiser (SP) was synthesised in one pot by the phosphor' \
               'ylation reaction of star-polyether with phosphoric acid. ' \
               'The synthesised SPs were characterised by means of proton nuclear magnetic resonance, high-performance ' \
               'liquid chromatography, Fourier transform infrared spectroscopy and gel permeation chromatography. ' \
               'Their dispersion ability, adsorption behaviour and retardation effect on cement hydration were investigated. ' \
               'It was proved that the star-shaped small-molecule phosphate compounds with longer polyether chains and' \
               ' more phosphate groups could be successfully applied as anti-clay SPs.'
    print('Tokenize:', Corenlp.word_tokenize(sentence))
    print('Coreference:', Corenlp.coref(sentence))'''


def coreference_resolution(sent:str, ent1, ent2):
    for title in paper_contents.keys():
        if sent in paper_contents[title]['Abstract']:
            paper_info = paper_contents[title]
            abstract = paper_info['Abstract']
            sent_pos = get_sent_pos(sent, abstract)
            cref_result = arrange_result(Corenlp.coref(abstract), sent_pos)
            sent_split = Corenlp.word_tokenize(sent)
            ent1, ent2 = word_tokenize(ent1), word_tokenize(ent2)
            for result in cref_result:
                Original_s_pos = result[1][0]
                orig_h_pos, orig_t_pos = result[1][1] - 1, result[1][2] - 1
                if Original_s_pos == sent_pos and judge_coref_pos(sent_split, ent1, ent2, [orig_h_pos, orig_t_pos]):
                    new_token, original_token = Corenlp.word_tokenize(result[0][3]), Corenlp.word_tokenize(result[1][3])
                    if sent_split[orig_h_pos: orig_t_pos] != original_token:
                        print('result token is wrong, coref result sent pos is wrong')
                        print('{:s} is oringinal sentence, {:s} is the token for replaced'.format(sent, result[1][3]))
                        break
                    #pop push
                    for pos in reversed(range(orig_h_pos, orig_t_pos, 1)):
                        sent_split.pop(pos)   # pop the old word one by one
                    for pos, t in zip(range(orig_h_pos, orig_t_pos + len(new_token), 1), new_token):
                        sent_split.insert(pos, t)  # push the new word into token list
            sent_split = replace_people_pronoun_split([ent1, ent2], sent_split)
            return sent_split, title
    print(None)


def judge_coref_pos(sent, ent1, ent2, result_pos):
    ent1_pos = get_token_pos(ent1, sent)
    ent2_pos = get_token_pos(ent2, sent)
    if len(ent1_pos[0]) == 1:
        ent1_pos[0].append(ent1_pos[0][0])
    if len(ent2_pos[0]) == 1:
        ent2_pos[0].append(ent2_pos[0][0])
    h_pos, t_pos = result_pos
    if ent1_pos is None or ent2_pos is None:
        print('ent pos is None')
    '''
        if (not (ent1_pos[0][0] <= h_pos <= ent1_pos[0][-1] or ent2_pos[0][0] <= h_pos <= ent2_pos[0][-1])) and \
                (not (ent1_pos[0][0] <= t_pos <= ent1_pos[0][-1] or ent2_pos[0][0] <= t_pos <= ent2_pos[0][-1])) and \
                (not (ent1_pos[0][0] >= h_pos and ent1_pos[0][-1] <= t_pos) or (ent2_pos[0][0] >= h_pos and ent2_pos[0][-1] <= t_pos)):  # How to simplify
            flag2 = True
        else:
            flag2 = False
        assert flag1 == flag2
        return flag2
        '''
    for pos in range(h_pos, t_pos):
        if ent1_pos[0][0] <= pos <= ent1_pos[0][-1] or ent2_pos[0][0] <= pos <= ent2_pos[0][-1]:
            return False
    return True




def arrange_result(coref_result, pos):
    arranged_result = []
    for result in coref_result:
        for num in range(1, len(result), 1):
            if result[num][0] == pos and result[0][-1] != result[num][-1]:
                if len(result) > 2:
                    result = cut_result(result, pos)
                    arranged_result.append(result)
                elif len(result) == 2:
                    arranged_result.append(result)
                break
    if len(arranged_result) > 1:
        for idx, result in enumerate(arranged_result):
            for idx_c, compare_result in enumerate(arranged_result[idx+1:]):
                if result[1][1] < compare_result[1][1]:
                    arranged_result[idx], arranged_result[idx + 1 + idx_c] = arranged_result[idx + 1 + idx_c], arranged_result[idx]
    return arranged_result


def cut_result(result, pos):
    for num in reversed(range(1, len(result), 1)):
        if result[num][0] != pos:
            result.pop(num)
    return result


def get_sent_pos(sent, abstract):
    sent_list = abstract.split('. ')
    for idx, s in enumerate(sent_list):
        if sent in s or s in sent:
            return idx + 1

def get_content_dict(csv_path):
    content_dict = {}
    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0].isdigit():  # judge the result by id
                paperinfo_dict = {}
                paperinfo_dict['Abstract'] = row[2]
                paperinfo_dict['Email'] = row[3]
                paperinfo_dict['Date'] = row[4]
                paperinfo_dict['Author'] = row[5]
                paperinfo_dict['Keywords'] = row[6]
                content_dict[row[1]] =paperinfo_dict
    f.close()
    return content_dict

def get_abstract_list(path):
    f = open(path, "r")
    lines = f.readlines()
    abstract_list = []
    for line in lines:
        abstract_list.append(line)
    return abstract_list


def word_tokenize(txt):
    return Corenlp.word_tokenize(txt)

Corenlp = StanfordCoreNLP(r'/home/pigd/Documents/Projects/knowledge_graph/stanford/CoreNLP/stanford-corenlp-4.1.0')
csv_path = '/home/pigd/Documents/Projects/knowledge_graph/data/knowledge_Graph.csv'
# Abstract_path = '/home/pigd/Documents/Projects/knowledge_graph/data/abstract_10k.txt'
# abstract_list = get_abstract_list(Abstract_path)
paper_contents = get_content_dict(csv_path=csv_path)


