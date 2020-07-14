
# coding: utf-8

# In[83]:


import requests
import pandas as pd
from bs4 import BeautifulSoup
artical_href = []
explode = []
title = []
category = []
title_length = []
publish_time = []
with_image = []
original = []
push_ratio_10 = []
shh_ratio_10 = []


# In[84]:


def fetch(url):
    response = requests.get(url, cookies={'over18': '1'})
    return response


# In[85]:


def get_article_content(article_url):
    resp = fetch(article_url)
    soup = BeautifulSoup(resp.text, 'lxml')
    result = soup.select('span.article-meta-value')
    if result:
        if len(result) > 3:
            #original? & category
            s = result[2].text.split(']', 1)
            if len(s)>1:
                cat = s[0].split('[', 1)
                if cat[0] == 'Re: ':
                    original.append(0);
                else:
                    original.append(1);
                category.append(cat[1])
            
                #title
                title_tmp = s[1]
                if len(title_tmp) > 0 and title_tmp[0] == ' ':
                    title_tmp = title_tmp.split(' ', 1)[1]
                    if ',' in title_tmp:
                        title_tmp = title_tmp.replace(',', ' ')
                title.append(title_tmp)
                title_length.append(len(title_tmp))
                publish_time.append(result[3].text)
                #print(title_tmp,' ', result[3].text)
            
                #with img?
                content_image = 0
                push_image = 0
                imgs = soup.findAll('a')
                image = 0
                for img in imgs:
                    if '.jpg' in img['href']:
                        image = 1;
                with_image.append(image)
            
            
                #push ratio & shh ratio for the first 10 reply
                count_push = 0
                count_shh = 0
                reply = soup.select('span.push-tag')
                idx = 0
                for item in reply:
                    span_item = item.select_one('span')
                    if item.text == '推 ':
                        count_push += 1
                    elif item.text == '噓 ':
                        count_shh += 1
                    idx += 1
                    if idx == 10:
                        break
                if idx == 0:
                    push_ratio_10.append(0.0)
                    shh_ratio_10.append(0.0)
                else:
                    push_ratio_10.append(count_push/idx)
                    shh_ratio_10.append(count_shh/idx)
                return 1
    return 0


# In[86]:


def get_all_href(url):
    resp = fetch(url)
    soup = BeautifulSoup(resp.text, "html.parser")
    result = soup.select('div.title')
    look = soup.select('div.nrec')
    exist = []
    regulated = []
    for item in result:
        a_item = item.select_one('a')
        title = item.text
        if a_item:
            regulated.append(get_article_content(article_url = 'https://www.ptt.cc'+a_item.get('href')))
            exist.append(1)
        else:
            regulated.append(0)
            exist.append(0)
    idx = 0
    for item in look:
        if exist[idx] == 1:
            if regulated[idx] == 1:
                if item.text == '爆':
                    explode.append(1)
                else:
                    explode.append(0)
        idx += 1


# In[87]:


url = "https://www.ptt.cc/bbs/Gossiping/index.html"
resp = fetch(url)
soup = BeautifulSoup(resp.text, 'html.parser')
btn = soup.select('div.btn-group > a')
up_page_href = btn[3]['href']
#從第70頁之後開始爬
first_page_index = up_page_href.split('.', 1)[0].split('index', 1)[1]
url = 'https://www.ptt.cc/bbs/Gossiping/index' + str(int(first_page_index)-70) + '.html'
#url = 'https://www.ptt.cc/bbs/Gossiping/index38977.html'
for page in range(0,1000):
    resp = fetch(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    btn = soup.select('div.btn-group > a')
    if btn:
        up_page_href = btn[3]['href']
        next_page_url = 'https://www.ptt.cc' + up_page_href
        url = next_page_url
        get_all_href(url)
    print('page ', page , ' done!')


# In[88]:


dict = {'explode':explode, 'title':title, 'title_length': title_length, 'Category':category, 'publish_time':publish_time, 'original':original, 'images':with_image, 'push_ratio_10':push_ratio_10, 'shh_ratio_10':shh_ratio_10}
df = pd.DataFrame(dict)
df.to_csv('output.csv')


