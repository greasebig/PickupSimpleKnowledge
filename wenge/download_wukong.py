import pandas as pd
import os
import requests
import multiprocessing
import sys

def run(dir_path,csv_id):
    file = "wukong_100m_"+str(csv_id)+".csv"
    path = os.path.join(dir_path,file)
    splitted = file.split(".")
    if splitted[-1] == 'csv':
        sub_dir_name = splitted[0]
        sub_dir_path = os.path.join(dir_path,sub_dir_name)
        new_csv_name = sub_dir_name+"_new.csv"
        new_csv_path = os.path.join(sub_dir_path,new_csv_name)
        new_url = []
        new_text = []
        new_file = []
        if not os.path.exists(sub_dir_path):
            os.mkdir(sub_dir_path)
        data = pd.read_csv(path)
        url_data = data['url']
        text_data = data['caption']
        idx = 0
        total_len = len(url_data)
        for i in range(total_len):
            file_name = splitted[0]+"_"+str(idx)+".jpg"
            file_path = os.path.join(sub_dir_path,file_name)
            url = url_data[i]
            text = text_data[i]
            try:
                r = requests.get(url)
                if not (r.headers['Content-Type']=='image/gif' or int(r.headers['Content-Length'])<400): 
                    with open(file_path,'wb') as f:
                            f.write(r.content)
                    new_url.append(url)
                    new_text.append(text) 
                    new_file.append(file_name)   
                    idx = idx + 1
            except Exception as e:
                print(url)
                print(text)           
            
        df = pd.DataFrame()
        df['url'] = new_url
        df['caption'] = new_text
        df['file'] = new_file
        df.to_csv(new_csv_path)

def download(urls,texts,csv_id,thread_i,save_dir,list_obj):
    length = len(urls)
    new_url = []
    new_text = []
    new_file = []
    for i in range(length):
        file_name = "wukong_100m_"+str(csv_id)+"_proc"+str(thread_i)+"_"+str(i)+".jpg"
        file_path = os.path.join(save_dir,file_name)
        url = urls[i]
        text = texts[i]
        try:
            r = requests.get(url)
            if not (r.headers['Content-Type']=='image/gif'):
                with open(file_path,'wb') as f:
                    f.write(r.content)
                new_url.append(url)
                new_text.append(text)
                new_file.append(file_name)
        except Exception as e:
            print(e)
    
    list_obj.append((new_url,new_text,new_file))
             

csv_id = int(sys.argv[1])
num_thread = 128
csv_file = "./wukong_release/wukong_100m_"+str(csv_id)+".csv"
save_dir = "./wukong_release/wukong_100m_"+str(csv_id)
new_csv_file = os.path.join(save_dir,"wukong_100m_"+str(csv_id)+"_new.csv")
if not os.path.exists(save_dir):
    os.mkdir(save_dir)
data = pd.read_csv(csv_file)
url_data = data['url'].tolist()
text_data = data['caption'].tolist()
data_len = len(url_data)
process_range = round(data_len/num_thread)
mgr = multiprocessing.Manager()
list_obj = mgr.list()
jobs = []
for i in range(0,data_len,process_range):
    upper_bound = min(i+process_range,data_len)
    urls = url_data[i:upper_bound]
    texts = text_data[i:upper_bound]
    p = multiprocessing.Process(target=download,args=(urls,texts,csv_id,i,save_dir,list_obj))
    jobs.append(p)
    p.start()

for p in jobs:
    p.join()

new_url = []
new_text = []
new_file = []
for t in list_obj:
    # t = q.get()
    new_url+=t[0]
    new_text+=t[1]
    new_file+=t[2]
df = pd.DataFrame()
df['url'] = new_url
df['caption'] = new_text
df['file'] = new_file
df.to_csv(new_csv_file)
