// Global state
let currentEmployees = [];

// Sample data presets to help users practice
const samplePresets = {
    1: {
        name: "David Kim",
        email: "david.k@company.com",
        role: "Kubernetes Specialist",
        department: "DevOps & Cloud",
        salary: 98000,
        status: "Active"
    },
    2: {
        name: "Aisha Patel",
        email: "aisha.p@company.com",
        role: "Security & Compliance Engineer",
        department: "Security",
        salary: 105000,
        status: "Active"
    },
    3: {
        name: "Carlos Gomez",
        email: "carlos.g@company.com",
        role: "QA Automation Engineer",
        department: "QA & Testing",
        salary: 82000,
        status: "Active"
    }
};

// DOM Elements
const employeesTableBody = document.getElementById('employeesTableBody');
const searchInput = document.getElementById('searchInput');
const departmentFilter = document.getElementById('departmentFilter');
const btnRefresh = document.getElementById('btnRefresh');
const btnOpenAddModal = document.getElementById('btnOpenAddModal');
const btnDownloadDump = document.getElementById('btnDownloadDump');

const statTotal = document.getElementById('statTotal') || document.getElementById('stat-total');
const statActive = document.getElementById('statActive') || document.getElementById('stat-active');
const statDepartments = document.getElementById('statDepartments') || document.getElementById('stat-departments');
const dbStatusText = document.getElementById('db-status-text');

// Modal Elements
const employeeModal = document.getElementById('employeeModal');
const employeeForm = document.getElementById('employeeForm');
const modalTitle = document.getElementById('modalTitle');
const btnCloseModal = document.getElementById('btnCloseModal');
const btnCancelModal = document.getElementById('btnCancelModal');

const employeeIdInput = document.getElementById('employeeId');
const formName = document.getElementById('formName');
const formEmail = document.getElementById('formEmail');
const formRole = document.getElementById('formRole');
const formDepartment = document.getElementById('formDepartment');
const formSalary = document.getElementById('formSalary');
const formStatus = document.getElementById('formStatus');

// Toast Element
const toast = document.getElementById('toast');

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    loadEmployees();
    loadDbStats();

    // Event listeners
    searchInput.addEventListener('input', debounce(loadEmployees, 300));
    departmentFilter.addEventListener('change', loadEmployees);
    btnRefresh.addEventListener('click', () => {
        loadEmployees();
        loadDbStats();
        showToast('Refreshed data from PostgreSQL', 'success');
    });

    btnOpenAddModal.addEventListener('click', openAddModal);
    btnCloseModal.addEventListener('click', closeModal);
    btnCancelModal.addEventListener('click', closeModal);
    employeeForm.addEventListener('submit', handleFormSubmit);

    btnDownloadDump.addEventListener('click', downloadDumpFile);
});

// Toast notification helper
function showToast(message, type = 'success') {
    toast.textContent = message;
    toast.className = `toast ${type}`;
    setTimeout(() => {
        toast.className = 'toast';
    }, 3500);
}

// Fetch database stats
async function loadDbStats() {
    try {
        const res = await fetch('/api/stats');
        if (res.ok) {
            const data = await res.json();
            if (dbStatusText) {
                dbStatusText.textContent = `Connected: ${data.database} (${data.host}:${data.port})`;
            }
        }
    } catch (err) {
        if (dbStatusText) {
            dbStatusText.textContent = 'Disconnected';
            dbStatusText.style.color = '#ef4444';
        }
    }
}

// Fetch employees with search & filter
async function loadEmployees() {
    const search = searchInput.value.trim();
    const dept = departmentFilter.value;

    let url = '/api/employees?';
    if (search) url += `search=${encodeURIComponent(search)}&`;
    if (dept) url += `department=${encodeURIComponent(dept)}&`;

    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error('Failed to fetch records');
        
        currentEmployees = await response.json();
        renderTable(currentEmployees);
        updateStats(currentEmployees);
    } catch (error) {
        console.error(error);
        employeesTableBody.innerHTML = `<tr><td colspan="8" class="text-center" style="color: #ef4444;">Error loading data: ${error.message}</td></tr>`;
    }
}

// Render records into table
function renderTable(employees) {
    if (!employees || employees.length === 0) {
        employeesTableBody.innerHTML = `<tr><td colspan="8" class="text-center loading-cell">No employee records found. Click "+ Add Employee" or use quick sample presets!</td></tr>`;
        return;
    }

    employeesTableBody.innerHTML = employees.map(emp => {
        const formattedDate = emp.created_at ? new Date(emp.created_at).toLocaleDateString() : 'N/A';
        const formattedSalary = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(emp.salary);
        
        const statusClass = {
            'Active': 'badge-active',
            'Remote': 'badge-remote',
            'On Leave': 'badge-leave',
            'Inactive': 'badge-inactive'
        }[emp.status] || 'badge-active';

        return `
            <tr>
                <td><strong>#${emp.id}</strong></td>
                <td>
                    <div class="emp-name">${escapeHtml(emp.name)}</div>
                    <div class="emp-email">${escapeHtml(emp.email)}</div>
                </td>
                <td>${escapeHtml(emp.role)}</td>
                <td>${escapeHtml(emp.department)}</td>
                <td><strong>${formattedSalary}</strong></td>
                <td><span class="badge ${statusClass}">${escapeHtml(emp.status)}</span></td>
                <td>${formattedDate}</td>
                <td class="text-right">
                    <div class="actions-cell">
                        <button class="btn btn-sm btn-secondary-outline" onclick="openEditModal(${emp.id})">Edit</button>
                        <button class="btn btn-sm btn-danger-outline" onclick="deleteEmployee(${emp.id}, '${escapeHtml(emp.name)}')">Delete</button>
                    </div>
                </td>
            </tr>
        `;
    }).join('');
}

// Update top statistics
function updateStats(employees) {
    if (statTotal) statTotal.textContent = employees.length;
    
    const activeCount = employees.filter(e => e.status === 'Active' || e.status === 'Remote').length;
    if (statActive) statActive.textContent = activeCount;

    const uniqueDepts = new Set(employees.map(e => e.department)).size;
    if (statDepartments) statDepartments.textContent = uniqueDepts;
}

// Modal handling
function openAddModal() {
    modalTitle.textContent = "Add New Employee";
    employeeIdInput.value = "";
    employeeForm.reset();
    formStatus.value = "Active";
    employeeModal.classList.add('active');
}

function openEditModal(id) {
    const emp = currentEmployees.find(e => e.id === id);
    if (!emp) return;

    modalTitle.textContent = `Edit Employee #${emp.id}`;
    employeeIdInput.value = emp.id;
    formName.value = emp.name;
    formEmail.value = emp.email;
    formRole.value = emp.role;
    formDepartment.value = emp.department;
    formSalary.value = emp.salary;
    formStatus.value = emp.status;

    employeeModal.classList.add('active');
}

function closeModal() {
    employeeModal.classList.remove('active');
}

// Form submission (Create or Update)
async function handleFormSubmit(e) {
    e.preventDefault();
    const id = employeeIdInput.value;
    const isEdit = Boolean(id);

    const payload = {
        name: formName.value.trim(),
        email: formEmail.value.trim(),
        role: formRole.value.trim(),
        department: formDepartment.value,
        salary: parseFloat(formSalary.value),
        status: formStatus.value
    };

    const url = isEdit ? `/api/employees/${id}` : '/api/employees';
    const method = isEdit ? 'PUT' : 'POST';

    try {
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || 'Failed to save record');
        }

        closeModal();
        showToast(isEdit ? 'Employee updated successfully!' : 'Employee added to PostgreSQL database!', 'success');
        loadEmployees();
        loadDbStats();
    } catch (err) {
        alert(`Error: ${err.message}`);
    }
}

// Delete Employee
async function deleteEmployee(id, name) {
    if (!confirm(`Are you sure you want to delete "${name}" from PostgreSQL?`)) return;

    try {
        const response = await fetch(`/api/employees/${id}`, { method: 'DELETE' });
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.detail || 'Delete failed');
        }

        showToast(`Employee #${id} deleted from database`, 'success');
        loadEmployees();
        loadDbStats();
    } catch (err) {
        alert(`Error: ${err.message}`);
    }
}

// Quick Sample Preset Helper
function fillAndOpenSample(presetId) {
    const data = samplePresets[presetId];
    if (!data) return;

    openAddModal();
    formName.value = data.name;
    formEmail.value = data.email;
    formRole.value = data.role;
    formDepartment.value = data.department;
    formSalary.value = data.salary;
    formStatus.value = data.status;
}

// Download Database SQL Dump directly
function downloadDumpFile() {
    window.location.href = '/api/backup/download';
    showToast('Generating and downloading devops_db_dump.sql...', 'success');
}

// Copy helper
function copySnippet(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Command copied to clipboard!', 'success');
    }).catch(() => {
        prompt('Copy this command:', text);
    });
}

// Utility: Debounce for fast searching
function debounce(func, delay) {
    let timeout;
    return (...args) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), delay);
    };
}

// Utility: Escape HTML
function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}
