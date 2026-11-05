# WhatsApp Desktop Enhancer

**Autor:** mrido1

O WhatsApp Desktop Enhancer melhora o uso do **aplicativo atual do WhatsApp para computador** (disponível na Microsoft Store) com o NVDA. Ele facilita a navegação e resolve problemas de interação causados pelas mudanças recentes na tecnologia do WhatsApp.

## Por que este complemento é necessário?

A versão do WhatsApp para Windows passou por grandes mudanças de arquitetura:

*   **Versão nativa (UWP):** entre **2021 e 2022**, o WhatsApp lançou uma versão nativa, com ótimo desempenho e bom suporte a leitores de tela.
*   **Versão WebView2:** a partir do **fim de 2025**, o WhatsApp passou a usar um mecanismo web (WebView2). Isso trouxe problemas para quem usa leitor de tela, como foco instável e conflitos com o modo de navegação.

**O problema:** como o novo aplicativo é baseado na web, o NVDA pode ativar o modo de navegação quando não deveria. Isso atrapalha atalhos como `Ctrl+F` e dificulta a digitação. Além disso, o foco pode ficar preso nos itens das listas.

**A solução:** o complemento **desativa e bloqueia o modo de navegação**, para o NVDA tratar o WhatsApp como um aplicativo comum. Se preferir, você pode desativar esse bloqueio nas configurações, mas isso não é recomendado.

## Atalhos do próprio WhatsApp (recomendados)

O aplicativo foi feito para ser usado pelo teclado. Dê preferência a estes atalhos, que costumam ser mais rápidos e confiáveis que qualquer script.

### Conversas

*   `Ctrl+Shift+U`: marcar como não lida
*   `Ctrl+Shift+M`: silenciar
*   `Ctrl+Shift+A`: arquivar a conversa
*   `Ctrl+Alt+Shift+P`: fixar a conversa
*   `Ctrl+]`: próxima conversa
*   `Ctrl+[`: conversa anterior
*   `Ctrl+Shift+N`: novo grupo
*   `Ctrl+Alt+N`: nova conversa
*   `Esc`: fechar a conversa
*   `Ctrl+Shift+B`: bloquear a conversa
*   `Ctrl+Alt+Shift+L`: etiquetar a conversa (WhatsApp Business)

### Navegação e busca

*   `Ctrl+Alt+/`: busca geral
*   `Ctrl+Shift+F`: buscar na conversa atual
*   `Alt+K`: busca avançada
*   `Ctrl+Alt+P`: perfil e recado
*   `Alt+I`: abrir os dados da conversa
*   `Alt+S`: configurações
*   `Alt+L`: bloquear o aplicativo
*   `Ctrl+1` a `Ctrl+9`: ir para a conversa daquela posição

### Mensagens

*   `Alt+R`: responder
*   `Ctrl+Alt+R`: responder em particular
*   `Ctrl+Alt+D`: encaminhar
*   `Alt+8`: favoritar a mensagem
*   `Ctrl+Seta para cima`: editar a última mensagem
*   `Alt+A`: abrir o painel de anexos
*   `Ctrl+Alt+E`: painel de emojis
*   `Ctrl+Alt+G`: painel de GIFs
*   `Ctrl+Alt+S`: painel de figurinhas

### Mensagens de voz

*   `Shift+.`: aumentar a velocidade de reprodução
*   `Shift+,`: diminuir a velocidade de reprodução
*   `Ctrl+Enter`: enviar a mensagem de voz
*   `Alt+P`: pausar a gravação
*   `Ctrl+Alt+Shift+R`: iniciar a gravação

## Recursos do complemento

Estes recursos complementam o WhatsApp onde ainda há dificuldades de acessibilidade.

### 1. Leitura das mensagens

*   **Menu de contexto (`Shift+Enter`):** abre o menu de opções da mensagem em foco.
*   **Mensagem de voz (`Enter`):** reproduz ou pausa a mensagem de voz em foco.
*   **Janela de texto (`Alt+C`):** abre a mensagem em foco em uma janela somente leitura. Nela, você pode ler com as setas e selecionar trechos. Pressione `Esc` para fechar.
*   **Cópia rápida (`Ctrl+C`):** copia o texto da mensagem em foco para a área de transferência.

### 2. Revisão do último texto falado

Como o complemento mantém o modo de navegação desativado, o cursor de revisão do NVDA pode não servir para rever avisos rápidos. Por isso, ele guarda a última fala para você revisar:

*   `NVDA+Seta para a esquerda` e `NVDA+Seta para a direita`: revisar caractere por caractere
*   `NVDA+Ctrl+Seta para a esquerda` e `NVDA+Ctrl+Seta para a direita`: revisar palavra por palavra
*   `NVDA+Seta para cima` e `NVDA+Seta para baixo`: revisar linha por linha

### 3. Filtro de números de telefone

Em grupos, números de pessoas fora dos seus contatos deixam a leitura longa e difícil de acompanhar. O complemento pode retirar esses números da fala e do braille.

Os filtros da lista de conversas e da lista de mensagens são configurados separadamente nas configurações do complemento. Você também pode atribuir um comando a cada um na caixa de diálogo Definir Comandos do NVDA.

### 4. Dicas de uso

O WhatsApp acrescenta instruções repetidas a cada item, como "Para acessar o menu e encontrar mais opções, pressione a tecla de seta para a esquerda ou direita".

As dicas são lidas por padrão. Para silenciá-las, desmarque a opção "Ler as dicas de uso ao navegar pela lista de conversas" nas configurações do complemento. O status da mensagem, como "lida" ou "entregue", continua sendo falado.

### 5. Navegação virtual em menus inacessíveis

Algumas partes do WhatsApp, como painéis de configurações e menus de diálogo, são difíceis de usar com o modo de navegação desativado. Nelas, o complemento monta uma lista temporária com as opções disponíveis.

*   **Setas para cima e para baixo:** percorrem as opções. O NVDA fala cada item e o estado dele, como ativado ou desativado, sem mudar o foco na tela.
*   **`Ctrl+Enter`:** ativa a opção escolhida.

**Importante:** este recurso ainda é experimental. Se encontrar um erro ou tiver uma ideia melhor, contribua pelo repositório no GitHub.

## Sugestões e contribuições

Sugestões, relatos de erros e contribuições de código são bem-vindos.

*   **E-mail:** [bredgreene5@gmail.com](mailto:bredgreene5@gmail.com)
*   **GitHub:** abra uma issue ou envie um pull request no repositório do projeto.
