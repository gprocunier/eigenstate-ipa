const siteBaseUrl = document.body?.dataset.baseurl || "";

const withBaseUrl = (path) => {
  if (!siteBaseUrl) {
    return path;
  }
  return `${siteBaseUrl}${path}`;
};

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

const loadScript = (src) => new Promise((resolve, reject) => {
  const existing = document.querySelector(`script[data-src="${src}"]`);
  if (existing) {
    if (existing.dataset.loaded === "true") {
      resolve();
      return;
    }
    existing.addEventListener("load", () => resolve(), { once: true });
    existing.addEventListener("error", (event) => reject(event), { once: true });
    return;
  }

  const script = document.createElement("script");
  script.src = src;
  script.defer = true;
  script.dataset.src = src;
  script.addEventListener("load", () => {
    script.dataset.loaded = "true";
    resolve();
  }, { once: true });
  script.addEventListener("error", (event) => reject(event), { once: true });
  document.head.appendChild(script);
});

const ensureStylesheet = (href) => {
  if (document.querySelector(`link[data-href="${href}"]`)) {
    return;
  }

  const link = document.createElement("link");
  link.rel = "stylesheet";
  link.href = href;
  link.dataset.href = href;
  document.head.appendChild(link);
};

const renderAsciinemaPlayers = async () => {
  const players = document.querySelectorAll("[data-asciinema-src]");
  if (!players.length) {
    return;
  }

  ensureStylesheet(withBaseUrl("/assets/vendor/asciinema-player.css"));
  await loadScript(withBaseUrl("/assets/vendor/asciinema-player.min.js"));

  players.forEach((container) => {
    if (container.dataset.rendered === "true") {
      return;
    }

    const src = container.dataset.asciinemaSrc;
    const poster = container.dataset.asciinemaPoster || "npt:0:08";
    const speed = Number(container.dataset.asciinemaSpeed || "1.3");
    const cols = Number(container.dataset.asciinemaCols || "132");
    const rows = Number(container.dataset.asciinemaRows || "40");

    window.AsciinemaPlayer.create(src, container, {
      autoPlay: false,
      controls: true,
      fit: "width",
      speed,
      poster,
      cols,
      rows
    });

    container.dataset.rendered = "true";
  });
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

const activateTocOnScroll = () => {
  const links = Array.from(document.querySelectorAll(".toc-block a[href^='#']"));
  if (!links.length || !("IntersectionObserver" in window)) {
    return;
  }

  const linkById = new Map(
    links.map((link) => [decodeURIComponent(link.getAttribute("href").slice(1)), link])
  );

  let activeId = "";

  const setActive = (id) => {
    if (!id || id === activeId) {
      return;
    }
    activeId = id;
    links.forEach((link) => {
      link.classList.toggle("is-active", link === linkById.get(id));
    });
  };

  const observer = new IntersectionObserver((entries) => {
    const visible = entries
      .filter((entry) => entry.isIntersecting)
      .sort((left, right) => left.boundingClientRect.top - right.boundingClientRect.top);

    if (visible.length) {
      setActive(visible[0].target.id);
    }
  }, {
    rootMargin: "-20% 0px -65% 0px",
    threshold: [0, 1]
  });

  linkById.forEach((_, id) => {
    const heading = document.getElementById(id);
    if (heading) {
      observer.observe(heading);
    }
  });

  if (links[0]) {
    const initialId = decodeURIComponent(links[0].getAttribute("href").slice(1));
    setActive(initialId);
  }
};

window.addEventListener("DOMContentLoaded", async () => {
  renderAdmonitions();
  renderToc();
  activateTocOnScroll();
  await renderMermaid();
  await renderAsciinemaPlayers();
});
