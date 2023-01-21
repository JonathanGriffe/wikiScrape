import psycopg2

conn = psycopg2.connect(host="localhost", database="wikiuser", user="wikiuser", password="myPGPW")
cur = conn.cursor()

path = [""]
cur.execute('''SELECT distance FROM Pages WHERE topic=%s''', (path[0],))
distance = cur.fetchone()[0] 



while distance:
    cur.execute('''SELECT p1.topic FROM Links JOIN Pages as p1 ON p1.id=parent_id JOIN Pages as p2 ON p2.id=child_id AND p2.topic=%s LIMIT 1''', (path[-1],))
    path.append(cur.fetchone()[0])
    distance -= 1

print(path)