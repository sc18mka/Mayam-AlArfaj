import pandas as pd
import re
import math #For Mathematical Operations
from collections import Counter #Counts the occurence of a value in a list
import ast #Helps in converting a string list to an object list
import sys #For existing the module

path ='C:/Users/Maryam/Desktop/similarity measure/' #Give the path of the excel files
df = pd.read_excel(path + 'Semantic Quran Knowledge Base.xlsx')
df2 = df.loc[(df['Concepts_A'] != "[]") | (df['Topics_A'] != "[]")]
df2.to_excel('new_result.xlsx', index = False)
df = df2

sentence_flag = input("Type '1' if you want to enter an English verse, or type '2' if you want to enter an Arabic verse\n")

if sentence_flag == "1" or sentence_flag == "2":
    pass
else:
    print ("Wrong input was given, please give either '1' or '2' as the value")
    print ("Exiting the module...")
    sys.exit()

decison_flag = input("Type '1' if you want to see all the similar verses, or type '2' if you want to see similarity between 2 verses\n")

if decison_flag == "1":
    Ref_sent = input('\nPlease enter the reference verse\n')
elif decison_flag == "2":
    Ref_sent = input('\nPlease enter the reference verse\n')
    sent = input('\nPlease enter the verse you want to compare\n')
else:
    print ("Wrong Input was given, exiting the module...")
    sys.exit()


if decison_flag == "1":
    if sentence_flag == "1":
        if Ref_sent not in df.Translation.tolist():
            print("The input verse is not part of the given corpus. Exiting the system..")
            sys.exit()

    elif sentence_flag == "2":
        if Ref_sent not in df.Verse.tolist():
            print("The input verse is not part of the given corpus. Exiting the system..")
            sys.exit()


if decison_flag == "2":
    if sentence_flag == "1":
        if Ref_sent not in df.Translation.tolist():
            print("The input verse is not part of the given corpus. Exiting the system..")
            sys.exit()
        if sent not in df.Translation.tolist():
            print("The input verse is not part of the given corpus. Exiting the system..")
            sys.exit()

    elif sentence_flag == "2":
        if Ref_sent not in df.Verse.tolist():
            print("The input verse is not part of the given corpus. Exiting the system..")
            sys.exit()
        if sent not in df.Verse.tolist():
            print("The input verse is not part of the given corpus. Exiting the system..")
            sys.exit()




def counter_cosine_similarity(c1, c2):
    """
    Calculates Cosine Similarity
    """
    c1 = Counter(c1)
    c2 = Counter(c2)
    terms = set(c1).union(c2)
    dotprod = sum(c1.get(k, 0) * c2.get(k, 0) for k in terms)
    magA = math.sqrt(sum(c1.get(k, 0)**2 for k in terms))
    magB = math.sqrt(sum(c2.get(k, 0)**2 for k in terms))
    return dotprod / (magA * magB)

def sentence_simalrity(sent, Ref_sent, df):
    if sentence_flag == "1":
        sent_mentioned_in = ast.literal_eval(df.loc[df['Translation'] == sent, 'Concepts_E'].iloc[0])
        ref_sent_mentioned_in = ast.literal_eval(df.loc[df['Translation'] == Ref_sent, 'Concepts_E'].iloc[0])
        sent_topic = ast.literal_eval(df.loc[df['Translation'] == sent, 'Topics_E'].iloc[0].replace("'s",'s'))
        ref_sent_topic = ast.literal_eval(df.loc[df['Translation'] == Ref_sent, 'Topics_E'].iloc[0].replace("'s", "s"))

    elif sentence_flag == "2":
        sent_mentioned_in = ast.literal_eval(df.loc[df['Verse'] == sent, 'Concepts_A'].iloc[0])
        ref_sent_mentioned_in = ast.literal_eval(df.loc[df['Verse'] == Ref_sent, 'Concepts_A'].iloc[0])
        sent_topic = ast.literal_eval(df.loc[df['Verse'] == sent, 'Topics_A'].iloc[0].replace("'s", 's'))
        ref_sent_topic = ast.literal_eval(df.loc[df['Verse'] == Ref_sent, 'Topics_A'].iloc[0].replace("'s", "s"))

    else:
        print ("Wrong input was given. Exiting the module...")
        sys.exit()

    if (len(ref_sent_topic) == len(sent_topic) == 0) and (len(sent_mentioned_in) == len(ref_sent_mentioned_in) == 0):
        if decison_flag == "2":
            print ("Not enough information presents. Topics are empty in both verses")
            return
        else:
            return

    c_sent_topic = sent_topic
    c_ref_sent_topic = ref_sent_topic
    c_mentioned_in = sent_mentioned_in
    c_ref_mentioned_in = ref_sent_mentioned_in
    try:
        topic_similairy = counter_cosine_similarity(c_sent_topic, c_ref_sent_topic)

    except:
        topic_similairy = 0
    try:
        Concept_Similarity = counter_cosine_similarity(c_mentioned_in, c_ref_mentioned_in)
    except:
        Concept_Similarity = 0

    if len(c_sent_topic) == len(c_ref_sent_topic) == 0:
        if (len(c_mentioned_in)>=2 and  len(c_ref_mentioned_in)>=1)  or (len(c_mentioned_in)>=1 and  len(c_ref_mentioned_in)>=2):
            return (Concept_Similarity)
        else:
            return 0
    elif len(c_mentioned_in) == len(c_ref_mentioned_in) == 0:
        return (topic_similairy)

    else:
        return (2*topic_similairy + Concept_Similarity)/3

if decison_flag == "2":
    print("\n")
    print (sentence_simalrity(sent, Ref_sent, df))

if decison_flag == "1":
    similarity_dict = {}
    similarity_dict['Reference_Verse'] = []
    similarity_dict['Similar_Verses'] = []
    similarity_dict['Similarity_Score'] = []

    if sentence_flag == "1":
        for translation in  df.Translation.tolist():
            score = sentence_simalrity(translation, Ref_sent, df)
            if score is not None:
                if score >= 0.5 and translation != Ref_sent:
                    similarity_dict['Reference_Verse'].append(Ref_sent)
                    similarity_dict['Similar_Verses'].append(translation)
                    similarity_dict['Similarity_Score'].append(score)

        pd.DataFrame({k: pd.Series(l) for k, l in similarity_dict.items()}).to_excel("similarity_results.xlsx", index = False)

        print('\nThe result is saved in "similarity_results" Excel file.')

    else:
        for translation in  df.Verse.tolist():
            score = sentence_simalrity(translation, Ref_sent, df)
            # print (score)
            if score is not None:
                if score >= 0.5 and translation != Ref_sent:
                    similarity_dict['Reference_Verse'].append(Ref_sent)
                    similarity_dict['Similar_Verses'].append(translation)
                    similarity_dict['Similarity_Score'].append(score)
        # print (similarity_dict)

        pd.DataFrame({k: pd.Series(l) for k, l in similarity_dict.items()}).to_excel("similarity_results.xlsx", index=False)

        print('\nThe result is saved in "similarity_results" Excel file.')
