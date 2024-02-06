# trabalho-webservice
Carrinho de compras
## Como executar 

#### Instalação
* Create venv
    ```
    $ virtualenv venv --python=3.10
    ```
    Linux
    ```
    $ source venv/bin/activate
   ```
   Windows
    ```
    $ .\venv\Scripts\activate
   ```
* Instalar bibliotecas
     ```
     pip install fastapi uvicorn pydantic

     ```
### Execução localhost
  ```
  $ uvicorn projeto:app --reload
   ```
