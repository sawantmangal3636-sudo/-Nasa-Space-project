backend/app.js
const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(cors());
app.use(express.json());

// Load publications.json
const DATA_PATH = path.join(__dirname, '..', 'data', 'publications.json');
let publications = [];
try {
  const raw = fs.readFileSync(DATA_PATH, 'utf8');
  publications = JSON.parse(raw);
  console.log(`Loaded ${publications.length} publications`);
} catch (err) {
  console.warn('Could not load publications.json:', err.message);
  publications = [];
}

// ----------------------
// Simple Search Function
// ----------------------
function normalize(s){ return (s||'').toLowerCase(); }

function scoreAgainstText(queryTokens, text){
  let score = 0;
  const t = normalize(text);
  queryTokens.forEach(token => {
    if (!token) return;
    if (t.includes(token)) score += 1;
    const occurrences = t.split(token).length - 1;
    if (occurrences > 1) score += (occurrences - 1) * 0.3;
  });
  return score;
}

function searchPubs(rawQuery, k = 5){
  if (!rawQuery || rawQuery.trim() === '') return [];
  const q = normalize(rawQuery).split(/\s+/).filter(Boolean);
  return publications.map(p => {
    const text = `${p.title} ${p.abstract} ${(p.keywords||[]).join(' ')} ${p.mission || ''} ${p.organism || ''}`;
    return { pub: p, score: scoreAgainstText(q, text) };
  })
  .filter(x => x.score > 0)
  .sort((a,b) => b.score - a.score)
  .slice(0, k)
  .map(x => x.pub);

// API Routes

app.get('/api/search', (req, res) => {
  const q = req.query.q || '';
  const results = searchPubs(q, 20);
  res.json({ count: results.length, results });
});

// POST /api/ask question-something
app.post('/api/ask', (req, res) => {
  const question = (req.body.question || '').trim();
  if (!question) return res.status(400).json({ error: 'Provide { "question": "..." }' });

  const matches = searchPubs(question, 6);
  if (matches.length === 0) {
    return res.json({
      answer: "I couldn't find publications that match that query.",
      sources: []
    });
  }

  let answer = `I found ${matches.length} relevant publication(s):\n\n`;
  matches.forEach((m, i) => {
    const snippet = (m.abstract || '').slice(0, 300).trim();
    answer += `${i+1}. ${m.title} (${m.year || 'n.d.'}) — ${m.organism || 'N/A'}\n   ${snippet}${snippet.length >= 300 ? '...' : ''}\n\n`;
  });

  const sources = matches.map(m => ({ id: m.pub_id, title: m.title, url: m.pdf_url || null }));
  res.json({ answer, sources });
});

// GET (api graph)
app.get('/api/graph', (req, res) => {
  const nodes = [];
  const edges = [];
  const nodeMap = new Map();

  publications.forEach((p) => {
    const pubNodeId = `pub_${p.pub_id}`;
    nodes.push({ id: pubNodeId, label: p.title, group: 'publication' });

    if (p.organism) {
      const orgId = `org_${p.organism.replace(/\W+/g,'_')}`;
      if (!nodeMap.has(orgId)) nodeMap.set(orgId, { id: orgId, label: p.organism, group: 'organism' });
      edges.push({ from: pubNodeId, to: orgId });
    }
    if (p.mission) {
      const missionId = `mis_${p.mission.replace(/\W+/g,'_')}`;
      if (!nodeMap.has(missionId)) nodeMap.set(missionId, { id: missionId, label: p.mission, group: 'mission' });
      edges.push({ from: pubNodeId, to: missionId });
    }
  });

  for (const v of nodeMap.values()) nodes.push(v);
  res.json({ nodes, edges });
});

// Serve frontend

const staticPath = path.join(__dirname, '..', 'web');
app.use(express.static(staticPath));

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`✅ Server running at http://localhost:${PORT}`);
});}