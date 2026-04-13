const renderAdmonitions = () => {
  document.querySelectorAll("blockquote").forEach((blockquote) => {
    const firstParagraph = blockquote.querySelector("p");
    if (!firstParagraph) {
      return;
    }

    const marker = firstParagraph.textContent.match(/^\s*\[!(IMPORTANT|NOTE|TIP|WARNING|CAUTION)\]\s*/);
    if (!marker) {
      return;
    }

    const kind = marker[1].toLowerCase();
    firstParagraph.innerHTML = firstParagraph.innerHTML.replace(/^\s*\[![A-Z]+\]\s*/, "");

    const title = document.createElement("p");
    title.className = "admonition-title";
    title.textContent = marker[1].charAt(0) + marker[1].slice(1).toLowerCase();

    blockquote.classList.add("admonition", "admonition-" + kind);
    blockquote.insertBefore(title, firstParagraph);
  });
};

const renderMermaid = async () => {
  const blocks = document.querySelectorAll("pre > code.language-mermaid");
  if (!blocks.length) {
    return;
  }

  blocks.forEach((code) => {
    const pre = code.parentElement;
    const container = document.createElement("div");
    container.className = "mermaid";
    container.textContent = code.textContent;
    pre.replaceWith(container);
  });

  const mermaid = (await import("https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs")).default;

  mermaid.initialize({
    startOnLoad: false,
    securityLevel: "loose",
    theme: "base",
    flowchart: {
      curve: "linear",
      htmlLabels: true
    },
    themeVariables: {
      primaryColor: "#ffffff",
      primaryTextColor: "#151515",
      primaryBorderColor: "#c7c7c7",
      lineColor: "#4d4d4d",
      secondaryColor: "#f2f2f2",
      secondaryTextColor: "#151515",
      secondaryBorderColor: "#c7c7c7",
      tertiaryColor: "#fce3e3",
      tertiaryTextColor: "#151515",
      tertiaryBorderColor: "#ee0000",
      background: "#ffffff",
      mainBkg: "#ffffff",
      clusterBkg: "#ffffff",
      clusterBorder: "#c7c7c7",
      actorBkg: "#ffffff",
      actorBorder: "#c7c7c7",
      actorTextColor: "#151515",
      labelBoxBkgColor: "#ffffff",
      labelTextColor: "#151515",
      edgeLabelBackground: "#ffffff",
      signalColor: "#4d4d4d",
      signalTextColor: "#151515",
      noteBkgColor: "#f2f2f2",
      noteBorderColor: "#c7c7c7",
      noteTextColor: "#151515",
      sequenceNumberColor: "#151515",
      fontFamily: "Red Hat Text"
    },
    themeCSS: `
      .node rect,
      .node polygon,
      .node path,
      .node circle {
        stroke-width: 1.5px;
      }
      .nodeLabel,
      .label foreignObject div,
      .edgeLabel {
        font-family: 'Red Hat Text', Helvetica, Arial, sans-serif !important;
        color: #151515 !important;
      }
      .cluster-label text,
      .cluster-label span {
        font-family: 'Red Hat Text', Helvetica, Arial, sans-serif !important;
        font-weight: 500;
        color: #151515 !important;
      }
      .edgePath .path,
      .flowchart-link {
        stroke: #4d4d4d !important;
        stroke-width: 1.5px !important;
        stroke-linecap: square;
      }
      .marker path {
        fill: #4d4d4d !important;
        stroke: #4d4d4d !important;
      }
      .actor {
        stroke-width: 1.5px !important;
      }
    `
  });

  await mermaid.run({ querySelector: ".mermaid" });
};

const renderToc = () => {
  const tocList = document.querySelector("[data-generated-toc]");
  if (!tocList) {
    return;
  }

  const tocBlock = tocList.closest(".toc-block");
  const rootSelector = tocBlock?.dataset.tocRoot || ".markdown-body";
  const levels = (tocBlock?.dataset.tocLevels || "h2,h3").split(",");
  const root = document.querySelector(rootSelector);
  if (!root) {
    return;
  }

  const headings = Array.from(root.querySelectorAll(levels.join(","))).filter((heading) => {
    return heading.id && heading.textContent.trim() && heading.textContent.trim() !== "Related docs:";
  });

  if (!headings.length) {
    tocBlock?.remove();
    return;
  }

  tocList.innerHTML = "";

  headings.forEach((heading) => {
    const item = document.createElement("li");
    item.className = `toc-${heading.tagName.toLowerCase()}`;

    const link = document.createElement("a");
    link.href = `#${heading.id}`;
    link.textContent = heading.textContent.trim();

    item.appendChild(link);
    tocList.appendChild(item);
  });
};

window.addEventListener("DOMContentLoaded", async () => {
  renderAdmonitions();
  renderToc();
  await renderMermaid();
});
