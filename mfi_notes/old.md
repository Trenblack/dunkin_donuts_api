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

# Problem #: 
- Method API 600 time limit. 
    - 600 one minute, like a batch
    - Wait til next minute?
    - Or maybe like 9 per second

# Future Improvements
- Sharding
- Data duplication
- Multiple workers + Load Balancers
- Proxy servers
- After old batches are completely processed, there is no need to have them in the same SQL table. You might aswell save their "report", and then keep all the old data in a seperate SQL table that wont be queried often. This will make our read and write on our main, active, SQL database faster.
- Retry queue, dead letter queu instead of directly updating the status to failed.

# Questions
- Is there repeat of "TO" and "FROM" ? Only in that case can we "optimize" aka make less than 50k requests.
