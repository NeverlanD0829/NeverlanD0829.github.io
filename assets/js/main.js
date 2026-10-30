(() => {
  'use strict';
  const root = document.documentElement;
  const toggle = document.querySelector('.theme-toggle');
  const media = matchMedia('(prefers-color-scheme: dark)');
  const updateThemeButton = () => {
    const dark = root.dataset.theme === 'dark';
    toggle?.setAttribute('aria-label', dark ? '切换到浅色模式' : '切换到深色模式');
    toggle?.setAttribute('aria-pressed', String(dark));
  };
  toggle?.addEventListener('click', () => {
    const next = root.dataset.theme === 'dark' ? 'light' : 'dark';
    root.dataset.theme = next;
    try { localStorage.setItem('neverland-theme', next); } catch {}
    updateThemeButton();
  });
  media.addEventListener('change', (event) => {
    let saved;
    try { saved = localStorage.getItem('neverland-theme'); } catch {}
    if (saved !== 'light' && saved !== 'dark') {
      root.dataset.theme = event.matches ? 'dark' : 'light';
      updateThemeButton();
    }
  });
  updateThemeButton();

  const dialog = document.getElementById('search-dialog');
  const input = document.getElementById('search-input');
  const results = document.getElementById('search-results');
  const status = document.getElementById('search-status');
  let indexPromise;
  let debounce;
  let previousFocus;
  const normalize = (text) => String(text || '').normalize('NFKC').toLocaleLowerCase();

  const loadIndex = () => {
    if (!indexPromise) {
      indexPromise = fetch(dialog.dataset.index)
        .then((response) => {
          if (!response.ok) throw new Error('Search index unavailable');
          return response.json();
        })
        .then((data) => {
          if (!Array.isArray(data)) throw new Error('Invalid search index');
          return data;
        })
        .catch((error) => { indexPromise = undefined; throw error; });
    }
    return indexPromise;
  };

  async function search() {
    status.textContent = '正在读取笔记…';
    let posts;
    try { posts = await loadIndex(); }
    catch {
      results.replaceChildren();
      status.textContent = '暂时无法加载搜索，请关闭后重试。你也可以通过文章页浏览。';
      return;
    }
    const terms = normalize(input.value.trim()).split(/\s+/u).filter(Boolean);
    const found = posts.map((post) => {
      const title = normalize(post.title);
      const tags = normalize((post.tags || []).join(' '));
      const text = normalize(`${post.title} ${tags} ${post.description} ${post.content}`);
      const match = terms.every((term) => text.includes(term));
      const score = terms.reduce((total, term) => total + (title.includes(term) ? 4 : 0) + (tags.includes(term) ? 2 : 0), 0);
      return { post, match, score };
    }).filter((item) => item.match).sort((a, b) => b.score - a.score);
    results.replaceChildren();
    const shown = found.slice(0, terms.length ? 30 : 5);
    status.textContent = terms.length
      ? (found.length ? `找到 ${found.length} 篇文章${found.length > 30 ? '，显示前 30 篇' : ''}` : '没有找到相关文章，换一个关键词试试。')
      : (found.length ? '最近的文章' : '还没有已发布的文章。');
    for (const { post } of shown) {
      const link = document.createElement('a');
      link.className = 'search-result';
      link.href = post.url;
      const title = document.createElement('h3');
      title.textContent = post.title;
      const summary = document.createElement('p');
      const content = post.content || post.description || '';
      const matchAt = terms.length ? normalize(content).indexOf(terms[0]) : -1;
      const start = Math.max(0, matchAt - 32);
      const excerpt = matchAt >= 0 ? content.slice(start, start + 140) : (post.description || content).slice(0, 140);
      summary.textContent = `${start > 0 ? '…' : ''}${excerpt}${excerpt.length === 140 ? '…' : ''}`;
      const date = document.createElement('span');
      date.className = 'result-date';
      date.textContent = post.date;
      link.append(title, summary, date);
      results.append(link);
    }
  }

  function openSearch() {
    if (dialog.open) return;
    previousFocus = document.activeElement;
    dialog.showModal();
    input.focus();
    search();
  }
  document.querySelectorAll('.search-trigger').forEach((button) => button.addEventListener('click', openSearch));
  document.getElementById('search-close')?.addEventListener('click', () => dialog.close());
  dialog?.addEventListener('close', () => previousFocus?.focus());
  dialog?.addEventListener('click', (event) => {
    const box = dialog.getBoundingClientRect();
    if (event.target === dialog && (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom)) dialog.close();
  });
  input?.addEventListener('input', () => { clearTimeout(debounce); debounce = setTimeout(search, 120); });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && dialog.open) {
      event.preventDefault();
      dialog.close();
      return;
    }
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') {
      event.preventDefault();
      if (dialog.open) dialog.close(); else openSearch();
    }
  });

  document.querySelectorAll('.prose .highlight').forEach((block) => {
    const code = block.querySelector('pre code');
    if (!code) return;
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'copy-code';
    button.textContent = '复制';
    button.setAttribute('aria-label', '复制代码');
    button.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(code.innerText);
        button.textContent = '已复制';
      } catch { button.textContent = '请选中复制'; }
      setTimeout(() => { button.textContent = '复制'; }, 2200);
    });
    block.append(button);
  });
})();
