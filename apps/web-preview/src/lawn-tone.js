// SPDX-License-Identifier: Apache-2.0
// Restrained procedural lawn tone; visual inference, not mapped vegetation.
export function markLawnTone(root, spec, assetSha) {
  if (
    spec?.version !== 1 ||
    spec.base_asset_sha256 !== assetSha ||
    spec.target_name !== "landscape-lawn" ||
    spec.expected_vertices !== 30659 ||
    spec.expected_color !== "91b66f" ||
    !Number.isFinite(spec.strength) ||
    spec.strength < 0 ||
    spec.strength > 0.12
  )
    throw Error("Invalid lawn tone treatment");
  const targets = [];
  root.traverse((o) => {
    if (o.isMesh && o.name === spec.target_name) targets.push(o);
  });
  if (targets.length !== 1) throw Error("Lawn target missing or ambiguous");
  const mesh = targets[0],
    m = mesh.material;
  if (
    mesh.userData.asset_kind !== "landscape-surface" ||
    mesh.geometry.attributes.position?.count !== spec.expected_vertices ||
    Array.isArray(m) ||
    !m.isMeshStandardMaterial ||
    m.map ||
    m.vertexColors ||
    m.color.getHexString() !== spec.expected_color
  )
    throw Error("Lawn source contract changed");
  let extension;
  if (spec.extension !== undefined) {
    const e = spec.extension;
    if (
      e.target_name !== "campus-lawn-extension" ||
      e.expected_vertices !== 47699 ||
      !Number.isFinite(e.strength) ||
      e.strength < 0 ||
      e.strength > 0.12
    )
      throw Error("Invalid lawn extension treatment");
    const matches = [];
    root.traverse((o) => {
      if (o.isMesh && o.name === e.target_name) matches.push(o);
    });
    if (matches.length !== 1)
      throw Error("Lawn extension missing or ambiguous");
    extension = matches[0];
    const material = extension.material;
    if (
      extension.userData.asset_kind !== "landscape-surface" ||
      extension.geometry.attributes.position?.count !== e.expected_vertices ||
      !extension.geometry.attributes.color ||
      Array.isArray(material) ||
      !material.isMeshStandardMaterial ||
      material.map ||
      !material.vertexColors ||
      material.color.getHexString() !== "ffffff"
    )
      throw Error("Lawn extension source contract changed");
  }
  mesh.userData = { ...mesh.userData, lawn_tone: { strength: spec.strength } };
  if (extension)
    extension.userData = {
      ...extension.userData,
      lawn_tone: { strength: spec.extension.strength },
    };
}
export function applyLawnTone(material, style) {
  if (material.userData.lawnTone) throw Error("Lawn tone already applied");
  material.userData.lawnTone = true;
  const previous = material.onBeforeCompile,
    key = material.customProgramCacheKey.bind(material);
  material.onBeforeCompile = (shader, renderer) => {
    previous.call(material, shader, renderer);
    shader.vertexShader = "varying vec3 lawnWorld;\n" + shader.vertexShader;
    shader.vertexShader = shader.vertexShader.replace(
      "#include <begin_vertex>",
      "#include <begin_vertex>\n lawnWorld=(modelMatrix*vec4(position,1.0)).xyz;",
    );
    shader.fragmentShader = "varying vec3 lawnWorld;\n" + shader.fragmentShader;
    shader.fragmentShader = shader.fragmentShader.replace(
      "#include <color_fragment>",
      `#include <color_fragment>
      float lawnA=sin(lawnWorld.x*.095+cos(lawnWorld.z*.067)*1.1);
      float lawnB=cos(lawnWorld.z*.11+sin(lawnWorld.x*.041));
      float lawnTone=lawnA*lawnB;
      float lawnFade=1.0-smoothstep(1.0,8.0,max(fwidth(lawnWorld.x),fwidth(lawnWorld.z)));
      diffuseColor.rgb*=1.0+${style.strength.toFixed(4)}*lawnTone*lawnFade;`,
    );
  };
  material.customProgramCacheKey = () => key() + `|lawn-tone-${style.strength}`;
  material.needsUpdate = true;
}
