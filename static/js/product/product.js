function deleteProduct(button) {
  const url = button.getAttribute("data-url");
  const deleteModal = document.getElementById("deleteStaticBackdrop");
  const deleteForm = deleteModal.querySelector(".modal-dialog form");
  deleteForm.setAttribute("action", url);
  deleteModal.addEventListener("hidden.bs.modal", () => {
    deleteForm.removeAttribute("action");
  });
}
