import * as THREE from 'three';

// Procedural objects for the gallery. All measurements are in room units.
export function buildGalleryProps() {
  const group = new THREE.Group();
  const hoverables = [];
  const gold = new THREE.MeshPhysicalMaterial({ color: 0xd2a547, metalness: 0.94, roughness: 0.19, clearcoat: 0.7, clearcoatRoughness: 0.12 });
  const darkGold = new THREE.MeshPhysicalMaterial({ color: 0x806024, metalness: 0.9, roughness: 0.29 });
  const ceramic = new THREE.MeshPhysicalMaterial({ color: 0x0438af, metalness: 0.18, roughness: 0.15, clearcoat: 1, clearcoatRoughness: 0.055 });
  const marble = new THREE.MeshPhysicalMaterial({ color: 0xebe5d6, roughness: 0.41, metalness: 0.03, clearcoat: 0.2, clearcoatRoughness: 0.5 });
  const marbleShade = new THREE.MeshPhysicalMaterial({ color: 0xcfc6b2, roughness: 0.55, metalness: 0.02 });
  const stone = new THREE.MeshPhysicalMaterial({ color: 0xd8cab2, roughness: 0.43, metalness: 0.08 });
  const stoneDark = new THREE.MeshPhysicalMaterial({ color: 0xa99980, roughness: 0.55, metalness: 0.08 });

  const mesh = (geometry, material, parent, position = [0, 0, 0]) => {
    const object = new THREE.Mesh(geometry, material);
    object.position.set(...position);
    object.castShadow = true;
    object.receiveShadow = true;
    parent.add(object);
    return object;
  };
  const ellipsoid = (parent, material, position, scale, segments = 48) => {
    const object = mesh(new THREE.SphereGeometry(1, segments, Math.round(segments * 0.7)), material, parent, position);
    object.scale.set(...scale);
    return object;
  };
  const ring = (parent, radius, tube, y, material = gold) => {
    const object = mesh(new THREE.TorusGeometry(radius, tube, 16, 96), material, parent, [0, y, 0]);
    object.rotation.x = Math.PI / 2;
    return object;
  };
  const cylinder = (parent, top, bottom, height, y, material, segments = 80) =>
    mesh(new THREE.CylinderGeometry(top, bottom, height, segments), material, parent, [0, y, 0]);

  function plinth(x, z, height, radius) {
    const pedestal = new THREE.Group();
    pedestal.position.set(x, 0, z);
    group.add(pedestal);
    cylinder(pedestal, radius * 1.08, radius * 1.13, 0.11, 0.055, stoneDark);
    cylinder(pedestal, radius * 1.03, radius * 1.08, 0.10, 0.16, stone);
    const shaftBottom = 0.21;
    const shaftTop = height - 0.15;
    const shaftHeight = shaftTop - shaftBottom;
    cylinder(pedestal, radius * 0.88, radius * 0.98, shaftHeight, shaftBottom + shaftHeight / 2, stone, 96);
    // Shallow, vertical reliefs give the stone a carved fluted surface.
    const fluteGeometry = new THREE.CylinderGeometry(radius * 0.025, radius * 0.025, shaftHeight * 0.96, 10);
    for (let i = 0; i < 24; i++) {
      const angle = i * Math.PI * 2 / 24;
      mesh(fluteGeometry, stoneDark, pedestal, [Math.sin(angle) * radius * 0.945, shaftBottom + shaftHeight / 2, Math.cos(angle) * radius * 0.945]);
    }
    cylinder(pedestal, radius * 1.08, radius * 0.92, 0.10, height - 0.10, stone);
    cylinder(pedestal, radius * 1.12, radius * 1.10, 0.10, height, stoneDark);
    ring(pedestal, radius * 1.095, 0.018, height + 0.048, darkGold);
    return height + 0.05;
  }

  // Golden, looping sculpture, modelled as solid metal rather than a cutout.
  const goldTop = plinth(-3.4, 0.9, 1.15, 0.53);
  const goldObject = new THREE.Group();
  goldObject.position.set(-3.4, goldTop, 0.9);
  goldObject.userData.kind = 'prop';
  goldObject.userData.name = 'Golden movement sculpture';
  group.add(goldObject);
  cylinder(goldObject, 0.27, 0.31, 0.11, 0.055, darkGold);
  cylinder(goldObject, 0.22, 0.25, 0.07, 0.14, gold);
  ring(goldObject, 0.23, 0.02, 0.17);
  const goldLoop = mesh(new THREE.TorusKnotGeometry(0.40, 0.10, 240, 32, 2, 3), gold, goldObject, [0, 0.83, 0]);
  goldLoop.scale.set(0.82, 1.35, 0.76);
  goldLoop.rotation.set(0.27, 0.2, -0.23);
  hoverables.push(goldObject);

  // A lathed cobalt vessel with a rolled lip, foot and fine gilt bands.
  const vaseTop = plinth(3.4, 0.6, 1.20, 0.60);
  const vaseObject = new THREE.Group();
  vaseObject.position.set(3.4, vaseTop, 0.6);
  vaseObject.userData.kind = 'prop';
  vaseObject.userData.name = 'Cobalt blue vessel';
  group.add(vaseObject);
  const profile = [
    [0.0,0.0],[0.30,0.0],[0.35,0.045],[0.34,0.10],[0.39,0.18],
    [0.48,0.29],[0.54,0.45],[0.56,0.62],[0.53,0.80],[0.46,0.96],
    [0.35,1.10],[0.25,1.22],[0.20,1.33],[0.19,1.48],[0.22,1.58],
    [0.30,1.64],[0.31,1.68],[0.25,1.71],[0.19,1.68],[0.16,1.61]
  ].map(([r,y]) => new THREE.Vector2(r,y));
  mesh(new THREE.LatheGeometry(profile, 128), ceramic, vaseObject);
  ring(vaseObject, 0.305, 0.018, 1.67);
  ring(vaseObject, 0.34, 0.015, 0.09, darkGold);
  ring(vaseObject, 0.205, 0.012, 1.40, darkGold);
  // The inset dark opening reads as depth from the gallery camera.
  const opening = mesh(new THREE.CircleGeometry(0.17, 80), new THREE.MeshStandardMaterial({ color: 0x071433, roughness: 0.23 }), vaseObject, [0,1.685,0]);
  opening.rotation.x = -Math.PI / 2;
  hoverables.push(vaseObject);

  // Classical marble portrait: a softly modelled bust with layered curls.
  const bustTop = plinth(0, 1.1, 1.10, 0.64);
  const bust = new THREE.Group();
  bust.position.set(0, bustTop, 1.1);
  bust.userData.kind = 'prop';
  bust.userData.name = 'Marble portrait bust';
  group.add(bust);
  cylinder(bust, 0.27, 0.34, 0.10, 0.05, marbleShade);
  cylinder(bust, 0.23, 0.28, 0.10, 0.14, marble);
  const shoulders = ellipsoid(bust, marble, [0,0.49,0], [0.64,0.36,0.28], 64);
  shoulders.rotation.x = -0.06;
  const torso = ellipsoid(bust, marble, [0,0.36,-0.015], [0.42,0.38,0.26], 64);
  torso.rotation.x = -0.12;
  // Overlapping folds suggest a carved drape across the torso.
  for (let i = 0; i < 4; i++) {
    const fold = ellipsoid(bust, i % 2 ? marbleShade : marble, [-0.22 + i * 0.13,0.36 - i * 0.018,0.20], [0.055,0.27,0.045], 32);
    fold.rotation.z = -0.38;
  }
  ellipsoid(bust, marble, [0,0.84,0.01], [0.19,0.32,0.18], 48);
  const head = ellipsoid(bust, marble, [0,1.30,0.025], [0.36,0.47,0.30], 64);
  head.rotation.z = -0.06;
  ellipsoid(bust, marble, [-0.34,1.29,0.02], [0.075,0.13,0.07], 32);
  ellipsoid(bust, marble, [0.34,1.29,0.02], [0.075,0.13,0.07], 32);
  ellipsoid(bust, marble, [0,1.28,0.31], [0.075,0.16,0.095], 40);
  ellipsoid(bust, marbleShade, [-0.14,1.37,0.29], [0.085,0.027,0.022], 32);
  ellipsoid(bust, marbleShade, [0.14,1.37,0.29], [0.085,0.027,0.022], 32);
  ellipsoid(bust, marbleShade, [0,1.06,0.282], [0.10,0.020,0.022], 32);
  ellipsoid(bust, marble, [0,0.99,0.24], [0.16,0.08,0.075], 32);
  // Many small, differently sized curls create a carved classical silhouette.
  for (let row = 0; row < 4; row++) {
    const count = row === 0 ? 11 : row === 1 ? 13 : row === 2 ? 11 : 8;
    const y = 1.52 + row * 0.105;
    const r = row === 3 ? 0.20 : row === 2 ? 0.30 : 0.36;
    for (let i = 0; i < count; i++) {
      const angle = i * Math.PI * 2 / count + row * 0.27;
      const size = 0.085 + 0.014 * Math.sin(i * 2.4 + row);
      ellipsoid(bust, marble, [Math.sin(angle)*r,y,Math.cos(angle)*r*0.82], [size,size*1.08,size], 24);
    }
  }
  ellipsoid(bust, marble, [0,1.72,0], [0.25,0.14,0.23], 40);
  hoverables.push(bust);

  return { group, hoverables };
}
