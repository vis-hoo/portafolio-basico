"use strict";

const CORNERS = ["top-left", "top-right", "bottom-right", "bottom-left"];

const sliders = {};
for (const corner of CORNERS) {
  sliders[corner] = {
    input: document.getElementById(corner),
    value: document.getElementById(`${corner}-value`),
  };
}

const previewBox = document.getElementById("preview-box");
const cssCode = document.getElementById("css-code");
const linkButton = document.getElementById("link-button");
const resetButton = document.getElementById("reset-button");
const copyButton = document.getElementById("copy-button");
const copyStatus = document.getElementById("copy-status");

let linked = false;

function getRadius() {
  return CORNERS.map((corner) => Number(sliders[corner].input.value));
}

function render() {
  const values = getRadius();
  for (let i = 0; i < CORNERS.length; i++) {
    sliders[CORNERS[i]].value.textContent = `${values[i]} px`;
  }
  previewBox.style.borderRadius = values.join("px ") + "px";
  cssCode.textContent = `border-radius: ${values.join("px ")}px;`;
}

function onSliderInput(event) {
  const source = event.target;
  if (linked) {
    for (const corner of CORNERS) {
      sliders[corner].input.value = source.value;
    }
  }
  render();
}

linkButton.addEventListener("click", () => {
  linked = !linked;
  linkButton.setAttribute("aria-pressed", String(linked));
  if (linked) {
    // Alinear todas las esquinas al valor de la primera al vincular.
    const value = sliders["top-left"].input.value;
    for (const corner of CORNERS) {
      sliders[corner].input.value = value;
    }
    render();
  }
});

resetButton.addEventListener("click", () => {
  for (const corner of CORNERS) {
    sliders[corner].input.value = 0;
  }
  render();
});

copyButton.addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(cssCode.textContent);
    copyStatus.textContent = "CSS copiado al portapapeles";
  } catch {
    copyStatus.textContent = "No se pudo copiar";
  }
  setTimeout(() => {
    copyStatus.textContent = "";
  }, 2000);
});

for (const corner of CORNERS) {
  sliders[corner].input.addEventListener("input", onSliderInput);
}

render();
