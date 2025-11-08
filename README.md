# Projeto Banco de Dados WeCon

## Integrantes: Letizia Lowatzki Baptistella (22.125.063-2), Manuella Filipe Peres (22.224.029-3), Rafaela Altheman de Campos (22.125.062-4)

## 1. Explicação do tema escolhido
O grupo escolheu realizar um projeto baseado em uma loja de roupas por conta do interesse e proximidade das integrantes com o assunto, inspirado na empresa "YouCom", a "WeCon" é uma marca de roupas, dentro do banco podemos acessar algumas ferramentas comuns dentro de uma loja de vestuário como: cadastro de clientes, estoque, histórico de compras, entre outras.

## 2. Justificativa para cada banco usado no projeto e definição de como S2 será implementado
Os seguintes bancos foram utilizados para o desenvolvimento do projeto:
  - Banco relacional: Supabase -> Utilizado para o cadastro dos clientes, foi escolhido pela familiaridade das membros com o banco de dados, visto que já foi utilizado em projetos anteriores dentro da faculdade, além de possuir um painel de fácil uso e recursos prontos que aceleram o desenvolvimento do projeto.
  - Bancos não relacionais:
    - MongoDB -> Utilizado para guardar os produtos em estoque da loja, foi escolhido pois permite dados mais flexíveis, como em formato JSON, visto que a quantidade de dados em um estoque é grande, esse recurso foi muito importante.
    - Neo4J -> Utilizado para o histórico de compras, foi escolhido por ser um banco de dados que possui uma interface que ajuda na análise dos dados, e consequentemente nos ajuda a reconhecer padrões para funções como recomendações de produtos aos clientes.
      
O S1 é uma interface gráfica desenvolvida em Python, responsável por coletar os dados dos usuários e enviar requisições para o S2. O S2 atua como intermediário entre o S1 e os três bancos de dados utilizados, recebendo as requisições, processando elas e executando as operações requisitadas.
Além disso, quando o S1 solicita informações o S2 consulta os bancos e retorna os dados para o S1, realizando assim toda a comunicação entre o sistema e as bases de dados.
Também, foi criado o código "wecon.py", que popula os bancos com dados falsos como nomes e endereços de clientes.

## 3. Explicação de como executar o projeto e quais serviços devem ser usados
1- Logue no Supabase e crie as tabelas necessárias para armazenar os dados dos clientes. <br>
2- Configure o MongoDB para armazenar os dados dos produtos. <br>
3- Configure o Neo4j para armazenar os relacionamentos entre clientes e produtos. <br>
4- Execute o código wecon.py para popular os bancos de dados. <br>
5- Inicie o S2 e, posteriormente, o S1 para interagir com o sistema. <br>
Comandos: python S2.py e python S1.py, após rodar os dois nessa ordem a interface abrirá e será possível cadastrar clientes e realizar as operações necessárias.


<img width="983" height="315" alt="image" src="https://github.com/user-attachments/assets/14eb78a6-c06c-47fd-ae64-26306350afe0" />
<img width="504" height="190" alt="image (1)" src="https://github.com/user-attachments/assets/aa1f32ea-7e27-4cc2-aeb3-e130791153c8" />
<img width="764" height="398" alt="image (2)" src="https://github.com/user-attachments/assets/ca9d6d82-0ced-429a-b399-bc9238b51756" />
