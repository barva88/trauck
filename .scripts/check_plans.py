import sqlite3, os

db = os.path.join(r'C:\Proyects\trauck','db.sqlite3')
if not os.path.exists(db):
    print('DB_NOT_FOUND', db)
else:
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    try:
        cur.execute("SELECT id,name,slug,price_usd,currency,stripe_product_id,stripe_price_id FROM billing_plan ORDER BY id DESC")
        rows = cur.fetchall()
        if rows:
            for r in rows:
                print('PLAN_ROW', r)
        else:
            print('NO_PLAN_ROWS')
    except Exception as e:
        print('ERROR', str(e))
    finally:
        conn.close()
