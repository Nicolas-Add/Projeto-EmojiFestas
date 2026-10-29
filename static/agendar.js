const f = document.getElementById('wizard');
const steps = [...f.querySelectorAll('.step')];
const marcadores = [...document.querySelectorAll('#steps li')];
const erroEl = document.getElementById('wizErro');
const brl = v => v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
let atual = 0;

// Cliente novo
const sel = document.getElementById('clienteSel'), novo = document.getElementById('novoCliente');
const toggleNovo = () => {
  novo.hidden = sel.value !== 'novo';
  novo.querySelectorAll('input').forEach((i, n) => i.required = !novo.hidden && n < 2);
};
sel.onchange = toggleNovo; toggleNovo();

// Disponibilidade do salão no dia escolhido
function disponibilidade() {
  const salao = f.querySelector('[name=salao_id]:checked')?.value, dia = f.data.value, el = document.getElementById('avail');
  if (!dia) return el.textContent = '';
  const ocup = OCUPADOS[salao]?.[dia] || [];
  el.className = 'avail ' + (ocup.length ? 'busy' : 'free');
  el.textContent = ocup.length ? `Já reservado nesse dia: ${ocup.join(', ')}. Escolha outro horário ou salão.` : 'Salão livre nesse dia.';
}

// Orçamento em tempo real
function orcamento() {
  const linhas = [...f.querySelectorAll('input[data-preco]:checked')].filter(i => i.dataset.nome).map(i => [i.dataset.nome, +i.dataset.preco]);
  const horas = +f.horas_extra.value;
  if (horas) linhas.push([`${horas}h a mais`, horas * HORA_EXTRA]);
  const total = linhas.reduce((s, [, v]) => s + v, 0);
  document.getElementById('lines').innerHTML = linhas.map(([n, v]) => `<li><span>${n}</span><span>${v ? brl(v) : '—'}</span></li>`).join('');
  document.getElementById('total').textContent = brl(total);
  document.getElementById('sinal').textContent = total ? `Sinal sugerido (30%): ${brl(total * .3)}` : '';
  document.getElementById('horasOut').textContent = horas ? `+${horas}h · ${brl(horas * HORA_EXTRA)}` : 'nenhuma';
  return linhas;
}

function revisao() {
  const cli = sel.value === 'novo' ? f.novo_nome.value : sel.selectedOptions[0].text.split(' · ')[0];
  const salao = f.querySelector('[name=salao_id]:checked').dataset.nome;
  const [a, m, d] = f.data.value.split('-');
  const itens = orcamento().filter(([n]) => !n.startsWith('Salão')).map(([n]) => n).join(', ') || '—';
  document.getElementById('review').innerHTML =
    `<dt>Cliente</dt><dd>${cli}</dd><dt>Local</dt><dd>${salao}</dd><dt>Data</dt><dd>${d}/${m}/${a} às ${f.inicio.value}</dd><dt>Pacote</dt><dd>${itens}</dd>`;
}

function valida() {
  const campos = [...steps[atual].querySelectorAll('input, select')].filter(c => !c.closest('[hidden]'));
  const ruim = campos.find(c => !c.checkValidity());
  if (ruim) { ruim.reportValidity(); return false; }
  if (atual === 1 && document.getElementById('avail').classList.contains('busy')) {
    erroEl.textContent = 'Atenção: confira o horário — o sistema vai recusar se cruzar com outra festa.';
  }
  if (atual === 2 && !f.querySelector('[name=combo_id]:checked').value && !f.querySelector('[name=extras]:checked')) {
    erroEl.textContent = 'Escolha um combo ou pelo menos um adicional.';
    return false;
  }
  return true;
}

function ir(n) {
  atual = n;
  steps.forEach((s, i) => s.hidden = i !== n);
  marcadores.forEach((m, i) => { m.classList.toggle('on', i === n); m.classList.toggle('done', i < n); });
  document.getElementById('voltar').hidden = n === 0;
  document.getElementById('avancar').hidden = n === steps.length - 1;
  document.getElementById('confirmar').hidden = n !== steps.length - 1;
  if (n === steps.length - 1) revisao();
}

document.getElementById('avancar').onclick = () => { erroEl.textContent = ''; if (valida()) ir(atual + 1); };
document.getElementById('voltar').onclick = () => { erroEl.textContent = ''; ir(atual - 1); };
f.addEventListener('input', () => { orcamento(); disponibilidade(); });
orcamento(); disponibilidade();
