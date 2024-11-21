### README - Configuração Inicial no Snowflake

Este guia descreve os passos necessários para realizar a configuração inicial no **Snowflake**, incluindo a criação de um banco de dados, schema, stage, upload de arquivos e criação de tabelas.

---

### **Passo 1: Criar o banco de dados**
1. Acesse sua conta Snowflake.
2. Execute o seguinte comando SQL para criar o banco de dados:

   ```sql
   CREATE DATABASE IMPACTA;
   ```

---

### **Passo 2: Criar o schema**
1. Dentro do banco de dados `IMPACTA`, crie um schema chamado `RAW` com o seguinte comando:

   ```sql
   CREATE SCHEMA RAW;
   ```

---

### **Passo 3: Criar a STAGE**
1. Crie uma stage chamada `STG_RAW` no schema `RAW`, que será utilizada para armazenar arquivos temporariamente:

   ```sql
   CREATE OR REPLACE STAGE RAW.STG_RAW;
   ```

2. Certifique-se de que a stage está configurada corretamente para receber os arquivos.

---

### **Passo 4: Fazer o upload do arquivo**
1. Utilize a interface gráfica do Snowflake para fazer o upload do arquivo manualmente para a `STG_RAW`:
   - No menu lateral, acesse **Data > Stages**.
   - Encontre a stage `RAW.STG_RAW`.
   - Clique em **Upload** e selecione o arquivo que deseja carregar.

---

### **Passo 5: Criar a tabela COFFEE**
1. No schema `RAW`, crie a tabela `COFFEE`, que irá armazenar os dados brutos da cafeteria. Certifique-se de configurar os campos corretamente (incluindo o formato de data e tipos de dados). Exemplo de criação:

   ```sql
   CREATE TABLE RAW.COFFEE (
       SALE_ID INTEGER,
       PRODUCT_NAME STRING,
       STORE_NAME STRING,
       SALE_DATE DATE,
       SALE_AMOUNT DECIMAL(10, 2)
   );
   ```

2. Ajuste o esquema da tabela com base no formato do arquivo carregado.

---

### **Dicas Importantes**
- Sempre verifique o formato do arquivo (CSV, JSON, etc.) e configure os tipos de dados adequadamente.
- Utilize comandos como `LIST @RAW.STG_RAW` para verificar se o arquivo foi carregado corretamente na stage.

Continua...