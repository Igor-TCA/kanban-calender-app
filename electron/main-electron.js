/**
 * Arquivo principal do Electron
 * Configura a janela desktop da aplicação Kanban
 */

const { app, BrowserWindow, Menu, shell } = require('electron');
const path = require('path');

// Manter referência global da janela para evitar garbage collection
let mainWindow;

/**
 * Cria a janela principal da aplicação
 */
function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1280,
        height: 720,
        minWidth: 800,
        minHeight: 600,
        title: 'Calendário Kanban',
        icon: path.join(__dirname, '..', 'assets', process.platform === 'win32' ? 'icon.ico' : 'icon.png'),
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            enableRemoteModule: false
        },
        show: false, // Mostrar apenas quando estiver pronto
        backgroundColor: '#121212'
    });

    // Carregar o arquivo HTML
    mainWindow.loadFile(path.join(__dirname, '..', 'frontend', 'index.html'));

    // Mostrar janela quando estiver pronta (evita flash branco)
    mainWindow.once('ready-to-show', () => {
        mainWindow.show();
    });

    // Abrir links externos no navegador padrão
    mainWindow.webContents.setWindowOpenHandler(({ url }) => {
        shell.openExternal(url);
        return { action: 'deny' };
    });

    // Limpar referência quando a janela for fechada
    mainWindow.on('closed', () => {
        mainWindow = null;
    });

    // Criar menu personalizado
    createMenu();
}

/**
 * Cria o menu da aplicação
 */
function createMenu() {
    const template = [
        {
            label: 'Arquivo',
            submenu: [
                {
                    label: 'Nova Tarefa',
                    accelerator: 'CmdOrCtrl+N',
                    click: () => {
                        mainWindow.webContents.executeJavaScript(`
                            document.getElementById('btn-nova-tarefa').click();
                        `);
                    }
                },
                {
                    label: 'Atualizar',
                    accelerator: 'CmdOrCtrl+R',
                    click: () => {
                        mainWindow.webContents.executeJavaScript('atualizarTudo()');
                    }
                },
                { type: 'separator' },
                {
                    label: 'Sair',
                    accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Alt+F4',
                    click: () => app.quit()
                }
            ]
        },
        {
            label: 'Visualizar',
            submenu: [
                {
                    label: 'Kanban',
                    accelerator: 'CmdOrCtrl+1',
                    click: () => {
                        mainWindow.webContents.executeJavaScript(`
                            document.querySelector('[data-aba="kanban"]').click();
                        `);
                    }
                },
                {
                    label: 'Agenda',
                    accelerator: 'CmdOrCtrl+2',
                    click: () => {
                        mainWindow.webContents.executeJavaScript(`
                            document.querySelector('[data-aba="agenda"]').click();
                        `);
                    }
                },
                { type: 'separator' },
                {
                    label: 'Alternar Tema',
                    accelerator: 'CmdOrCtrl+T',
                    click: () => {
                        mainWindow.webContents.executeJavaScript('alternarTema()');
                    }
                },
                { type: 'separator' },
                {
                    label: 'Tela Cheia',
                    accelerator: 'F11',
                    click: () => {
                        mainWindow.setFullScreen(!mainWindow.isFullScreen());
                    }
                },
                {
                    label: 'Ferramentas do Desenvolvedor',
                    accelerator: 'F12',
                    click: () => {
                        mainWindow.webContents.toggleDevTools();
                    }
                }
            ]
        },
        {
            label: 'Ajuda',
            submenu: [
                {
                    label: 'Sobre',
                    click: () => {
                        const { dialog } = require('electron');
                        dialog.showMessageBox(mainWindow, {
                            type: 'info',
                            title: 'Sobre',
                            message: 'Calendário Kanban',
                            detail: 'Versão 1.0.0\n\nAplicação para gerenciamento de tarefas semanais.\n\n© 2025 DevBroCorp'
                        });
                    }
                }
            ]
        }
    ];

    const menu = Menu.buildFromTemplate(template);
    Menu.setApplicationMenu(menu);
}

// Quando o Electron estiver pronto
app.whenReady().then(() => {
    createWindow();

    // No macOS, recriar janela quando clicar no ícone do dock
    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});

// Fechar app quando todas as janelas forem fechadas (exceto macOS)
app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

// Segurança: desabilitar navegação para URLs externas
app.on('web-contents-created', (event, contents) => {
    contents.on('will-navigate', (event, navigationUrl) => {
        const parsedUrl = new URL(navigationUrl);
        if (parsedUrl.origin !== 'file://') {
            event.preventDefault();
        }
    });
});
