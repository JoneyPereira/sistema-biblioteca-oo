# Diagrama de Casos de Uso
```mermaid
%% Diagrama de Casos de Uso
%% https://mermaid.live/edit para visualizar

%%{init: {'theme': 'default'}}%%
graph TD
    Usuario -->|Autenticar| Sistema
    Usuario -->|Consultar livros| Sistema
    Usuario -->|Solicitar empréstimo| Sistema
    Usuario -->|Devolver livro| Sistema

    Bibliotecario -->|Autenticar| Sistema
    Bibliotecario -->|Cadastrar livro| Sistema
    Bibliotecario -->|Cadastrar usuário| Sistema
    Bibliotecario -->|Calcular multa| Sistema

    Sistema -->|Solicita pagamento| SistemaPagamento
```
