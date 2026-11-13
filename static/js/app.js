// Só interações de tela. Nenhuma regra da biblioteca fica no JavaScript.

// Pede confirmação antes de enviar formulários marcados com data-confirmar.
document.querySelectorAll("form[data-confirmar]").forEach((formulario) => {
  formulario.addEventListener("submit", (evento) => {
    if (!window.confirm(formulario.dataset.confirmar)) evento.preventDefault();
  });
});

// Filtra as linhas de uma tabela conforme o texto digitado.
document.querySelectorAll("input[data-filtrar]").forEach((campo) => {
  const linhas = document.querySelectorAll(`#${campo.dataset.filtrar} tbody tr`);
  campo.addEventListener("input", () => {
    const termo = campo.value.toLowerCase();
    linhas.forEach((linha) => { linha.hidden = !linha.textContent.toLowerCase().includes(termo); });
  });
});
