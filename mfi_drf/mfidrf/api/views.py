from rest_framework.response import Response
from rest_framework.decorators import api_view
import collections
import xml.etree.ElementTree as ET
import uuid
from .models import Employee


@api_view(["GET", "POST"])
def getData(request):
    response = Response()
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "*"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "*"
    if request.method == "GET":
        response.data = {2:"k"}
    elif request.method == "POST":
        t = request.FILES['upload_file']
        response.data = helper(t.file)
    return response

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
        "total_cost": str(round(total,2)),
        "total_payments":sum([s[2] for s in sources]),
        "branches": branches,
        "sources": sources,
        "batch_id": "BAT_"+ uuid.uuid4().hex[:10]
    }
    return data

@api_view(["GET", "POST"])
def processData(request):
    print('yes')
    # Create batch data, SQL table, and Map 1 in one go
    response = Response()
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "*"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "*"
    data = {
        "dunkin_id": '10',
        "mfi_acc_id":"acc_xd",
        "name": "tren black"
    }
    x, created = Employee.objects.update_or_create(defaults=data)
    if created:
        x.save()
    response.data = {'status':'idk'}
    # if request.method == "GET":
    #     response.data = {2:"k"}
    # elif request.method == "POST":
    #     t = request.FILES['upload_file']
    #     response.data = helper(t.file)
    return response    


"""
Ledger:
batch
    date_created: timestamp
    total_cost: string
    total_payments: int
    branches
        [
            (id, need_to_recieve, received_so_far, payments_so_far)
        ]
    sources
        [
            (id, need_to_pay, paid_so_far, payments_so_far)
        ]

- GetCSV(batchId, type(branches or sources))
___
payment_id: int
batch_id: BAT_uuid4
to: d_id (dunkin_id)
from: d_id
amt: string
status: [not executed, pending, approved]
created_at: timestamp
last_updated: timestamp
eta: timestamp
mfi_payment_id: int

- GetCSV(batchId, type=payments)
    - SQL command to get by batch_id from payemts table
- CreateCSV with info from MAP[d_id]

___
(dont have to worry about branche since its irrelevant to payemnts)
MAP 1
d_id:
    mfi_acc_id: "",
    type: "emp or corp",
    first_name: "",
    "plaid_id",
    ..

MAP 2
mfi_acc_id:
    d_id

Instead of these Maps, we can have a SQL table for Employees/Entities?
___
Add all to queue 1:
Process Payment Queeu

For each payment_id in q1:
    If to/from d_id does not have mfi_acc_id in map1:
        send to q2
    else
        get payment from payment SQL using payment_id
        use map 1 to convert to mfi_acc_id
        send Payment to MFI 
        MFI response -> Update Payments SQL, Ledger

For each payment_id in q2:
    get payment from payment SQL using payment_id
    use map1 for info of to/from
    use that info to create entity/account
    update the mfi_acc_id field in map 1
    create mfi_acc_id row in map 2
    send payment_id to queue 1

___
Web hooks:

Mfi -> server with acc_info
use map1/2 to get info to update Payments SQL, Ledger


___
- GetBatches()
    Lists all batches
"""