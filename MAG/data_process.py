import csv
import pandas as pd
import re


def main():
    buf = ''
    #abstract_dict = {}
    abstract = ''
    '''
    data_df = pd.read_csv('/home/windlbl/Documents/MagData.csv', error_bad_lines=False)
    data_df.head()
    buf = data_df.loc[0, :]
    print(data_df)
    '''
    
    path = '/home/windlbl/Documents/knowledge_graph/MAG_data/Test.csv'
    with open(path, 'w') as f:
        csv_write = csv.writer(f)
        csv_head = ["Title", "Journal", "Year", "Abstract"]
        csv_write.writerow(csv_head)
    path = '/home/windlbl/Documents/knowledge_graph/MAG_data/Test.csv'
    with open('/home/windlbl/Documents/MagData.csv')as f:
        table_data = csv.reader(f)
        count = 0
        #write_data = pd.DataFrame()
        for raw_data in table_data:
            count += 1
            if count > 1:
                if count == 40:
                    print('stop')
                with open(path, 'a+') as f:
                    csv_write = csv.writer(f)
                    write_data = [raw_data[1], raw_data[4], raw_data[2]]   #Title Journal Year
                    info, absract_raw = pre_process(raw_data[5:])
                    absract_len = get_len(info)
                    abstract_dict = creat_dict(absract_raw)
                    abstract = post_process(compose(abstract_dict, absract_len))
                    write_data.append(abstract)
                #write_data.append({"Title": row[1], "Journal": row[4], "Year": row[2], "Abstract": abstract}, ignore_index=True)
                    csv_write.writerow(write_data)
            if count == 50:
                #write_data.to_csv(path)
                break
                del table_data




def get_keys(d, value):
    '''
            Get the key(word) using value(position number)
    '''
    for k, v in d.items():
        if value in v:
            return k
    return ''

def compose(dict, len):
    '''
         Cat each word into a complete abstract.
    '''
    abstract = ''
    for num in range(len):
        word = get_keys(dict, str(num))
        abstract = abstract + ' ' + word
    return abstract

def get_len(str):
    spec_cond = re.compile(r'[:](.*?)[,]', re.S)  # the condition of extracting abstract from text
    value_str = re.findall(spec_cond, str)
    value = int(value_str[0])

    return value

def creat_dict(str):
    '''
        Create a dictionary using the raw data
        key:'word'
        value: ['position',...]
    '''
    dict_buf = {}
    for key, value in zip(str[::2], str[1::2]):
        spec_cond = re.compile(r'[[](.*?)[]]', re.S)  # the condition of extracting abstract from text
        value_str = re.findall(spec_cond, value)[0].split(',')
        dict_buf[key] = value_str

    return dict_buf

def pre_process(str):
    '''
        Process the raw data into two part.
    '''
    buf = ''
    for word in str:
        buf = buf + ',' + word
    buf_split = buf.split('{')
    assert buf_split[0] == ','
    front = buf_split[1]
    abstract_raw = buf_split[-1]
    abstract_raw = abstract_raw.split('\\"')[1:]      #[1:] in order to discard the '' in the front
    return front, abstract_raw

def post_process(abstract):
    if abstract.find("\\u0027") != -1:
        abstract = abstract.replace('\\\\u0027', "'")
    if abstract.find("\\\\r\\\\n") != -1:
        abstract = abstract.replace('\\\\r\\\\n', ' ')
    return abstract

if __name__ == '__main__':
    main()