class RotaDoBemApp {
    constructor() {
        this.apiUrl = 'http://localhost:5000/api';
        this.token = localStorage.getItem('rota_token');
        this.role = localStorage.getItem('rota_role');
        this.currentPage = 'dashboard';
        this.init();
    }

    init() {
        if (document.getElementById('login-form')) {
            this.initLoginPage();
        } else if (document.querySelector('.nav-list')) {
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

            // SALVA TOKEN + ROLE
            localStorage.setItem('rota_token', result.access_token);
            localStorage.setItem('rota_role', result.role);

            window.location.href = '/dashboard';
        } catch (error) {
            errorElement.textContent = error.message;
            errorElement.style.display = 'block';
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
        this.setupModal();

        this.loadPage('dashboard'); // Carrega a página inicial
    }

    setupModal() {
        const overlay = document.getElementById('modal-overlay');
        const closeBtn = document.getElementById('modal-close');
        const cancelBtn = document.querySelector('#modal-footer .btn-cancel');

        const closeModal = () => {
            overlay.style.display = 'none';
        };

        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) closeModal();
        });
        closeBtn.addEventListener('click', closeModal);
        cancelBtn.addEventListener('click', closeModal);
    }

    applyRolePermissions() {
        const permissions = {
            admin: ['dashboard', 'doacoes', 'doadores', 'receptores', 'estoque', 'rotas'],
            doador: ['dashboard', 'doacoes', 'estoque'],
            receptor: ['dashboard', 'doacoes', 'estoque'],
            motorista: ['dashboard', 'doacoes', 'rotas'],
            estoquista: ['dashboard', 'doacoes', 'estoque']
        };

        const allowed = permissions[this.role] || ['dashboard'];

        document.querySelectorAll('.nav-item a').forEach(link => {
            const page = link.getAttribute('data-page');
            if (!allowed.includes(page)) {
                link.parentElement.style.display = 'none';
            }
        });

        document.querySelectorAll('.page').forEach(page => {
            const id = page.id.replace('page-', '');
            if (!allowed.includes(id)) {
                page.style.display = 'none';
            }
        });
    }


    setupNavigation() {
        document.querySelectorAll('.nav-item a').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = link.getAttribute('data-page');
                this.loadPage(page);
            });
        });
    }

    loadPage(page) {
        const allowed = this.getAllowedPages();
        if (!allowed.includes(page)) {
            this.showAlert('Acesso negado a esta área.', 'error');
            return;
        }

        document.querySelectorAll('.page').forEach(p => p.style.display = 'none');
        const target = document.getElementById(`page-${page}`);
        if (target) target.style.display = 'block';

        this.currentPage = page;
        this.highlightActiveNav(page);

        this[`load${page.charAt(0).toUpperCase() + page.slice(1)}`]?.();
    }

    getAllowedPages() {
        const map = {
            admin: ['dashboard', 'doacoes', 'doadores', 'receptores', 'estoque', 'rotas'],
            doador: ['dashboard', 'doacoes', 'estoque'],
            receptor: ['dashboard', 'doacoes', 'estoque'],
            motorista: ['dashboard', 'doacoes', 'rotas'],
            estoquista: ['dashboard', 'doacoes', 'estoque']
        };
        return map[this.role] || ['dashboard'];
    }

    highlightActiveNav(page) {
        document.querySelectorAll('.nav-item a').forEach(link => {
            link.classList.toggle('active', link.getAttribute('data-page') === page);
        });
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

    async loadDashboard() {
        const container = document.querySelector('#page-dashboard .stats-container');
        container.innerHTML = '<div class="loading">Carregando estatísticas...</div>';
        try {
            const stats = await this.apiFetch(`${this.apiUrl}/stats`);
            container.innerHTML = `
                <div class="stat-item"><strong>${stats.doacoes}</strong> Doações</div>
                <div class="stat-item"><strong>${stats.motoristas}</strong> Motoristas</div>
                <div class="stat-item"><strong>${stats.rotas_pendentes}</strong> Rotas Pendentes</div>
            `;
        } catch (err) {
            container.innerHTML = `<div class="alert alert-error">${err.message}</div>`;
        }
    }

    async loadDoacoes() {
        const container = document.getElementById('doacoes-list');
        container.innerHTML = '<div class="loading">Carregando doações...</div>';
        try {
            const doacoes = await this.apiFetch(`${this.apiUrl}/doacoes`);
            this.renderDoacoes(doacoes, container);
        } catch (err) {
            container.innerHTML = `<div class="alert alert-error">${err.message}</div>`;
        }
    }

    async loadRotas() {
        const container = document.getElementById('rotas-list');
        container.innerHTML = '<div class="loading">Carregando rotas...</div>';
        try {
            const rotas = await this.apiFetch(`${this.apiUrl}/rotas?status=pendente`);
            this.renderRotas(rotas, container);
        } catch (err) {
            container.innerHTML = `<div class="alert alert-error">${err.message}</div>`;
        }
    }

    renderDoacoes(doacoes, container) {
        if (!doacoes || doacoes.length === 0) {
            container.innerHTML = '<div class="alert alert-info">Nenhuma doação encontrada</div>';
            return;
        }

        container.innerHTML = doacoes.map(doacao => `
            <div class="donation-card">
                <div class="donation-card-header">
                    <h4>${doacao.alimento}</h4>
                </div>
                <div class="donation-card-body">
                    <div class="info-item">
                        <i class="fas fa-box"></i>
                        <span>${doacao.quantidade} ${doacao.unidade}</span>
                    </div>
                    <div class="info-item">
                        <i class="fas fa-calendar-times"></i>
                        <span>Validade: ${new Date(doacao.validade).toLocaleDateString()}</span>
                    </div>
                    <div class="info-item">
                        <i class="fas fa-info-circle"></i>
                        <span>Status: <span class="status-badge status-${doacao.status}">${doacao.status}</span></span>
                    </div>
                </div>
                <div class="donation-card-footer">
                    <!-- Chama a nova função showDonationDetails -->
                    <button class="btn-details" onclick="app.showDonationDetails('${doacao._id}')">
                        Ver Detalhes
                    </button>
                </div>
            </div>
        `).join('');
    }

    async showDonationDetails(doacaoId) {
        const modalOverlay = document.getElementById('modal-overlay');
        const modalBody = document.getElementById('modal-body');
        const modalFooter = document.getElementById('modal-footer');

        modalBody.innerHTML = '<div class="loading">Carregando...</div>';
        modalOverlay.style.display = 'flex';

        try {
            // Busca os detalhes da doação específica
            const doacao = await this.apiFetch(`${this.apiUrl}/doacoes/${doacaoId}`);

            modalBody.innerHTML = `
                <p><strong>Alimento:</strong> ${doacao.alimento}</p>
                <p><strong>Quantidade:</strong> ${doacao.quantidade} ${doacao.unidade}</p>
                <p><strong>Validade:</strong> ${new Date(doacao.validade).toLocaleDateString()}</p>
                <p><strong>Status:</strong> ${doacao.status}</p>
                <p><strong>ID Doador:</strong> ${doacao.doador_id} (Precisamos buscar o nome)</p>
            `;

            // Lógica do botão "Aceitar"
            if (this.role === 'receptor' && doacao.status === 'pendente') {
                modalFooter.style.display = 'flex';
                const acceptBtn = modalFooter.querySelector('.btn-accept');
                acceptBtn.replaceWith(acceptBtn.cloneNode(true));
                modalFooter.querySelector('.btn-accept').addEventListener('click', () => {
                    this.acceptDonation(doacaoId);
                });
            } else {
                modalFooter.style.display = 'none'; // Esconde botões se não puder aceitar
            }

        } catch (err) {
            modalBody.innerHTML = `<div class="alert alert-error">${err.message}</div>`;
        }
    }

    async acceptDonation(doacaoId) {
        try {
            // Atualiza o status da doação para 'aceita'
            await this.apiFetch(`${this.apiUrl}/doacoes/${doacaoId}`, {
                method: 'PUT',
                body: JSON.stringify({ status: 'aceita' })
            });

            document.getElementById('modal-overlay').style.display = 'none';
            this.showAlert('Doação aceita com sucesso!', 'success');
            this.loadPage('doacoes');

        } catch (err) {
            this.showAlert(`Erro ao aceitar doação: ${err.message}`, 'error');
        }
    }

    renderRotas(rotas, container) {
        if (rotas.length === 0) {
            container.innerHTML = '<div class="alert alert-info">Nenhuma rota pendente</div>';
            return;
        }
        container.innerHTML = `
            <table>
                <thead><tr><th>Resumo</th><th>Distância</th><th>Duração</th><th>Status</th></tr></thead>
                <tbody>
                    ${rotas.map(r => `
                        <tr>
                            <td>${r.resumo_rota}</td>
                            <td>${r.distancia_texto}</td>
                            <td>${r.duracao_texto}</td>
                            <td><span class="status-badge status-${r.status}">${r.status}</span></td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>`;
    }

    async apiFetch(url, options = {}) {
        const headers = {
            ...options.headers,
            'Authorization': `Bearer ${this.token}`,
            'Content-Type': 'application/json',
        };

        const response = await fetch(url, { ...options, headers });

        if (response.status === 401 || response.status === 403) {
            localStorage.removeItem('rota_token');
            localStorage.removeItem('rota_role');
            window.location.href = '/login';
            throw new Error('Sessão expirada');
        }

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.erro || 'Erro na requisição');
        }

        return response.json();
    }

    showAlert(msg, type = 'info') {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type}`;
        alert.textContent = msg;
        document.querySelector('main').prepend(alert);
        setTimeout(() => alert.remove(), 4000);
    }
}

// Inicializa
document.addEventListener('DOMContentLoaded', () => {
    window.app = new RotaDoBemApp();
});