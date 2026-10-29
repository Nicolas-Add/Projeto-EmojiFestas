// Menu mobile
const navLinks = document.getElementById('navLinks');
document.getElementById('menuBtn').onclick = () => navLinks.classList.toggle('open');
navLinks.querySelectorAll('a').forEach(a => a.onclick = () => navLinks.classList.remove('open'));

// Orçamento
const form = document.getElementById('simForm');
const brl = v => v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 });
const HORA_EXTRA = 200;
const nome = input => input.closest('label').querySelector('span').firstChild.textContent.trim();

function calcular() {
  const salao = form.querySelector('[name=salao]:checked');
  const combo = form.querySelector('[name=combo]:checked');
  const horas = +form.horas.value;
  const linhas = [[`Salão ${nome(salao)}`, +salao.value], [`Combo ${nome(combo)}`, +combo.value]];
  form.querySelectorAll('[name=extra]:checked').forEach(e => linhas.push([nome(e), +e.value]));
  if (horas) linhas.push([`${horas}h a mais`, horas * HORA_EXTRA]);

  const total = linhas.reduce((s, [, v]) => s + v, 0);
  document.getElementById('lines').innerHTML = linhas.map(([n, v]) => `<li><span>${n}</span><span>${v ? brl(v) : '—'}</span></li>`).join('');
  document.getElementById('total').textContent = brl(total);
  document.getElementById('sinal').textContent = `Sinal pra reservar (30%): ${brl(total * 0.3)}`;
  document.getElementById('horasOut').textContent = horas ? `${horas}h · ${brl(horas * HORA_EXTRA)}` : 'nenhuma';
}
form.addEventListener('input', calcular);
calcular();
