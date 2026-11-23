const input = document.getElementById('apiUrl');
const statusEl = document.getElementById('status');
const catalogo = document.getElementById('catalogo');
const form = document.getElementById('livroForm');

function enderecoInicial() {
  const salvo = localStorage.getItem('livrariaApi');
  const url = new URL(window.location.href);
  // Ignora localhost salvo por engano quando o site está publicado na nuvem.
  if (salvo && !(url.hostname !== 'localhost' && url.hostname !== '127.0.0.1' && /^http:\/\/(localhost|127\.0\.0\.1)(:|\/|$)/.test(salvo))) return salvo;
  if (url.hostname.endsWith('.app.github.dev')) {
    return `${url.protocol}//${url.host.replace(/-5500\.app\.github\.dev$/, '-5000.app.github.dev')}`;
  }
  if (url.hostname === '127.0.0.1' || url.hostname === 'localhost') {
    return 'http://localhost:5000';
  }
  // No Azure, a mesma aplicação Flask entrega o site e a API.
  return url.origin;
}
input.value = enderecoInicial();
function apiUrl() { return input.value.trim().replace(/\/+$/, ''); }
function aviso(msg, erro=false) { statusEl.textContent=msg; statusEl.style.color=erro?'#b5293e':'#606d80'; }

async function buscarLivros() {
  aviso('Carregando livros...');
  catalogo.replaceChildren();
  try {
    const resposta = await fetch(`${apiUrl()}/livros`);
    if (!resposta.ok) {
      const dados = await resposta.json().catch(() => ({}));
      throw new Error(dados.erro || `HTTP ${resposta.status}`);
    }
    const livros = await resposta.json();
    aviso(`${livros.length} livro(s) encontrado(s) no catálogo.`);
    if (!livros.length) { catalogo.textContent='Nenhum livro cadastrado.'; return; }
    livros.forEach(livro => {
      const card=document.createElement('article'); card.className='book';
      const titulo=document.createElement('h3'); titulo.textContent=livro.titulo;
      const autor=document.createElement('p'); autor.textContent=`Por ${livro.autor}`;
      const preco=document.createElement('p'); preco.className='price';
      preco.textContent=Number(livro.preco).toLocaleString('pt-BR',{style:'currency',currency:'BRL'});
      const botao=document.createElement('button'); botao.type='button'; botao.textContent='Excluir livro';
      botao.addEventListener('click',()=>excluirLivro(livro.id));
      card.append(titulo,autor,preco,botao);catalogo.append(card);
    });
  } catch(e) { aviso(`Não foi possível acessar a API (${e.message}). Confira a URL e a conexão com o banco.`,true); }
}
async function excluirLivro(id) {
  if (!confirm('Deseja excluir este livro?')) return;
  try { const r=await fetch(`${apiUrl()}/livros/${encodeURIComponent(id)}`,{method:'DELETE'});if(!r.ok)throw new Error(`HTTP ${r.status}`);await buscarLivros(); }
  catch(e){aviso(`Erro ao excluir: ${e.message}`,true)}
}
form.addEventListener('submit',async e=>{
  e.preventDefault();
  const dados=Object.fromEntries(new FormData(form).entries());dados.preco=Number(dados.preco);
  try {
    const r=await fetch(`${apiUrl()}/livros`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(dados)});
    if(!r.ok){const msg=await r.json();throw new Error(msg.erro||`HTTP ${r.status}`)}
    form.reset();await buscarLivros();
  } catch(e){aviso(`Erro ao cadastrar: ${e.message}`,true)}
});
document.getElementById('connectBtn').addEventListener('click',()=>{localStorage.setItem('livrariaApi',apiUrl());buscarLivros()});
document.getElementById('refreshBtn').addEventListener('click',buscarLivros);
buscarLivros();
