"""
# CAFE

Esta é uma DAG que faz o processo de carga do fluxo de DW da cafeteria.

"""

import pendulum
from airflow.models.dag import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.hooks.base import BaseHook
import snowflake.connector as sc
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
import os

minha_conexao = "snowflake_conn"
meu_arquivo = "COFFEE/coffee_shop_sales*"

diretorio_raiz = os.environ.get("AIRFLOW_HOME")

with DAG(
    dag_id="01_coffee",
    schedule=None,
    start_date=pendulum.datetime(2024, 11, 18, tz="UTC"),
    tags=["coffee", "dw"],
    doc_md=__doc__,
    description="esta é a descrição da DAG",
):

    # Obtém a conexão do banco de dados do Airflow
    def obter_credenciais_conexao(conn_id):
        conexao = BaseHook.get_connection(f"{conn_id}")

        if conexao:
            login = conexao.login
            senha = conexao.password
            conta = conexao.extra.split('"account": "')[1].split('"')[0]
            regiao = conexao.extra.split('"region": "')[1].split('"')[0]
            return login, senha, conta, regiao
        else:
            print(f"A conexão com o ID '{conn_id}' não foi encontrada.")
            return None, None

    def envia_arquivo(arquivo):
        login, senha, conta, regiao = obter_credenciais_conexao(minha_conexao)
        conn = sc.connect(user=login, password=senha, account=f"{conta}.{regiao}")
        conn.cursor().execute(
            f"""
PUT file://dags/{arquivo} @IMPACTA.RAW.STG_RAW AUTO_COMPRESS=FALSE OVERWRITE = TRUE;
"""
        )
        return f"arquivo {arquivo} enviado para a STAGE @IMPACTA.RAW.STG_RAW"

    start = EmptyOperator(task_id="start")
    envia_arquivo_para_nuvem = PythonOperator(
        task_id="envia_arquivo_para_nuvem",
        python_callable=envia_arquivo,
        op_args=[f"{meu_arquivo}"],
        doc_md="Task que envia o arquivo csv para a nuvem do Snowflake",
    )
    # Executar a consulta usando SnowflakeOperator
    sql1 = """
CREATE or replace TABLE "IMPACTA"."RAW"."COFFEE" ( transaction_id NUMBER(38, 0) , transaction_date DATE , transaction_time TIME , store_id NUMBER(38, 0) , store_location VARCHAR , product_id NUMBER(38, 0) , transaction_qty NUMBER(38, 0) , unit_price NUMBER(38, 1) , product_category VARCHAR , product_type VARCHAR , product_detail VARCHAR , Size VARCHAR , Total_bill NUMBER(38, 1) , Month_Name VARCHAR , Day_Name VARCHAR , Hour NUMBER(38, 0) , Day_of_Week NUMBER(38, 0) , Month NUMBER(38, 0) ); 

CREATE TEMP FILE FORMAT "IMPACTA"."RAW"."temp_file_format_cafe"
	TYPE=CSV
    SKIP_HEADER=1
    FIELD_DELIMITER=';'
    TRIM_SPACE=TRUE
    FIELD_OPTIONALLY_ENCLOSED_BY='"'
    REPLACE_INVALID_CHARACTERS=TRUE
    DATE_FORMAT='DD/MM/YYYY'
    TIME_FORMAT=AUTO
    TIMESTAMP_FORMAT=AUTO; 

COPY INTO "IMPACTA"."RAW"."COFFEE" 
FROM (SELECT $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18
	FROM '@"IMPACTA"."RAW"."STG_RAW"') 
PATTERN = '.*coffee_shop_sales_.*csv'
FILE_FORMAT = '"IMPACTA"."RAW"."temp_file_format_cafe"' 
ON_ERROR=ABORT_STATEMENT 
;
"""
    copy_file = SnowflakeOperator(
        task_id="copy_file",
        sql=sql1,
        snowflake_conn_id=minha_conexao,  # Nome da conexão configurada no Airflow para o Snowflake
        autocommit=True,
        split_statements=True,
    )
    sql_dim_product = """
MERGE INTO IMPACTA.COFFEE.DIM_PRODUCT AS destino
USING (
    SELECT DISTINCT
        product_id,
        product_category,
        product_type,
        product_detail,
        size
    FROM IMPACTA.RAW.COFFEE
) AS origem
ON destino.product_id = origem.product_id
WHEN MATCHED THEN
    UPDATE SET
        destino.product_category = origem.product_category,
        destino.product_type = origem.product_type, 
        destino.product_detail = origem.product_detail, 
        destino.size = origem.size
WHEN NOT MATCHED THEN
    INSERT (product_id, product_category, product_type, product_detail, size) 
    VALUES (origem.product_id, origem.product_category, origem.product_type, origem.product_detail, origem.size);
"""
    coffee_dim_product = SnowflakeOperator(
        task_id="coffee_dim_product",
        sql=sql_dim_product,
        snowflake_conn_id=minha_conexao,
        autocommit=True,
        split_statements=True,
    )
    sql_dim_store = """
MERGE INTO IMPACTA.COFFEE.DIM_STORE AS destino
USING (
    SELECT DISTINCT
        store_id, store_location
    FROM IMPACTA.RAW.COFFEE
) AS origem
ON destino.store_id = origem.store_id
WHEN MATCHED THEN
  UPDATE SET destino.store_location = origem.store_location
WHEN NOT MATCHED THEN
  INSERT (store_id, store_location) 
  VALUES (origem.store_id, origem.store_location);
"""
    coffee_dim_store = SnowflakeOperator(
        task_id="coffee_dim_store",
        sql=sql_dim_store,
        snowflake_conn_id=minha_conexao,
        autocommit=True,
        split_statements=True,
    )
    sql_fact_sales = """
MERGE INTO IMPACTA.COFFEE.FACT_SALES AS destino
USING (select distinct transaction_id, transaction_date, transaction_time, store_id, product_id, transaction_qty, unit_price, total_bill from IMPACTA.RAW.COFFEE) AS origem
ON destino.transaction_id = origem.transaction_id
WHEN MATCHED THEN
  UPDATE SET destino.transaction_date = origem.transaction_date,
  destino.transaction_time = origem.transaction_time,
  destino.store_id = origem.store_id,
  destino.product_id = origem.product_id,
  destino.transaction_qty = origem.transaction_qty,
  destino.unit_price = origem.unit_price,
  destino.total_bill = origem.total_bill
WHEN NOT MATCHED THEN
  INSERT (transaction_id, transaction_date, transaction_time, store_id, product_id, transaction_qty, unit_price, total_bill) 
  VALUES (origem.transaction_id, origem.transaction_date, origem.transaction_time, origem.store_id, origem.product_id, origem.transaction_qty, origem.unit_price, origem.total_bill);
"""
    coffee_fact_sales = SnowflakeOperator(
        task_id="coffee_fact_sales",
        sql=sql_fact_sales,
        snowflake_conn_id=minha_conexao,
        autocommit=True,
        split_statements=True,
    )
    sql_remove = """
REMOVE '@"IMPACTA"."RAW"."STG_RAW"/' PATTERN = '.*coffee_shop_sales_.*csv'
"""
    coffee_remove_file = SnowflakeOperator(
        task_id="coffee_remove_file",
        sql=sql_remove,
        snowflake_conn_id=minha_conexao,
        autocommit=True,
        split_statements=True,
    )
    coffee_move_file_process = BashOperator(
        task_id="coffee_move_file_process",
        bash_command=f"mv {diretorio_raiz}/dags/COFFEE/coffee_shop_sales_*.csv {diretorio_raiz}/dags/COFFEE/process/",
    )
    end = EmptyOperator(task_id="end")


start >> envia_arquivo_para_nuvem >> copy_file
(
    copy_file
    >> (coffee_dim_product, coffee_dim_store)
    >> coffee_fact_sales
    >> (coffee_remove_file, coffee_move_file_process)
    >> end
)
