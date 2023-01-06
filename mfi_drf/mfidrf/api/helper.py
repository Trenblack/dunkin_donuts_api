import datetime
import uuid
from django.db import connection
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
import collections
import xml.etree.ElementTree as ET
from .models import Employee, Source, Payment, Batch
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
import json

BATCH_DB_NAME = "batch.db"

def get_batches():
    #batch_id = "BAT_"+ uuid.uuid4().hex[:10]
    #now = datetime.datetime.now()
    #return JsonResponse(json.dumps(serializers.serialize('json', Batch.objects.all())))
    query = Batch.objects.all().values()
    d = []
    for each in query:
        cur_data = {
            "batch_id": each["batch_id"],
            "date_approved": json.loads(each['data'])["date_approved"]
        }
        cur = json.loads(each['data'])['data']
        if "total_cost" in cur:
            cur_data['status'] = "IN PROGRESS"
            total = sum(x['initial_owed_count'] for x in cur['sources'])
            paid = sum(x['paid_so_far_count'] for x in cur['sources'])
            cur_data['payments_remaining'] = total-paid
        else:
            cur_data['status'] = 'INITIALIZING'
            cur_data['payments_remaining'] = "..."
        d.append(cur_data)
    return JsonResponse({'batch_list': list(d)})


def newParse(file, approved=False):
    # if batch_id already in batch, return 'already approved'
    branch_amt = collections.defaultdict(float)
    branch_cnt = collections.defaultdict(int)
    source_amt = collections.defaultdict(float)
    source_cnt = collections.defaultdict(int)
    total = 0

    batch_id = "BAT_"+ uuid.uuid4().hex[:10]
    now = datetime.datetime.now().strftime("%B %d, %Y at %H:%M:%S")
    if approved:
        b = Batch()
        b.batch_id = batch_id
        b.data = json.dumps({"date_approved":now, "data":{}}, cls=DjangoJSONEncoder)
        b.save()

    curEmp = Employee()
    curSource = Source()
    curPayment = Payment()
    sourceMap = {}
    pays = []

    context = ET.iterparse(file, events=("start", "end"))

    for index, (event, elem) in enumerate(context):
        # Get the root element.
        if index == 0:
            root = elem 
        # Using array index assumes XML will preserve format order.
        # If we cannot make this assumption, check each elem.tag individually.
        if event == "end" and elem.tag == "Employee":
            curEmp = Employee.objects.get(pk=elem[0].text)
            #arr = [elem[x].text for x in range(len(elem))]
            #d_id, d_branch, f_name, l_name, dob, phone = arr
            #curEmp.d_id, curEmp.d_branch, = d_id, d_branch
            root.clear()
            elem.clear()
        if event == "end" and elem.tag == "Payor":
            # arr = [elem[x].text for x in range(len(elem)-1)]
            # d_id, aba_routing, acc_num, name, dba, ein = arr
            #curSource.d_id = d_id
            d_id = elem[0].text
            if d_id in sourceMap:
                curSource = sourceMap[d_id]
            else:
                curSource = Source.objects.get(pk=d_id)
                sourceMap[d_id] = curSource
            root.clear()
            elem.clear()
        # if event == "end" and elem.tag == "Payee":
        #     plaid, loan_acc = elem[0].text, elem[1].text
        #     root.clear()
        if event == "end" and elem.tag == "Amount":
            if approved:
                curPayment.amount = elem.text
                curPayment.pay_to = curEmp
                curPayment.pay_from = curSource
                curPayment.batch_id = batch_id
                curPayment.last_updated = now
                #curPayment.save()
                pays.append(curPayment)
                curPayment = Payment()
            amt = float(elem.text[1:])
            total += amt
            branch_amt[curEmp.d_branch] += amt
            branch_cnt[curEmp.d_branch] += 1
            source_amt[curSource.d_id] += amt
            source_cnt[curSource.d_id] += 1
            root.clear()
            elem.clear()

    Payment.objects.bulk_create(pays)

    branches = [
        {
            "branch_id": k, 
            "initial_owed": "$" + str(round(v,2)),
            "initial_owed_count": branch_cnt[k],
            "paid_so_far": "$0", 
            "paid_so_far_count":0,
            "last_updated": now
        } for k,v in branch_amt.items()
    ]
    sources = [
        {
            "dunkin_id": k, 
            "initial_owed": "$" + str(round(v,2)),
            "initial_owed_count": source_cnt[k],
            "paid_so_far": "$0", 
            "paid_so_far_count":0,
            "last_updated": now
        } for k,v in source_amt.items()
    ]
    #sources = [(k,"$" + str(round(v,2)), source_cnt[k]) for k,v in source_amt.items()]
    data = {
        "total_cost": str(round(total,2)),
        "total_payments":sum(source_cnt.values()),
        "branches": branches,
        "sources": sources,
    }
    if approved:
        b = Batch.objects.get(batch_id=batch_id)
        b.data = json.dumps({"date_approved":now, "data":data}, cls=DjangoJSONEncoder)
        b.save()
    return data

def succint_view(file):
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
        if event == "end" and elem.tag == "Payor":
            # ... process record elements ...
            cur[1] = elem[0].text
            root.clear()
        if event == "end" and elem.tag == "Amount":
            # ... process record elements ...
            amt = float(elem.text[1:])
            total += amt
            branch_amt[cur[0]] += amt
            branch_cnt[cur[0]] += 1
            source_amt[cur[1]] += amt
            source_cnt[cur[1]] += 1
            root.clear()

    branches = [(k,"$" + str(round(v,2)), branch_cnt[k]) for k,v in branch_amt.items()]
    sources = [(k,"$" + str(round(v,2)), source_cnt[k]) for k,v in source_amt.items()]
    data = {
        "total_cost": str(round(total,2)),
        "total_payments":sum([s[2] for s in sources]),
        "branches": branches,
        "sources": sources,
    }
    return data

def qs_to_csv_response(qs, filename):
    sql, params = qs.query.sql_with_params()
    sql = f"COPY ({sql}) TO STDOUT WITH (FORMAT CSV, HEADER, DELIMITER E'\t')"
    filename = f'{filename}-{timezone.now():%Y-%m-%d_%H-%M-%S}.csv'
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={filename}'
    with connection.cursor() as cur:
        sql = cur.mogrify(sql, params)
        cur.copy_expert(sql, response)
    return response