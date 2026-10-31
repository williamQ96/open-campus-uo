import * as THREE from 'three';

export function createCharacter() {
  const root=new THREE.Group();
  root.name='whitebox-explorer';
  const white=new THREE.MeshStandardMaterial({color:0xfaf8ee,roughness:.8});
  const accent=new THREE.MeshStandardMaterial({color:0x68846c,roughness:.8});
  const part=(geometry,material,x,y,z,parent=root)=>{
    const mesh=new THREE.Mesh(geometry,material);mesh.position.set(x,y,z);mesh.castShadow=true;parent.add(mesh);return mesh;
  };
  part(new THREE.SphereGeometry(.19,20,14),white,0,1.58,0);
  part(new THREE.CapsuleGeometry(.2,.47,6,14),white,0,1.08,0);
  // A small chest mark makes heading legible without adding non-placeholder detail.
  part(new THREE.BoxGeometry(.14,.06,.025),accent,0,1.19,.19);
  const limb=(x,y,r,length)=>{
    const pivot=new THREE.Group();pivot.position.set(x,y,0);root.add(pivot);
    part(new THREE.CapsuleGeometry(r,length,4,10),white,0,-length/2-.03,0,pivot);
    return pivot;
  };
  const arms=[limb(-.29,1.27,.065,.43),limb(.29,1.27,.065,.43)];
  const legs=[limb(-.12,.75,.085,.54),limb(.12,.75,.085,.54)];
  return {root,animate(time,moving){const a=moving?Math.sin(time*10)*.45:0;arms[0].rotation.x=a;arms[1].rotation.x=-a;legs[0].rotation.x=-a;legs[1].rotation.x=a;}};
}
