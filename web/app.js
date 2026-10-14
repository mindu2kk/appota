const userSelect = document.querySelector('#user');
const identity = document.querySelector('#identity');
const form = document.querySelector('#ask-form');
const question = document.querySelector('#question');
const messages = document.querySelector('#messages');
let users = [];

function escapeHtml(value) {
  return String(value).replace(/[&<>'"]/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[char]));
}

function renderIdentity() {
  const user = users.find(item => item.id === userSelect.value);
  identity.textContent = user ? `${user.company} · ${user.department} · ${user.role}` : '';
}

function addMessage(kind, html) {
  const node = document.createElement('div');
  node.className = `message ${kind}`;
  node.innerHTML = html;
  messages.appendChild(node);
  messages.scrollTop = messages.scrollHeight;
}

async function loadUsers() {
  const response = await fetch('/api/users');
  const payload = await response.json();
  users = payload.users;
  userSelect.innerHTML = users.map(user => `<option value="${escapeHtml(user.id)}">${escapeHtml(user.name)}</option>`).join('');
  renderIdentity();
}

form.addEventListener('submit', async event => {
  event.preventDefault();
  const text = question.value.trim();
  if (!text) return;
  addMessage('user', escapeHtml(text));
  question.value = '';
  const button = form.querySelector('button');
  button.disabled = true;
  try {
    const response = await fetch('/api/ask', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({user_id: userSelect.value, question: text})
    });
    const result = await response.json();
    const sources = (result.citations || []).map(source =>
      `<div class="source"><strong>Nguồn:</strong> ${escapeHtml(source.title)} · v${escapeHtml(source.version)} · hiệu lực ${escapeHtml(source.effective_from)} · ${escapeHtml(source.owner)}</div>`
    ).join('');
    const trace = result.trace || {};
    const traceHtml = `<div class="trace">Đã xét ${trace.authorized_active_documents_considered ?? 0} tài liệu hợp lệ · Kết quả: ${escapeHtml(trace.reason || trace.resolution || result.status)}</div>`;
    addMessage(result.status === 'answered' ? 'answer' : 'refused', `${escapeHtml(result.answer)}${sources}${traceHtml}`);
  } catch (error) {
    addMessage('refused', 'Không thể kết nối tới dịch vụ. Vui lòng thử lại.');
  } finally {
    button.disabled = false;
    question.focus();
  }
});

userSelect.addEventListener('change', renderIdentity);
document.querySelectorAll('[data-question]').forEach(button => button.addEventListener('click', () => {
  question.value = button.dataset.question;
  question.focus();
}));

loadUsers().catch(() => addMessage('refused', 'Không tải được danh sách người dùng demo.'));
