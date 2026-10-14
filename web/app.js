const userSelect = document.querySelector('#user');
const identity = document.querySelector('#identity');
const form = document.querySelector('#ask-form');
const question = document.querySelector('#question');
const messages = document.querySelector('#messages');
let users = [];
let documents = [];
const staticMode = location.hostname.endsWith('github.io');

function normalize(value) {
  return String(value).toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9]+/g, ' ').trim();
}

function isAuthorized(user, doc) {
  if (!doc.access.roles.includes(user.role)) return false;
  if (doc.scope.level === 'group') return true;
  if (doc.scope.company !== user.company) return false;
  return doc.scope.level === 'company' || doc.scope.department === user.department;
}

function isActive(doc) {
  const today = new Date().toISOString().slice(0, 10);
  return doc.effective_from <= today && (!doc.effective_to || today <= doc.effective_to);
}

function citation(doc) {
  return {document_id: doc.id, title: doc.title, version: doc.version, effective_from: doc.effective_from, owner: doc.owner};
}

function versionKey(version) {
  return version.split('.').map(Number);
}

function compareVersion(left, right) {
  const a = versionKey(left);
  const b = versionKey(right);
  for (let i = 0; i < Math.max(a.length, b.length); i += 1) {
    if ((a[i] || 0) !== (b[i] || 0)) return (a[i] || 0) - (b[i] || 0);
  }
  return 0;
}

function askStatic(userId, text) {
  const user = users.find(item => item.id === userId);
  if (!user) return {status: 'refused', answer: 'Không xác định được danh tính người hỏi.', citations: [], trace: {reason: 'UNKNOWN_USER'}};
  const active = documents.filter(doc => isAuthorized(user, doc) && isActive(doc));
  const score = doc => doc.keywords.filter(keyword => normalize(text).includes(normalize(keyword))).length;
  let candidates = active.filter(doc => score(doc) > 0);
  const trace = {
    user_context: {company: user.company, department: user.department, role: user.role},
    authorized_active_documents_considered: active.length,
    matched_documents: candidates.length,
    policy: 'authorization -> validity -> relevance -> specificity -> version'
  };
  if (!candidates.length) return {status: 'refused', answer: 'Không tìm thấy tài liệu được phép truy cập và còn hiệu lực để trả lời câu hỏi này.', citations: [], trace: {...trace, reason: 'INSUFFICIENT_EVIDENCE'}};
  candidates.sort((a, b) => score(b) - score(a));
  const topIntent = candidates[0].intent;
  candidates = candidates.filter(doc => doc.intent === topIntent);
  const specificity = doc => ({group: 1, company: 2, department: 3})[doc.scope.level];
  const maxSpecificity = Math.max(...candidates.map(specificity));
  candidates = candidates.filter(doc => specificity(doc) === maxSpecificity);
  candidates.sort((a, b) => compareVersion(b.version, a.version));
  const newest = candidates[0].version;
  const winners = candidates.filter(doc => compareVersion(doc.version, newest) === 0);
  if (new Set(winners.map(doc => doc.content)).size > 1) {
    return {
      status: 'refused',
      answer: 'Có nhiều tài liệu cùng mức ưu tiên nhưng nội dung mâu thuẫn. Hệ thống từ chối kết luận; vui lòng liên hệ chủ sở hữu chính sách.',
      citations: winners.map(citation),
      trace: {...trace, resolution: 'conflict_detected', reason: 'CONFLICTING_EVIDENCE'}
    };
  }
  const chosen = winners[0];
  return {status: 'answered', answer: chosen.content, citations: [citation(chosen)], trace: {...trace, resolution: 'answered', selected_scope: chosen.scope.level, selected_version: chosen.version}};
}

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
  if (staticMode) {
    [users, documents] = await Promise.all([
      fetch('data/users.json').then(response => response.json()),
      fetch('data/documents.json').then(response => response.json())
    ]);
  } else {
    const response = await fetch('/api/users');
    const payload = await response.json();
    users = payload.users;
  }
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
    const result = staticMode
      ? askStatic(userSelect.value, text)
      : await fetch('/api/ask', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({user_id: userSelect.value, question: text})
        }).then(response => response.json());
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
