/**
 * Electronic Butterfly — Interactive 3D CAD Inspector & Kinematics Simulator
 * Powered by Three.js
 *
 * Coordinate Convention: ISO Aerospace / Robotics Standard
 * - X: Longitudinal axis (+X = Forward / Head / Leading edge, -X = Aft / Tail)
 * - Y: Lateral axis (+Y = Port / Left Wing, -Y = Starboard / Right Wing)
 * - Z: Vertical axis (+Z = Upward / Dorsal, -Z = Downward / Ventral / Stand)
 */

// Global 3D State
let scene, camera, renderer, controls;
let activeCADMesh = null;
let activeCADGroup = null;
let currentSTLFile = "butterfly_full_assembly.stl";
let isWireframe = false;
let isAutoRotate = false;
let isSimulating = false;

// Geometry Cache for Real CAD STL Models
const stlCache = {};

// Kinematics & Simulation State
let simAssemblyGroup = null;
let simLeftWingGroup = null;
let simRightWingGroup = null;
let currentMode = "flutter";
let currentPalette = "biolum";
let flapSpeed = 1.5;      // Hz
let flapAmp = 28;         // Degrees
let centerAngle = 45;     // Degrees
let isSurging = false;
let surgeStartTime = 0;
let lastTouchVal = 0;

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
  camera.up.set(0, 0, 1); // Z-axis is VERTICAL UP
  camera.position.set(160, -180, 110); // Isometric view: from front-right-above

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
  controls.target.set(0, 0, -10);

  // Setup Lighting
  setupLighting();

  // Horizontal Ground Grid in X-Y Plane at base of stand (Z = -92)
  const gridHelper = new THREE.GridHelper(300, 30, 0x1e293b, 0x0f172a);
  gridHelper.rotation.x = Math.PI / 2; // Lie in the horizontal X-Y plane
  gridHelper.position.set(0, 0, -92);
  scene.add(gridHelper);

  // 3D Coordinate Tripod (AxesHelper in ISO convention)
  // Red = X (Longitudinal), Green = Y (Lateral), Blue = Z (Vertical Up)
  const axesHelper = new THREE.AxesHelper(60);
  scene.add(axesHelper);

  // Groups for Static CAD Inspection and Articulated Simulation
  activeCADGroup = new THREE.Group();
  scene.add(activeCADGroup);

  simAssemblyGroup = new THREE.Group();
  simAssemblyGroup.visible = false;
  scene.add(simAssemblyGroup);

  // Load Initial Model (Default: Static CAD Inspection)
  loadCADModel(currentSTLFile);

  // Window resize handler
  window.addEventListener("resize", onWindowResize);

  // Animation Loop
  animate(0);
}

function setupLighting() {
  ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
  scene.add(ambientLight);

  // Key directional light from upper front
  dirLight = new THREE.DirectionalLight(0xffffff, 1.4);
  dirLight.position.set(120, -140, 180);
  dirLight.castShadow = true;
  dirLight.shadow.mapSize.width = 1024;
  dirLight.shadow.mapSize.height = 1024;
  scene.add(dirLight);

  // Fill directional light from upper rear
  const fillLight = new THREE.DirectionalLight(0x38bdf8, 0.6);
  fillLight.position.set(-100, 120, 80);
  scene.add(fillLight);

  // Soft bottom fill
  const bottomLight = new THREE.DirectionalLight(0x10b981, 0.25);
  bottomLight.position.set(0, 0, -120);
  scene.add(bottomLight);
}

// Fetch Model Metadata Catalog from Server API
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

// Helper to Load and Cache Real STL Geometry
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

// Load CAD Model (.STL) in Static Inspection Mode
function loadCADModel(stlFileName) {
  currentSTLFile = stlFileName;

  // Clear previous static CAD meshes
  while (activeCADGroup.children.length > 0) {
    const obj = activeCADGroup.children[0];
    if (obj.geometry && !stlCache[stlFileName]) obj.geometry.dispose();
    if (obj.material) obj.material.dispose();
    activeCADGroup.remove(obj);
  }

  // Ensure simulation group is hidden
  if (!isSimulating) {
    simAssemblyGroup.visible = false;
    activeCADGroup.visible = true;
  }

  // Update UI Stats
  updateSpecsCard(stlFileName);
  document.getElementById("spec-triangles").innerText = "Loading STL...";

  loadSTLGeometry(stlFileName).then(geometry => {
    // Compute dimensions in ISO coordinates
    geometry.computeBoundingBox();
    const bb = geometry.boundingBox;
    const sizeX = (bb.max.x - bb.min.x).toFixed(1);
    const sizeY = (bb.max.y - bb.min.y).toFixed(1);
    const sizeZ = (bb.max.z - bb.min.z).toFixed(1);
    document.getElementById("spec-dim").innerText = `X:${sizeX} × Y:${sizeY} × Z:${sizeZ} mm`;

    const triCount = geometry.attributes.position.count / 3;
    document.getElementById("spec-triangles").innerText = `${triCount.toLocaleString()} Triangles`;

    // PBR Material matching engineering color
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

    // Frame camera smoothly in ISO coordinate space
    fitCameraToObject(activeCADMesh);
  }).catch(err => {
    console.error("Error loading STL model:", err);
    document.getElementById("spec-triangles").innerText = "Load Failed";
  });
}

// Update Specs Card on left HUD
function updateSpecsCard(stlFileName) {
  const meta = modelCatalog[stlFileName] || {
    name: stlFileName.replace(".stl", "").replace(/_/g, " ").toUpperCase(),
    file: stlFileName,
    step: stlFileName.replace(".stl", ".step"),
    type: "CAD Model",
    features: "Precision 3D CAD model generated via build123d parametric script."
  };

  document.getElementById("spec-name").innerText = meta.name;
  document.getElementById("spec-filename").innerText = `${meta.file} ${meta.size_stl ? "(" + meta.size_stl + ")" : ""}`;
  document.getElementById("spec-features").innerText = meta.features;
  document.getElementById("spec-type").innerText = (meta.type || "CAD INSPECTION").toUpperCase();

  const dlStep = document.getElementById("spec-download-step");
  if (dlStep) {
    dlStep.href = `/models/${meta.step || meta.file.replace(".stl", ".step")}`;
    dlStep.innerText = `Download .STEP ${meta.size_step ? "(" + meta.size_step + ")" : ""}`;
  }
}

// Adjust camera distance to frame any sized object in ISO Z-Up Space
function fitCameraToObject(object, offset = 1.4) {
  const boundingBox = new THREE.Box3();
  boundingBox.setFromObject(object);

  const center = boundingBox.getCenter(new THREE.Vector3());
  const size = boundingBox.getSize(new THREE.Vector3());

  const maxDim = Math.max(size.x, size.y, size.z);
  const fov = camera.fov * (Math.PI / 180);
  let dist = Math.abs((maxDim / 2) / Math.tan(fov / 2)) * offset;
  dist = Math.max(dist, 50);

  // Position camera at front-right isometric angle in ISO coordinate space (Z is UP)
  camera.position.set(center.x + dist * 0.9, center.y - dist * 1.1, center.z + dist * 0.65);
  controls.target.copy(center);
  controls.update();
}

// Toggle Simulation Mode
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

    // Switch to Real CAD Articulated Assembly
    activeCADGroup.visible = false;
    simAssemblyGroup.visible = true;

    if (simAssemblyGroup.children.length === 0) {
      statusText.innerText = "Loading Real CAD STL Parts for Simulation...";
      await buildArticulatedButterfly();
      statusText.innerText = "Active Kinematic Simulation (Real CAD Model Flapping)";
    }
    fitCameraToObject(simAssemblyGroup);
  } else {
    btn.innerText = "▶ Start Flapping Simulation";
    btn.classList.remove("btn-sim-stop");
    panel.classList.add("panel-collapsed");
    indicator.querySelector(".dot").className = "dot idle";
    statusText.innerText = "Static CAD Inspection Mode (Simulation Idle)";

    // Switch back to Static CAD Model
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

  // Real CAD PBR Materials
  const bodyMat = new THREE.MeshStandardMaterial({ color: 0x475569, metalness: 0.5, roughness: 0.4 });
  const servoMat = new THREE.MeshStandardMaterial({ color: 0x1d4ed8, metalness: 0.4, roughness: 0.35 });
  const hornMat = new THREE.MeshStandardMaterial({ color: 0xf8fafc, metalness: 0.2, roughness: 0.4 });
  const wingMat = new THREE.MeshStandardMaterial({
    color: 0x10b981,
    metalness: 0.3,
    roughness: 0.35,
    side: THREE.DoubleSide
  });
  const standMat = new THREE.MeshStandardMaterial({ color: 0x334155, metalness: 0.5, roughness: 0.5 });

  // Load the EXACT SAME real CAD STL geometries
  const [bodyGeom, servoGeom, hornGeom, leftWingGeom, rightWingGeom, standGeom, lidGeom] = await Promise.all([
    loadSTLGeometry("body.stl"),
    loadSTLGeometry("mg90s_servo.stl"),
    loadSTLGeometry("mg90s_servo_horn.stl"),
    loadSTLGeometry("left_wing.stl"),
    loadSTLGeometry("right_wing.stl"),
    loadSTLGeometry("base_stand.stl"),
    loadSTLGeometry("base_stand_lid.stl")
  ]);

  // 1. Central Body Chassis (Real body.stl)
  const bodyMesh = new THREE.Mesh(bodyGeom, bodyMat);
  bodyMesh.castShadow = true;
  bodyMesh.receiveShadow = true;
  root.add(bodyMesh);

  // 2. Real MG90S Servos installed inside the body pockets
  // Left Servo in left thorax bay
  const servoLeftMesh = new THREE.Mesh(servoGeom, servoMat);
  servoLeftMesh.rotation.set(Math.PI / 2, 0, Math.PI / 2, 'XYZ');
  servoLeftMesh.position.set(8.0, 9.0, 2.0);
  root.add(servoLeftMesh);

  // Right Servo in right thorax bay
  const servoRightMesh = new THREE.Mesh(servoGeom, servoMat);
  servoRightMesh.rotation.set(Math.PI / 2, 0, Math.PI / 2, 'XYZ');
  servoRightMesh.position.set(8.0, -9.0, 2.0);
  root.add(servoRightMesh);

  // 3. Base Stand & Lid
  const standMesh = new THREE.Mesh(standGeom, standMat);
  standMesh.position.set(-2.0, 0, -92.0);
  root.add(standMesh);

  const lidMesh = new THREE.Mesh(lidGeom, standMat);
  lidMesh.position.set(-2.0, 0, -92.0);
  root.add(lidMesh);

  // 4. Left Articulated Wing Pivot Group (Hinged at servo shaft X=8.0, Y=9.0, Z=2.0)
  simLeftWingGroup = new THREE.Group();
  simLeftWingGroup.position.set(8.0, 9.0, 2.0);
  root.add(simLeftWingGroup);

  // Left Horn mated onto left servo spline
  const hornLeftMesh = new THREE.Mesh(hornGeom, hornMat);
  hornLeftMesh.rotation.set(Math.PI / 2, 0, Math.PI / 2, 'XYZ');
  hornLeftMesh.position.set(0, 0, 0);
  simLeftWingGroup.add(hornLeftMesh);

  // Real Left Wing (left_wing.stl) mounted onto the horn & hinge
  const leftWingMesh = new THREE.Mesh(leftWingGeom, wingMat);
  leftWingMesh.position.set(-8.0, -9.0, -2.0); // Offset so hinge axis matches (0, 0, 0)
  simLeftWingGroup.add(leftWingMesh);

  // 5. Right Articulated Wing Pivot Group (Hinged at servo shaft X=8.0, Y=-9.0, Z=2.0)
  simRightWingGroup = new THREE.Group();
  simRightWingGroup.position.set(8.0, -9.0, 2.0);
  root.add(simRightWingGroup);

  // Right Horn mated onto right servo spline
  const hornRightMesh = new THREE.Mesh(hornGeom, hornMat);
  hornRightMesh.rotation.set(-Math.PI / 2, 0, -Math.PI / 2, 'XYZ');
  hornRightMesh.position.set(0, 0, 0);
  simRightWingGroup.add(hornRightMesh);

  // Real Right Wing (right_wing.stl) mounted onto the horn & hinge
  const rightWingMesh = new THREE.Mesh(rightWingGeom, wingMat);
  rightWingMesh.position.set(-8.0, 9.0, -2.0);
  simRightWingGroup.add(rightWingMesh);

  // 6. Addressable LED Pixels on the Real Lateral Wings (in X-Y plane)
  ledMeshesLeft = [];
  ledMeshesRight = [];
  const ledCoords = [
    [32.0, 36.0, 1.8],
    [36.0, 68.0, 1.8],
    [10.0, 60.0, 1.8],
    [-15.0, 45.0, 1.8]
  ];

  ledCoords.forEach(([wx, wy, wz]) => {
    const ledGeo = new THREE.CylinderGeometry(3.5, 3.5, 1.2, 16);
    ledGeo.rotateX(Math.PI / 2); // Align cylinder axis along Z

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

// UI Event Listeners
function setupUIEvents() {
  // CAD Model Selector Dropdown
  const select = document.getElementById("model-select");
  select.addEventListener("change", (e) => {
    const chosen = e.target.value;
    if (isSimulating) {
      toggleSimulation(); // Stop simulation when inspecting individual CAD parts
    }
    loadCADModel(chosen);
  });

  // Start / Stop Simulation Button
  document.getElementById("btn-toggle-sim").addEventListener("click", () => {
    toggleSimulation();
  });

  // Wireframe Toggle
  const btnWireframe = document.getElementById("btn-wireframe");
  btnWireframe.addEventListener("click", () => {
    isWireframe = !isWireframe;
    btnWireframe.classList.toggle("active", isWireframe);
    btnWireframe.innerText = isWireframe ? "📐 Solid" : "📐 Wireframe";
    if (activeCADMesh && activeCADMesh.material) {
      activeCADMesh.material.wireframe = isWireframe;
    }
  });

  // Auto-Rotate Toggle (Default: OFF)
  const btnRotate = document.getElementById("btn-autorotate");
  btnRotate.addEventListener("click", () => {
    isAutoRotate = !isAutoRotate;
    controls.autoRotate = isAutoRotate;
    btnRotate.classList.toggle("active", isAutoRotate);
    btnRotate.innerText = isAutoRotate ? "🔄 Spin: ON" : "🔄 Spin: OFF";
  });

  // Reset Camera View (Returns to front-right isometric view in ISO Z-Up space)
  document.getElementById("btn-reset-cam").addEventListener("click", () => {
    if (isSimulating && simAssemblyGroup) {
      fitCameraToObject(simAssemblyGroup);
    } else if (activeCADMesh) {
      fitCameraToObject(activeCADMesh);
    } else {
      camera.position.set(160, -180, 110);
      controls.target.set(0, 0, -10);
      controls.update();
    }
  });

  // Simulation Panel Fold / Unfold
  const panelToggle = document.getElementById("panel-toggle");
  panelToggle.addEventListener("click", () => {
    document.getElementById("kinematics-panel").classList.toggle("panel-collapsed");
  });

  // Kinematic Behavior Mode Buttons
  document.querySelectorAll(".mode-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
      document.querySelectorAll(".mode-btn").forEach(b => b.classList.remove("active"));
      e.target.classList.add("active");
      const mode = e.target.dataset.mode;
      if (mode) applyKinematicMode(mode);
    });
  });

  // Touch Antenna Surge
  const btnTouch = document.getElementById("btn-touch");
  if (btnTouch) {
    btnTouch.addEventListener("click", triggerCapacitiveTouch);
  }

  // LED Palette Buttons
  document.querySelectorAll(".pal-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
      document.querySelectorAll(".pal-btn").forEach(b => b.classList.remove("active"));
      e.target.classList.add("active");
      currentPalette = e.target.dataset.pal;
    });
  });

  // Sliders
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
      flapSpeed = 0.2;
      flapAmp = 8;
      centerAngle = 65;
      break;
    case "breathe":
      flapSpeed = 0.6;
      flapAmp = 16;
      centerAngle = 50;
      break;
    case "flutter":
      flapSpeed = 1.8;
      flapAmp = 28;
      centerAngle = 45;
      break;
    case "flight":
      flapSpeed = 3.2;
      flapAmp = 38;
      centerAngle = 40;
      break;
    case "glide":
      flapSpeed = 0.1;
      flapAmp = 4;
      centerAngle = 18;
      break;
  }
  document.getElementById("slider-speed").value = flapSpeed;
  document.getElementById("val-speed").innerText = `${flapSpeed.toFixed(1)} Hz`;
  document.getElementById("slider-amp").value = flapAmp;
  document.getElementById("val-amp").innerText = `${flapAmp.toFixed(0)}°`;
}

function triggerCapacitiveTouch() {
  isSurging = true;
  surgeStartTime = performance.now() / 1000;
  lastTouchVal = 450;
  const teleTouch = document.getElementById("tele-touch");
  teleTouch.innerText = "TRIGGERED! (+450 delta)";
  teleTouch.style.color = "#f59e0b";

  setTimeout(() => {
    isSurging = false;
    teleTouch.innerText = "Idle (0 delta)";
    teleTouch.style.color = "#34d399";
  }, 2200);
}

// Animation & Render Loop
function animate(timestamp) {
  requestAnimationFrame(animate);

  const t = timestamp * 0.001; // seconds

  // Update OrbitControls
  controls.update();

  // If in Kinematic Simulation Mode: Flap the REAL CAD WINGS
  if (isSimulating && simLeftWingGroup && simRightWingGroup) {
    let activeSpeed = flapSpeed;
    let activeAmp = flapAmp;

    if (isSurging) {
      activeSpeed = 3.6;
      activeAmp = 38;
    }

    const angleRad = Math.sin(t * activeSpeed * Math.PI * 2) * (activeAmp * (Math.PI / 180));
    const currentAngleDeg = centerAngle + (angleRad * (180 / Math.PI));

    // Flapping rotation around X-axis (roll / dihedral flapping axis) -> causes vertical Z travel!
    simLeftWingGroup.rotation.x = angleRad;
    simRightWingGroup.rotation.x = -angleRad;

    // Update Telemetry
    document.getElementById("tele-angle").innerText = `${currentAngleDeg.toFixed(1)}°`;
    const isDown = Math.cos(t * activeSpeed * Math.PI * 2) > 0;
    document.getElementById("tele-phase").innerText = isDown ? "Downstroke" : "Upstroke";

    // Update LED Shaders
    updateLEDColors(t);
  }

  renderer.render(scene, camera);
}

// Update LED Pixel Colors based on Selected Palette
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
