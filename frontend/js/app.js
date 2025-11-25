class RotaDoBemApp {
    constructor() {
        this.apiUrl = 'http://localhost:5000/api';
        this.token = localStorage.getItem('rota_token');
        this.role = localStorage.getItem('rota_role');
        this.currentPage = 'doacoes'; 
        this.init();
    }

    init() {
        if (document.getElementById('login-form')) {
            this.initLoginPage();
        } else if (document.querySelector('.sidebar')) {
            this.initDashboardPage();
        }
    }

    initLoginPage() {
        const form = document.getElementById('login-form');
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleLogin(e.target);
            });
        }
    }

    async handleLogin(form) {
        const formData = new FormData(form);
        const data = Object.fromEntries(formData);
        const errorElement = document.getElementById('login-error');

        try {
            const response = await fetch(`${this.apiUrl}/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });

            const result = await response.json();

            if (!response.ok) throw new Error(result.erro || 'Erro no login');

            localStorage.setItem('rota_token', result.access_token);
            localStorage.setItem('rota_role', result.role);

            window.location.href = '/dashboard';
        } catch (error) {
            if (errorElement) {
                errorElement.textContent = error.message;
                errorElement.style.display = 'block';
            } else {
                alert(error.message);
            }
        }
    }

    initDashboardPage() {
        if (!this.token) {
            window.location.href = '/login';
            return;
        }

        this.applyRolePermissions();
        this.setupNavigation();
        this.setupLogout();
        this.loadPage(this.currentPage);

        if (this.role === 'doador') {
            const btnNova = document.getElementById('btn-nova-doacao');
            if (btnNova) {
                btnNova.style.display = 'flex';
                btnNova.onclick = () => document.getElementById('modal-nova-doacao').style.display = 'flex';
            }
            const formNova = document.getElementById('form-nova-doacao');
            if (formNova) formNova.addEventListener('submit', (e) => this.handleNovaDoacao(e));
        }
    }

    applyRolePermissions() {
        const permissions = {
            admin: ['doacoes', 'doadores', 'receptores', 'estoque', 'rotas'],
            doador: ['doacoes', 'historico'], // Alterado: Doador vê suas doações ativas e seu histórico
            receptor: ['doacoes', 'finalizadas'], // Alterado: Receptor vê doações para aceitar e recebidas
            motorista: ['doacoes', 'rotas']
        };

        const allowed = permissions[this.role] || ['doacoes'];

        document.querySelectorAll('.nav-link').forEach(link => {
            const page = link.getAttribute('data-page');
            if (page && !allowed.includes(page)) {
                link.parentElement.style.display = 'none';
            }
        });

        document.querySelectorAll('.page-section').forEach(section => {
            const id = section.id.replace('page-', '');
            // Mantém a página atual (doacoes) sempre no DOM para não quebrar o inicio
            if (!allowed.includes(id) && id !== 'doacoes') {
                section.remove();
            }
        });
    }

    setupNavigation() {
        document.querySelectorAll('.nav-link[data-page]').forEach(link => {
            link.addEventListener('click', () => {
                const page = link.getAttribute('data-page');
                this.loadPage(page);
            });
        });
    }

    loadPage(page) {
        console.log("Carregando:", page);
        if (page === 'doacoes') this.loadDoacoes();
        if (page === 'rotas') this.loadRotas();
        if (page === 'finalizadas') this.loadFinalizadas();
        if (page === 'historico') this.loadHistorico();
    }

    setupLogout() {
        const logoutBtn = document.getElementById('logout-btn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', (e) => {
                e.preventDefault();
                localStorage.removeItem('rota_token');
                localStorage.removeItem('rota_role');
                window.location.href = '/login';
            });
        }
    }

    // --- FUNÇÕES DE CARREGAMENTO ---

    async loadDoacoes() {
        const container = document.getElementById('doacoes-list');
        if(!container) return;
        container.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: #999;">Buscando doações...</p>';
        
        try {
            // Se for receptor, vê pendentes. Doador vê as suas ativas.
            let query = '';
            if (this.role === 'receptor') query = '?status=pendente';

            const doacoes = await this.apiFetch(`${this.apiUrl}/doacoes${query}`);
            this.renderDoacoes(doacoes, container);
        } catch (err) {
            container.innerHTML = `<div style="color: red; text-align: center; grid-column: 1/-1;">Erro: ${err.message}</div>`;
        }
    }

    async loadHistorico() {
        const container = document.getElementById('historico-list');
        if(!container) return;
        container.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: #999;">Buscando histórico...</p>';
        
        try {
            const doacoes = await this.apiFetch(`${this.apiUrl}/doacoes?status=finalizadas`);
            
            if (!doacoes || doacoes.length === 0) {
                container.innerHTML = '<p style="grid-column: 1/-1; text-align: center;">Nenhuma doação finalizada ainda.</p>';
                return;
            }

            container.innerHTML = doacoes.map(d => this.createCardHTML(d)).join('');
        } catch (err) {
            container.innerHTML = `<div style="color: red;">Erro: ${err.message}</div>`;
        }
    }

    async loadFinalizadas() {
        const container = document.getElementById('finalizadas-list');
        if(!container) return;
        container.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: #999;">Buscando recebidos...</p>';
        
        try {
            const doacoes = await this.apiFetch(`${this.apiUrl}/doacoes?status=finalizadas`);
            
            if (!doacoes || doacoes.length === 0) {
                container.innerHTML = '<p style="grid-column: 1/-1; text-align: center;">Nenhum recebimento registrado.</p>';
                return;
            }

            container.innerHTML = doacoes.map(d => this.createCardHTML(d)).join('');
        } catch (err) {
            container.innerHTML = `<div style="color: red;">Erro: ${err.message}</div>`;
        }
    }

    // Helper para renderizar cards
    createCardHTML(d) {
        const dataValidade = new Date(d.validade).toLocaleDateString('pt-BR');
        let statusClass = 'status-pendente';
        if (d.status === 'aceita') statusClass = 'status-aceita';
        if (d.status === 'concluida' || d.status === 'recebida') statusClass = 'status-concluida';

        const id = d._id || d.id;

        return `
        <div class="donation-card">
            <div class="card-header">
                <h4>${d.alimento}</h4>
                <span class="status-badge ${statusClass}">${d.status}</span>
            </div>
            <div class="card-body">
                <div class="info-item"><i class="fas fa-weight-hanging"></i> <span>${d.quantidade} ${d.unidade}</span></div>
                <div class="info-item"><i class="fas fa-calendar-alt"></i> <span>Validade: ${dataValidade}</span></div>
            </div>
            <div class="card-footer">
                <button class="btn-outline" onclick="app.showDonationDetails('${id}')">Ver Detalhes</button>
            </div>
        </div>`;
    }

    renderDoacoes(doacoes, container) {
        if (!doacoes || doacoes.length === 0) {
            container.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: #999;">Nenhuma doação encontrada.</p>';
            return;
        }
        container.innerHTML = doacoes.map(d => this.createCardHTML(d)).join('');
    }

    // --- MODAL E AÇÕES ---

    // --- AÇÕES DO MOTORISTA (Função Atualizada) ---

    async showDonationDetails(id) {
        const modal = document.getElementById('modal-overlay');
        const body = document.getElementById('modal-body');
        const btn = document.getElementById('btn-acao-principal'); // Usando o ID correto do HTML
        
        // Reseta estado do modal
        body.innerHTML = '<div style="text-align:center; padding:20px;"><i class="fas fa-spinner fa-spin"></i> Carregando detalhes...</div>';
        modal.style.display = 'flex';
        
        // Garante que os botões de fechar funcionam
        const closeModal = () => { modal.style.display = 'none'; };
        document.getElementById('btn-cancelar-detalhe').onclick = closeModal;
        document.getElementById('modal-close').onclick = closeModal;

        try {
            // 1. Busca dados da doação
            const d = await this.apiFetch(`${this.apiUrl}/doacoes/${id}`);
            
            let rotaInfo = '';
            let rotaId = null;
            
            // 2. Se for Motorista E a doação estiver pronta, busca/calcula a rota
            if (this.role === 'motorista' && (d.status === 'aceita' || d.status === 'a caminho')) {
                try {
                    // Chama o endpoint que calcula (ou pega do cache) a rota
                    const rota = await this.apiFetch(`${this.apiUrl}/rotas/calcular/${id}`);
                    
                    if (rota && rota.distancia_texto) {
                        rotaId = rota._id || rota.id;
                        rotaInfo = `
                            <div style="background: #f0fdf4; padding: 15px; border-radius: 8px; margin: 15px 0; border: 1px solid #bbf7d0;">
                                <h4 style="margin:0 0 10px 0; color: var(--success); display:flex; align-items:center; gap:8px;">
                                    <i class="fas fa-map-marked-alt"></i> Dados da Rota
                                </h4>
                                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                                    <div>
                                        <small style="color: #666;">Distância Total</small>
                                        <div style="font-weight: bold; font-size: 1.1rem;">${rota.distancia_texto}</div>
                                    </div>
                                    <div>
                                        <small style="color: #666;">Tempo Estimado</small>
                                        <div style="font-weight: bold; font-size: 1.1rem;">${rota.duracao_texto}</div>
                                    </div>
                                </div>
                                <div style="margin-top: 10px; padding-top: 10px; border-top: 1px dashed #bbf7d0;">
                                    <small style="color: #666;">Resumo:</small>
                                    <div>${rota.resumo_rota}</div>
                                    <a href="${rota.google_maps_link}" target="_blank" style="display:inline-block; margin-top:5px; color: var(--primary); font-weight:600; text-decoration:none;">
                                        <i class="fas fa-external-link-alt"></i> Abrir no Google Maps
                                    </a>
                                </div>
                            </div>
                        `;
                    }
                } catch (rotaErr) {
                    console.error("Erro ao calcular rota:", rotaErr);
                    rotaInfo = `<div style="color: orange; margin: 10px 0;">Não foi possível calcular a rota no momento.</div>`;
                }
            }

            // 3. Monta o HTML do corpo do modal
            const dataFormatada = new Date(d.validade).toLocaleDateString('pt-BR');
            
            body.innerHTML = `
                <h2 style="color: var(--primary); margin-bottom: 0.5rem;">${d.alimento}</h2>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px;">
                    <div style="background: #f8fafc; padding: 10px; border-radius: 6px;">
                        <small style="color:gray">Quantidade</small><br>
                        <strong>${d.quantidade} ${d.unidade}</strong>
                    </div>
                    <div style="background: #f8fafc; padding: 10px; border-radius: 6px;">
                        <small style="color:gray">Validade</small><br>
                        <strong>${dataFormatada}</strong>
                    </div>
                </div>
                
                <div style="margin-bottom: 10px;">
                    <small style="color:gray">Status Atual</small><br>
                    <span class="status-badge status-${d.status.replace(' ', '')}">${d.status.toUpperCase()}</span>
                </div>

                ${rotaInfo}
            `;

            // 4. Configura o Botão de Ação (Clona para remover eventos antigos)
            const newBtn = btn.cloneNode(true);
            btn.parentNode.replaceChild(newBtn, btn);

            // Lógica de qual botão mostrar
            if (this.role === 'motorista' && d.status === 'aceita') {
                newBtn.textContent = 'Aceitar Corrida';
                newBtn.style.display = 'block';
                newBtn.className = 'btn-primary'; // Garante a cor laranja
                // Se a rota falhou, ainda permite aceitar mas sem ID da rota (backend trata ou falha)
                newBtn.onclick = () => {
                    if(rotaId) this.acceptDelivery(rotaId);
                    else alert("Erro: Rota não calculada. Tente fechar e abrir novamente.");
                };
            } 
            else if (this.role === 'motorista' && d.status === 'a caminho') {
                newBtn.textContent = 'Finalizar Entrega';
                newBtn.style.display = 'block';
                newBtn.style.backgroundColor = 'var(--success)'; // Verde
                newBtn.onclick = () => {
                    if(rotaId) this.finishDelivery(rotaId);
                    else alert("Erro: ID da rota perdido.");
                };
            } 
            else if (this.role === 'receptor' && d.status === 'pendente') {
                newBtn.textContent = 'Aceitar Doação';
                newBtn.style.display = 'block';
                newBtn.className = 'btn-primary';
                newBtn.onclick = () => this.acceptDonation(id);
            } 
            else {
                newBtn.style.display = 'none'; // Esconde se não tiver ação
            }

        } catch (err) { 
            console.error(err);
            body.innerHTML = `<div class="alert alert-error">Erro ao carregar: ${err.message}</div>`; 
        }
    }

    async acceptDonation(id) {
        if (!confirm("Aceitar esta doação?")) return;
        try {
            await this.apiFetch(`${this.apiUrl}/doacoes/${id}/aceitar`, { method: 'PUT' });
            alert('Sucesso! Doação aceita.');
            this.loadDoacoes();
        } catch (err) {
            alert(`Erro: ${err.message}`);
        }
    }

    closeNovaDoacaoModal() { document.getElementById('modal-nova-doacao').style.display = 'none'; }

    async handleNovaDoacao(e) {
        e.preventDefault();
        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData);
        data.quantidade = parseFloat(data.quantidade);

        try {
            await this.apiFetch(`${this.apiUrl}/doacoes`, { method: 'POST', body: JSON.stringify(data) });
            this.closeNovaDoacaoModal();
            alert('Publicado!');
            e.target.reset();
            this.loadDoacoes();
        } catch (err) {
            alert('Erro: ' + err.message);
        }
    }

    async loadRotas() {
        const container = document.getElementById('rotas-list');
        if(!container) return;
        container.innerHTML = '<p>Carregando...</p>';
        try {
            const rotas = await this.apiFetch(`${this.apiUrl}/rotas`);
            if(!rotas || rotas.length === 0) {
                container.innerHTML = '<p style="color: #777;">Nenhuma rota.</p>';
                return;
            }
            container.innerHTML = rotas.map(r => `<div>Rota ID: ${r._id || r.id} - Status: ${r.status}</div>`).join('');
        } catch (err) {
            container.innerHTML = `<p style="color: red">${err.message}</p>`;
        }
    }

    async apiFetch(url, options = {}) {
        const headers = { ...options.headers, 'Authorization': `Bearer ${this.token}`, 'Content-Type': 'application/json' };
        const response = await fetch(url, { ...options, headers });
        if (response.status === 401 || response.status === 403) {
            localStorage.removeItem('rota_token');
            localStorage.removeItem('rota_role');
            window.location.href = '/login';
            throw new Error('Sessão expirada');
        }
        const data = await response.json();
        if (!response.ok) throw new Error(data.erro || data.error || 'Erro');
        return data;
    }
}

document.addEventListener('DOMContentLoaded', () => { window.app = new RotaDoBemApp(); });