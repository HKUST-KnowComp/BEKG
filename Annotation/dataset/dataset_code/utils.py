import os
import re


def get_token_pos(token_split, sent):
    if len(token_split) == 1:
        if sent.count(token_split[0]) == 1:
            return [[sent.index(token_split[0])]]
        elif sent.count(token_split[0]) > 1:
            sent_txt = ''
            for s in sent:
                sent_txt = sent_txt + s + ' '
            print('{:s}\n'.format(sent_txt))
            rank = int(input('Choose which {:s} in the sentence is correct'.format(token_split[0])))
            idx = [[index for (index, value) in enumerate(sent) if value == token_split[0]][rank - 1]]
            print(idx)
            return [idx]
    else:
        for idx, t_sent in enumerate(sent):
            if t_sent == token_split[0] and sent[idx + 1] == token_split[1]:
                for idx_t, t_entity in enumerate(token_split[1:]):
                    if t_entity != sent[idx + 1 + idx_t]:
                        if t_entity == sent[idx + 1 + idx_t].lower():    # sometimes the ollie occurs problems, it turn the small into big lol, your English is pretty poor.
                            sent[idx + 1 + idx_t] = sent[idx + 1 + idx_t].lower()
                        else:
                            break
                if token_split[1 + idx_t] == sent[idx + 1 + idx_t]:
                    pos = []
                    for rank in range(idx, idx+len(token_split)):
                        pos.append(rank)
                    return [pos]
        print('Entity cannot get position in sentence')

def get_paths_from_anns(path):
    """get image path list from image folder"""
    assert os.path.isdir(path), '{:s} is not a valid directory'.format(path)
    images = []
    for dirpath, _, fnames in sorted(os.walk(path)):
        for fname in sorted(fnames):
            if fname.endswith('.ann'):
                img_path = os.path.join(dirpath, fname)
                images.append(img_path)
    assert images, '{:s} has no valid image file'.format(path)
    return images


def replace_people_pronoun_ent(ent_txt):
    if ent_txt in ['We', 'The author', 'we', 'I', 'The authors']:  # 'This research', 'The findings', 'this essay']
        return 'Authors'
    else:
        return ent_txt


def replace_people_pronoun_split(ent_list, sent_split):
    for ent in ent_list:
        if ent[0] in ['We', 'The author', 'we', 'I']:
            print(' replace {:s} into "Authors" successfully \n'.format(ent[0]))
            if get_token_pos(ent, sent_split) is None:
                print('stop')
            sent_split[get_token_pos(ent, sent_split)[0][0]] = 'Authors'
    return sent_split


def get_sent_list(path):
    # get sentences from plain txt(the input of ollie) and list them
    f = open(path, "r")
    lines = f.readlines()
    sent_list = []
    for line in lines:
        sent_list.append(line)
    return sent_list


def get_ent_dict(path):
    f = open(path, "r")
    lines = f.readlines()
    ent_dict = {}
    for line in lines:
        if line[0] == 'T':
            info_group = line.strip().split('\t')
            entID = info_group[0]
            ent_text = info_group[-1].replace('  ', ' ')
            ##Here must have a better way.
            # for idx, text in enumerate(ent_text):
            # ent_text[idx] = ent_text[idx].strip()
            ent_dict[entID] = ent_text.strip()
    return ent_dict


def get_ollie_result(path):
    f_r = open(path, "r", encoding="utf-8")
    lines = f_r.readlines()
    for idx, line in enumerate(lines):
        if line.find('.') > 20 and idx != len(lines)-1 and lines[idx+1] not in\
                ("No extractions found.\n", "No extractions found.", "\n"):
            if idx == 0:
                pre_sent = line
            else:
                if line == pre_sent:
                    continue
                else:
                    pre_sent = line
            ###Pre-Process
            raw_ERE = lines[idx + 1]
            prepared_ERE = ent_rel_preprocess(raw_ERE)
            if len(prepared_ERE.split(';')) != 3:
                print(None)
            ent1, relation, ent2 = prepared_ERE.split(';')

def ent_rel_preprocess(line):
    ENTITY_REGEX = re.compile(r'[(](.*)[)]', re.S)
    line = line.split(':')
    if len(line) == 2:
        ent_rel_ent = line[-1]
    elif len(line) > 2:
        ent_rel_ent = line[1]
        for s in line[2:]:
            ent_rel_ent = ent_rel_ent + ':' + s
    else:
        print(None)
    if ent_rel_ent.count(')') > 1:
        ent_rel_ent.replace('(', '((')

    ent_rel_ent = ENTITY_REGEX.split(ent_rel_ent.strip())[1]

    return ent_rel_ent