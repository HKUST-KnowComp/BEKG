#import pandas as pd
#import os.path as osp
import json
import pdb
import os
from brat import brat
def main():
    source_path = '/home/pigd/Documents/Projects/knowledge_graph/brat/brat-v1.3_Crunchy_Frog/data/dataset_annotation/affect'
    conf_path = _get_paths_from_confs(source_path)
    for txt_path in conf_path:
        print("Adding {:s} conf file".format(txt_path.split("/")[-2]))
        conf = 'good_result' + '\t' + 'Arg1:Entity, Arg2:Entity\n'
        with open(txt_path, "r") as f:
            lines = f.readlines()
            lines.insert(29, conf)
            f.close()
        with open(txt_path, 'w') as cw:
            for line in lines:
                cw.write(line)
            cw.close()


def _get_paths_from_files(path, filetype):
    """get image path list from image folder"""
    assert os.path.isdir(path), '{:s} is not a valid directory'.format(path)
    paths = []
    for dirpath, _, fnames in sorted(os.walk(path)):
        for fname in sorted(fnames):
            if fname.endswith(filetype):
                file_path = os.path.join(dirpath, fname)
                paths.append(file_path)
    assert paths, '{:s} has no valid {:s} file'.format(path, filetype)
    return paths

def conf_writer(file, rel: str):
    f = open(file, "r")
    lines = f.readlines()
    for idx, line in enumerate(lines):
        if '[relations]' in line:
            line_idx = idx
            break
    #pdb.set_trace()
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

def replace_rel(file, target_rel: str, merge_rel:str):
    f = open(file, "r")
    lines = f.readlines()
    for idx, line in enumerate(lines):
        if target_rel in line:
            #pdb.set_trace()
            if line[0]=='R':
                lines[idx] = line.replace(target_rel, merge_rel) #'__'.join([target_rel, merge_rel]))
            else:
                lines[idx] = line
            print('Finish replacing {:s} in {:s}\n'.format(target_rel, file))
    with open(file, 'w') as cw:
        #pdb.set_trace()
        for line in lines:
            cw.write(line)
        cw.close()


def parse_ann(ann_lines):
    ann_result = {}
    for line in ann_lines:
        if line[0] == 'T':
            ent_index, _, ent = line.split('\t')
            ann_result[ent_index] = {'Entity': ent.strip()}
        if line[0] == 'R':
            if len(line.split('\t')) != 3:
                print(None)
            rel_index, rel_info, _ = line.split('\t')
            relation, h, t = rel_info.split(' ')
            h_index, t_index = h.split(':')[-1], t.split(':')[-1]
            instance = {'token_h': ann_result[h_index]['Entity'], 'token_t': ann_result[t_index]['Entity']}
            if '-'.join((h_index, t_index)) in ann_result.keys():
                if relation in ['True', 'False', 'Ture']:
                    ann_result['-'.join((h_index, t_index))]['annotation'] = relation
                else:
                    ann_result['-'.join((h_index, t_index))]['relation'] = relation
            elif '-'.join((t_index, h_index)) in ann_result.keys():
                if relation in ['True', 'False', 'Ture']:
                    ann_result['-'.join((t_index, h_index))]['annotation'] = relation
                else:
                    ann_result['-'.join((t_index, h_index))]['relation'] = relation
            else:
                if relation in ['True', 'False', 'Ture']:
                    instance['annotation'] = relation
                else:
                    instance['relation'] = relation
                ann_result['-'.join((h_index, t_index))] = instance
    return ann_result


def fliter_keys(data:dict):
    keys_buf = list(data.keys())
    for key in keys_buf:
        if '-' not in key:
            data.pop(key)
    return data

def reverse_key(key:str):
    head, tail = key.split('-')
    return '-'.join((tail, head))

def compare_twice_result(ann_1_path, ann_2_path, clean_txt_path):
    EREs = []
    different_keys = []
    sents = []
    total_count = 0
    true_count = 0
    txt_path = ann_1_path.replace('.ann', '.txt')
    new_txt_path = clean_txt_path
    f_w = open(new_txt_path, 'w')
    f_txt = open(txt_path, "r")
    sents_list = f_txt.readlines()
    f_ann_1, f_ann_2 = open(ann_1_path, "r"), open(ann_2_path, "r")
    ann_1_lines, ann_2_lines = f_ann_1.readlines(), f_ann_2.readlines()
    ann_1_results, ann_2_results = parse_ann(ann_1_lines), parse_ann(ann_2_lines)
    ann_1_results, ann_2_results = fliter_keys(ann_1_results), fliter_keys(ann_2_results)
    #ann_1_results_keys = sorted(ann_1_results.keys(), key=lambda x: int(x.split('-')[-1][1:]))
    for ann_1_key, sent in zip(ann_1_results.keys(), sents_list):
        total_count += 1
        if ann_1_key in ann_2_results.keys():
            ann_2_key = ann_1_key
        else:
            ann_2_key = reverse_key(ann_1_key)
        ins_1, ins_2 = ann_1_results[ann_1_key], ann_2_results[ann_2_key]
        if 'annotation' not in ins_1.keys() or 'relation' not in ins_1.keys():
            print(None)
        ent_1_h, relation, ent_1_t, annotation_1 = ins_1['token_h'], ins_1['relation'], ins_1['token_t'], ins_1['annotation']
        if 'annotation' not in ins_2.keys() or 'relation' not in ins_2.keys():
            print(None)
        ent_2_h, relation, ent_2_t, annotation_2 = ins_2['token_h'], ins_2['relation'], ins_2['token_t'], ins_2['annotation']
        if not (ent_1_h == ent_2_h or ent_1_h == ent_2_t):
            print(None)
        assert ent_1_h == ent_2_h or ent_1_h == ent_2_t
        if not (ent_1_h in sent and ent_1_t in sent):
            print('None')
        assert ent_1_h in sent and ent_1_t in sent
        if annotation_1 != annotation_2:
            sents.append(sent)
            EREs.append(';'.join((ent_1_h, relation, ent_1_t)))
            different_keys.append(ann_1_key)
        else:
            if annotation_1 == 'True':
                true_count += 1
    sents = clean_repeated(sents)
    for sent in sents:
        f_w.write(sent)
    f_w.close()
    for k in different_keys:
        ann_1_results.pop(k)
    return EREs, ann_1_results, total_count, true_count


def clean_repeated(sentences: list):
    sent_map = {}
    for sent in reversed(sentences):
        if sent not in sent_map.keys():
            sent_map[sent] = True
        else:
            sentences.pop(sent)
    return sentences


def third_brat_annotation():
    first_ann_paths = _get_paths_from_files('/Users/pigd/入口/知识图谱/data/brat/rel_building_annotation_1', 'ann')
    second_ann_paths = _get_paths_from_files('/Users/pigd/入口/知识图谱/data/brat/rel_building_annotation_2', 'ann')
    same_result_path = '/Users/pigd/入口/知识图谱/data/FewRel/Twice_annotation_same.json'
    same_result = {}
    total_count = 0
    ture_count = 0
    different_result = 0
    same_count = 0
    for path_1, path_2 in zip(first_ann_paths, second_ann_paths):
        # pdb.set_trace()
        # replace_rel(file_path, 'related_to', 'contribute_to') #'reveal', 'suggest')
        # f = open(file_path, "r")
        task_name = path_1.split('/')[-2]
        Brat = brat('', task_name, '/Users/pigd/入口/知识图谱/data/brat/rel_building_annotation_3')
        clean_txt_path = os.path.join(Brat.rel_path, Brat.rel_name + '.txt')
        EREs, ann_result, total_c, ture_c = compare_twice_result(path_1, path_2, clean_txt_path)
        same_result[task_name] = ann_result
        total_count += total_c
        ture_count += ture_c
        different_r = len(EREs)
        different_result += different_r
        same_count += total_c - different_r
        print('{:s} task totally has {:d} relations, {:d} are different, the accuracy in the rest is {:.2f}%'
              .format(task_name, total_c, different_r, ture_c/(total_c-different_r) * 100))
        Brat.annotator(EREs, clean_txt_path)
    print('Totally got {:d} relations, {:d} are different, {:d} are same, the accuracy in the same is {:.2f}%'
          .format(total_count, different_result, same_count, ture_count / same_count * 100))
    f_w = open(same_result_path, 'w')
    json.dump(same_result, f_w)
    f_w.close()

if __name__ == '__main__':
    third_brat_annotation()
    #file_paths = _get_paths_from_files('/Users/pigd/入口/知识图谱/data/brat/rel_building_annotation_2', 'ann')
    #for file_path in file_paths:

        #pdb.set_trace()
        #replace_rel(file_path, 'Ture', 'True') #'reveal', 'suggest')
        #f = open(file_path, "r")
        #result = parse_ann(f.readlines())
        #print('Adding relation to {:s} conf file'.format(conf_writer(file_path, 'True')))
