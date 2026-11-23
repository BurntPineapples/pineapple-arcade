// Forgiving search: ignores spaces/punctuation, tolerates typos, matches initials and categories.
const norm = s => s.toLowerCase().replace(/&/g, ' and ').replace(/[^a-z0-9]+/g, ' ').trim();

function lev(a, b) {
  if (Math.abs(a.length - b.length) > 2) return 9;
  // Damerau-style: swapped letters ("xm3" vs "x3m") count as one typo
  let pp = [], prev = Array.from({ length: b.length + 1 }, (_, i) => i);
  for (let i = 1; i <= a.length; i++) {
    const cur = [i];
    for (let j = 1; j <= b.length; j++) {
      cur[j] = Math.min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
      if (i > 1 && j > 1 && a[i - 1] === b[j - 2] && a[i - 2] === b[j - 1]) cur[j] = Math.min(cur[j], pp[j - 2] + 1);
    }
    pp = prev; prev = cur;
  }
  return prev[b.length];
}

const isSubseq = (q, s) => { let i = 0; for (const ch of s) if (ch === q[i]) i++; return i === q.length; };

function tokenScore(tok, words, compact) {
  let best = 0;
  const tol = tok.length >= 6 ? 2 : tok.length >= 3 ? 1 : 0;
  for (const w of words) {
    if (w === tok) return 4;
    if (w.startsWith(tok)) best = Math.max(best, 3);
    else if (w.includes(tok)) best = Math.max(best, 2);
    else if (tol && best < 1.5 && (tok[0] === w[0] || tok[1] === w[1]) && (lev(tok, w) <= tol || lev(tok, w.slice(0, tok.length)) <= tol)) best = 1.5; // first-letters gate skips most typo checks
  }
  if (!best && tok.length >= 3 && compact.includes(tok)) best = 2;
  return best;
}

// game: {t, c:[categories]} -> score (0 = no match)
function score(q, game) {
  const nq = norm(q);
  if (!nq) return 1;
  const cq = nq.replace(/ /g, '');
  // normalized title parts cached on the game; 30k games re-normalized per keystroke is the slow part
  const p = game._p || (game._p = (() => {
    const title = norm(game.t), words = title.split(' ');
    return { title, words, compact: title.replace(/ /g, ''), initials: words.map(w => w[0]).join(''), cats: (game.c || []).map(norm) };
  })());
  const { title, words, compact, cats } = p;
  let s = 0;
  if (title === nq || compact === cq) s += 20;
  else if (compact.startsWith(cq)) s += 12;
  else if (compact.includes(cq)) s += 8;
  if (cq.length >= 2 && p.initials.startsWith(cq)) s += 7; // initials: "fnf"
  const toks = nq.split(' ');
  let hit = 0;
  for (const tok of toks) {
    let ts = tokenScore(tok, words, compact);
    if (!ts && cats.some(c => c.startsWith(tok) || (tok.length > 3 && lev(tok, c) <= 1))) ts = 1;
    if (ts) hit++;
    s += ts;
  }
  if (hit < Math.ceil(toks.length / 2) && s < 7) return 0;
  if (toks.length > 1 && hit === toks.length) s += 3; // every word matched beats one exact word
  if (!s && cq.length >= 4 && isSubseq(cq, compact)) s = 0.5;
  return s;
}

function search(q, games) {
  return games.map(g => [score(q, g), g]).filter(x => x[0] > 0)
    .sort((a, b) => b[0] - a[0] || (b[1].hot ? 1 : 0) - (a[1].hot ? 1 : 0)).map(x => x[1]);
}

if (typeof module !== 'undefined') module.exports = { search, score, norm };
