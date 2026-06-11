"""nest-ledger API 集成测试"""
import requests
import sys

BASE = "http://localhost:8000/api/v1"
passed = 0
failed = 0


def test(label, resp, expected=200):
    global passed, failed
    exps = expected if isinstance(expected, list) else [expected]
    ok = resp.status_code in exps
    if ok:
        passed += 1
    else:
        failed += 1
    mark = "[PASS]" if ok else "[FAIL]"
    print(f"  {mark} {label} (HTTP {resp.status_code})")
    if not ok:
        print(f"       Expected {exps}, body: {resp.text[:200]}")
    return ok


print("=" * 60)
print("nest-ledger API 集成测试")
print("=" * 60)

# 1. 健康检查
print("\n1. Health")
resp = requests.get(f"{BASE}/health")
test("GET /health", resp)

# 2. 认证
print("\n2. Auth")
r1 = requests.post(f"{BASE}/auth/dev/login", json={"nickname": "XiaoMing"})
test("Dev login - XiaoMing", r1)
t1 = r1.json()["token"]
u1 = r1.json()["user_id"]

r2 = requests.post(f"{BASE}/auth/dev/login", json={"nickname": "XiaoHong"})
test("Dev login - XiaoHong", r2)
t2 = r2.json()["token"]
u2 = r2.json()["user_id"]

h1 = {"Authorization": f"Bearer {t1}"}
h2 = {"Authorization": f"Bearer {t2}"}

resp = requests.get(f"{BASE}/family/info")
test("Unauthorized -> 403", resp, [401, 403])

# 3. 家庭
print("\n3. Family")
r = requests.post(f"{BASE}/family/create", json={"name": "OurNest"}, headers=h1)
test("Create family", r)
code = r.json()["invite_code"]

r = requests.post(f"{BASE}/family/create", json={"name": "X"}, headers=h1)
test("Duplicate create -> 400", r, 400)

r = requests.get(f"{BASE}/family/info", headers=h1)
test("Get family info", r)
print(f"       Members: {len(r.json()['members'])}")

r = requests.post(f"{BASE}/family/join", json={"invite_code": code}, headers=h2)
test("Join family", r)

r = requests.get(f"{BASE}/family/info", headers=h1)
test("Get family info (2 people)", r)
print(f"       Members: {len(r.json()['members'])}")

# 4. 记账
print("\n4. Accounting")
tx = {"amount": 35.5, "category": "餐饮", "type": "expense", "date": "2026-06-12", "note": "supermarket"}
r = requests.post(f"{BASE}/transaction/add", json=tx, headers=h1)
test("Add expense: food 35.5", r)

tx = {"amount": 10000, "category": "工资", "type": "income", "date": "2026-06-01", "note": "salary"}
r = requests.post(f"{BASE}/transaction/add", json=tx, headers=h2)
test("Add income: salary 10000", r)

for amt, cat in [(120, "交通"), (88, "购物"), (2000, "住房"), (50, "娱乐")]:
    requests.post(f"{BASE}/transaction/add", json={
        "amount": amt, "category": cat, "type": "expense", "date": "2026-06-12", "note": ""
    }, headers=h1)
print("  + 4 extra expenses added")

r = requests.get(f"{BASE}/transaction/list?month=2026-06", headers=h1)
test("List June transactions", r)
d = r.json()
print(f"       Income:{d['total_income']}  Expense:{d['total_expense']}  Items:{len(d['items'])}")

r = requests.get(f"{BASE}/transaction/stats?month=2026-06", headers=h1)
test("Monthly stats", r)
d = r.json()
print(f"       Balance: {d['balance']}")
for c in d['expense_by_category'][:3]:
    print(f"       {c['category']}: {c['amount']} ({c['percent']}%)")

items = requests.get(f"{BASE}/transaction/list?month=2026-06", headers=h1).json()['items']
others = [i for i in items if i['user_id'] != u1]
if others:
    r = requests.delete(f"{BASE}/transaction/{others[0]['id']}", headers=h1)
    test("Delete others record -> 403", r, 403)

mine = [i for i in items if i['user_id'] == u1]
if mine:
    r = requests.delete(f"{BASE}/transaction/{mine[0]['id']}", headers=h1)
    test("Delete my record", r)

# 5. 日历
print("\n5. Calendar")
evt = {"title": "Pay Rent", "start_time": "2026-06-15T09:00:00", "repeat_type": "monthly", "repeat_day": 15, "note": "don't forget"}
r = requests.post(f"{BASE}/event/create", json=evt, headers=h1)
test("Create event: Pay Rent (monthly)", r)

evt = {"title": "Date Night", "start_time": "2026-06-20T18:00:00", "repeat_type": "none", "repeat_day": 0, "note": "anniversary"}
r = requests.post(f"{BASE}/event/create", json=evt, headers=h2)
test("Create event: Date Night", r)

r = requests.get(f"{BASE}/event/list?month=2026-06", headers=h1)
test("List June events", r)
evts = r.json()['events']
print(f"       Events: {len(evts)}")

my_evts = [e for e in evts if e['is_mine']]
if my_evts:
    r = requests.put(f"{BASE}/event/{my_evts[0]['id']}", json={"title": "Pay Rent (updated)"}, headers=h1)
    test("Edit event", r)
    r = requests.delete(f"{BASE}/event/{my_evts[0]['id']}", headers=h1)
    test("Delete event", r)

# Result
print()
print("=" * 60)
total = passed + failed
print(f"Result: {passed}/{total} passed")
if failed == 0:
    print("ALL TESTS PASSED")
    sys.exit(0)
else:
    print(f"{failed} FAILED")
    sys.exit(1)
