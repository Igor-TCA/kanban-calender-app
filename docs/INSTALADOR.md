# Criando o Instalador do Calendário Kanban

Este guia explica como criar um instalador (setup wizard) para a aplicação.

## Pré-requisitos

1. **Node.js** (versão 18 ou superior)
   - Download: https://nodejs.org/
   - Verifique: `node --version`

2. **npm** (vem com Node.js)
   - Verifique: `npm --version`

## Passo a Passo

### 1. Instalar Dependências

Abra o terminal na pasta do projeto e execute:

```bash
npm install
```

Isso instalará o Electron e o Electron Builder.

### 2. Testar a Aplicação

Antes de criar o instalador, teste se está funcionando:

```bash
npm start
```

A aplicação deve abrir como um programa desktop.

### 3. Criar o Ícone (Opcional)

Para ter um ícone personalizado no instalador:

1. Converta o `assets/icon.svg` para `.ico` (Windows) usando:
   - https://convertio.co/svg-ico/
   - https://cloudconvert.com/svg-to-ico
   
2. Salve como `assets/icon.ico`

3. Tamanhos recomendados: 16x16, 32x32, 48x48, 256x256

### 4. Gerar o Instalador

```bash
npm run build:win
```

Ou para todas as plataformas:
```bash
npm run build
```

### 5. Encontrar o Instalador

O instalador será gerado em:
```
dist-instalador/
├── Calendário Kanban Setup 1.0.0.exe   <- Instalador Windows
└── ...
```

## Opções do Instalador (NSIS)

O instalador criado tem as seguintes características:

- ✅ **Wizard completo** (não é instalação silenciosa)
- ✅ **Permite escolher pasta de instalação**
- ✅ **Cria atalho na Área de Trabalho**
- ✅ **Cria atalho no Menu Iniciar**
- ✅ **Desinstalador incluído**
- ✅ **Idioma em Português (Brasil)**

## Estrutura de Arquivos

```
KANBAN_APP/
├── package.json           # Configuração do projeto
├── main-electron.js       # Ponto de entrada Electron
├── frontend/              # Aplicação web
│   ├── index.html
│   ├── css/
│   └── js/
├── assets/
│   ├── icon.svg          # Ícone fonte
│   └── icon.ico          # Ícone Windows (criar)
└── dist-instalador/      # Saída (gerado após build)
```

## Comandos Disponíveis

| Comando | Descrição |
|---------|-----------|
| `npm start` | Executa a aplicação em modo desenvolvimento |
| `npm run build` | Cria instaladores para todas as plataformas |
| `npm run build:win` | Cria instalador apenas para Windows |
| `npm run build:mac` | Cria instalador apenas para macOS |
| `npm run build:linux` | Cria instalador apenas para Linux |

## Personalizações

### Alterar Informações do Instalador

Edite o `package.json`:

```json
{
  "name": "calendario-kanban",
  "version": "1.0.0",           // Versão do app
  "description": "Sua descrição",
  "author": "Seu Nome",
  "build": {
    "productName": "Nome do Programa",
    "appId": "com.seudominio.app"
  }
}
```

### Alterar Comportamento do Instalador

No `package.json`, seção `build.nsis`:

```json
"nsis": {
  "oneClick": false,                        // false = wizard completo
  "allowToChangeInstallationDirectory": true, // permitir mudar pasta
  "createDesktopShortcut": true,            // atalho na área de trabalho
  "createStartMenuShortcut": true,          // atalho no menu iniciar
  "shortcutName": "Nome do Atalho"
}
```

## Solução de Problemas

### "electron não é reconhecido"
```bash
npm install
```

### Erro ao criar instalador
Verifique se:
1. Node.js está instalado corretamente
2. Você tem permissão de escrita na pasta
3. O antivírus não está bloqueando

### Ícone não aparece
1. Certifique-se que `assets/icon.ico` existe
2. O arquivo .ico deve ter múltiplos tamanhos (16, 32, 48, 256)

## Distribuição

Após criar o instalador:

1. Teste em uma máquina limpa (sem Node.js instalado)
2. Verifique se instala e desinstala corretamente
3. Distribua o arquivo `.exe` aos usuários

Os usuários só precisam executar o instalador - não precisam de Node.js!
