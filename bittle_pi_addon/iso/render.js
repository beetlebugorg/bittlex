// Line-art PNGs of the build steps. iso_render.py serves this page, the STLs and jobs.json,
// and saves each PNG that the page posts back. The look comes from web/lineart.js (also used by the viewer).
import * as THREE from "three";
import { STLLoader } from "three/addons/loaders/STLLoader.js";
import { THEMES, addLights, partMesh, setLook, guideLine, setGuide, placeMatrix, spreadTags } from "lineart";

const status = (t) => { document.getElementById("status").textContent = t; };
const cfg = await (await fetch("/iso/jobs.json")).json();

const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(1);
renderer.setClearColor(0x000000, 0);
document.body.append(renderer.domElement);
const scene = new THREE.Scene();
const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, -10000, 10000);
addLights(scene, camera);

// ---- parts: one mesh per id (a mirrored part is its own id with the same file)
const loader = new STLLoader();
const geoms = new Map();
async function geometry(file) {
  if (!geoms.has(file)) geoms.set(file, loader.loadAsync("/" + file).then((g) => { g.computeVertexNormals(); return g; }));
  return geoms.get(file);
}
const parts = {};
const used = new Set(cfg.jobs.flatMap((j) => j.show));
let n = 0;
await Promise.all([...used].map(async (id) => {
  const def = cfg.parts[id];
  const { mesh, edges } = partMesh(await geometry(def.file));
  mesh.matrixAutoUpdate = false;
  mesh.visible = false;
  scene.add(mesh);
  const mirror = new THREE.Matrix4().makeScale(def.transform === "mirror_x" ? -1 : 1, 1, def.transform === "mirror_z" ? -1 : 1);
  mesh.updateMatrixWorld(true);
  mesh.matrix.copy(mirror);
  mesh.updateMatrixWorld(true);
  const home = new THREE.Box3().setFromObject(mesh);
  parts[id] = { def, mesh, edges, mirror, home };
  status(`loaded ${++n} / ${used.size}`);
}));

const guides = [];
function clearGuides() { for (const g of guides) scene.remove(g); guides.length = 0; }

function boxOf(ids) {
  const b = new THREE.Box3();
  for (const id of ids) if (parts[id]) { parts[id].mesh.updateMatrixWorld(true); b.expandByObject(parts[id].mesh); }
  return b;
}
function homeBoxOf(ids) {
  const b = new THREE.Box3();
  for (const id of ids) if (parts[id]) b.union(parts[id].home);
  return b;
}

function renderJob(job) {
  const theme = job.theme, T = THEMES[theme];
  const show = new Set(job.show), focus = new Set(job.focus || []), ghost = new Set(job.ghost || []);
  for (const [id, p] of Object.entries(parts)) {
    p.mesh.visible = show.has(id);
    if (!show.has(id)) continue;
    const off = new THREE.Vector3(...((job.offset || {})[id] || [0, 0, 0]));
    const deg = (job.turn || {})[id] || 0;
    const pivot = new THREE.Vector3(...((job.pivot || {})[id] || p.home.getCenter(new THREE.Vector3()).toArray()));
    p.mesh.matrix.copy(placeMatrix(pivot, deg, off)).multiply(p.mirror);
    p.mesh.updateMatrixWorld(true);
    setLook(p.mesh, p.edges, theme, { finish: p.def.finish, focus: focus.has(id), ghost: ghost.has(id),
                                      fill: job.color ? p.def.color : null });   // job.color: each part in its own color
    p.mesh.renderOrder = ghost.has(id) ? 1 : 0;
  }
  // One dashed guide and one tag for each name among the parts that move
  clearGuides();
  const byTag = new Map();
  for (const id of job.show) if (focus.has(id)) {
    const t = (job.tag || {})[id] || parts[id].def.tag;
    if (!byTag.has(t)) byTag.set(t, []);
    byTag.get(t).push(id);
  }
  for (const ids of byTag.values()) {
    const a = homeBoxOf(ids).getCenter(new THREE.Vector3()), b = boxOf(ids).getCenter(new THREE.Vector3());
    if (a.distanceTo(b) > 1) {
      const g = guideLine(theme);
      setGuide(g, a, b, theme);
      scene.add(g);
      guides.push(g);
    }
  }
  // Camera: orthographic, along dir, fit to the frame parts (their places now and at home)
  const W = job.width, H = job.height;
  renderer.setSize(W, H, false);
  const dir = new THREE.Vector3(...job.dir).normalize();
  const frameIds = job.frame || job.show;
  const box = boxOf(frameIds);
  if (job.frame_home !== false) box.union(homeBoxOf(frameIds.filter((id) => focus.has(id))));
  const c = box.getCenter(new THREE.Vector3());
  camera.position.copy(c).addScaledVector(dir, 2000);
  camera.up.set(0, 1, 0);
  camera.lookAt(c);
  camera.updateMatrixWorld(true);
  // Fit to the projected corners of every frame part (tighter than one box)
  const inv = camera.matrixWorldInverse;
  let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity;
  for (const id of frameIds) {
    const p = parts[id];
    if (!p || !p.mesh.visible) continue;
    const pos = p.mesh.geometry.attributes.position;
    const M = new THREE.Matrix4().multiplyMatrices(inv, p.mesh.matrixWorld);
    const v = new THREE.Vector3();
    const step = Math.max(1, Math.floor(pos.count / 4000));
    for (let i = 0; i < pos.count; i += step) {
      v.fromBufferAttribute(pos, i).applyMatrix4(M);
      if (v.x < x0) x0 = v.x; if (v.x > x1) x1 = v.x; if (v.y < y0) y0 = v.y; if (v.y > y1) y1 = v.y;
    }
  }
  const pad = job.pad ?? 0.05;
  const tagRoom = byTag.size ? (job.tag_room ?? 0.12) : 0;
  let w = x1 - x0, h = y1 - y0;
  const cx = (x0 + x1) / 2;
  let top = y1 + h * tagRoom, bot = y0;
  h = top - bot;
  const scale = Math.max(w / (W * (1 - 2 * pad)), h / (H * (1 - 2 * pad)));   // mm per pixel
  const cy = (top + bot) / 2;
  camera.left = cx - (W / 2) * scale; camera.right = cx + (W / 2) * scale;
  camera.top = cy + (H / 2) * scale; camera.bottom = cy - (H / 2) * scale;
  camera.updateProjectionMatrix();
  renderer.render(scene, camera);

  // Composite: the render, then the tags
  const out = document.createElement("canvas");
  out.width = W; out.height = H;
  const g = out.getContext("2d");
  g.drawImage(renderer.domElement, 0, 0);
  if (job.tags !== false && byTag.size) {
    const s = job.tag_scale || 1;
    const fs = 11.5 * s, px = 8 * s, py = 3 * s;
    g.font = `600 ${fs}px "JetBrains Mono", "JetBrainsMono Nerd Font", "Noto Sans Mono", monospace`;
    const tags = [];
    for (const [name, ids] of byTag) {
      const b = boxOf(ids);
      const p = b.getCenter(new THREE.Vector3());
      p.y = b.max.y;
      p.project(camera);
      const tw = g.measureText(name).width + 2 * px, th = fs * 1.2 + 2 * py;
      tags.push({ name, x: ((p.x + 1) / 2) * W - tw / 2, y: ((1 - p.y) / 2) * H - th * 1.3, w: tw, h: th });
    }
    spreadTags(tags, 3 * s);
    for (const t of tags) {
      t.x = Math.min(Math.max(t.x, 2), W - t.w - 2);
      t.y = Math.max(t.y, 2);
      g.beginPath();
      g.roundRect(t.x, t.y, t.w, t.h, t.h / 2);
      g.fillStyle = T.tagBg;
      g.fill();
      g.lineWidth = Math.max(1, s);
      g.strokeStyle = T.accent;
      g.stroke();
      g.fillStyle = T.accent;
      g.textBaseline = "middle";
      g.fillText(t.name, t.x + px, t.y + t.h / 2 + 0.5 * s);
    }
  }
  return new Promise((res) => out.toBlob(res, "image/png"));
}

await document.fonts.load(`600 12px "JetBrains Mono"`).catch(() => {});
let k = 0;
for (const job of cfg.jobs) {
  status(`render ${++k} / ${cfg.jobs.length}: ${job.name}`);
  const blob = await renderJob(job);
  await fetch("/iso/save/" + job.name + ".png", { method: "POST", body: blob });
}
await fetch("/iso/done", { method: "POST", body: "ok" });
status("done");
