const zone = document.getElementById("dropzone");
const input = zone.querySelector('input[type="file"]');
const fileName = document.getElementById("file-name");

function showSelectedFile() {
  fileName.textContent = input.files[0]?.name ?? "Choose a PDF";
}

function highlight(active) {
  zone.classList.toggle("is-active", active);
}

input.addEventListener("change", showSelectedFile);

zone.addEventListener("dragover", (event) => {
  event.preventDefault();
  highlight(true);
});

zone.addEventListener("dragleave", () => highlight(false));

zone.addEventListener("drop", (event) => {
  event.preventDefault();
  highlight(false);
  input.files = event.dataTransfer.files;
  showSelectedFile();
});
