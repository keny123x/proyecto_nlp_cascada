export function node(tag, text = '', className = '') {
  const item = document.createElement(tag);
  item.textContent = text; item.className = className; return item;
}
export const percent = (value) => Number.isFinite(value)
  ? `${(value * 100).toLocaleString('es', {minimumFractionDigits:1,maximumFractionDigits:1})} %` : 'No disponible';
export function table(headers, rows, caption) {
  const wrap = node('div', '', 'table-scroll');
  const grid = node('table'); grid.append(node('caption', caption));
  const head = node('thead'); const tr = node('tr');
  headers.forEach((label) => { const th = node('th', label); th.scope = 'col'; tr.append(th); });
  head.append(tr); const body = node('tbody');
  rows.forEach((values) => { const row = node('tr'); values.forEach((value) => {
    const cell = node('td'); cell.append(value instanceof Node ? value : document.createTextNode(String(value))); row.append(cell);
  }); body.append(row); });
  grid.append(head, body); wrap.append(grid); return wrap;
}
