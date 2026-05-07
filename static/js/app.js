document.addEventListener("submit", (event) => {
  const form = event.target;
  const priceInput = form.querySelector('input[name="price"]');
  if (priceInput && Number(priceInput.value) <= 0) {
    event.preventDefault();
    priceInput.focus();
    alert("Price must be greater than zero.");
  }
});
