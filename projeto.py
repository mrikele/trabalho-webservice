from fastapi import FastAPI
from typing import List
from pydantic import BaseModel

app = FastAPI()

OK = "OK"
FALHA = "FALHA"

# Classe representando os dados do endereço do cliente
class Endereco(BaseModel):
    rua: str
    cep: str
    cidade: str
    estado: str

# Classe representando os dados do cliente
class Usuario(BaseModel):
    id: int
    nome: str
    email: str
    senha: str

# Classe representando a lista de endereços de um cliente
class ListaDeEnderecosDoUsuario(BaseModel):
    usuario: Usuario
    enderecos: List[Endereco] = []

# Classe representando os dados do produto
class Produto(BaseModel):
    id: int
    nome: str
    descricao: str
    preco: float

# Classe representando o carrinho de compras de um cliente com uma lista de produtos
class CarrinhoDeCompras(BaseModel):
    id_usuario: int
    id_produtos: List[Produto] = []
    preco_total: float
    quantidade_de_produtos: int

db_usuarios = {}
db_produtos = {}
db_end = {}        # enderecos_dos_usuarios
db_carrinhos = {}

class OrganizarConsulta:
    def __init__(self):
        self.db_usuarios = []
        self.db_produtos = []
        self.db_enderecos = []
        self.db_carrinhos = []

    def usuario_id(self, id_usuario: int): #usuario por id
        for usuario in self.db_usuarios:
            if usuario.id == id_usuario:
                return usuario

    def usuarios_nome(self, nome: str): #usuario pelo nome
        usuarios = []
        for usuario in self.db_usuarios:
            if usuario.nome.split()[0] == nome:
                usuarios.append(usuario)
        return usuarios

    def senhafunc(self, senha: str) -> bool:
        return len(senha) >= 3

    def emailfunc(self, email: str) -> bool:
        return "@" in email

    def mesmo_dominio(self, dominio: str):
        emails = []
        for usuario in self.db_usuarios:
            if dominio == usuario.email.split("@")[1]:
                emails.append({"e-mail": usuario.email})
        return emails

    def validaruser(self, id: int, email: str, senha: str) -> bool:
        return self.emailfunc(email) and self.senhafunc(senha) and not self.usuario_id(id)

    def produto_id_exibir(self, id: int):
        for produto in self.db_produtos:
            if produto.id == id:
                return produto

    def exibircarrinho(self, id_usuario: int):
        for carrinho in self.db_carrinhos:
            if carrinho.id_usuario == id_usuario:
                return carrinho

    def tirardocarrinho(self, id_produto: int):
        for verifica in self.db_carrinhos:
            for produto in verifica.produtos:
                if produto.id == id_produto:
                    verifica.produtos.remove(produto)

    def enderecos_usuario(self, id_usuario: int):
        for registro in self.db_enderecos:
            if registro.usuario.id == id_usuario:
                return registro.enderecos

cons = OrganizarConsulta()

# Criar um usuário,
# se tiver outro usuário com o mesmo ID retornar falha, 
# se o email não tiver o @ retornar falha, 
# senha tem que ser maior ou igual a 3 caracteres, 
# senão retornar OK
@app.post("/usuario/")
async def criar_usuário(usuario: Usuario):
    if cons.validaruser(usuario.id, usuario.email, usuario.senha):
        cons.db_usuarios.append(usuario)
        return OK
    return FALHA
    
# Se o id do usuário existir, retornar os dados do usuário
# senão retornar falha
@app.get("/usuario/")
async def retornar_usuario(id: int):
    usuario_encontrado = cons.usuario_id(id)
    return usuario_encontrado if usuario_encontrado else FALHA

# Se existir um usuário com exatamente o mesmo nome, retornar os dados do usuário
# senão retornar falha
@app.get("/usuario/nome")
async def usuarios_mesmo_nome(nome: str):
    usuario_encontrado = cons.usuarios_nome(nome)
    return usuario_encontrado if usuario_encontrado else FALHA

# Se o id do usuário existir, deletar o usuário e retornar OK
# senão retornar falha
# ao deletar o usuário, deletar também endereços e carrinhos vinculados a ele
@app.delete("/usuario/")
async def deletar_usuario(id: int):
    usuario_encontrado = cons.usuario_id(id)
    carrinho_encontrado = cons.exibircarrinho(id)
    enderecos_encontrados = cons.enderecos_usuario(id)
    if usuario_encontrado:
        cons.db_usuarios.remove(usuario_encontrado)
        if carrinho_encontrado:
            cons.db_carrinhos.remove(carrinho_encontrado)
        if enderecos_encontrados:
            cons.db_enderecos.remove(enderecos_encontrados)
        return OK
    return FALHA

# Se não existir usuário com o id_usuario retornar falha, 
# senão retornar uma lista de todos os endereços vinculados ao usuário
# caso o usuário não possua nenhum endereço vinculado a ele, retornar 
# uma lista vazia
### Estudar sobre Path Params: (https//fastapi.tiangolo.com/tutorial/path-params/)
@app.get("/usuario/{id_usuario}/endereços/")
async def return_end(id_usuario: int):
    enderecos_encontrados = cons.enderecos_usuario(id_usuario)
    if enderecos_encontrados:
        return enderecos_encontrados
    return FALHA

# Retornar todos os emails que possuem o mesmo domínio
# (domínio do email é tudo que vêm depois do @)
# senão retornar falha
@app.get("/usuarios/emails/")
async def retornar_emails(dominio: str):
    emails_encontrados = cons.mesmo_dominio(dominio)
    return emails_encontrados if emails_encontrados else FALHA

# Se não existir usuário com o id_usuario retornar falha, 
# senão cria um endereço, vincula ao usuário e retornar OK
@app.post("/endereco/{id_usuario}/")
async def criar_endereco(endereco: Endereco, id_usuario: int):
    usuario_cadastrado = cons.usuario_id(id_usuario)
    enderecos_encontrados = cons.enderecos_usuario(id_usuario)
    if usuario_cadastrado:
        if enderecos_encontrados:
            enderecos_encontrados.append(endereco)
        else:
            cons.db_enderecos.append(ListaDeEnderecosDoUsuario(usuario=usuario_cadastrado, enderecos=[endereco]))
        return OK
    return FALHA

# Se tiver outro produto com o mesmo ID retornar falha, 
# senão cria um produto e retornar OK
@app.post("/produto/")
async def criar_produto(produto: Produto):
    produto_encontrado = cons.produto_id_exibir(produto.id)
    if not produto_encontrado:
        cons.db_produtos.append(produto)
        return OK
    return FALHA

# Se não existir produto com o id_produto retornar falha, 
# senão deleta produto correspondente ao id_produto e retornar OK
# (lembrar de desvincular o produto dos carrinhos do usuário)
@app.delete("/produto/{id_produto}/")
async def deletar_produto(id_produto: int):
    produto_cadastrado = cons.produto_id_exibir(id_produto)
    if produto_cadastrado:
        cons.db_produtos.remove(produto_cadastrado)
        cons.tirardocarrinho(id_produto)
        return OK
    return FALHA

# Se não existir usuário com o id_usuario ou id_produto retornar falha, 
# se não existir um carrinho vinculado ao usuário, crie o carrinho
# e retornar OK
# senão adiciona produto ao carrinho e retornar OK
@app.post("/carrinho/{id_usuario}/{id_produto}/")
async def addcarrinho(id_usuario: int, id_produto: int):
    usuario_cadastrado = cons.usuario_id(id_usuario)
    produto_cadastrado = cons.produto_id_exibir(id_produto)
    carrinho_ok = cons.exibircarrinho(id_usuario)

    if usuario_cadastrado and produto_cadastrado:
        if carrinho_ok:
            carrinho_ok.produtos.append(produto_cadastrado)
            carrinho_ok.preco_total += produto_cadastrado.preco
            carrinho_ok.quantidade = len(carrinho_ok.produtos) 
        else:
            carrinho = CarrinhoDeCompras(id_usuario=id_usuario, produtos=[produto_cadastrado], preco_total=produto_cadastrado.preco, quantidade=1)
            cons.db_carrinhos.append(carrinho)
        return OK
    return FALHA

# Se não existir carrinho com o id_usuario retornar falha, 
# senão retorna o carrinho de compras.
@app.get("/carrinho/{id_usuario}/")
async def exibircarrinho(id_usuario: int):
    carrinho_ok = cons.exibircarrinho(id_usuario)
    return carrinho_ok if carrinho_ok else FALHA
    
# Se não existir carrinho com o id_usuario retornar falha, 
# senão retorna o o número de itens e o valor total do carrinho de compras.
@app.get("/carrinho/{id_usuario}/")
async def retornar_total_carrinho(id_usuario: int):
    carrinho_ok = cons.exibircarrinho(id_usuario)
    totalcompras = 0
    if carrinho_ok:
        for produtos in carrinho_ok.produtos:
            totalcompras += produtos.preco
        return carrinho_ok.quantidade, totalcompras
    else:
        return FALHA

# Se não existir usuário com o id_usuario retornar falha, 
# senão deleta o carrinho correspondente ao id_usuario e retornar OK
@app.delete("/carrinho/{id_usuario}/")
async def deletar_carrinho(id_usuario: int):
    carrinho_ok = cons.exibircarrinho(id_usuario)
    if carrinho_ok:
        cons.db_carrinhos.remove(carrinho_ok)
        return OK
    return FALHA

@app.get("/")
async def bem_vinda():
    site = "Seja bem vindo"
    return site.replace('\n', '')
