from rest_framework.response import Response
from rest_framework.decorators import api_view
import collections
import xml.etree.ElementTree as ET
import uuid
from .models import Employee, Source, Payment, Batch
from .helper import qs_to_csv_response, succint_view, get_batches, newParse



@api_view(["GET", "POST"])
def getCsv(request):
    response = Response()
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "*"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "*"
    if request.method == "POST":
        print('kek_-----')
        print(request.data)
        csv_type, batch_id = request.data['type'], request.data['batch_id']
        if csv_type == "payments":
            return qs_to_csv_response(Payment.objects.all(), 'payments') 
        elif csv_type == "sources":
            return Response({'batchId':batch_id})
    if request.method == "GET":
        response.data = get_batches()
        return response

@api_view(["GET", "POST"])
def getData(request):
    response = Response()
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "*"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "*"
    if request.method == "GET":
        #return qs_to_csv_response(Payment.objects.all(), 'sources')
        pass
    elif request.method == "POST":
        t = request.FILES['upload_file']
        response.data = succint_view(t.file)
    return response



@api_view(["GET", "POST"])
def processData(request):
    print('yes')
    # Create batch data, SQL table, and Map 1 in one go
    response = Response()
    # response["Access-Control-Allow-Origin"] = "*"
    # response["Access-Control-Allow-Methods"] = "*"
    # response["Access-Control-Max-Age"] = "1000"
    # response["Access-Control-Allow-Headers"] = "*"
    # x, created = Employee.objects.update_or_create(defaults=data)
    # if created:
    #     x.save()
    if request.method == "GET":
        response.data = {2:"k"}
    elif request.method == "POST":
        t = request.FILES['upload_file']
        response.data = newParse(t.file, approved=True)
    return response    

def sql_helper(file):
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
        if index == 0:
            root = elem # might not need root at all
        if event == "end" and elem.tag == "DunkinId":
            # employee_id
            if swap > 0:
                cur_employee_id = elem.text
                newEmp.d_id = cur_employee_id
                if cur_employee_id in empSeen:
                    curPayment.pay_to = Employee.objects.get(d_id=cur_employee_id)
            else:
                cur_source_id = elem.text
                newSource.d_id = cur_source_id
                if cur_source_id in sourceSeen:
                    curPayment.pay_from = Source.objects.get(d_id=cur_source_id)
            root.clear()
            swap *= -1
        elif event == "end" and elem.tag == "DunkinBranch":
            # ... process record elements ...
            cur_employee_branch = elem.text
            cur[0] = cur_employee_branch
            newEmp.d_branch = cur_employee_branch
            root.clear()
        elif event == "end" and elem.tag == "FirstName":
            # ... process record elements ...
            cur_employee_fname = elem.text
            newEmp.first_name = cur_employee_fname
            root.clear()
        elif event == "end" and elem.tag == "LastName":
            # ... process record elements ...
            newEmp.last_name = elem.text
            root.clear()
        elif event == "end" and elem.tag == "PhoneNumber":
            # ... process record elements ...
            newEmp.phone = elem.text
            root.clear()
        elif event == "end" and elem.tag == "ABARouting":
            newSource.aba_routing = elem.tag
            root.clear()
        elif event == "end" and elem.tag == "AccountNumber":
            cur_source_acc = elem.text
            newSource.account_number = cur_source_acc
            root.clear()
        elif event == "end" and elem.tag == "Name":
            newSource.name = elem.text
            root.clear()
        elif event == "end" and elem.tag == "DBA":
            newSource.dba = elem.text
        elif event == "end" and elem.tag == "EIN":
            newSource.ein = elem.text
            root.clear()
        elif event == "end" and elem.tag == "PlaidId":
            newEmp.plaid_id = elem.text
            root.clear()
        elif event == "end" and elem.tag == "LoanAccountNumber":
            newEmp.loan_acc = elem.text
            root.clear()
        elif event == "end" and elem.tag == "Amount":
            # ... process record elements ...
            amt = float(elem.text[1:])
            curPayment.amount = amt
            curPayment.batch_id = batch_id
            if cur_employee_id not in empSeen:
                newEmp.save()
                # x, created = Employee.objects.update_or_create(newEmp)
                # if created:
                #     x.save()
                empSeen.add(cur_employee_id)
                curPayment.pay_to = newEmp
            if cur_source_id not in sourceSeen:
                # x, created = Employee.objects.update_or_create(newSource)
                # if created:
                #     x.save()
                newSource.save()
                sourceSeen.add(cur_source_id)
                curPayment.pay_from = newSource
            curPayment.save()
            # x, created = Employee.objects.update_or_create(curPayment)
            # if created:
            #     x.save()
            newEmp = Employee()
            newSource = Source()
            curPayment = Payment()
            #
            cur = ["", ""]
            root.clear()


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
Payment:
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
- Mention that we can include "Owed/Received" options, and this would 
be good for double sided ledger verify check, but for now and the sake
of simplicity, i am going to opt to keep them independant from payments.
- Need an independant ledger also cuz returned money and shit...
- ledger is ONLY credit/debit, sum=0. Else, you're thinking of wallet.

Seperating "batch" data from "user/employee" data.
- Decided to keep a consistent database of users and payers, since it 
will be largely the same people every 2 weeks. Data that is independant
of the payment date.
- XML required also can be greatly reduced to just "to/from/amt"

User Payment option:
user table 
-> wallet
    owed, received, payments
                    -> payment object
-> ledger ID
    debit, credit

Also lets us run a query on a user, "total received/owed, by batch"
- Wallet does not need owed/received technically cuz it can be calculated
from the payments objects themselves. owed/received will increase read
speed but how often do we read it?

- Wide column datastore like Cassandra for large one to many 
relationship? TIL.
- So instead of wallet object, you just have wide column for user to
payments



First, make the Schema, then talk about why Sql or noSQl, how to do it
in noSql, and then say for simplicity of this assignment, you use SQL.
    - Also, ACID!

Okay, so MAYBE SAY THIS:
Both

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