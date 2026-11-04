// SPDX-License-Identifier: Apache-2.0
// A restrained, illustrative material treatment; it does not create geometry.
export function markPavingJoints(root, spec, assetSha) {
  if (
    spec?.version !== 1 ||
    spec.base_asset_sha256 !== assetSha ||
    spec.target_name !== "landscape-paving" ||
    spec.expected_vertices !== 5088 ||
    spec.expected_color !== "cdbb9f" ||
    !Number.isFinite(spec.spacing_m) ||
    spec.spacing_m < 2 ||
    spec.spacing_m > 5 ||
    !Number.isFinite(spec.width_m) ||
    spec.width_m < 0.01 ||
    spec.width_m > 0.08 ||
    !Number.isFinite(spec.strength) ||
    spec.strength < 0 ||
    spec.strength > 0.2
  )
    throw Error("Invalid paving treatment");
  const targets = [];
  root.traverse((o) => {
    if (o.isMesh && o.name === spec.target_name) targets.push(o);
  });
  if (targets.length !== 1) throw Error("Paving target missing or ambiguous");
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
    throw Error("Paving source contract changed");
  mesh.userData = {
    ...mesh.userData,
    paving_joints: {
      spacing_m: spec.spacing_m,
      width_m: spec.width_m,
      strength: spec.strength,
    },
  };
}
export function applyPavingJoints(material, style) {
  if (material.userData.pavingJoints)
    throw Error("Paving treatment already applied");
  material.userData.pavingJoints = true;
  const previous = material.onBeforeCompile,
    key = material.customProgramCacheKey.bind(material);
  material.onBeforeCompile = (shader, renderer) => {
    previous.call(material, shader, renderer);
    shader.vertexShader = "varying vec3 pavingWorld;\n" + shader.vertexShader;
    shader.vertexShader = shader.vertexShader.replace(
      "#include <begin_vertex>",
      "#include <begin_vertex>\n pavingWorld=(modelMatrix*vec4(position,1.0)).xyz;",
    );
    shader.fragmentShader =
      "varying vec3 pavingWorld;\n" + shader.fragmentShader;
    shader.fragmentShader = shader.fragmentShader.replace(
      "#include <color_fragment>",
      `#include <color_fragment>
      vec2 pavingUV=pavingWorld.xz / ${style.spacing_m.toFixed(4)};
      vec2 pavingDistance=min(fract(pavingUV),1.0-fract(pavingUV));
      vec2 pavingAA=max(fwidth(pavingUV),vec2(0.0001));
      vec2 pavingLine=1.0-smoothstep(vec2(${(style.width_m / style.spacing_m).toFixed(6)}),vec2(${(style.width_m / style.spacing_m).toFixed(6)})+pavingAA,pavingDistance);
      float pavingFade=1.0-smoothstep(0.08,0.8,max(fwidth(pavingWorld.x),fwidth(pavingWorld.z)));
      diffuseColor.rgb*=1.0-${style.strength.toFixed(4)}*max(pavingLine.x,pavingLine.y)*pavingFade;`,
    );
  };
  material.customProgramCacheKey = () =>
    key() +
    `|paving-joints-${style.spacing_m}-${style.width_m}-${style.strength}`;
  material.needsUpdate = true;
}
