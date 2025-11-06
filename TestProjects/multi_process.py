# Recommended options and minimal examples
# Central allocator (main process assigns claims until budget exhausted). Simple and deterministic; best for single-process orchestration.
# multiprocessing.Manager.Value + Lock (quick in-memory cross-process sync)



# example, not tied to workspace path
import multiprocessing

def worker(claim, remaining, lock):
    # claim is dict with 'amount' needed
    with lock:
        if remaining.value >= claim['amount']:
            remaining.value -= claim['amount']
            allocated = True
        else:
            allocated = False
    if not allocated:
        return {"id": claim["id"], "status": "skipped"}
    # do the work for allocated claim
    # ...
    return {"id": claim["id"], "status": "processed"}

if __name__ == "__main__":
    claims = [{"id": i, "amount": a} for i, a in enumerate([10,20,30,40,50])]
    total_amount = 100.0
    mgr = multiprocessing.Manager()
    remaining = mgr.Value('d', total_amount)
    lock = mgr.Lock()
    with multiprocessing.Pool(4) as p:
        results = p.starmap(worker, [(c, remaining, lock) for c in claims])
    print(results)
    print("remaining:", remaining.value)


# Atomic DB allocation (recommended for production / multi-host). Use an atomic update so only one worker succeeds per allocation attempt.

# requires pymongo
from pymongo import MongoClient, ReturnDocument

def try_allocate_budget(db, claim_amount):
    # budget doc e.g. {"_id": "budget", "remaining": 100.0}
    res = db.budgets.find_one_and_update(
        {"_id": "budget", "remaining": {"$gte": claim_amount}},
        {"$inc": {"remaining": -claim_amount}},
        return_document=ReturnDocument.BEFORE
    )
    return res is not None

# usage
client = MongoClient("mongodb://...") 
db = client.mydb
if try_allocate_budget(db, 25.0):
    # proceed and persist work
    pass
else:
    # not enough budget
    pass


# Practical tips

# If claims are small and frequent, allocate in chunks to workers to reduce contention.
# Always make operations idempotent and log allocation attempts + outcomes.
# Add retries with exponential backoff for transient conflicts.
# For Dry Run (in-memory), central allocator / Manager is fine. For Final Run (persisted balances and audit), use DB atomic ops.