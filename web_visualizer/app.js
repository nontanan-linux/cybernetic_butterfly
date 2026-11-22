/**
 * Electronic Butterfly — Interactive 3D CAD Inspector & Kinematics Simulator
 * Powered by Three.js
 *
 * Coordinate Convention: ISO Aerospace / Robotics Standard
 * - X: Longitudinal axis (+X = Forward / Head / Antennae, -X = Aft / Abdomen)
 * - Y: Lateral axis (+Y = Port / Left Wing, -Y = Starboard / Right Wing)
 * - Z: Vertical axis (+Z = Upward / Dorsal, -Z = Downward / Ventral / Legs)
 */

// Global 3D State
let scene, camera, renderer, controls;
let activeCADMesh = null;
let activeCADGroup = null;
let currentSTLFile = "butterfly_full_assembly.stl";
let isWireframe = false;
let isAutoRotate = false;
let isSimulating = false;

// Geometry Cache for CAD STL Models
const stlCache = {};

// Kinematics & Simulation State (Matches config/kinematics.param.yaml)
let simAssemblyGroup = null;
let simLeftWingGroup = null;
let simRightWingGroup = null;
let currentMode = "flutter";
let currentPalette = "biolum";
let flapSpeed = 1.2;      // Hz
let flapAmp = 25;         // Degrees
let centerAngle = 45;     // Degrees (45° = Horizontal neutral CAD posture)
let isSurging = false;

// LED Meshes
let ledMeshesLeft = [], ledMeshesRight = [];
let ambientLight, dirLight;

// Model Catalog Cache
let modelCatalog = {};

// Initialize on DOM Ready
document.addEventListener("DOMContentLoaded", () => {
  initViewer();
  fetchModelCatalog();
  setupUIEvents();
});

function initViewer() {
  const container = document.getElementById("canvas-container");

  // Scene setup
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x080b12);
  scene.fog = new THREE.FogExp2(0x080b12, 0.002);

  // Camera setup (ISO Coordinate System: Z is UP)
  camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 2500);
  camera.up.set(0, 0, 1);
  camera.position.set(160, -180, 110);

  // WebGL Renderer
  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  container.appendChild(renderer.domElement);

  // Orbit Controls (Auto-Rotate is OFF by default)
  controls = new THREE.OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  controls.autoRotate = false;
  controls.autoRotateSpeed = 1.0;
  controls.target.set(0, 0, -5);

  // Setup Lighting
  setupLighting();

  // Horizontal Ground Grid in X-Y Plane at butterfly foot level (Z = -38.3)
  const gridHelper = new THREE.GridHelper(600, 60, 0x1e293b, 0x0f172a);
  gridHelper.rotation.x = Math.PI / 2;
  gridHelper.position.set(0, 0, -38.3);
  scene.add(gridHelper);

  // 3D Coordinate Tripod (AxesHelper in ISO convention)
  const axesHelper = new THREE.AxesHelper(60);
  scene.add(axesHelper);

  // Groups for Static CAD Inspection and Articulated Simulation
  activeCADGroup = new THREE.Group();
  scene.add(activeCADGroup);

  simAssemblyGroup = new THREE.Group();
  simAssemblyGroup.visible = false;
  scene.add(simAssemblyGroup);

  // Load Initial Model
  loadCADModel(currentSTLFile);

  window.addEventListener("resize", onWindowResize);
  animate(0);
}

function setupLighting() {
  ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
  scene.add(ambientLight);

  dirLight = new THREE.DirectionalLight(0xffffff, 1.4);
  dirLight.position.set(120, -140, 180);
  dirLight.castShadow = true;
  dirLight.shadow.mapSize.width = 1024;
  dirLight.shadow.mapSize.height = 1024;
  scene.add(dirLight);

  const fillLight = new THREE.DirectionalLight(0x38bdf8, 0.6);
  fillLight.position.set(-100, 120, 80);
  scene.add(fillLight);

  const bottomLight = new THREE.DirectionalLight(0x10b981, 0.25);
  bottomLight.position.set(0, 0, -120);
  scene.add(bottomLight);
}

async function fetchModelCatalog() {
  try {
    const res = await fetch("/api/models");
    if (res.ok) {
      const data = await res.json();
      data.forEach(item => {
        modelCatalog[item.file] = item;
      });
      updateSpecsCard(currentSTLFile);
    }
  } catch (err) {
    console.warn("Could not fetch /api/models, using fallback metadata:", err);
  }
}

function loadSTLGeometry(filename) {
  return new Promise((resolve, reject) => {
    if (stlCache[filename]) {
      resolve(stlCache[filename]);
      return;
    }
    const loader = new THREE.STLLoader();
    loader.load(
      `/models/${filename}`,
      (geom) => {
        geom.computeVertexNormals();
        stlCache[filename] = geom;
        resolve(geom);
      },
      undefined,
      (err) => reject(err)
    );
  });
}

function applyWireframeToGroup(group, wireframeState) {
  if (!group) return;
  group.traverse((child) => {
    if (child.isMesh && child.material) {
      child.material.wireframe = wireframeState;
    }
  });
}

// Load CAD Model (.STL) in Static Inspection Mode
async function loadCADModel(stlFileName) {
  currentSTLFile = stlFileName;

  while (activeCADGroup.children.length > 0) {
    activeCADGroup.remove(activeCADGroup.children[0]);
  }

  if (!isSimulating) {
    simAssemblyGroup.visible = false;
    activeCADGroup.visible = true;
  }

  updateSpecsCard(stlFileName);
  document.getElementById("spec-triangles").innerText = "Loading STL...";

  try {
    if (stlFileName === "butterfly_full_assembly.stl") {
      // Load 4 Generated Parts + 2 External Read-Only Hardware Models
      const [bodyGeom, servoGeom, hornGeom, leftWingGeom, rightWingGeom, legsGeom] = await Promise.all([
        loadSTLGeometry("body.stl"),
        loadSTLGeometry("mg90s_servo.stl"),
        loadSTLGeometry("mg90s_servo_horn.stl"),
        loadSTLGeometry("left_wing.stl"),
        loadSTLGeometry("right_wing.stl"),
        loadSTLGeometry("butterfly_legs.stl")
      ]);

      const makeMat = (hex, metal = 0.45, rough = 0.38, doubleSide = false) =>
        new THREE.MeshStandardMaterial({
          color: hex,
          metalness: metal,
          roughness: rough,
          wireframe: isWireframe,
          side: doubleSide ? THREE.DoubleSide : THREE.FrontSide
        });

      const bodyMesh = new THREE.Mesh(bodyGeom, makeMat(0x475569, 0.5, 0.4));

      const servoL = new THREE.Mesh(servoGeom, makeMat(0x1d4ed8, 0.4, 0.35));
      servoL.rotation.set(0, Math.PI / 2, Math.PI / 2, "XYZ");
      servoL.position.set(8.0, 9.0, 2.0);

      const servoR = new THREE.Mesh(servoGeom, makeMat(0x1d4ed8, 0.4, 0.35));
      servoR.rotation.set(0, Math.PI / 2, Math.PI / 2, "XYZ");
      servoR.position.set(8.0, -9.0, 2.0);

      const hornL = new THREE.Mesh(hornGeom, makeMat(0xf8fafc, 0.2, 0.4));
      hornL.rotation.set(0, Math.PI / 2, Math.PI / 2, "XYZ");
      hornL.position.set(8.0, 9.0, 2.0);

      const hornR = new THREE.Mesh(hornGeom, makeMat(0xf8fafc, 0.2, 0.4));
      hornR.rotation.set(0, Math.PI / 2, -Math.PI / 2, "XYZ");
      hornR.position.set(8.0, -9.0, 2.0);

      const wingL = new THREE.Mesh(leftWingGeom, makeMat(0x10b981, 0.3, 0.35, true));
      const wingR = new THREE.Mesh(rightWingGeom, makeMat(0x10b981, 0.3, 0.35, true));

      const legsMesh = new THREE.Mesh(legsGeom, makeMat(0x334155, 0.5, 0.5));

      const allParts = [bodyMesh, servoL, servoR, hornL, hornR, wingL, wingR, legsMesh];
      let totalTris = 0;
      allParts.forEach((m) => {
        m.castShadow = true;
        m.receiveShadow = true;
        activeCADGroup.add(m);
        totalTris += m.geometry.attributes.position.count / 3;
      });

      activeCADMesh = activeCADGroup;
      const bb = new THREE.Box3().setFromObject(activeCADGroup);
      const size = bb.getSize(new THREE.Vector3());
      document.getElementById("spec-dim").innerText =
        `X:${size.x.toFixed(1)} × Y:${size.y.toFixed(1)} × Z:${size.z.toFixed(1)} mm`;
      document.getElementById("spec-triangles").innerText = `${totalTris.toLocaleString()} Triangles (8 Solids)`;

      fitCameraToObject(activeCADGroup);
    } else {
      const geometry = await loadSTLGeometry(stlFileName);
      geometry.computeBoundingBox();
      const bb = geometry.boundingBox;
      const sizeX = (bb.max.x - bb.min.x).toFixed(1);
      const sizeY = (bb.max.y - bb.min.y).toFixed(1);
      const sizeZ = (bb.max.z - bb.min.z).toFixed(1);
      document.getElementById("spec-dim").innerText = `X:${sizeX} × Y:${sizeY} × Z:${sizeZ} mm`;

      const triCount = geometry.attributes.position.count / 3;
      document.getElementById("spec-triangles").innerText = `${triCount.toLocaleString()} Triangles`;

      const meta = modelCatalog[stlFileName] || {};
      const matColor = meta.color ? new THREE.Color(meta.color) : new THREE.Color(0x38bdf8);

      const material = new THREE.MeshStandardMaterial({
        color: matColor,
        metalness: 0.45,
        roughness: 0.35,
        wireframe: isWireframe
      });

      activeCADMesh = new THREE.Mesh(geometry, material);
      activeCADMesh.castShadow = true;
      activeCADMesh.receiveShadow = true;
      activeCADGroup.add(activeCADMesh);

      fitCameraToObject(activeCADMesh);
    }
  } catch (err) {
    console.error("Error loading STL model:", err);
    document.getElementById("spec-triangles").innerText = "Load Failed";
  }
}

// Update Specs Card on left HUD
function updateSpecsCard(stlFileName) {
  const meta = modelCatalog[stlFileName] || {
    name: stlFileName.replace(".stl", "").replace(/_/g, " ").toUpperCase(),
    file: stlFileName,
    step: stlFileName === "butterfly_full_assembly.stl" ? "butterfly_full_assembly.step" : null,
    type: "CAD MODEL",
    features: "Precision 3D CAD model."
  };

  document.getElementById("spec-name").innerText = meta.name;
  document.getElementById("spec-filename").innerText = `${meta.file} ${meta.size_stl ? "(" + meta.size_stl + ")" : ""}`;
  document.getElementById("spec-features").innerText = meta.features;
  document.getElementById("spec-type").innerText = (meta.type || "CAD INSPECTION").toUpperCase();

  const stepContainer = document.getElementById("spec-step-container");
  if (stepContainer) {
    if (meta.step) {
      stepContainer.innerHTML = `<a id="spec-download-step" href="/models/${meta.step}" download>Download .STEP ${meta.size_step ? "(" + meta.size_step + ")" : ""}</a>`;
    } else {
      stepContainer.innerHTML = `<span style="color:#34d399;">.STL Only (3D Print Part)</span>`;
    }
  }
}

function fitCameraToObject(object, offset = 1.4) {
  const boundingBox = new THREE.Box3();
  boundingBox.setFromObject(object);

  const center = boundingBox.getCenter(new THREE.Vector3());
  const size = boundingBox.getSize(new THREE.Vector3());

  const maxDim = Math.max(size.x, size.y, size.z);
  const fov = camera.fov * (Math.PI / 180);
  let dist = Math.abs((maxDim / 2) / Math.tan(fov / 2)) * offset;
  dist = Math.max(dist, 50);

  camera.position.set(center.x + dist * 0.9, center.y - dist * 1.1, center.z + dist * 0.65);
  controls.target.copy(center);
  controls.update();
}

async function toggleSimulation() {
  isSimulating = !isSimulating;
  const btn = document.getElementById("btn-toggle-sim");
  const panel = document.getElementById("kinematics-panel");
  const indicator = document.getElementById("sim-indicator");
  const statusText = document.getElementById("sim-status-text");

  if (isSimulating) {
    btn.innerText = "⏹ Stop Simulation";
    btn.classList.add("btn-sim-stop");
    panel.classList.remove("panel-collapsed");
    indicator.querySelector(".dot").className = "dot active";
    statusText.innerText = "Active Kinematic Simulation (Real CAD Model Flapping)";

    activeCADGroup.visible = false;
    simAssemblyGroup.visible = true;

    if (simAssemblyGroup.children.length === 0) {
      statusText.innerText = "Loading Real CAD STL Parts for Simulation...";
      await buildArticulatedButterfly();
      statusText.innerText = "Active Kinematic Simulation (Real CAD Model Flapping)";
    }
    applyWireframeToGroup(simAssemblyGroup, isWireframe);
    fitCameraToObject(simAssemblyGroup);
  } else {
    btn.innerText = "▶ Start Flapping Simulation";
    btn.classList.remove("btn-sim-stop");
    panel.classList.add("panel-collapsed");
    indicator.querySelector(".dot").className = "dot idle";
    statusText.innerText = "Static CAD Inspection Mode (Simulation Idle)";

    simAssemblyGroup.visible = false;
    activeCADGroup.visible = true;
    if (activeCADMesh) {
      fitCameraToObject(activeCADMesh);
    }
  }
}

// Build Articulated Butterfly USING THE EXACT SAME REAL CAD STL MODELS
async function buildArticulatedButterfly() {
  while (simAssemblyGroup.children.length > 0) {
    simAssemblyGroup.remove(simAssemblyGroup.children[0]);
  }

  const root = new THREE.Group();
  simAssemblyGroup.add(root);

  const bodyMat = new THREE.MeshStandardMaterial({ color: 0x475569, metalness: 0.5, roughness: 0.4, wireframe: isWireframe });
  const servoMat = new THREE.MeshStandardMaterial({ color: 0x1d4ed8, metalness: 0.4, roughness: 0.35, wireframe: isWireframe });
  const hornMat = new THREE.MeshStandardMaterial({ color: 0xf8fafc, metalness: 0.2, roughness: 0.4, wireframe: isWireframe });
  const wingMat = new THREE.MeshStandardMaterial({
    color: 0x10b981,
    metalness: 0.3,
    roughness: 0.35,
    side: THREE.DoubleSide,
    wireframe: isWireframe
  });
  const legsMat = new THREE.MeshStandardMaterial({ color: 0x334155, metalness: 0.5, roughness: 0.5, wireframe: isWireframe });

  const [bodyGeom, servoGeom, hornGeom, leftWingGeom, rightWingGeom, legsGeom] = await Promise.all([
    loadSTLGeometry("body.stl"),
    loadSTLGeometry("mg90s_servo.stl"),
    loadSTLGeometry("mg90s_servo_horn.stl"),
    loadSTLGeometry("left_wing.stl"),
    loadSTLGeometry("right_wing.stl"),
    loadSTLGeometry("butterfly_legs.stl")
  ]);

  // 1. Central Body Chassis (Head + Clubbed Antennae + Thorax + 14500 Battery Abdomen)
  const bodyMesh = new THREE.Mesh(bodyGeom, bodyMat);
  bodyMesh.castShadow = true;
  bodyMesh.receiveShadow = true;
  root.add(bodyMesh);

  // 2. External MG90S Servos installed inside thorax bays
  const servoLeftMesh = new THREE.Mesh(servoGeom, servoMat);
  servoLeftMesh.rotation.set(0, Math.PI / 2, Math.PI / 2, "XYZ");
  servoLeftMesh.position.set(8.0, 9.0, 2.0);
  root.add(servoLeftMesh);

  const servoRightMesh = new THREE.Mesh(servoGeom, servoMat);
  servoRightMesh.rotation.set(0, Math.PI / 2, Math.PI / 2, "XYZ");
  servoRightMesh.position.set(8.0, -9.0, 2.0);
  root.add(servoRightMesh);

  // 3. Tucked 6 Butterfly Legs (butterfly_legs.stl)
  const legsMesh = new THREE.Mesh(legsGeom, legsMat);
  root.add(legsMesh);

  // 4. Left Articulated Wing Pivot Group (Hinged at servo shaft X=8.0, Y=9.0, Z=2.0)
  simLeftWingGroup = new THREE.Group();
  simLeftWingGroup.position.set(8.0, 9.0, 2.0);
  root.add(simLeftWingGroup);

  const hornLeftMesh = new THREE.Mesh(hornGeom, hornMat);
  hornLeftMesh.rotation.set(0, Math.PI / 2, Math.PI / 2, "XYZ");
  hornLeftMesh.position.set(0, 0, 0);
  simLeftWingGroup.add(hornLeftMesh);

  const leftWingMesh = new THREE.Mesh(leftWingGeom, wingMat);
  leftWingMesh.position.set(-8.0, -9.0, -2.0);
  simLeftWingGroup.add(leftWingMesh);

  // 5. Right Articulated Wing Pivot Group (Hinged at servo shaft X=8.0, Y=-9.0, Z=2.0)
  simRightWingGroup = new THREE.Group();
  simRightWingGroup.position.set(8.0, -9.0, 2.0);
  root.add(simRightWingGroup);

  const hornRightMesh = new THREE.Mesh(hornGeom, hornMat);
  hornRightMesh.rotation.set(0, Math.PI / 2, -Math.PI / 2, "XYZ");
  hornRightMesh.position.set(0, 0, 0);
  simRightWingGroup.add(hornRightMesh);

  const rightWingMesh = new THREE.Mesh(rightWingGeom, wingMat);
  rightWingMesh.position.set(-8.0, 9.0, -2.0);
  simRightWingGroup.add(rightWingMesh);

  // 6. Addressable LED Pixels seated inside the 4 LED vein-node pockets on each 2x-larger, 1.2mm-thin wing blade
  ledMeshesLeft = [];
  ledMeshesRight = [];
  const ledCoords = [
    [54.0, 92.0, 2.40],
    [86.0, 175.0, 2.40],
    [36.0, 135.0, 2.40],
    [-52.0, 105.0, 2.40]
  ];

  ledCoords.forEach(([wx, wy, wz]) => {
    const ledGeo = new THREE.CylinderGeometry(3.5, 3.5, 0.9, 16);
    ledGeo.rotateX(Math.PI / 2);

    const ledMatL = new THREE.MeshBasicMaterial({ color: 0x38bdf8 });
    const ledL = new THREE.Mesh(ledGeo, ledMatL);
    ledL.position.set(wx - 8.0, wy - 9.0, wz - 2.0);
    simLeftWingGroup.add(ledL);
    ledMeshesLeft.push(ledL);

    const ledMatR = new THREE.MeshBasicMaterial({ color: 0x38bdf8 });
    const ledR = new THREE.Mesh(ledGeo, ledMatR);
    ledR.position.set(wx - 8.0, -wy - (-9.0), wz - 2.0);
    simRightWingGroup.add(ledR);
    ledMeshesRight.push(ledR);
  });
}

function setupUIEvents() {
  const select = document.getElementById("model-select");
  select.addEventListener("change", (e) => {
    const chosen = e.target.value;
    if (isSimulating) {
      toggleSimulation();
    }
    loadCADModel(chosen);
  });

  document.getElementById("btn-toggle-sim").addEventListener("click", () => {
    toggleSimulation();
  });

  const btnWireframe = document.getElementById("btn-wireframe");
  btnWireframe.addEventListener("click", () => {
    isWireframe = !isWireframe;
    btnWireframe.classList.toggle("active", isWireframe);
    btnWireframe.innerText = isWireframe ? "📐 Solid" : "📐 Wireframe";
    applyWireframeToGroup(activeCADGroup, isWireframe);
    applyWireframeToGroup(simAssemblyGroup, isWireframe);
  });

  const btnRotate = document.getElementById("btn-autorotate");
  btnRotate.addEventListener("click", () => {
    isAutoRotate = !isAutoRotate;
    controls.autoRotate = isAutoRotate;
    btnRotate.classList.toggle("active", isAutoRotate);
    btnRotate.innerText = isAutoRotate ? "🔄 Spin: ON" : "🔄 Spin: OFF";
  });

  document.getElementById("btn-reset-cam").addEventListener("click", () => {
    if (isSimulating && simAssemblyGroup) {
      fitCameraToObject(simAssemblyGroup);
    } else if (activeCADMesh) {
      fitCameraToObject(activeCADMesh);
    } else {
      camera.position.set(160, -180, 110);
      controls.target.set(0, 0, -5);
      controls.update();
    }
  });

  const panelToggle = document.getElementById("panel-toggle");
  panelToggle.addEventListener("click", () => {
    document.getElementById("kinematics-panel").classList.toggle("panel-collapsed");
  });

  document.querySelectorAll(".mode-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
      document.querySelectorAll(".mode-btn").forEach(b => b.classList.remove("active"));
      e.target.classList.add("active");
      const mode = e.target.dataset.mode;
      if (mode) applyKinematicMode(mode);
    });
  });

  const btnTouch = document.getElementById("btn-touch");
  if (btnTouch) {
    btnTouch.addEventListener("click", triggerCapacitiveTouch);
  }

  document.querySelectorAll(".pal-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
      document.querySelectorAll(".pal-btn").forEach(b => b.classList.remove("active"));
      e.target.classList.add("active");
      currentPalette = e.target.dataset.pal;
    });
  });

  const sliderSpeed = document.getElementById("slider-speed");
  const valSpeed = document.getElementById("val-speed");
  sliderSpeed.addEventListener("input", (e) => {
    flapSpeed = parseFloat(e.target.value);
    valSpeed.innerText = `${flapSpeed.toFixed(1)} Hz`;
  });

  const sliderAmp = document.getElementById("slider-amp");
  const valAmp = document.getElementById("val-amp");
  sliderAmp.addEventListener("input", (e) => {
    flapAmp = parseFloat(e.target.value);
    valAmp.innerText = `${flapAmp.toFixed(0)}°`;
  });

  const sliderLight = document.getElementById("slider-light");
  const valLight = document.getElementById("val-light");
  sliderLight.addEventListener("input", (e) => {
    const val = parseInt(e.target.value);
    ambientLight.intensity = (val / 100) * 0.9;
    dirLight.intensity = (val / 100) * 1.5;
    valLight.innerText = val < 30 ? "Night / Cyber" : val < 70 ? "Dusk" : "Daylight";
  });
}

function applyKinematicMode(mode) {
  currentMode = mode;
  switch (mode) {
    case "sleep":
      flapSpeed = 0.0;
      flapAmp = 0;
      centerAngle = 80;
      break;
    case "breathe":
      flapSpeed = 0.4;
      flapAmp = 8;
      centerAngle = 60;
      break;
    case "flutter":
      flapSpeed = 1.2;
      flapAmp = 25;
      centerAngle = 45;
      break;
    case "flight":
      flapSpeed = 2.2;
      flapAmp = 30;
      centerAngle = 45;
      break;
    case "glide":
      flapSpeed = 0.2;
      flapAmp = 3;
      centerAngle = 20;
      break;
  }
  document.getElementById("slider-speed").value = flapSpeed;
  document.getElementById("val-speed").innerText = `${flapSpeed.toFixed(1)} Hz`;
  document.getElementById("slider-amp").value = flapAmp;
  document.getElementById("val-amp").innerText = `${flapAmp.toFixed(0)}°`;
}

function triggerCapacitiveTouch() {
  isSurging = true;
  const teleTouch = document.getElementById("tele-touch");
  teleTouch.innerText = "TRIGGERED! (+450 delta)";
  teleTouch.style.color = "#f59e0b";

  setTimeout(() => {
    isSurging = false;
    teleTouch.innerText = "Idle (0 delta)";
    teleTouch.style.color = "#34d399";
  }, 2500);
}

function animate(timestamp) {
  requestAnimationFrame(animate);

  const t = timestamp * 0.001;
  controls.update();

  if (isSimulating && simLeftWingGroup && simRightWingGroup) {
    let activeSpeed = flapSpeed;
    let activeAmp = flapAmp;
    let activeCenter = centerAngle;

    if (isSurging) {
      activeSpeed = 3.5;
      activeAmp = 32;
      activeCenter = 45;
    }

    let currentAngleDeg = activeCenter;
    let angVel = 0.0;

    if (activeSpeed > 0.0 && activeAmp > 0.0) {
      const omega = 2.0 * Math.PI * activeSpeed;
      const h1 = Math.sin(omega * t);
      const h2 = 0.22 * Math.sin(2.0 * omega * t + 0.35);
      const stroke = h1 + h2;
      currentAngleDeg = activeCenter + activeAmp * stroke;
      angVel = activeAmp * (omega * Math.cos(omega * t) + 2.0 * omega * 0.22 * Math.cos(2.0 * omega * t + 0.35));
    }

    currentAngleDeg = Math.max(15.0, Math.min(85.0, currentAngleDeg));

    const flapRad = ((currentAngleDeg - 45.0) * Math.PI) / 180.0;
    simLeftWingGroup.rotation.x = flapRad;
    simRightWingGroup.rotation.x = -flapRad;

    document.getElementById("tele-angle").innerText = `${currentAngleDeg.toFixed(1)}°`;
    const phaseText =
      activeSpeed <= 0.0 || activeAmp <= 0.0
        ? "Folded (Rest)"
        : angVel >= 0.0
        ? "▲ Upstroke"
        : "▼ Downstroke";
    document.getElementById("tele-phase").innerText = phaseText;

    updateLEDColors(t);
  }

  renderer.render(scene, camera);
}

function updateLEDColors(t) {
  const palettes = {
    biolum: [0x00f0ff, 0x00a8ff, 0x0044ff, 0x00e5ff],
    morpho: [0x0077ff, 0x00d4ff, 0x0022cc, 0x38bdf8],
    monarch: [0xff4500, 0xff8c00, 0xffa500, 0xff2200],
    aurora: [0x10b981, 0x06b6d4, 0x8b5cf6, 0xec4899]
  };

  const colors = palettes[currentPalette] || palettes.biolum;

  for (let i = 0; i < ledMeshesLeft.length; i++) {
    const phaseOffset = i * 0.5;
    const pulse = 0.5 + 0.5 * Math.sin(t * 3.0 + phaseOffset);
    const col = new THREE.Color(colors[i % colors.length]).multiplyScalar(pulse);

    if (ledMeshesLeft[i]) ledMeshesLeft[i].material.color.copy(col);
    if (ledMeshesRight[i]) ledMeshesRight[i].material.color.copy(col);
  }
}

function onWindowResize() {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
}
