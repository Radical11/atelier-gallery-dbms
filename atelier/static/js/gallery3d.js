import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { Reflector } from 'three/addons/objects/Reflector.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { buildGalleryProps } from './gallery-props.js';

const hero = document.querySelector('.museum-stage');
if (hero) mountGallery().catch(error => console.warn('The illustrated gallery remains available.', error));

async function mountGallery() {
  const originals = [...hero.querySelectorAll('.wall-frame')].map(link => ({
    src:link.querySelector('img')?.src, title:link.querySelector('img')?.alt || 'Atelier collection', href:link.href
  }));
  const renderer = new THREE.WebGLRenderer({antialias:true,alpha:false,powerPreference:'high-performance',stencil:false});
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 0.82;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  const canvas = renderer.domElement;
  canvas.className='gallery-webgl';
  canvas.setAttribute('aria-hidden','true');
  canvas.draggable=false;
  canvas.addEventListener('dragstart',event=>event.preventDefault());

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x17080c);
  scene.fog = new THREE.FogExp2(0x241018,0.014);
  const camera = new THREE.PerspectiveCamera(48,1,0.1,60);
  camera.position.set(0,4.15,12.6);
  const look = new THREE.Vector3(0,2.55,-1.7);
  camera.lookAt(look);
  const environment = new THREE.PMREMGenerator(renderer);
  const environmentScene = new RoomEnvironment();
  const environmentTarget = environment.fromScene(environmentScene,0.025);
  scene.environment=environmentTarget.texture;
  scene.environmentIntensity=0.55;
  environmentScene.dispose();
  environment.dispose();

  const gold = new THREE.MeshPhysicalMaterial({color:0xd6a84e,metalness:0.94,roughness:0.19,clearcoat:0.55,clearcoatRoughness:0.1});
  const brightGold = new THREE.MeshPhysicalMaterial({color:0xf0cf7d,metalness:0.86,roughness:0.16});
  const velvet = new THREE.MeshStandardMaterial({color:0x640d24,roughness:0.91});
  const dark = new THREE.MeshStandardMaterial({color:0x180c0b,roughness:0.38,metalness:0.25});
  const ivory = new THREE.MeshStandardMaterial({color:0xf3e9cf,roughness:0.8});
  const wood = new THREE.MeshStandardMaterial({color:0x251209,roughness:0.4});
  function box(w,h,d,material,x,y,z) {
    const mesh = new THREE.Mesh(new THREE.BoxGeometry(w,h,d),material);
    mesh.position.set(x,y,z);mesh.castShadow=true;mesh.receiveShadow=true;return mesh;
  }
  scene.add(box(23,8.5,0.35,velvet,0,4.25,-4.8));
  scene.add(box(0.35,8.5,23,velvet,-10,4.25,4));
  scene.add(box(0.35,8.5,23,velvet,10,4.25,4));
  scene.add(box(23,0.2,22,dark,0,8,4));
  for(const y of [0.12,0.32,6.4,6.6,7.2]) scene.add(box(22,0.075,0.14,gold,0,y,-4.54));
  for(const x of [-7.4,-5.2,-1.6,1.6,5.2,7.4]) scene.add(box(0.045,5.75,0.08,gold,x,3.35,-4.53));

  for(const x of [-6.7,6.7]) for(const z of [-3.0,3.4]) {
    const column=new THREE.Group();column.position.set(x,0,z);
    const shaft=new THREE.Mesh(new THREE.CylinderGeometry(0.27,0.34,6.4,64),gold);
    shaft.position.y=3.4;shaft.castShadow=shaft.receiveShadow=true;column.add(shaft);
    for(let i=0;i<16;i++) {
      const angle=i/16*Math.PI*2;
      const flute=new THREE.Mesh(new THREE.CylinderGeometry(0.025,0.025,6.1,8),brightGold);
      flute.position.set(Math.cos(angle)*0.3,3.4,Math.sin(angle)*0.3);column.add(flute);
    }
    for(const [y,r,h] of [[0.15,.48,.3],[.38,.4,.14],[6.62,.42,.2],[6.88,.54,.28]]) {
      const ring=new THREE.Mesh(new THREE.CylinderGeometry(r,r,h,64),gold);ring.position.y=y;column.add(ring);
    }
    scene.add(column);
  }

  const reflectionSize=1536;
  const mirror=new Reflector(new THREE.PlaneGeometry(26,27),{color:0x5b4b40,textureWidth:reflectionSize,textureHeight:reflectionSize,clipBias:0.003,multisample:2});
  mirror.rotation.x=-Math.PI/2;mirror.position.set(0,-0.015,4);
  scene.add(mirror);
  const marbleCanvas=document.createElement('canvas');marbleCanvas.width=marbleCanvas.height=1024;
  const mc=marbleCanvas.getContext('2d');mc.fillStyle='#96816e';mc.fillRect(0,0,1024,1024);
  for(let i=0;i<48;i++) {
    mc.beginPath();mc.strokeStyle=`rgba(235,217,183,${0.03+(i%5)*0.01})`;mc.lineWidth=1+i%4;
    mc.moveTo(0,i*29);mc.bezierCurveTo(300,i*17+200,600,i*37-150,1024,i*23+70);mc.stroke();
  }
  const marbleTexture=new THREE.CanvasTexture(marbleCanvas);marbleTexture.colorSpace=THREE.SRGBColorSpace;
  marbleTexture.wrapS=marbleTexture.wrapT=THREE.RepeatWrapping;marbleTexture.repeat.set(7,8);
  const floor=new THREE.Mesh(new THREE.PlaneGeometry(26,27),new THREE.MeshPhysicalMaterial({map:marbleTexture,color:0xe2cbb0,metalness:0.3,roughness:0.2,clearcoat:1,transparent:true,opacity:0.42,depthWrite:false}));
  floor.rotation.x=-Math.PI/2;floor.position.set(0,-0.01,4);floor.receiveShadow=true;scene.add(floor);
  const inlay=new THREE.MeshBasicMaterial({color:0xd0aa64,transparent:true,opacity:0.32});
  for(let x=-9;x<=9;x+=1.5) scene.add(box(0.014,0.004,23,inlay,x,0.006,5));
  for(let z=-4;z<=15;z+=1.5) scene.add(box(20,0.004,0.014,inlay,0,0.007,z));

  const props=buildGalleryProps();scene.add(props.group);
  const hoverables=[...props.hoverables];
  const loader=new THREE.TextureLoader();
  const textures=await Promise.all(originals.map(item=>item.src?loader.loadAsync(item.src).catch(()=>null):Promise.resolve(null)));

  function frameShape(width,height,border,depth) {
    const shape=new THREE.Shape();shape.moveTo(-width/2,-height/2);shape.lineTo(width/2,-height/2);shape.lineTo(width/2,height/2);shape.lineTo(-width/2,height/2);shape.closePath();
    const hole=new THREE.Path();hole.moveTo(-width/2+border,-height/2+border);hole.lineTo(-width/2+border,height/2-border);hole.lineTo(width/2-border,height/2-border);hole.lineTo(width/2-border,-height/2+border);hole.closePath();shape.holes.push(hole);
    return new THREE.ExtrudeGeometry(shape,{depth,bevelEnabled:true,bevelSegments:4,steps:1,bevelSize:0.045,bevelThickness:0.045,curveSegments:16});
  }
  function makePainting(item,texture,index) {
    const group=new THREE.Group();
    group.position.set([-3.35,3.35,0][index]||0,index===2?4.65:3.6,-4.25);
    group.userData={kind:'painting',name:item.title,href:item.href};
    group.add(box(2.55,2.95,0.22,wood,0,0,-0.02));
    const outer=new THREE.Mesh(frameShape(2.55,2.95,.17,.2),gold);outer.castShadow=true;group.add(outer);
    const inner=new THREE.Mesh(frameShape(2.22,2.62,.045,.12),brightGold);inner.position.z=.2;group.add(inner);
    group.add(box(2.17,2.57,.045,ivory,0,0,.2));
    if(texture) {texture.colorSpace=THREE.SRGBColorSpace;texture.anisotropy=Math.min(16,renderer.capabilities.getMaxAnisotropy());}
    const artwork=new THREE.Mesh(new THREE.PlaneGeometry(1.88,1.88),new THREE.MeshStandardMaterial({map:texture,color:texture?0xffffff:0x93321f,roughness:0.67}));
    artwork.position.z=.241;group.add(artwork);
    const glass=new THREE.Mesh(new THREE.PlaneGeometry(1.9,1.9),new THREE.MeshPhysicalMaterial({color:0xffffff,transparent:true,opacity:.045,roughness:.06,metalness:.15,clearcoat:1,depthWrite:false}));glass.position.z=.249;group.add(glass);
    for(const x of [-1.19,1.19]) for(const y of [-1.39,1.39]) {
      const flourish=new THREE.Mesh(new THREE.TorusKnotGeometry(.065,.022,48,8,2,3),brightGold);flourish.position.set(x,y,.27);group.add(flourish);
    }
    scene.add(group);hoverables.push(group);
  }
  originals.slice(0,3).forEach((item,index)=>makePainting(item,textures[index],index));

  // Plaques and the museum sign remain actual surfaces inside the room.
  function label(text,width,height) {
    const cv=document.createElement('canvas');cv.width=1024;cv.height=256;
    const c=cv.getContext('2d');c.fillStyle='#260911';c.fillRect(0,0,1024,256);
    c.strokeStyle='#c49d54';c.lineWidth=10;c.strokeRect(12,12,1000,232);
    c.fillStyle='#f3d996';c.textAlign='center';c.font='64px Georgia';c.fillText(text,512,150,900);
    const tex=new THREE.CanvasTexture(cv);tex.colorSpace=THREE.SRGBColorSpace;
    return new THREE.Mesh(new THREE.PlaneGeometry(width,height),new THREE.MeshBasicMaterial({map:tex}));
  }
  const sign=label('ATELIER',3.3,.8);sign.position.set(0,6.7,-4.48);scene.add(sign);
  for(let i=0;i<Math.min(originals.length,2);i++) {
    const plaque=label(originals[i].title,1.65,.28);plaque.position.set(i===0?-3.35:3.35,1.85,-4.46);scene.add(plaque);
  }

  for(const x of [-4.8,-1.65,1.65,4.8]) {
    const post=new THREE.Group();post.position.set(x,0,2.55);
    const stem=new THREE.Mesh(new THREE.CylinderGeometry(.035,.055,.86,24),gold);stem.position.y=.47;post.add(stem);
    const base=new THREE.Mesh(new THREE.CylinderGeometry(.17,.2,.08,32),gold);base.position.y=.05;post.add(base);
    const ball=new THREE.Mesh(new THREE.SphereGeometry(.09,24,16),gold);ball.position.y=.96;post.add(ball);scene.add(post);
  }
  for(const [a,b] of [[-4.8,-1.65],[-1.65,1.65],[1.65,4.8]]) {
    const curve=new THREE.CatmullRomCurve3([new THREE.Vector3(a,.93,2.55),new THREE.Vector3((a+b)/2,.64,2.55),new THREE.Vector3(b,.93,2.55)]);
    const rope=new THREE.Mesh(new THREE.TubeGeometry(curve,48,.035,10,false),new THREE.MeshStandardMaterial({color:0x8f1232,roughness:.85}));scene.add(rope);
  }

  scene.add(new THREE.HemisphereLight(0xffe8bd,0x2b1024,.8));
  scene.add(new THREE.AmbientLight(0xffd7b8,.18));
  function spotlight(x,y,z,tx,ty,tz,intensity,color=0xffdfac,shadow=true) {
    const light=new THREE.SpotLight(color,intensity,30,.48,.65,2);
    light.position.set(x,y,z);light.target.position.set(tx,ty,tz);light.castShadow=shadow;
    light.shadow.mapSize.set(2048,2048);light.shadow.normalBias=.035;light.shadow.bias=-.00005;light.shadow.camera.near=.4;light.shadow.camera.far=26;
    scene.add(light,light.target);return light;
  }
  spotlight(-5.8,7,4,-3.35,3,-3.6,48);
  spotlight(5.8,7,4,3.35,3,-3.6,48);
  spotlight(0,7.5,4.5,0,2,1,54,0xfff1db);
  spotlight(-7,4,-1,1,2,1,24,0xff3963,false);
  spotlight(7,4,-2,-1,2,0,25,0x506bff,false);
  const cursorLight=new THREE.PointLight(0xffd58a,9,8,2);cursorLight.position.set(0,4,4);scene.add(cursorLight);

  const glow=new THREE.MeshBasicMaterial({color:0xffc75b,toneMapped:false});
  for(const x of [-6.7,6.7]) {
    const strip=box(.045,6.4,.04,glow,x,3.3,-2.65);scene.add(strip);
  }
  const count=80,positions=new Float32Array(count*3),speeds=new Float32Array(count);
  for(let i=0;i<count;i++) {positions[i*3]=(Math.random()-.5)*17;positions[i*3+1]=Math.random()*7;positions[i*3+2]=(Math.random()-.5)*12;speeds[i]=.025+Math.random()*.045;}
  const particlesGeometry=new THREE.BufferGeometry();particlesGeometry.setAttribute('position',new THREE.BufferAttribute(positions,3));
  const particleCanvas=document.createElement('canvas');particleCanvas.width=particleCanvas.height=32;
  const pc=particleCanvas.getContext('2d'),gradient=pc.createRadialGradient(16,16,0,16,16,16);gradient.addColorStop(0,'#fff5d4');gradient.addColorStop(.18,'#ffdc96');gradient.addColorStop(1,'rgba(255,190,70,0)');pc.fillStyle=gradient;pc.fillRect(0,0,32,32);
  const particleTexture=new THREE.CanvasTexture(particleCanvas);
  const particles=new THREE.Points(particlesGeometry,new THREE.PointsMaterial({map:particleTexture,color:0xffdf97,size:.025,transparent:true,opacity:.2,depthWrite:false,blending:THREE.AdditiveBlending}));scene.add(particles);

  const target=new THREE.WebGLRenderTarget(1,1,{type:THREE.HalfFloatType,samples:4});
  const composer=new EffectComposer(renderer,target);composer.addPass(new RenderPass(scene,camera));
  const bloom=new UnrealBloomPass(new THREE.Vector2(1,1),.28,.45,1.45);composer.addPass(bloom);composer.addPass(new OutputPass());

  const picks=[];
  scene.updateMatrixWorld(true);
  for(const object of hoverables) {
    object.userData.restPosition=object.position.clone();object.userData.restRotation=object.rotation.clone();
    const bounds=new THREE.Box3().setFromObject(object),size=bounds.getSize(new THREE.Vector3()),center=bounds.getCenter(new THREE.Vector3());
    object.worldToLocal(center);
    const pick=new THREE.Mesh(new THREE.BoxGeometry(size.x+.12,size.y+.12,size.z+.18),new THREE.MeshBasicMaterial({visible:false}));
    pick.position.copy(center);pick.userData.target=object;object.add(pick);picks.push(pick);
  }

  hero.prepend(canvas);
  const raycaster=new THREE.Raycaster(),pointer=new THREE.Vector2(9,9);
  const mouse={x:0,y:0};let selected=null,visible=true,handle=0,last=0,deadline=0,phase=0,first=true;
  const reduce=window.matchMedia('(prefers-reduced-motion: reduce)');
  const animated=()=>document.documentElement.classList.contains('effects-on')&&!reduce.matches;
  function resize() {
    const w=hero.clientWidth,h=hero.clientHeight;
    const dpr=Math.min(window.devicePixelRatio||1,2);
    renderer.setPixelRatio(dpr);renderer.setSize(w,h,false);
    composer.setPixelRatio(dpr);composer.setSize(w,h);
    camera.aspect=w/h;camera.position.z=w<700?18:12.6;camera.updateProjectionMatrix();
    renderSoon();
  }
  function renderSoon() {if(!handle&&visible&&!document.hidden) handle=requestAnimationFrame(render);}
  function render(now) {
    handle=0;
    if(!visible||document.hidden)return;
    if(animated()&&now<deadline) {renderSoon();return;}
    deadline=animated()?Math.max(deadline+1000/120,now):now;
    const delta=Math.min((now-(last||now))/1000,.05);last=now;
    const active=animated();phase+=active?delta:0;
    const x=active?mouse.x:0,y=active?mouse.y:0;
    camera.position.x=THREE.MathUtils.lerp(camera.position.x,x*1.4,.055);
    camera.position.y=THREE.MathUtils.lerp(camera.position.y,4.15+y*.45,.055);
    look.set(x*.22,2.55+y*.15,-1.7);camera.lookAt(look);
    cursorLight.position.set(x*5,4+y*2,3.5);
    scene.updateMatrixWorld(true);
    raycaster.setFromCamera(pointer,camera);
    const hit=raycaster.intersectObjects(picks,false)[0];
    selected=hit?hit.object.userData.target:null;
    canvas.style.cursor=selected?.userData.href?'pointer':'default';
    for(let i=0;i<hoverables.length;i++) {
      const object=hoverables[i],rest=object.userData.restPosition,rotation=object.userData.restRotation,focused=active&&selected===object;
      const painting=object.userData.kind==='painting';
      object.position.z=THREE.MathUtils.lerp(object.position.z,rest.z+(focused?(painting?3.2:.9):0),.09);
      object.position.y=THREE.MathUtils.lerp(object.position.y,rest.y+(focused?0.12:0)+(active&&!painting?Math.sin(phase*.8+i)*.018:0),.08);
      object.rotation.y=THREE.MathUtils.lerp(object.rotation.y,rotation.y+(focused?x*.28:active?Math.sin(phase*.35+i)*.025:0),.07);
      object.rotation.x=THREE.MathUtils.lerp(object.rotation.x,rotation.x+(focused?-y*.12:0),.07);
    }
    if(active) {
      for(let i=0;i<count;i++) {positions[i*3+1]+=delta*speeds[i];if(positions[i*3+1]>7)positions[i*3+1]=0;}
      particlesGeometry.attributes.position.needsUpdate=true;
    }
    bloom.enabled=active;
    composer.render(delta);
    if(first) {hero.classList.add('webgl-ready');first=false;}
    if(active)renderSoon();
  }
  hero.addEventListener('pointermove',event=>{
    if(event.pointerType==='touch')return;
    const rect=hero.getBoundingClientRect();
    pointer.set((event.clientX-rect.left)/rect.width*2-1,-((event.clientY-rect.top)/rect.height)*2+1);
    mouse.x=pointer.x;mouse.y=pointer.y;renderSoon();
  });
  hero.addEventListener('pointerleave',()=>{pointer.set(9,9);mouse.x=mouse.y=0;renderSoon();});
  canvas.addEventListener('click',()=>{if(selected?.userData.href)location.assign(selected.userData.href);});
  const observer=new IntersectionObserver(entries=>{
    visible=entries[0].isIntersecting;
    if(visible){last=0;renderSoon();}else{cancelAnimationFrame(handle);handle=0;}
  },{threshold:.01});observer.observe(hero);
  const preferenceObserver=new MutationObserver(()=>{last=0;renderSoon();});
  preferenceObserver.observe(document.documentElement,{attributes:true,attributeFilter:['class']});
  document.addEventListener('visibilitychange',()=>{if(document.hidden){cancelAnimationFrame(handle);handle=0;}else{last=0;renderSoon();}});
  canvas.addEventListener('webglcontextlost',event=>{event.preventDefault();cancelAnimationFrame(handle);handle=0;hero.classList.remove('webgl-ready');});
  const resizeObserver=new ResizeObserver(resize);resizeObserver.observe(hero);resize();
}
