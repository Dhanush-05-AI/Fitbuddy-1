document.querySelectorAll("form[data-loading]").forEach((form) => {
  form.addEventListener("submit", () => {
    const overlay = document.createElement("div");
    overlay.className = "loading-overlay";
    overlay.setAttribute("role", "status");
    overlay.innerHTML = '<div class="spinner"></div><p></p>';
    overlay.querySelector("p").textContent = form.dataset.loading;
    document.body.appendChild(overlay);
    form.querySelectorAll("button").forEach((b) => (b.disabled = true));
  });
});
window.addEventListener("pageshow", (e) => {
  if (!e.persisted) return;
  document.querySelectorAll(".loading-overlay").forEach((el) => el.remove());
  document.querySelectorAll("form[data-loading] button").forEach((b) => (b.disabled = false));
});
