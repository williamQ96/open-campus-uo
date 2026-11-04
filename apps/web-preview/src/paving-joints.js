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
  const radial = spec.radial;
  if (
    radial !== undefined &&
    (!Array.isArray(radial.center_xz) ||
      radial.center_xz.length !== 2 ||
      !radial.center_xz.every(Number.isFinite) ||
      radial.center_xz[0] < -290 ||
      radial.center_xz[0] > -270 ||
      radial.center_xz[1] < 25 ||
      radial.center_xz[1] > 45 ||
      !Number.isFinite(radial.radius_m) ||
      radial.radius_m < 4 ||
      radial.radius_m > 12 ||
      !Number.isFinite(radial.ring_spacing_m) ||
      radial.ring_spacing_m < 0.25 ||
      radial.ring_spacing_m > 1 ||
      !Number.isFinite(radial.joint_width_m) ||
      radial.joint_width_m < 0.01 ||
      radial.joint_width_m > 0.04 ||
      !Number.isFinite(radial.strength) ||
      radial.strength < 0 ||
      radial.strength > 0.25)
  )
    throw Error("Invalid radial paving treatment");
  mesh.userData = {
    ...mesh.userData,
    paving_joints: {
      spacing_m: spec.spacing_m,
      width_m: spec.width_m,
      strength: spec.strength,
      ...(radial
        ? { radial: { ...radial, center_xz: [...radial.center_xz] } }
        : {}),
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
      ${
        style.radial
          ? `
      vec2 radialOffset=pavingWorld.xz-vec2(${style.radial.center_xz.map((v) => v.toFixed(4)).join(",")});
      float radialDistance=length(radialOffset);
      float radialMask=1.0-smoothstep(${(style.radial.radius_m - 0.8).toFixed(4)},${style.radial.radius_m.toFixed(4)},radialDistance);
      float ringCoord=radialDistance/${style.radial.ring_spacing_m.toFixed(4)};
      float ringDist=min(fract(ringCoord),1.0-fract(ringCoord));
      float ringAA=max(fwidth(ringCoord),0.0001);
      float ringLine=1.0-smoothstep(${(style.radial.joint_width_m / style.radial.ring_spacing_m).toFixed(5)},${(style.radial.joint_width_m / style.radial.ring_spacing_m).toFixed(5)}+ringAA,ringDist);
      float ringIndex=floor(ringCoord);
      float ringSegments=max(6.0,floor(6.2831853*max((ringIndex+0.5)*${style.radial.ring_spacing_m.toFixed(4)},0.5)/0.30));
      float brickCoord=(atan(radialOffset.y,radialOffset.x)/6.2831853+0.5)*ringSegments+mod(ringIndex,2.0)*0.5;
      float brickDist=min(fract(brickCoord),1.0-fract(brickCoord));
      float brickAA=max(fwidth(brickCoord),0.0001);
      float brickLine=1.0-smoothstep(0.035,0.035+brickAA,brickDist);
      float radialFade=1.0-smoothstep(0.08,0.7,max(fwidth(pavingWorld.x),fwidth(pavingWorld.z)));
      float existingJoint=${style.strength.toFixed(4)}*max(pavingLine.x,pavingLine.y)*pavingFade;
      diffuseColor.rgb*=1.0-mix(existingJoint,${style.radial.strength.toFixed(4)}*max(ringLine,brickLine)*radialFade,radialMask);
      `
          : `diffuseColor.rgb*=1.0-${style.strength.toFixed(4)}*max(pavingLine.x,pavingLine.y)*pavingFade;`
      }`,
    );
  };
  material.customProgramCacheKey = () =>
    key() +
    `|paving-joints-${style.spacing_m}-${style.width_m}-${style.strength}|radial-${JSON.stringify(style.radial ?? null)}`;
  material.needsUpdate = true;
}
