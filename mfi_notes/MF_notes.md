# Summary
Build a dashboard that can do these things:
    1. upload XML roster of employees
    2. Make payments to student loans
    3. Generate reports

# System Design


# Front end
React and MUI

# Back end
- Maybe just need a database?
- Use AWS serverless tbh.

# Overall
- Priority is not performance, it is consistancy and correctness. We want to make sure that nobody is double charged, payments arent marked as completed when they're not, and that failed payments are handeled properly. At the same time, we want to give Dunkin the ability to view and manage their data well. We also want to keep the design simple.
- 50k requests over 2 weeks. The key here is to make sure it is safe from possible errors as finance errors are deadly.
- Also, accounting and data is important. You want access to all data for
like tax reasons and just general post or end of year calculations and
budgeting.

# Problem #: Processing Large XML files
- Back end? Front end? 

# Problem #: Picking a Data Structure
- Aggregated/Summary Data
- Indivudal data/status of every payment
- SQL? It will be ACID.
- PER BATCH (BATCH processing)
- One table with "batch" as a param, query for that batch
- Document where each "batch" is a different object.

How to design Data such that we have both aggregated data, and individual data. Along with that, we have this data for each XML batch. 
    - XML batch table.
    - XML Batch
        - [...source accounts]
            - [total paid, total_must_pay, payments_completed, payments_must_complete]

How will aggregate data work with states of each payment? What if we want a report when only half of the payments of this branch are settled?
    - Start with total debt, total, and lower it
    - (total payed, total need to pay)


Indivudal Data:
- Fast writes
- Can slice and dice data however needed
- Can recalculate numbers
BUT
- Slow reads
- Costly for large scale

Agregate Data:
- Fast reads
- data is ready for decision making
BUT
- Can only query data the way it was aggregated
- Requires data aggregation pipeline? May not be true for what you're doing here.

- Scale: We know for sure it'll be around 50k changes, once every two weeks. SQL is fine for scale. 
- Payment SQL table should not care about ledger at all, but have a seperate SQL table as a ledger that DOES NOT care about the branch at all. Overall, just keep this same ledger table for eternity, and you can occasionally clean it up. This is just a check


Schema for Aggr (table within batch)
- ID
- Type: "source" or "branch"
- Balance Due (branch is -, source is +)
- How many Payments they each expect/made


Actually, YEAH. Create the batch when you first send in the data to get it back. If they discard it, delete the aggr batch from the doc. If approved, just have to send create the SQL data after the fact.

# Problem #: Same Student, Multiple Payment
- Seperate Payments (better for indivudal data)
- Combine (less requests made)
- Batch or Stream processing?
    - Payment object table: [from, to, many-to-1: source_payments, amt]
    - Source_payments table: [every indivudal row]

# Problem #: Displaying Data Before Approving
- Displaying Aggregated/Summary Data
- Individual data? Search? Ctrl F? Custom search bar
    - Large tables, rendering rows?
    - May just say "Choosing to ignore this problem for now, but heres how I could solve this."
    - Pagination?

# Problem #: Failed Payments 
- Some fail, some don't?
- Reversal?
- Even if the payment works but we fail to get a response, if the user clicks "pay" again, it'll get the same completed update without sending it again, idemp key.

# Problem #: Double Payments
- Idemp key
- Idempt key by file, and another one for payment

# Problem #: Inconsistent Data
- Double Ledger
    - All employees?
    - One for each source?
    - One for each branch? Then branch has to be a diff table...
    - Maybe do the double ledge in the aggregate shit
    - Double Ledge idea: (5 sources), (30 branches). SOLVES BOTH CSV PROBLEMS!!!! SO FIRE.
- Nighly service to keep up to date

# Problem #: Pay in/out Flow
- When should the XML upload data be sent to a DB? After uploaded? Or after approved?
    - Maybe put in a middle database so you dont have to recompute once it approves.
    - Or hash the file and save in cache. This also prevents repeat submission of the same file. 
        - What if someone canceled the prev file or it failed and they DO want to try the same file again?
- Queue
    - What if queue goes down? How to keep data up?
- Retry Queue
- When to update Ledger? 
- When to update website with "success" feedback?
- Webhooks?
- Need to crate MFI resources... (entities, acc, payment)

XML -> Create Batch -> Display Batch -> Approve Batch -> Batch queue -> Easy Retrieve of Batch Data

So then how do we get data of indivudal payment per batch?
    - Might have to legit just be 2 SQL databases that we update. 
    - MFI -> Ping a agr_payment is complete -> updates agr_payment sql table -> updates all entries of individual row sql table that got put into that -> use that data to generate CSV of each payment.
    - I guess ultimately, these 2 SQL databases are the real meat. The aggregate data are just basically some internet hashmaps to prevent us from having to query often.
    - Or I guess you only need 1 table for each individual payment. When MFI returns that a users payment is complete, we just update each inidivudal payment row that relied on it?
    - Once a night, do the SQL query and make sure it adds up.


    Asynchronously, the PSP calls the payment service with the payment status via a webhook. The webhook is an URL on the payment system side that was registered with the PSP during the initial setup with the PSP. When the payment system receives payment events through the webhook, it extracts the payment status and updates the payment_order_status field in the Payment Order database table.   

Possible status:
unprocessed -> pending -> completed/failed
- Updated by Webhooks

Or another option for "upload xml":
1. Click/Drag the XML file on
2. Client process the file, creates ledger locally
3. Display data, client -> Send back approve/deny
4. If approve, send 2 requests. 1 for creating ledger, 1 for SQL.

Don't think I can do that. Seems like client really do be crashing.

____
Flow of "upload xml":
1. Click/Drag the XML file on
2. Client -> Backend: Post request with file
3. a Lambda will process this file
4. Lambda -> Create Ledger for this batch
5. Lambda -> send client SQL json
6. Display data, Client -> Send back approve/deny
7. if approve, send SQL json data and "Start Batch"
    if deny, just delete the ledger, move on.

Flow of "Start Batch":
1. Client -> Backend: POST request with batch data
2. Backend -> Store payment data in SQL database 
3. Backend -> Redirect user
4. Backend -> Queue, batch data

Flow for each payment in queue process:
5. Queue -> Lambdas -> Method
    - If no MFI account attatched to id, create one first, then create payment.
6. Sucessful response, Method -> Lambda -> Update SQL to pending

Flow of "Update purchase"
1. MFI webhooks -> Backend -> Update SQL, update Ledger

Flow of "Get XML"
1. Client -> Backend: Post Request with Batch ID
2. Backend -> (1,2:Ledger, 3:SQL) Table: Get with batch ID
3. Create into cvs, -> client

____

Wait wtf. You need to create a fucking entity and account for each fucking employee and source... You can use a redis table to keep them hash so you only need to do that once.

DunkinId to AccountId hashmap

# Problem #: 
- Method API 600 time limit. 
    - 600 one minute, like a batch
    - Wait til next minute?
    - Or maybe like 9 per second
- Creating unique batch ID.. KeyGen? 
- Creating unique Idemp key..?

# Future Improvements
- Sharding
- Data duplication
- Multiple workers + Load Balancers
- Proxy servers
- After old batches are completely processed, there is no need to have them in the same SQL table. You might aswell save their "report", and then keep all the old data in a seperate SQL table that wont be queried often. This will make our read and write on our main, active, SQL database faster.
- Retry queue, dead letter queu instead of directly updating the status to failed.
- Async with Kafka instead of Amazon SQS

# Questions
- Is there repeat of "TO" and "FROM" ? Only in that case can we "optimize" aka make less than 50k requests.

# Queues
- Real Time Streaming (Kafka) or Event Driven architechture (Amazon sqs) (pub-sub)
- Choosing Amazon SQS since it works well with Lambda. Does most of the work. First 1 million requests per month is free, so 50k * 2 = 100k per month = free.
    - Amazon SQS options: Standard vs FIFO. We choose Standard because we don't need FIFO since order does not matter, and we prefer faster processing. We also don't have to worry about resending the same message multiple times due to idenmp.



- Async vs Sync
- Why not use MFI Api to generate reports? 
- Assumptions: Will assume ALL currency is in USD.
- Make sure to Store "amount" in DB as a string.



_____

Things to suggest:

client (xml file) -> getData (jsonData) -> client approve (xml file)
    - Since this sends the same file twice, we can actually save the
    last xml file when the client sends it in and return a batch_id,
    and approve will just send the batch_id back. If discard, delete
    the file. If left without discarding, the next file will override
    it anyway so it does not matter.

Database:
User
    - For these requirements, all we technically need is two way map.
    - Ledger (owe, received). 
    - This will help verify shit. Also give us indivudal payment data.
    - Requirements does not ask for payment owed per user, or 
- Wide column datastore

front end:
    - Search bar, user specific data.

Queue:
    - Retry queue
    - Dead letter queue


Performance Optimizations:
    - Sharding
        - Different ways to shard.
    - Load balance
    - ...

- After making this I realized that much of the bookkeeping was actually already handeled my methodfi. Oops, but also additonal services could be used to run once a night to make sure updates and consitent.

___
# Final Draft


## Problem
- Priority
- Scale

## Frontend
- A single page web app for simplcity. no routing.
- Memory persists with local storage. Dont care rn.
- No consideration for security.

## Data
### Schema
For the scope of this problem, we actually don't need to create any tables for employees or sources. No "reporting" data on employees ever needs to be used. It would be enough to have just a map for d_id to acc_id. However, since payment systems are so important in this, and in accounting, end of year, and overall just checking that our payments will go through okay and safely, I will create them anyway.

XML gives us a unique identifier for everyone, d_id. Method Fi used acc_id. It may be confusing to have two unique identifiers for the same object. In order to be able to talk to our internal database, we will use d_id, but to talk to method_fi, we use acc_id. So, we will two key:value stores to easily switch between them.

{
    d_id: acc_id,
    ...
}
{
    acc_id:d_id,
    ...
}

Once there is a method fi table for each of our entities, we actually don't need to "keep" track of entities since Method Fi does already. All we need is this map. However, it is good to keep this table anyway. Especially since the first time we run this, we have to create the accounts ourselves.

- Employee:
    d_id, mfi_created:bool, branch, first_name, last_name, phone, email, dob, plaid, loan, ..
- Source:
    d_id, mfi_created:bool, aba_routing, account_number, name, dba,ein, metadata ..

- Payment:
    id, batch_id, to/from, amt, idemp_key, status, time_created, last_updated

We also need a map to go back and forth between payment_id to mfi_payment_id.

Ive assumed that currency will be USD and did not specify further.

Reading vs Writing (People may want CSV quite often, so it may be worth it to also maintain aggregate data like this). We could always recalculate and use it to double check. Write speed should be very fast because there are only 5 sources and 30 branches. In general, I've assumed these won't scale up, and will both remain under 100.

Aggr Data

Two of the requests to generate CSV are just batch aggregate data. We can keep track of it along the way.
- Benefits: 
   - Super fast read speed + don't have to query any data
   - Super fast write speed because sources/branch count is low
   - An additional layer that keeps track of balances. Acts like a ledger/wallet almost to verify that it adds up to 0. If it does not, we can alert early that there is a data mismatch.
   - Can divide data by batch more efficiently

We can do a query on the payments table a form data by branch and by source. FROM * GET where BATCH_ID, and then use that to create the data.

It would be faster to maintain aggr data by batch.

{
    batch_id:
        date_approved: timestamp
        sources: [
            {
                d_id,
                initial_owed,
                initial_owed_count,
                paid_so_far,
                paid_so_far_count,
                last_updated
            },
            ...
        ]
        branches: [
            {
                branch_id,
                initial_owed,
                initial_owed_count,
                paid_so_far,
                paid_so_far_count,
                last_updated
            },
            ...
        ]
}

User wallet
So a problem here is we also want to obviously keep track of how much each user is owed/paid, or a wallet. This can be calculated with the payments table. However, there are a few benefits to having an additonal system.
    1. Faster read data, can get employee data without calculations
    2. Additional layer to double check payment balances are correct

One solution is to create a table for wallets that would be 1:1 with  its respective employee, and this can maintain aggregated data. This is positive because we don't have to do any calculations when we query for an account.

Another solution is that we can build a relationship between users and all the payments they are in. Then, we still have to query, but it'll be much faster. Another benefit of this is that we can generate a payment history list for each user. In SQL, this can be a one to many relationship, and in NoSQL, this can be with a wide column datastore like Cassandra.

Depending on how often we expect employee balance information to be requested, we can implement one or both of these. But since this problem does not ask for any employee specific data, I will not implement this.

Ledger
A debit/credit system to make sure every payment is accounted for. This can be implemented as one table with employees and sources alike.
- Ledger
    d_id, debit, credit
- Double payments can be caught
- This is good to have sources and employees in the same table, because we can keep track of returns and reversed payments now.

For the scope of this problem, I will not implement this.

History
Its probably also smart to record every "attempted" action as a log somewhere just in case of errors, or accounting, or checking. For the scope of this problem, I will not implement this.

- Floating point error/amt conversion. Will not worry.

### Execution
- NoSql
    - Scales well. 
    - Key:object for emp/source/payment
    - Can distribute it more

## ..

## Queue

## Flow/API endpoints

## Problems
- payments database with finished rows.. move it to another one.
- Things to suggest above list