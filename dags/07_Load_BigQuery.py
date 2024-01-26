from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models.connection import Connection
from time import time_ns
from datetime import datetime , timedelta
from airflow.utils.dates import days_ago
import os
from pymongo import MongoClient
from pandas import DataFrame
from google.cloud import bigquery
import pandas as pd
import sqlalchemy as db
from sqlalchemy import text

default_args = {
    'owner': 'WilsonR',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

################################################################
#################### AUX FUNCTIONS ##############################
################################################################
def get_connect_mongo():

    CONNECTION_STRING ="mongodb+srv://atlas:T6.HYX68T8Wr6nT@cluster0.enioytp.mongodb.net/?retryWrites=true&w=majority"
    client = MongoClient(CONNECTION_STRING)

    return client

def transform_date(text):
    text = str(text)
    d = text[0:10]
    return d

def transform_date(text):
    text = str(text)
    d = text[0:10]
    return d


def get_group_status(text):
    text = str(text)
    if text =='CLOSED':
        d='END'
    elif text =='COMPLETE':
        d='END'
    else :
        d='TRANSIT'
    return d

def get_connect_mongo_wr():

    CONNECTION_STRING ="mongodb+srv://wilson4rodriguez:gkE8QLSu1VyeLmyX@cluster0.bxk0mjp.mongodb.net/?retryWrites=true&w=majority"
    client = MongoClient(CONNECTION_STRING)

    return client



def start_process():
    print(" INICIO EL PROCESO!")

def end_process():
    print(" FIN DEL PROCESO!")

################################################################
#################### LOAD ORDERS ##############################
################################################################
def load_orders():
    print(f" INICIO LOAD ORDERS")
    dbconnect = get_connect_mongo()
    dbname=dbconnect["retail_db"]
    collection_name = dbname["orders"] 
    orders = collection_name.find({})  
    orders_df = DataFrame(orders)
    dbconnect.close()
    orders_df['_id'] = orders_df['_id'].astype(str)
    orders_df['order_date']  = orders_df['order_date'].map(transform_date)
    orders_df['order_date'] = pd.to_datetime(orders_df['order_date'], format='%Y-%m-%d').dt.date
    orders_rows=len(orders_df)
    if orders_rows>0 :
        client = bigquery.Client(project='amiable-webbing-411501')
        table_id =  "amiable-webbing-411501.dep_raw.orders"
        job_config = bigquery.LoadJobConfig(
            schema=[
                bigquery.SchemaField("_id", bigquery.enums.SqlTypeNames.STRING),
                bigquery.SchemaField("order_id", bigquery.enums.SqlTypeNames.INTEGER),
                bigquery.SchemaField("order_date", bigquery.enums.SqlTypeNames.DATE),
                bigquery.SchemaField("order_customer_id", bigquery.enums.SqlTypeNames.INTEGER),
                bigquery.SchemaField("order_status", bigquery.enums.SqlTypeNames.STRING),
            ],
            write_disposition="WRITE_TRUNCATE",
        )
        job = client.load_table_from_dataframe(
            orders_df, table_id, job_config=job_config
        )  
        job.result()  # Wait for the job to complete.

        table = client.get_table(table_id)  # Make an API request.
        print(
            "Loaded {} rows and {} columns to {}".format(
                table.num_rows, len(table.schema), table_id
            )
        )
    else : 
        print('alerta no hay registros en la tabla orders')


################################################################
#################### LOAD ORDER_ITEMS ##############################
################################################################

def load_order_items():
    print(f" INICIO LOAD ORDER ITEMS")
    dbconnect = get_connect_mongo()
    dbname=dbconnect["retail_db"]
    collection_name = dbname["order_items"] 
    order_items = collection_name.find({})  
    order_items_df = DataFrame(order_items)
    dbconnect.close()
    order_items_df['_id'] = order_items_df['_id'].astype(str)
    order_items_df['order_date']  = order_items_df['order_date'].map(transform_date)
    order_items_df['order_date'] = pd.to_datetime(order_items_df['order_date'], format='%Y-%m-%d').dt.date
    order_items_rows=len(order_items_df)
    if order_items_rows>0 :
        client = bigquery.Client(project='amiable-webbing-411501')

        table_id =  "amiable-webbing-411501.dep_raw.order_items"
        job_config = bigquery.LoadJobConfig(
            schema=[
                bigquery.SchemaField("_id", bigquery.enums.SqlTypeNames.STRING),
                bigquery.SchemaField("order_date", bigquery.enums.SqlTypeNames.DATE),
                bigquery.SchemaField("order_item_id", bigquery.enums.SqlTypeNames.INTEGER),
                bigquery.SchemaField("order_item_order_id", bigquery.enums.SqlTypeNames.INTEGER),
                bigquery.SchemaField("order_item_product_id", bigquery.enums.SqlTypeNames.INTEGER),
                bigquery.SchemaField("order_item_quantity", bigquery.enums.SqlTypeNames.INTEGER),
                bigquery.SchemaField("order_item_subtotal", bigquery.enums.SqlTypeNames.FLOAT),
                bigquery.SchemaField("order_item_product_price", bigquery.enums.SqlTypeNames.FLOAT),
            ],
            write_disposition="WRITE_TRUNCATE",
        )


        job = client.load_table_from_dataframe(
            order_items_df, table_id, job_config=job_config
        )  
        job.result()  # Wait for the job to complete.

        table = client.get_table(table_id)  # Make an API request.
        print(
            "Loaded {} rows and {} columns to {}".format(
                table.num_rows, len(table.schema), table_id
            )
        )
    else : 
        print('alerta no hay registros en la tabla order_items')
    
################################################################
#################### LOAD PRODUCTS##############################
################################################################
def load_products():
    print(f" INICIO LOAD PRODUCTS")
    dbconnect = get_connect_mongo()
    dbname=dbconnect["retail_db"]
    collection_name = dbname["products"] 
    products = collection_name.find({})
    products_df = DataFrame(products)
    dbconnect.close()
    products_df['_id'] = products_df['_id'].astype(str)
    products_df['product_description'] = products_df['product_description'].astype(str)
    products_rows=len(products_df)
    print(f" Se obtuvo  {products_rows}  Filas")
    products_rows=len(products_df)
    if products_rows>0 :
        client = bigquery.Client(project='amiable-webbing-411501')
        table_id =  "amiable-webbing-411501.dep_raw.products"
        job_config = bigquery.LoadJobConfig(
            schema=[
                bigquery.SchemaField("_id", bigquery.enums.SqlTypeNames.STRING),
                bigquery.SchemaField("product_id", bigquery.enums.SqlTypeNames.INTEGER),
                bigquery.SchemaField("product_category_id", bigquery.enums.SqlTypeNames.INTEGER),
                bigquery.SchemaField("product_name", bigquery.enums.SqlTypeNames.STRING),
                bigquery.SchemaField("product_description", bigquery.enums.SqlTypeNames.STRING),
                bigquery.SchemaField("product_price", bigquery.enums.SqlTypeNames.FLOAT),
                bigquery.SchemaField("product_image", bigquery.enums.SqlTypeNames.STRING),
            ],
            write_disposition="WRITE_TRUNCATE",
        )


        job = client.load_table_from_dataframe(
            products_df, table_id, job_config=job_config
        )  
        job.result()  # Wait for the job to complete.

        table = client.get_table(table_id)  # Make an API request.
        print(
            "Loaded {} rows and {} columns to {}".format(
                table.num_rows, len(table.schema), table_id
            )
        )
    else : 
        print('alerta no hay registros en la tabla productos')



################################################################
#################### LOAD CUSTOMERS ############################
################################################################
def load_customers():
    print(f" INICIO LOAD CUSTOMERS")
    dbconnect = get_connect_mongo()
    dbname=dbconnect["retail_db"]
    collection_name = dbname["customers"] 
    # customers = collection_name.find({},{"_id":1,"customer_id":1})  filtrar columna
    customers = collection_name.find({})
    customers_df = DataFrame(customers)
    dbconnect.close()
    customers_df['_id'] = customers_df['_id'].astype(str)
    customers_rows=len(customers_df)
    if customers_rows>0 :
        client = bigquery.Client(project='amiable-webbing-411501')

        table_id =  "amiable-webbing-411501.dep_raw.customers"
        job_config = bigquery.LoadJobConfig(
            schema=[
                bigquery.SchemaField("_id", bigquery.enums.SqlTypeNames.STRING),
                bigquery.SchemaField("customer_id", bigquery.enums.SqlTypeNames.INTEGER),
                bigquery.SchemaField("customer_fname", bigquery.enums.SqlTypeNames.STRING),
                bigquery.SchemaField("customer_lname", bigquery.enums.SqlTypeNames.STRING),
                bigquery.SchemaField("customer_email", bigquery.enums.SqlTypeNames.STRING),
                bigquery.SchemaField("customer_password", bigquery.enums.SqlTypeNames.STRING),
                bigquery.SchemaField("customer_street", bigquery.enums.SqlTypeNames.STRING),
                bigquery.SchemaField("customer_city", bigquery.enums.SqlTypeNames.STRING),
                bigquery.SchemaField("customer_state", bigquery.enums.SqlTypeNames.STRING),
                bigquery.SchemaField("customer_zipcode", bigquery.enums.SqlTypeNames.INTEGER),
            ],
            write_disposition="WRITE_TRUNCATE",
        )


        job = client.load_table_from_dataframe(
            customers_df, table_id, job_config=job_config
        )  
        job.result()  # Wait for the job to complete.

        table = client.get_table(table_id)  # Make an API request.
        print(
            "Loaded {} rows and {} columns to {}".format(
                table.num_rows, len(table.schema), table_id
            )
        )
    else : 
        print('alerta no hay registros en la tabla customers')


################################################################
#################### LOAD CATEGORIES ###########################
################################################################
def load_categories():
    print(f" INICIO LOAD CATEGORIES")
    dbconnect = get_connect_mongo()
    dbname=dbconnect["retail_db"]
    collection_name = dbname["categories"] 
    categories = collection_name.find({})
    categories_df = DataFrame(categories)
    dbconnect.close()
    categories_df = categories_df.drop(columns=['_id'])
    categories_rows=len(categories_df)
    if categories_rows>0 :
        client = bigquery.Client(project='amiable-webbing-411501')

        table_id =  "amiable-webbing-411501.dep_raw.categories"
        job_config = bigquery.LoadJobConfig(
            schema=[
                bigquery.SchemaField("category_id", bigquery.enums.SqlTypeNames.INTEGER),
                bigquery.SchemaField("category_department_id", bigquery.enums.SqlTypeNames.INTEGER),
                bigquery.SchemaField("category_name", bigquery.enums.SqlTypeNames.STRING),
            ],
            write_disposition="WRITE_TRUNCATE",
        )


        job = client.load_table_from_dataframe(
            categories_df, table_id, job_config=job_config
        )  
        job.result()  # Wait for the job to complete.

        table = client.get_table(table_id)  # Make an API request.
        print(
            "Loaded {} rows and {} columns to {}".format(
                table.num_rows, len(table.schema), table_id
            )
        )
    else : 
        print('alerta no hay registros en la tabla categories')
       

################################################################
#################### LOAD DEPARTMENTS #########################
################################################################
def load_departments():
    print(f" INICIO LOAD DEPARTMENTS")
    dbconnect = get_connect_mongo()
    dbname=dbconnect["retail_db"]
    collection_name = dbname["departments"] 
    departments = collection_name.find({})
    departments_df = DataFrame(departments)
    dbconnect.close()
    departments_df = departments_df.drop(columns=['_id'])
    departments_rows=len(departments_df)
    if departments_rows>0 :
        client = bigquery.Client(project='amiable-webbing-411501')

        table_id =  "amiable-webbing-411501.dep_raw.departments"
        job_config = bigquery.LoadJobConfig(
            schema=[
                bigquery.SchemaField("department_id", bigquery.enums.SqlTypeNames.INTEGER),
                bigquery.SchemaField("department_name", bigquery.enums.SqlTypeNames.STRING)
            ],
            write_disposition="WRITE_TRUNCATE",
        )


        job = client.load_table_from_dataframe(
            departments_df, table_id, job_config=job_config
        )  
        job.result()  # Wait for the job to complete.

        table = client.get_table(table_id)  # Make an API request.
        print(
            "Loaded {} rows and {} columns to {}".format(
                table.num_rows, len(table.schema), table_id
            )
        )
    else : 
        print('alerta no hay registros en la tabla departments')


################################################################
#################### CAPA MASTER ###############################
################################################################
def load_master():
    print(f" INICIO LOAD MASTER")
    client = bigquery.Client(project='amiable-webbing-411501')
    sql = """
        SELECT *
        FROM `amiable-webbing-411501.dep_raw.order_items`
    """
    m_order_items_df = client.query(sql).to_dataframe()
    client = bigquery.Client(project='amiable-webbing-411501')
    sql_2 = """
        SELECT *
        FROM `amiable-webbing-411501.dep_raw.orders`
    """
    m_orders_df = client.query(sql_2).to_dataframe()
    df_join = m_orders_df.merge(m_order_items_df, left_on='order_id', right_on='order_item_order_id', how='inner')
    df_master=df_join[[ 'order_id', 'order_date_x', 'order_customer_id',
       'order_status',  'order_item_id',
       'order_item_order_id', 'order_item_product_id', 'order_item_quantity',
       'order_item_subtotal', 'order_item_product_price']]
    df_master=df_master.rename(columns={"order_date_x":"order_date"})
    df_master['order_status_group']  = df_master['order_status'].map(get_group_status)
    df_master['order_date'] = df_master['order_date'].astype(str)
    df_master['order_date'] = pd.to_datetime(df_master['order_date'], format='%Y-%m-%d').dt.date
    ##ADD ORDER_ITEMS_SUBTOTAL_MN#####
    tipo_cambio = pd.read_csv("https://www.sunat.gob.pe/a/txt/tipoCambio.txt",sep='|',header=None).rename(columns={0:"Fecha",1:"Precio_venta",2:"Precio_Compra"})
    t_cam=tipo_cambio["Precio_venta"][0]
    df_master['order_item_subtotal_mn'] = df_master['order_item_subtotal'].apply(lambda x: x*t_cam)

    df_master_rows=len(df_master)
    if df_master_rows>0 :
        client = bigquery.Client(project='amiable-webbing-411501')

        table_id =  "amiable-webbing-411501.dep_raw.master_order"
        job_config = bigquery.LoadJobConfig(
            schema=[
                bigquery.SchemaField("order_id", bigquery.enums.SqlTypeNames.INTEGER),
                bigquery.SchemaField("order_date", bigquery.enums.SqlTypeNames.DATE),
                bigquery.SchemaField("order_customer_id", bigquery.enums.SqlTypeNames.INTEGER),
                bigquery.SchemaField("order_status", bigquery.enums.SqlTypeNames.STRING),
                bigquery.SchemaField("order_item_id", bigquery.enums.SqlTypeNames.INTEGER),
                bigquery.SchemaField("order_item_order_id", bigquery.enums.SqlTypeNames.INTEGER),
                bigquery.SchemaField("order_item_product_id", bigquery.enums.SqlTypeNames.INTEGER),
                bigquery.SchemaField("order_item_quantity", bigquery.enums.SqlTypeNames.INTEGER),
                bigquery.SchemaField("order_item_subtotal", bigquery.enums.SqlTypeNames.FLOAT),
                bigquery.SchemaField("order_item_product_price", bigquery.enums.SqlTypeNames.FLOAT),
                bigquery.SchemaField("order_status_group", bigquery.enums.SqlTypeNames.STRING),
                bigquery.SchemaField("order_item_subtotal_mn", bigquery.enums.SqlTypeNames.FLOAT),
            ],
            write_disposition="WRITE_TRUNCATE",
        )


        job = client.load_table_from_dataframe(
            df_master, table_id, job_config=job_config
        )  
        job.result()  # Wait for the job to complete.

        table = client.get_table(table_id)  # Make an API request.
        print(
            "Loaded {} rows and {} columns to {}".format(
                table.num_rows, len(table.schema), table_id
            )
        )
    else : 
        print('alerta no hay registros en la tabla master_order')


################################################################
#################### LOAD TABLE BI #############################
################################################################
def load_table_bi():
    print(f" INICIO LOAD AND CREATE BI")
    client = bigquery.Client(project='amiable-webbing-411501')
    query_string = """
    create or replace table `amiable-webbing-411501.dep_raw.bi_orders` as
    SELECT 
    order_date,c.category_name ,d.department_name 
    , sum (a.order_item_subtotal) order_item_subtotal
    , sum (a.order_item_quantity) order_item_quantity
    FROM `amiable-webbing-411501.dep_raw.master_order` a
    inner join  `amiable-webbing-411501.dep_raw.products` b on
    a.order_item_product_id=b.product_id
    inner join `amiable-webbing-411501.dep_raw.categories` c on
    b.product_category_id=c.category_id
    inner join `amiable-webbing-411501.dep_raw.departments` d on
    c.category_department_id=d.department_id
    group by order_date,c.category_name ,d.department_name
    """
    query_job = client.query(query_string)
    rows = list(query_job.result())
    print(rows)

################################################################
#################### LOAD AND CREATE CLIENT_SEGMENT ############
################################################################
def load_customer_segment():
    print(f" INICIO LOAD AND CREATE CUSTOMER SEGMENT")
    client = bigquery.Client(project='amiable-webbing-411501')
    query_string = """
    create or replace table `amiable-webbing-411501.dep_raw.customer_segment` as
    select customer_id,category_name , order_item_subtotal from
    (
    SELECT customer_id,category_name,order_item_subtotal,
    RANK() OVER (PARTITION BY customer_id ORDER BY order_item_subtotal DESC) AS rank_ 
    FROM (
        SELECT 
        d.customer_id ,c.category_name 
        , sum (a.order_item_subtotal) order_item_subtotal
        FROM `amiable-webbing-411501.dep_raw.master_order` a
        inner join  `amiable-webbing-411501.dep_raw.products` b on
        a.order_item_product_id=b.product_id
        inner join `amiable-webbing-411501.dep_raw.categories` c on
        b.product_category_id=c.category_id
        inner join `amiable-webbing-411501.dep_raw.customers` d on
        a.order_customer_id=d.customer_id
        group by 1,2
        )
    )
    where rank_=1
    """
    query_job = client.query(query_string)
    rows = list(query_job.result())
    print(rows)    
################################################################
#################### LOAD CUSTOMER SEGMENT ON MONGODB ##########
################################################################
def load_customer_seg_mongodb():
    print(f" INICIO LOAD CUSTOMER_MONGODB")
    client3 = bigquery.Client(project='amiable-webbing-411501')
    sql = """
        SELECT *
        FROM `amiable-webbing-411501.dep_raw.customer_segment`
        LIMIT 50
    """
    customer_segment_df = client3.query(sql).to_dataframe()
    dbconnect = get_connect_mongo_wr()
    dbname=dbconnect["retail_db"]
    collection_name = dbname["customer_segment_Wilson_Rodriguez"]
    data_insert= customer_segment_df.to_dict(orient="records")
    collection_name.insert_many(data_insert)
    dbconnect.close()



################################################################
#################### DAG CREATION ##############################
################################################################
with DAG(
    dag_id="load_BigQuery",
    schedule="20 04 * * *", 
    start_date=days_ago(2), 
    default_args=default_args
) as dag:
    step_start = PythonOperator(
        task_id='start_id',
        python_callable=start_process,
        dag=dag
    )
    step_load_orders = PythonOperator(
        task_id='load_orders_id',
        python_callable=load_orders,
        dag=dag
    )
    step_load_order_items = PythonOperator(
        task_id='load_order_items_id',
        python_callable=load_order_items,
        dag=dag
    )
    step_load_products = PythonOperator(
        task_id='load_products_id',
        python_callable=load_products,
        dag=dag
    )
    step_load_customers = PythonOperator(
        task_id='load_customers_id',
        python_callable=load_customers,
        dag=dag
    )
    step_load_categories = PythonOperator(
        task_id='load_categories_id',
        python_callable=load_categories,
        dag=dag
    )
    step_load_departments= PythonOperator(
        task_id='load_departments_id',
        python_callable=load_departments,
        dag=dag
    )
    step_master= PythonOperator(
        task_id='load_master_id',
        python_callable=load_master,
        dag=dag
    )
    step_bi= PythonOperator(
        task_id='load_bi_id',
        python_callable=load_table_bi,
        dag=dag
    )
    step_customer_seg= PythonOperator(
        task_id='load_customer_seg_id',
        python_callable=load_customer_segment,
        dag=dag
    )
    step_customer_seg_mongodb= PythonOperator(
        task_id='load_customer_seg_mongodb_id',
        python_callable=load_customer_seg_mongodb,
        dag=dag
    )
    step_end = PythonOperator(
        task_id='end_id',
        python_callable=end_process,
        dag=dag
    )
    ###DAG PARALELO#####
    step_start>>step_load_orders
    step_start>>step_load_order_items
    step_start>>step_load_products
    step_start>>step_load_customers
    step_start>>step_load_categories
    step_start>>step_load_departments
    step_load_orders>>step_master
    step_load_order_items>>step_master
    step_load_products>>step_master
    step_load_customers>>step_master
    step_load_categories>>step_master
    step_load_departments>>step_master
    step_master>>step_bi
    step_master>>step_customer_seg
    step_customer_seg>>step_customer_seg_mongodb
    step_customer_seg_mongodb>>step_end
    step_bi>>step_end
    ###DAG NORMAL###
    #step_start>>step_load_orders>>step_load_order_items>>step_load_products>>step_load_customers>>step_load_categories>>step_load_departments>>step_end
