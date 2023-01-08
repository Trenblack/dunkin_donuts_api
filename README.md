## Problem
- Priority
Must be robust.

- Scale

## Frontend
For the frontend, I just created a basic react app using the MUI library suggest in the prompt. It was my first time using this library, but found it to be simple and efficient. 

The app consists of two pages: One for submitting new reports, and one for viewing old reports(seperated by batches, with the ability go generate CSV files for each batch). 

When creating a new report, to view the XML data in a "succint" way, I've created a parser in the back end that returns aggregated data. That data is then displayed as a table that can be sorted by either branches or sources. 

I've chosen to handle the parsing in the backend to prevent the client from having to heavy computations. Using a Python library built on C, and XML with about 50k rows can be processed and returned in under one second. 

In the future, there can also be some way to view data by individual users. This can be done through taking advantage of virtualized lists, pagination, and a "search bar" feature. Due to the structure of this system, this feature would be easy to implement into the existing codebase. However, since the question did not ask for this, I've decided to skip this feature for now. And since this is meant to be a basic memo, I've also decided to not worry about things like memory persistance, security, or production level react/javascript code.

Demo seen here:
https://youtu.be/MDe__1Vc5Sc

[![Demo](https://i.imgur.com/wNcAkAt.png)](https://youtu.be/MDe__1Vc5Sc)


## Data
### Schema
XML gives us a unique identifier for everyone, d_id. Method Fi used acc_id. It may be confusing to have two unique identifiers for the same object. In order to be able to talk to our internal database, we will use d_id, but to talk to method_fi, we use acc_id. So, we will two key:value stores to easily switch between them.

d_id_to_acc_id:

{

    d_id: acc_id,
    
    ...
    
}


acc_id_to_d_id:

{

    acc_id:d_id,
    
    ...
    
}



For the scope of this problem, we actually don't need to create any tables for employees or sources. No "reporting" data on employees ever needs to be used. It would be enough to have just a map for d_id to acc_id. Furthermore, Method API already keeps track of entities. However, since payment systems usually care a lot about being able to report data by each user, I will create them anyway. This is especially useful if we assume that MFI acc_id's dont already exist for each d_id, and we have to create entitys/accounts ourselves.

Objects Models:

1) Employee: (d_id, mfi_created:bool, branch, first_name, last_name, phone, email, dob, plaid, loan, metadata ..)
2) Source: (d_id, mfi_created:bool, aba_routing, account_number, name, dba,ein, metadata ..)
3) Payment: (id, batch_id, to/from, amt, idemp_key, status, time_created, last_updated)

I will assume that currency is always USD, and will not worry about payment ammount floating point errors.

Note: We may also need a map to convert between the payment_id from MFI's requests and our own table.

To generate CSV, we could simply do a query on the payments table specifying batch_id, and using the status/amt to calculate how much each source/branch has paid. Another way that would be to maintain another table for aggregated data, where each entry corresponds with one batch. This would be faster for reading and generating CSV files since we don't have to recalculate, but it will also lead to more writes and having to maintain two databases. However, since there are only about 5 sources and 30 branches, the write speed will not scale up with the increases in payments. Furthermore, this can also act as another, seperate, table that also keeps track of payments, and having two seperate records of payments can help making sure that no errors have occured. 


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


### Wallet
We might want to keep track of how much each source/employee is owed/paid, or a wallet. This would be something that is independant of batches. One way to acquire such data is to just do a query on the payments table where we filter by all rows where the from/to columns is the source/employees's d_id. Using the "amt" and "status" columns, we can calculate how much each employee/source has been overall paid/received. This will work, but can lead to many heavy queries if done very often.

Another approach is to maintain an additonal system. Some of the benefits are as follows:
    1. Faster read data, can get employee data without querying the payments table and making calculations.
    2. Additional layer to double check payment balances are correct.
    
While some of the cons here are the increased complexity from maintaining another system, a possibility of inconsistent data, and many more writes than our previous approach. 

One way of implementing this can be to create a table for wallets that would be 1:1 with its respective employee, and this can maintain aggregated data per user. This would be a very simple system to maintain, and would very quickly be able to read and provide aggregated data per employee/source. However, this loses the ability to get a list of all payments involvng a user, which may be important down the line in generating payment histories or doing bookeeping.

To sidestep this, another solution can be to build a relationship between users and all the payments they are in. Then, we still have to calculate each payment to provide aggregated data, but we can retrieve the payments corresponding with each employee/source very quickly, while still having the option to generate a payment history list for each employee/source. In SQL, this can be done with a one to many relationship, and in NoSQL, this can be done with a wide column datastore like Cassandra.

Depending on how often we expect employee balance information to be requested, we can implement one or both of these. But since this problem does not ask for any employee specific data, I will not implement any of these. 

### Ledger
A debit/credit system to make sure every payment is accounted for. This can be implemented as one table with employees and sources alike. This will help double payments be caught, as well as give a place to keep track of credit/debit which will aid in tracking returns and reversed payments. The philosophy here is that the total sum of the debit and credit should equal to 0, and if it does not, that is an early flag that something has went wrong. 

Ledger object: (pk=d_id, debit, credit, last_updated?)

For the scope of this problem, I will not implement this.

### History
Its probably also smart to log every action attempted in case of errors or accounting. 


## Flow/API endpoints
- Get Aggr Data

- Approve Payment
Client -> Approve(xml file) -> Server -> adds payments to payments table, creates new batch object, add payment_id's to Payment Queue

- 2 Task Queues

For each payment_id in payment queue:
    If to/from d_id does not have mfi_acc_id in map1:
        send payment_id to account queue
    else
        get to/from from payment table using payment_id
        use converter maps to convert to mfi_acc_id
        use that to create new Payment request to MFI API
        MFI response -> Update Payments table status

For each payment_id in account_queue:
    get to/from id from payment table using payment_id
    use employee/source table to get data of to/from using to/from id
    send request to MFI api to create entity/account
    update the mfi_acc_id fields in converter map
    send payment_id to payment queue

- Get batches
GET request

Client -> Server -> returns list of batche_id's with some summarized data

- Get CSV
POST request, (batch_id, type) where type can be payment, source, or branch. 

Client -> Get CSV(batch_id, source/branch) -> Server -> returns csv created from batch data table

Client -> Get CSV(batch_id, payment) -> Server -> returns csv created from payment table, filtered by batch_id.

- Update Payment status

MFI Webhooks -> Server -> acc_id to d_id map -> updates Payment table, get batch_id, -> update batch aggregated data.

## Points of Error
Due to the robust nature that is required of financial tracking and executing systems, there are many points of error that need to be addressed. The whole scope of these errors are beyond the scope of this problem, so I've listed just a few below + possible solutions.

1) Double Payments

Since the payment executor queue uses Payment objects from the Payment's table, which includes a idempotent key, we do not have to worry about the payments queue sending multiple requests to the MFI Api, which takes in an idempotent key. Sending in multiple requests from this queue to the MFI Api would thus be the same as sending in one request. Another possibility is that the client sends the same file to the server under the "approve payment" gateway. This could happen from the client pressing the "approve" batch button multiple times very quickly. However, since the batch_id is generated before the approve payment request is sent, this batch_id also acts like an idempotent key at this stage, and thus further approve requests can be ignored once the batch_id processing has began. Lastly, if someone sends in the same file twice but on seperate times (leading to seperate batch_id's), we could also keep a hash of files to make sure no duplicate files are being approved.

## A few ways to Improve

- After old batches are completely processed, there is no need to have them in the same payments table. We could occasionaly run a script to move old payments to an another readonly table. This will make our read and write on our main payments table faster.
- Add Retry queue and dead letter queu instead of directly updating the status to failed.
- Many Improvements (eg: sharding, multiple workers, load balancers, data duplicates) can be automatically implemented by using softwares like AWS. 
- Routinley run checks to make sure aggregated data table, payments table, and MFI payments are all in sync.
