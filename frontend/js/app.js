// Rota do Bem - Frontend JavaScript
class RotaDoBemApp {
    constructor() {
        this.apiUrl = 'http://localhost:5000/api';
        this.currentUser = null;
        this.init();
    }

    init() {
        this.checkApiStatus();
        this.setupEventListeners();
        this.loadInitialData();
    }

    // Verificar status da API
    async checkApiStatus() {
        try {
            const response = await fetch(`${this.apiUrl}`);
            const data = await response.json();
            
            const statusElement = document.querySelector('.status');
            if (data.status) {
                statusElement.className = 'status status-online';
                statusElement.innerHTML = `
                    <h3>✅ Backend Online</h3>
                    <p>Sistema funcionando corretamente!</p>
                    <p><strong>Versão:</strong> ${data.versao || '1.0.0'}</p>
                `;
            }
        } catch (error) {
            console.error('API não está respondendo:', error);
            const statusElement = document.querySelector('.status');
            statusElement.className = 'status status-offline';
            statusElement.innerHTML = `
                <h3>❌ Backend Offline</h3>
                <p>Verifique se o servidor está rodando</p>
                <p>Execute: <code>python run.py</code></p>
            `;
        }
    }

    // Configurar event listeners
    setupEventListeners() {
        // Navegação
        document.querySelectorAll('.nav-item a').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = e.target.getAttribute('data-page');
                this.showPage(page);
            });
        });

        // Formulários
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleFormSubmit(e.target);
            });
        });
    }

    // Carregar dados iniciais
    async loadInitialData() {
        // Carregar estatísticas se existir
        await this.loadStats();
    }

    // Mostrar página específica
    showPage(page) {
        // Esconder todas as páginas
        document.querySelectorAll('.page').forEach(p => {
            p.style.display = 'none';
        });

        // Mostrar página selecionada
        const targetPage = document.getElementById(`page-${page}`);
        if (targetPage) {
            targetPage.style.display = 'block';
        }

        // Carregar dados da página
        this.loadPageData(page);
    }

    // Carregar dados da página
    async loadPageData(page) {
        switch(page) {
            case 'doadores':
                await this.loadDoadores();
                break;
            case 'receptores':
                await this.loadReceptores();
                break;
            case 'doacoes':
                await this.loadDoacoes();
                break;
            case 'estoque':
                await this.loadEstoque();
                break;
            case 'rotas':
                await this.loadRotas();
                break;
        }
    }

    // Carregar estatísticas
    async loadStats() {
        try {
            // Simular dados de estatísticas
            const stats = {
                totalDoadores: 150,
                totalReceptores: 45,
                totalDoacoes: 320,
                totalItens: 1250
            };

            this.updateStatsDisplay(stats);
        } catch (error) {
            console.error('Erro ao carregar estatísticas:', error);
        }
    }

    // Atualizar display de estatísticas
    updateStatsDisplay(stats) {
        const statsContainer = document.querySelector('.stats-container');
        if (statsContainer) {
            statsContainer.innerHTML = `
                <div class="stat-item">
                    <h3>${stats.totalDoadores}</h3>
                    <p>Doadores</p>
                </div>
                <div class="stat-item">
                    <h3>${stats.totalReceptores}</h3>
                    <p>Receptores</p>
                </div>
                <div class="stat-item">
                    <h3>${stats.totalDoacoes}</h3>
                    <p>Doações</p>
                </div>
                <div class="stat-item">
                    <h3>${stats.totalItens}</h3>
                    <p>Itens Doados</p>
                </div>
            `;
        }
    }

    // Carregar doadores
    async loadDoadores() {
        const container = document.getElementById('doadores-list');
        if (!container) return;

        container.innerHTML = '<div class="loading"><div class="spinner"></div>Carregando doadores...</div>';

        try {
            const response = await fetch(`${this.apiUrl}/doadores`);
            const doadores = await response.json();
            
            this.renderDoadores(doadores);
        } catch (error) {
            container.innerHTML = '<div class="alert alert-error">Erro ao carregar doadores</div>';
        }
    }

    // Renderizar doadores
    renderDoadores(doadores) {
        const container = document.getElementById('doadores-list');
        if (!container) return;

        if (doadores.length === 0) {
            container.innerHTML = '<div class="alert alert-info">Nenhum doador encontrado</div>';
            return;
        }

        const html = `
            <table>
                <thead>
                    <tr>
                        <th>Nome</th>
                        <th>Email</th>
                        <th>Telefone</th>
                        <th>Endereço</th>
                        <th>Ações</th>
                    </tr>
                </thead>
                <tbody>
                    ${doadores.map(doador => `
                        <tr>
                            <td>${doador.nome}</td>
                            <td>${doador.email}</td>
                            <td>${doador.telefone}</td>
                            <td>${doador.endereco?.cidade || 'N/A'}</td>
                            <td>
                                <button onclick="app.editDoador('${doador.id}')" class="btn">Editar</button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;

        container.innerHTML = html;
    }

    // Carregar receptores
    async loadReceptores() {
        const container = document.getElementById('receptores-list');
        if (!container) return;

        container.innerHTML = '<div class="loading"><div class="spinner"></div>Carregando receptores...</div>';

        try {
            const response = await fetch(`${this.apiUrl}/receptores`);
            const receptores = await response.json();
            
            this.renderReceptores(receptores);
        } catch (error) {
            container.innerHTML = '<div class="alert alert-error">Erro ao carregar receptores</div>';
        }
    }

    // Renderizar receptores
    renderReceptores(receptores) {
        const container = document.getElementById('receptores-list');
        if (!container) return;

        if (receptores.length === 0) {
            container.innerHTML = '<div class="alert alert-info">Nenhum receptor encontrado</div>';
            return;
        }

        const html = `
            <table>
                <thead>
                    <tr>
                        <th>Nome</th>
                        <th>Email</th>
                        <th>Telefone</th>
                        <th>Endereço</th>
                        <th>Capacidade</th>
                        <th>Ações</th>
                    </tr>
                </thead>
                <tbody>
                    ${receptores.map(receptor => `
                        <tr>
                            <td>${receptor.nome}</td>
                            <td>${receptor.email}</td>
                            <td>${receptor.telefone}</td>
                            <td>${receptor.endereco?.cidade || 'N/A'}</td>
                            <td>${receptor.capacidade || 'N/A'}</td>
                            <td>
                                <button onclick="app.editReceptor('${receptor.id}')" class="btn">Editar</button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;

        container.innerHTML = html;
    }

    // Carregar doações
    async loadDoacoes() {
        const container = document.getElementById('doacoes-list');
        if (!container) return;

        container.innerHTML = '<div class="loading"><div class="spinner"></div>Carregando doações...</div>';

        try {
            const response = await fetch(`${this.apiUrl}/doacoes`);
            const doacoes = await response.json();
            
            this.renderDoacoes(doacoes);
        } catch (error) {
            container.innerHTML = '<div class="alert alert-error">Erro ao carregar doações</div>';
        }
    }

    // Renderizar doações
    renderDoacoes(doacoes) {
        const container = document.getElementById('doacoes-list');
        if (!container) return;

        if (doacoes.length === 0) {
            container.innerHTML = '<div class="alert alert-info">Nenhuma doação encontrada</div>';
            return;
        }

        const html = `
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Doador</th>
                        <th>Receptor</th>
                        <th>Itens</th>
                        <th>Status</th>
                        <th>Data</th>
                        <th>Ações</th>
                    </tr>
                </thead>
                <tbody>
                    ${doacoes.map(doacao => `
                        <tr>
                            <td>${doacao.id}</td>
                            <td>${doacao.doador_nome || 'N/A'}</td>
                            <td>${doacao.receptor_nome || 'N/A'}</td>
                            <td>${doacao.itens?.length || 0} itens</td>
                            <td><span class="status-badge status-${doacao.status}">${doacao.status}</span></td>
                            <td>${new Date(doacao.data_criacao).toLocaleDateString()}</td>
                            <td>
                                <button onclick="app.viewDoacao('${doacao.id}')" class="btn">Ver</button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;

        container.innerHTML = html;
    }

    // Carregar estoque
    async loadEstoque() {
        const container = document.getElementById('estoque-list');
        if (!container) return;

        container.innerHTML = '<div class="loading"><div class="spinner"></div>Carregando estoque...</div>';

        try {
            // Simular dados de estoque
            const estoque = [
                { id: 1, item: 'Arroz', quantidade: 50, unidade: 'kg', receptor: 'Casa do Bem' },
                { id: 2, item: 'Feijão', quantidade: 30, unidade: 'kg', receptor: 'Casa do Bem' },
                { id: 3, item: 'Macarrão', quantidade: 25, unidade: 'pacotes', receptor: 'Lar dos Idosos' },
                { id: 4, item: 'Óleo', quantidade: 15, unidade: 'litros', receptor: 'Casa do Bem' }
            ];
            
            this.renderEstoque(estoque);
        } catch (error) {
            container.innerHTML = '<div class="alert alert-error">Erro ao carregar estoque</div>';
        }
    }

    // Renderizar estoque
    renderEstoque(estoque) {
        const container = document.getElementById('estoque-list');
        if (!container) return;

        const html = `
            <table>
                <thead>
                    <tr>
                        <th>Item</th>
                        <th>Quantidade</th>
                        <th>Unidade</th>
                        <th>Receptor</th>
                        <th>Ações</th>
                    </tr>
                </thead>
                <tbody>
                    ${estoque.map(item => `
                        <tr>
                            <td>${item.item}</td>
                            <td>${item.quantidade}</td>
                            <td>${item.unidade}</td>
                            <td>${item.receptor}</td>
                            <td>
                                <button onclick="app.editEstoque('${item.id}')" class="btn">Editar</button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;

        container.innerHTML = html;
    }

    // Carregar rotas
    async loadRotas() {
        const container = document.getElementById('rotas-list');
        if (!container) return;

        container.innerHTML = '<div class="loading"><div class="spinner"></div>Carregando rotas...</div>';

        try {
            // Simular dados de rotas
            const rotas = [
                { id: 1, origem: 'Doador A', destino: 'Receptor B', distancia: '5.2 km', tempo: '15 min' },
                { id: 2, origem: 'Doador C', destino: 'Receptor D', distancia: '8.7 km', tempo: '25 min' }
            ];
            
            this.renderRotas(rotas);
        } catch (error) {
            container.innerHTML = '<div class="alert alert-error">Erro ao carregar rotas</div>';
        }
    }

    // Renderizar rotas
    renderRotas(rotas) {
        const container = document.getElementById('rotas-list');
        if (!container) return;

        const html = `
            <table>
                <thead>
                    <tr>
                        <th>Origem</th>
                        <th>Destino</th>
                        <th>Distância</th>
                        <th>Tempo</th>
                        <th>Ações</th>
                    </tr>
                </thead>
                <tbody>
                    ${rotas.map(rota => `
                        <tr>
                            <td>${rota.origem}</td>
                            <td>${rota.destino}</td>
                            <td>${rota.distancia}</td>
                            <td>${rota.tempo}</td>
                            <td>
                                <button onclick="app.viewRota('${rota.id}')" class="btn">Ver Rota</button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;

        container.innerHTML = html;
    }

    // Manipular envio de formulário
    handleFormSubmit(form) {
        const formData = new FormData(form);
        const data = Object.fromEntries(formData);
        
        console.log('Dados do formulário:', data);
        
        // Aqui você implementaria a lógica de envio para a API
        this.showAlert('Formulário enviado com sucesso!', 'success');
    }

    // Mostrar alerta
    showAlert(message, type = 'info') {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type}`;
        alert.textContent = message;
        
        document.body.insertBefore(alert, document.body.firstChild);
        
        setTimeout(() => {
            alert.remove();
        }, 5000);
    }

    // Métodos de edição (placeholders)
    editDoador(id) {
        this.showAlert(`Editando doador ${id}`, 'info');
    }

    editReceptor(id) {
        this.showAlert(`Editando receptor ${id}`, 'info');
    }

    editEstoque(id) {
        this.showAlert(`Editando item ${id}`, 'info');
    }

    viewDoacao(id) {
        this.showAlert(`Visualizando doação ${id}`, 'info');
    }

    viewRota(id) {
        this.showAlert(`Visualizando rota ${id}`, 'info');
    }
}

// Inicializar aplicação quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', () => {
    window.app = new RotaDoBemApp();
    const doarBtn = document.querySelector('.cta-button.primary');
    if (doarBtn) {
        doarBtn.addEventListener('click', function(e) {
            e.preventDefault();
            var form = document.getElementById('doacao-form');
            if (form) {
                form.scrollIntoView({behavior:'smooth'});
                setTimeout(function(){
                    var nome = form.querySelector('input[name="nome"]') || form.querySelector('input');
                    if (nome) {
                        nome.focus();
                        nome.style.boxShadow = '0 0 0 2px #E67E22';
                        setTimeout(()=>{nome.style.boxShadow = ''}, 2200);
                    }
                }, 900);
            }
        });
    }
});

// Leaflet MAP INTEGRATION
// Função para detectar localização real do usuário e mostrar marcador
function localizarUsuarioNoMapa(map) {
    if (!navigator.geolocation) {
        alert('Geolocalização não suportada no seu navegador!');
        return;
    }
    navigator.geolocation.getCurrentPosition(function(position) {
        var lat = position.coords.latitude;
        var lon = position.coords.longitude;
        map.setView([lat, lon], 14);
        L.marker([lat, lon], {icon: L.icon({
            iconUrl: 'https://cdn.iconscout.com/icon/free/png-256/location-1766-433787.png',
            iconSize: [32, 32],
            iconAnchor: [16, 32]
        })}).addTo(map).bindPopup('Você está aqui!').openPopup();
    }, function() {
        // Se negar, não faz nada
    });
}

if (document.getElementById('map')) {
    var map = L.map('map').setView([-14.2400732, -53.1805017], 4); // Centro Brasil
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);
    // Pins fixos de exemplo (cidade)
    L.marker([-23.55052, -46.633308]).addTo(map).bindPopup('São Paulo');
    L.marker([-22.906847, -43.172896]).addTo(map).bindPopup('Rio de Janeiro');
    L.marker([-19.916681, -43.934493]).addTo(map).bindPopup('Belo Horizonte');
    L.marker([-30.0346471, -51.2176584]).addTo(map).bindPopup('Porto Alegre');

    // Solicitar localização automática ao abrir a página
    localizarUsuarioNoMapa(map);

    // Botão localização explícito
    var btn = document.getElementById('btn-localizar-mapa');
    if (btn) {
      btn.onclick = function(){ localizarUsuarioNoMapa(map); };
    }
}
