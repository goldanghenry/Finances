/* MathJax 3 + pymdownx.arithmatex (generic). Load BEFORE tex-mml-chtml.js */
window.MathJax = {
  tex: {
    inlineMath: [["\\(", "\\)"]],
    displayMath: [["\\[", "\\]"]],
    processEscapes: true,
    processEnvironments: true,
    packages: { "[+]": ["ams", "noerrors", "noundefined"] },
  },
  options: {
    ignoreHtmlClass: ".*|",
    processHtmlClass: "arithmatex",
  },
};

function typesetMath() {
  if (!window.MathJax?.startup?.promise) {
    return;
  }
  MathJax.startup.promise.then(() => {
    if (MathJax.startup?.output?.clearCache) {
      MathJax.startup.output.clearCache();
    }
    MathJax.typesetClear();
    MathJax.texReset();
    return MathJax.typesetPromise();
  });
}

/* Material instant navigation — must reset cache between SPA page swaps */
if (typeof document$ !== "undefined") {
  document$.subscribe(typesetMath);
} else {
  document.addEventListener("DOMContentLoaded", typesetMath);
}
