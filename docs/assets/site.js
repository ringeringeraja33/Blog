(() => {
  const root = document.documentElement;
  const body = document.body;
  const baseurl = body.dataset.baseurl || "";
  const searchUrl = `${baseurl}/search.json`;
  let postsPromise;

  const loadPosts = () => {
    if (!postsPromise) {
      postsPromise = fetch(searchUrl)
        .then((response) => {
          if (!response.ok) throw new Error(`HTTP ${response.status}`);
          return response.json();
        })
        .catch(() => []);
    }
    return postsPromise;
  };

  const savedTheme = localStorage.getItem("aevum-theme");
  const preferredTheme = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  const applyTheme = (theme) => {
    root.dataset.theme = theme;
    document.querySelector('meta[name="theme-color"]')?.setAttribute("content", theme === "dark" ? "#171715" : "#f4f1ea");
    const utterances = document.querySelector(".utterances-frame");
    utterances?.contentWindow?.postMessage({ type: "set-theme", theme: theme === "dark" ? "github-dark" : "github-light" }, "https://utteranc.es");
  };
  applyTheme(savedTheme || preferredTheme);

  document.querySelector("[data-theme-toggle]")?.addEventListener("click", () => {
    const next = root.dataset.theme === "dark" ? "light" : "dark";
    localStorage.setItem("aevum-theme", next);
    applyTheme(next);
  });

  const menuButton = document.querySelector(".mobile-menu-button");
  const navigation = document.querySelector("#site-navigation");
  menuButton?.addEventListener("click", () => {
    const isOpen = menuButton.getAttribute("aria-expanded") === "true";
    menuButton.setAttribute("aria-expanded", String(!isOpen));
    navigation?.classList.toggle("is-open", !isOpen);
  });

  document.querySelector("[data-random-post]")?.addEventListener("click", async () => {
    const posts = await loadPosts();
    if (!posts.length) return;
    const candidates = posts.filter((post) => post.url !== window.location.pathname);
    const pool = candidates.length ? candidates : posts;
    window.location.href = pool[Math.floor(Math.random() * pool.length)].url;
  });

  const dialog = document.querySelector("[data-search-dialog]");
  const input = document.querySelector("[data-search-input]");
  const results = document.querySelector("[data-search-results]");
  const status = document.querySelector("[data-search-status]");
  const closeSearch = () => {
    if (!dialog) return;
    dialog.hidden = true;
    body.classList.remove("dialog-open");
  };
  const openSearch = async () => {
    if (!dialog) return;
    dialog.hidden = false;
    body.classList.add("dialog-open");
    await loadPosts();
    input?.focus();
  };

  document.querySelector("[data-search-open]")?.addEventListener("click", openSearch);
  document.querySelectorAll("[data-search-close]").forEach((element) => element.addEventListener("click", closeSearch));
  document.addEventListener("keydown", (event) => {
    if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
      event.preventDefault();
      openSearch();
    }
    if (event.key === "Escape" && dialog && !dialog.hidden) closeSearch();
  });

  const escapeHtml = (value) => String(value).replace(/[&<>'"]/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" })[character]);
  input?.addEventListener("input", async () => {
    const query = input.value.trim().toLocaleLowerCase("zh-CN");
    if (!results || !status) return;
    results.innerHTML = "";
    if (!query) {
      status.textContent = "输入关键词开始搜索。";
      return;
    }
    const posts = await loadPosts();
    const matches = posts.filter((post) => [post.title, post.description, post.content, ...(post.categories || []), ...(post.tags || [])].join(" ").toLocaleLowerCase("zh-CN").includes(query)).slice(0, 20);
    status.textContent = matches.length ? `找到 ${matches.length} 篇文章` : "没有匹配的文章。";
    results.innerHTML = matches.map((post) => `<li><a href="${escapeHtml(post.url)}"><strong>${escapeHtml(post.title)}</strong><span>${escapeHtml(post.date)} · ${escapeHtml(post.description || "")}</span></a></li>`).join("");
  });

  const articleBody = document.querySelector("[data-article-body]");
  const toc = document.querySelector("[data-toc]");
  const tocCard = document.querySelector("[data-toc-card]");
  if (articleBody && toc && tocCard) {
    const headings = [...articleBody.querySelectorAll("h2, h3")];
    if (headings.length) {
      const usedIds = new Set();
      headings.forEach((heading, index) => {
        let id = heading.id || heading.textContent.trim().toLocaleLowerCase("zh-CN").replace(/[^\p{L}\p{N}]+/gu, "-").replace(/^-|-$/g, "") || `section-${index + 1}`;
        const baseId = id;
        let suffix = 2;
        while (usedIds.has(id)) id = `${baseId}-${suffix++}`;
        usedIds.add(id);
        heading.id = id;
        const link = document.createElement("a");
        link.href = `#${encodeURIComponent(id)}`;
        link.textContent = heading.textContent;
        link.className = heading.tagName === "H3" ? "toc-level-3" : "toc-level-2";
        toc.append(link);
      });
      tocCard.hidden = false;
    }

    articleBody.querySelectorAll("img").forEach((image) => {
      image.tabIndex = 0;
      image.setAttribute("role", "button");
      image.setAttribute("aria-label", image.alt ? `查看大图：${image.alt}` : "查看大图");
      const openLightbox = () => {
        const overlay = document.createElement("div");
        overlay.className = "lightbox";
        overlay.tabIndex = 0;
        overlay.innerHTML = `<img src="${escapeHtml(image.currentSrc || image.src)}" alt="${escapeHtml(image.alt || "")}"><button type="button" aria-label="关闭大图">×</button>`;
        const close = () => overlay.remove();
        overlay.addEventListener("click", close);
        overlay.addEventListener("keydown", (event) => { if (event.key === "Escape") close(); });
        document.body.append(overlay);
        overlay.focus();
      };
      image.addEventListener("click", openLightbox);
      image.addEventListener("keydown", (event) => { if (event.key === "Enter") openLightbox(); });
    });
  }

  const progressBar = document.querySelector("[data-reading-progress]");
  const progressText = document.querySelector("[data-reading-percent]");
  const backToTop = document.querySelector(".back-to-top");
  const updateScroll = () => {
    const scrollable = document.documentElement.scrollHeight - window.innerHeight;
    const percent = scrollable > 0 ? Math.min(100, Math.max(0, (window.scrollY / scrollable) * 100)) : 0;
    if (progressBar) progressBar.style.transform = `scaleX(${percent / 100})`;
    if (progressText) progressText.textContent = `${Math.round(percent)}%`;
    backToTop?.classList.toggle("is-visible", window.scrollY > 700);
  };
  window.addEventListener("scroll", updateScroll, { passive: true });
  updateScroll();
  backToTop?.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));

  document.querySelector("[data-copy-link]")?.addEventListener("click", async (event) => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      event.currentTarget.textContent = "已复制";
    } catch {
      event.currentTarget.textContent = "复制失败";
    }
  });
})();
