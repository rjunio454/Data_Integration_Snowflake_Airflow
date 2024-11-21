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

Claro! Aqui está a descrição aprimorada para o **Passo 5** do seu README, explicando como criar a tabela `COFFEE` no schema `RAW` via interface gráfica do Snowflake.

---

### **Passo 5: Criar a Tabela COFFEE**

Neste passo, vamos criar a tabela `COFFEE` no schema `RAW` para armazenar os dados brutos da cafeteria. Para isso, siga os passos abaixo utilizando a interface gráfica do Snowflake.

#### 1. **Criar a Tabela a partir de um Arquivo**
   - Acesse o **Snowflake Web UI**.
   - No painel lateral esquerdo, escolha o **Database** `IMPACTA`.
   - Selecione o **Schema** `RAW`, onde a tabela será criada.
   - Clique em **Create** no canto superior direito e selecione **Table** > **From File**.
   
   Isso permitirá que você crie a tabela diretamente a partir de um arquivo carregado previamente (como um arquivo CSV ou outro tipo de arquivo de dados). A interface gráfica tentará automaticamente mapear as colunas e os tipos de dados com base no conteúdo do arquivo.

#### 2. **Ajustar o Esquema da Tabela**
   Após carregar o arquivo para a tabela `COFFEE`, você precisará ajustar o esquema para garantir que todos os tipos de dados estejam corretos. Isso pode incluir:
   - **Formato de Data**: Se o arquivo contém campos de data, verifique se o formato está correto (por exemplo, `YYYY-MM-DD`). Ajuste o tipo de dado da coluna para `DATE` ou outro tipo adequado.
   - **Tipos de Dados**: Verifique se todos os campos possuem os tipos de dados corretos, como `VARCHAR`, `NUMBER`, etc. Caso necessário, altere o tipo de dado diretamente na interface gráfica.
   
   
   Para ajustar o esquema:
   - Clique em **Table** no painel esquerdo, selecione a tabela `COFFEE` e edite as colunas conforme necessário.
   - Se o tipo de dados da coluna precisar ser alterado, clique no nome da coluna e modifique o tipo de dados.

#### 3. **Salvar as Alterações**
   Após ajustar o esquema da tabela para garantir que os tipos de dados estejam corretos, clique em **Save** para confirmar as mudanças.

---

Agora a tabela `COFFEE` estará pronta para armazenar os dados brutos da cafeteria no schema `RAW` e pronta para ser usada no processo de carga de dados.

---

Continua...