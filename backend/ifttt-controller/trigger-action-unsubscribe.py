import json, requests, decimal, psycopg2, time
from psycopg2 import pool

schema = 'public'
postgreSQL_pool = psycopg2.pool.SimpleConnectionPool(1, 20, host="",database="", user="", password="", port="", options=f'-c search_path={schema}',)
postgres_conn  = postgreSQL_pool.getconn()

def lambda_handler(event, context):
	id_tag = event['id']
	try:
		cur = postgres_conn.cursor()

		#update trigger with uuid
		sql = 'UPDATE triggers_actions SET active = FALSE WHERE unique_id = \''+str(id_tag)+'\';'
		cur.execute(sql)
		postgres_conn.commit()
		
		#close database
		cur.close()


	except (Exception, psycopg2.DatabaseError) as error:
			print(error)
	finally:
		print ('finally')
	
	return {'unsubscribe':'successful'}