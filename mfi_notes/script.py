file_path = r'dunkin.xml'
import xml.etree.ElementTree as ET
import collections
import json

class Employee:
    def __init__(self):
        self.d_id = ""
        self.mfi_created = ""
        self.d_branch = ""
        self.first_name = ""
        self.last_name = ""
        self.phone = ""
        self.plaid_id = ""
        self.loan_acc = ""
    def __str__(self):
        return json.dumps(self.__dict__)

class Source:
    def __init__(self):
        self.d_id = ""
        self.mfi_created = ""
        self.aba_routing = ""
        self.account_number = ""
        self.name = ""
        self.dba = ""
        self.ein = ""
    def __str__(self):
        return json.dumps(self.__dict__)

class Payment:
    def __init__(self):
        self.batch_id = ""
        self.pay_to = ""
        self.pay_from = ""
        self.amount = ""
        self.status = "NOT EXECUTED"
        self.last_updated = ""
    def __str__(self):
        return json.dumps(self.__dict__)


# def user_table(file):
#     context = ET.iterparse(file, events=("start", "end"))
#     newEmp = Employee()
#     newSource = Source()
#     curPayment = Payment()

emp_list = []
source_list = []
payment_list = []

def helper(file):
    context = ET.iterparse(file, events=("start", "end"))
    batch_id = 'xd'
    cur = ["", ""]
    newEmp = Employee()
    newSource = Source()
    curPayment = Payment()
    empSeen = set()
    sourceSeen = set()
    cur_employee_id = ""
    cur_source_id = ""
    swap = 1
    for index, (event, elem) in enumerate(context):
        # Get the root element.
        #print(index, event, elem, elem.text)
        if index == 0:
            root = elem # might not need root at all
        if event == "end" and elem.tag == "DunkinId":
            # employee_id
            if swap > 0:
                cur_employee_id = elem.text
                newEmp.d_id = cur_employee_id
                print(cur_employee_id)
                curPayment.pay_to = cur_employee_id
            else:
                cur_source_id = elem.text
                newSource.d_id = cur_source_id
                curPayment.pay_from = cur_source_id
            swap *= -1
            elem.clear()
        elif event == "end" and elem.tag == "DunkinBranch":
            # ... process record elements ...
            cur_employee_branch = elem.text
            cur[0] = cur_employee_branch
            newEmp.d_branch = cur_employee_branch
            elem.clear()
        elif event == "end" and elem.tag == "FirstName":
            # ... process record elements ...
            cur_employee_fname = elem.text
            newEmp.first_name = cur_employee_fname
            elem.clear()
        elif event == "end" and elem.tag == "AccountNumber":
            cur_source_acc = elem.text
            newSource.account_number = cur_source_acc
            elem.clear()
        elif event == "end" and elem.tag == "Amount":
            # ... process record elements ...
            amt = float(elem.text[1:])
            curPayment.amount = amt
            curPayment.batch_id = batch_id
            if cur_employee_id not in empSeen:
                emp_list.append(newEmp)
                empSeen.add(cur_employee_id)
            if cur_source_id not in sourceSeen:
                source_list.append(newSource)
                sourceSeen.add(cur_source_id)
            payment_list.append(curPayment)
            newEmp = Employee()
            newSource = Source()
            curPayment = Payment()
            #
            cur = ["", ""]
            elem.clear()
        root.clear()

helper(file_path)
for x in emp_list:
    print(x)
for x in source_list:
    print(x)
for x in payment_list:
    print(x)

    # d_id, first_name, last_name, email


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