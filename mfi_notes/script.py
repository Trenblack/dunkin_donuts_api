file_path = r'dunkin.xml'
import xml.etree.ElementTree as ET
import collections


def helper(file):
    branch_amt = collections.defaultdict(float)
    branch_cnt = collections.defaultdict(int)
    source_amt = collections.defaultdict(float)
    source_cnt = collections.defaultdict(int)
    total = 0

    context = ET.iterparse(file, events=("start", "end"))
        
    cur = ["", ""]
    for index, (event, elem) in enumerate(context):
        # Get the root element.
        if index == 0:
            root = elem
        if event == "end" and elem.tag == "DunkinBranch":
            # ... process record elements ...
            cur[0] = elem.text
            root.clear()
        if event == "end" and elem.tag == "AccountNumber":
            # ... process record elements ...
            cur[1] = elem.text
            root.clear()
        if event == "end" and elem.tag == "Amount":
            # ... process record elements ...
            amt = float(elem.text[1:])
            total += amt
            branch_amt[cur[0]] += amt
            branch_cnt[cur[0]] += 1
            source_amt[cur[1]] += amt
            source_cnt[cur[1]] += 1
            cur = ["", ""]
            root.clear()

    branches = [(k,"$" + str(round(v,2)), branch_cnt[k]) for k,v in branch_amt.items()]
    sources = [(k,"$" + str(round(v,2)), source_cnt[k]) for k,v in source_amt.items()]
    data = {
        "total": "$"+str(round(total,2)),
        "branches": branches,
        "sources": sources
    }
    return data

print(helper(file_path))

""" 
from xml.etree.ElementTree import iterparse
#from cElementTree import iterparse
import pandas as pd
import collections

file_path = r'dunkin.xml'
branch_list = collections.defaultdict(dict)


for _, elem in iterparse(file_path, events=("end",)):
    cur = ["",0]
    if elem.tag == "DunkinBranch":
        cur[0] = elem.text
    if elem.tag == "Amount":
        cur[1] = float(elem.text[1:])
    # if elem.tag == "row":
    #     for child in elem:
    #         print(child.tag, child.attrib)
    #         for c2 in child:
    #             print("\t {}, {}".format(c2.tag, c2.attrib))
    #             for c3 in c2:
    #                 print("\t \t {}, {}".format(c3.tag, c3.text))
    #    print(elem.attrib)
        # dict_list.append({'Employee': elem.attrib['Employee'],
        #                   'UserId': elem.attrib['UserId'],
        #                   'Name': elem.attrib['Name'],
        #                   'Date': elem.attrib['Date'],
        #                   'Class': elem.attrib['Class'],
        #                   'TagBased': elem.attrib['TagBased']})

        # dict_list.append(elem.attrib)      # ALTERNATIVELY, PARSE ALL ATTRIBUTES

        elem.clear()
    print(cur)

#df = pd.DataFrame(dict_list)
#print(df)
"""