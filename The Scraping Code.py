import requests #Helps in extracting URL content
from bs4 import BeautifulSoup #Helps you read extract given information from website
import pandas as pd #Dataframe, helps in storing/manipulating/saving the table
import time #To capture run time
import threading #For creating different threads for simulataneous running of functions
import re #For regular expression
import sys
import gc #For garbage collection
final_info = []


def url_parser(url):
    '''
    Responsilbe for extracting the back-end content
    '''
    try:
        # print (url)
        t1 = time.time()
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        # print ('Parsing time: ', time.time() - t1)
    except:
        print ("Unable to parse the website, please check the link or internet connection")

    return soup

def find_next_page(soup, Base_url):
    '''
    Checks if next page exist and if yes then returns the link for next page
    '''
    productDivs = soup.find_all('li', {'class' : 'PagedList-skipToNext'})
    if len(productDivs) > 0:
        for div in productDivs:
            return Base_url +div.find('a')['href']
    else:
        return False


def find_resource(soup_resource, Base_url):
    '''
    Responsible for finding links to different resources available on the page
    '''
    link_list_1st_page = []
    for link in soup_resource.find_all('a'):
        try:
            if 'Resource' in link.get('href'):
                link_list_1st_page.append(Base_url+link.get('href'))
        except:
            pass
    return link_list_1st_page


def extract_label(url):
    try:
        soup = url_parser(url)
        productDivs = soup.find('ul', {'class': 'list-unstyled'})
        label_list = productDivs.text.strip().split('\n\r\n')
    except:
        print ("Issue with the extract label function")
    return label_list[0].strip(), label_list[1].strip()

def discuss_tipic(url):
    try:
        soup = url_parser(url)
        productDivs = soup.find('ul', {'class': 'list-unstyled'})
        label_list = productDivs.text.strip().split('\n\r\n')
    except:
        print("Issue with the discuss topic function")
    return label_list[0].strip(), label_list[1].strip()

def exctract_display_text(resource_url):
    '''
    Extracts various information from label page
    '''
    soup_resource_result = url_parser(resource_url)
    table = soup_resource_result.find('table', {'class': 'table table-condensed'})

    global final_info
    rows = table.find_all('tr')
    row_cnt = 0
    for row in rows:
        cols = row.find_all('td')
        try:
            if 'DisplayText' in cols[0].text:
                return (cols[1].text.strip())
            else:
                pass

        except Exception as e:
            if row_cnt != 0:
                print("Exception Identified Table 1")
                print (str(e))
                print(resource_url)
            pass






def exctract_info_frm_reource_link(resource_url):
    '''
    Extracts various information from label page
    '''
    soup_resource_result = url_parser(resource_url)
    table = soup_resource_result.find('table', {'class': 'table table-condensed'})

    global final_info
    rows = table.find_all('tr')
    mapping_dict = {}
    mapping_dict['mentioned_in_A'] = []
    mapping_dict['mentioned_in_E'] = []
    mapping_dict['topic_E'] = []
    mapping_dict['topic_A'] = []
    mapping_dict['label'] = ""
    mapping_dict['chapter_Index'] = ""
    mapping_dict['Verse_Index'] = ""
    mapping_dict['Verse_display_text'] = ""
    mapping_dict['desc_ByJalalayn'] = []
    mapping_dict['desc_ByMuyasser'] = []

    mapping_dict['slightlySImilarEnglish'] = []
    mapping_dict['slightlySImilarArebic'] = []
    mapping_dict['stronglySImilarEnglish'] = []
    mapping_dict['stronglySImilarArebic'] = []
    mapping_dict['remarks'] = []
    row_cnt = 0
    for row in rows:
        cols = row.find_all('td')
        try:
            if "rdfs:label" in cols[0].text:
                label = cols[1].text.strip().split('\n\r\n')
                mapping_dict['label'] = label[1]
            elif 'DiscussTopic' in cols[0].text:
                elms = cols[1].select("td, a")
                eng_topic = []
                for topic in cols[1].text.strip().split('\n'):
                    if ":" in topic.replace('\r',"").strip() or topic.replace('\r',"").strip() == "":
                        pass
                    else:
                        eng_topic.append(topic)
                mapping_dict['topic_E'] = eng_topic
                link_lists =  [i.attrs["href"] for i in elms] #Finds the links
                for links in link_lists:
                    topic_A, topic_E = discuss_tipic(links)
                    if re.match('[a-z|A-Z]+', topic_E):
                        mapping_dict['topic_A'].append(topic_A)
                    else:
                        mapping_dict['topic_A'].append(topic_E)

            elif 'SlightlySimilar' in cols[0].text:
                elms = cols[1].select("td, a")
                eng_topic = []
                arb_topic = []
                for topic in cols[1].text.strip().split('\n'):
                    if ":" in topic.replace('\r',"").strip() or topic.replace('\r',"").strip() == "":
                        pass
                    else:
                        eng_topic.append(topic)
                mapping_dict['slightlySImilarEnglish'] = eng_topic
                link_lists =  [i.attrs["href"] for i in elms] #Finds the links
                for links in link_lists:
                    mapping_dict['slightlySImilarArebic'].append(exctract_display_text(links))
            elif 'StronglySimilar' in cols[0].text:
                elms = cols[1].select("td, a")
                eng_topic = []
                for topic in cols[1].text.strip().split('\n'):
                    if ":" in topic.replace('\r', "").strip() or topic.replace('\r', "").strip() == "":
                        pass
                    else:
                        eng_topic.append(topic)
                mapping_dict['stronglySImilarEnglish'] = eng_topic
                link_lists = [i.attrs["href"] for i in elms]  # Finds the links
                for links in link_lists:
                    mapping_dict['stronglySImilarArebic'].append(exctract_display_text(links))

            elif "ChapterIndex" in cols[0].text:
                mapping_dict['chapter_Index'] = cols[1].text.strip()
            elif 'DisplayText' in cols[0].text:
                mapping_dict['Verse_display_text'] = cols[1].text.strip()
            elif 'VerseIndex' in cols[0].text:
                mapping_dict['Verse_Index'] = cols[1].text.strip()
            elif 'descByJalalayn' in cols[0].text:
                mapping_dict['desc_ByJalalayn'] = cols[1].text.strip()
            elif 'descByMuyasser' in cols[0].text:
                mapping_dict['desc_ByMuyasser'] = cols[1].text.strip()
            else:
                pass

        except Exception as e:
            if row_cnt != 0:
                print("Exception Identified Table 1")
                print (str(e))
                print(resource_url)
            pass


    table2 = soup_resource_result.find('table', {'id': 'tableAddInfo','class': 'table table-condensed'})
    rows = table2.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        try:
            if 'MentionedIn' in cols[2].text:
                elms = cols[0].select("td, a")
                A_label, E_label = extract_label(elms[0].attrs["href"])
                mapping_dict['mentioned_in_A'].append(A_label)
                mapping_dict['mentioned_in_E'].append(cols[1].text.replace('\r',"").replace('\n',"").strip())
        except Exception as e:
            if row_cnt != 0:
                print("Exception Identified Table 2")
                print (str(e))
                print(resource_url)
            pass
        row_cnt += 1
    mapping_dict['slightlySImilarArebic'] = list(filter(lambda a: a != None, mapping_dict['slightlySImilarArebic']))
    mapping_dict['stronglySImilarArebic'] = list(filter(lambda a: a != None, mapping_dict['stronglySImilarArebic']))
    if len(mapping_dict['mentioned_in_E']) != len(mapping_dict['mentioned_in_A']):
        mapping_dict['remarks'].append('Wrong in Mentioned in')
    if len(mapping_dict['topic_A']) != len(mapping_dict['topic_E']):
        mapping_dict['remarks'].append("Topic Issue")
    if len(mapping_dict['label'].strip()) == "":
        mapping_dict['remarks'].append("Label Issue")
    if len(mapping_dict['stronglySImilarArebic']) != len(mapping_dict['stronglySImilarEnglish']):
        mapping_dict['remarks'].append("Strongly Similar sentence issue")
    if len(mapping_dict['slightlySImilarArebic']) != len(mapping_dict['slightlySImilarEnglish']):
        mapping_dict['remarks'].append("Slightly Similar sentence issue")



    final_info.append(mapping_dict)
    print (final_info)





def main():
    global final_info

    Base_url = 'http://quranontology.com'
    url = 'http://quranontology.com/Concept'
    global df, row_num
    df = pd.DataFrame( columns=['Sr No', 'Content', 'Label_A'])
    row_num = 1
    def recur(concept_url, count):
        threads = []
        global final_info
        print ("last page link ", concept_url)
        t1 = time.time()
        soup_resource = url_parser(concept_url)
        resource_url_list = find_resource(soup_resource, Base_url)
        for resource in resource_url_list:
            resource = threading.Thread(target=exctract_info_frm_reource_link, args=(resource, ))
            resource.start()
            threads.append(resource)
        for j in threads:
            j.join()
        print(time.time() - t1)

        count += 1
        gc.collect()
        try:
            page_num = re.findall('page=([0-9]+)', concept_url)[0]
        except:
            page_num = 1

        if count % 1 == 0 and count != 0:
            df = pd.DataFrame(final_info)
            df.to_excel(str(page_num) + '.xlsx', index=False)

        next_page_link = find_next_page(soup_resource, Base_url)
        if next_page_link != False:
            final_info = []
            recur(next_page_link, count)



    starting_url = 'http://quranontology.com/Concept/Verse?page=1&pageSize=20'
    recur(starting_url, count = 0)


# main()


"""
For Aggregating the files in one file
"""


def aggregate_file(file_names):
    cnt = 0
    for name in file_names:
        if cnt == 0:
            df = pd.read_excel(name)
        else:
            df_tmp = pd.read_excel(name)
            df = df.append(df_tmp, ignore_index = True)
        cnt+=1
    df.to_excel('result.xlsx', index = False)
