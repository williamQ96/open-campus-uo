// SPDX-License-Identifier: Apache-2.0
import { Quaternion, Vector3 } from "three";

// This cycle follows distance rather than playback time. During the 60%
// stance, moving the foot back by the actor's travel keeps it on the ground.
const stance = 0.6;
const alongX = new Vector3(1, 0, 0);
const ahead = new Vector3(0, 0, 1);

export function createStudentWalk(root, body, height) {
  const legs = ["Left", "Right"].map((side) => ({
    upper: body.getObjectByName(side + "UpLeg"),
    lower: body.getObjectByName(side + "Leg"),
    foot: body.getObjectByName(side + "Foot"),
    toes: body.getObjectByName(side + "Toes"),
    arm: body.getObjectByName(side + "Arm"),
  }));
  const shoes = body
    .getObjectsByProperty("isSkinnedMesh", true)
    .find((mesh) => mesh.material?.name.includes("sneaker"));
  if (!shoes || legs.some((leg) => Object.values(leg).some((bone) => !bone)))
    return null;

  const ratio = height / 1.78;
  const cycle = 0.99 * ratio;
  const standingY = body.position.y;
  const vertex = new Vector3();
  const sole = [Infinity, Infinity];
  root.updateMatrixWorld(true);
  for (let i = 0; i < shoes.geometry.attributes.position.count; i++) {
    root.worldToLocal(shoes.localToWorld(shoes.getVertexPosition(i, vertex)));
    const side = vertex.x >= 0 ? 0 : 1;
    sole[side] = Math.min(sole[side], vertex.y);
  }
  if (sole.some((y) => !Number.isFinite(y))) return null;
  const pos = (bone) => bone.getWorldPosition(new Vector3());
  const forwardCenter = (pos(legs[0].foot).z + pos(legs[1].foot).z) / 2;
  const movingBones = [];
  const records = legs.map((leg, i) => {
    for (const bone of Object.values(leg))
      movingBones.push({ bone, base: bone.quaternion.clone() });
    const hip = pos(leg.upper);
    const knee = pos(leg.lower);
    const ankle = pos(leg.foot);
    return {
      ...leg,
      thigh: hip.distanceTo(knee),
      shin: knee.distanceTo(ankle),
      contact: ankle.y - sole[i] + 0.002,
      ankleX: ankle.x,
      idleAnkle: new Vector3(),
      shoeRotation: leg.foot.getWorldQuaternion(new Quaternion()),
      toesRotation: leg.toes.quaternion.clone(),
    };
  });

  const facing = new Quaternion();
  const parentRotation = new Quaternion();
  const actorRotation = new Quaternion();
  const delta = new Quaternion();
  const hip = new Vector3();
  const knee = new Vector3();
  const ankle = new Vector3();
  const wish = new Vector3();
  const turnFrom = new Vector3();
  const turnTo = new Vector3();
  const direction = new Vector3();
  const forward = new Vector3();
  const pole = new Vector3();
  let travelled = 0;
  let blend = 0;
  let posed = false;

  function aim(bone, from, current, target) {
    turnFrom.subVectors(current, from).normalize();
    turnTo.subVectors(target, from).normalize();
    delta.setFromUnitVectors(turnFrom, turnTo);
    bone.parent.getWorldQuaternion(parentRotation);
    bone.quaternion.premultiply(
      actorRotation
        .copy(parentRotation)
        .invert()
        .multiply(delta)
        .multiply(parentRotation),
    );
  }

  return {
    restore() {
      if (!posed) return;
      body.position.y = standingY;
      for (const { bone, base } of movingBones) bone.quaternion.copy(base);
      posed = false;
    },
    apply(distance, dt, moving) {
      if (moving) travelled += distance;
      blend += (Number(moving) - blend) * (1 - Math.exp(-dt * 16));
      if (blend < 0.001) return;
      posed = true;
      for (const { bone, base } of movingBones) base.copy(bone.quaternion);
      const phase = (travelled / cycle) % 1;
      const sway = Math.cos(phase * 4 * Math.PI);
      for (const leg of records) leg.foot.getWorldPosition(leg.idleAnkle);
      body.position.y = standingY - (0.085 + 0.008 * sway) * ratio * blend;
      root.getWorldQuaternion(facing);
      forward.copy(ahead).applyQuaternion(facing);

      for (const [i, leg] of records.entries()) {
        const p = (phase + i * 0.5) % 1;
        const swing = Math.max(0, (p - stance) / (1 - stance));
        const smooth = swing * swing * (3 - 2 * swing);
        const strike = cycle * stance * 0.5;
        const stepZ =
          p <= stance ? strike - p * cycle : strike * (2 * smooth - 1);
        const lift = Math.sin(swing * Math.PI) ** 2 * 0.095 * ratio;
        wish.set(leg.ankleX, leg.contact + lift, forwardCenter + stepZ);
        root.localToWorld(wish).lerp(leg.idleAnkle, 1 - blend);

        leg.upper.getWorldPosition(hip);
        leg.lower.getWorldPosition(knee);
        leg.foot.getWorldPosition(ankle);
        direction.subVectors(wish, hip);
        const reach = Math.max(
          Math.abs(leg.thigh - leg.shin) + 0.001,
          Math.min(direction.length(), leg.thigh + leg.shin - 0.001),
        );
        direction.normalize();
        wish.copy(hip).addScaledVector(direction, reach);
        pole
          .copy(forward)
          .addScaledVector(direction, -forward.dot(direction))
          .normalize();
        const center =
          (leg.thigh ** 2 - leg.shin ** 2 + reach ** 2) / (reach * 2);
        const bend = Math.sqrt(Math.max(0, leg.thigh ** 2 - center ** 2));
        pole.multiplyScalar(bend).add(hip).addScaledVector(direction, center);
        aim(leg.upper, hip, knee, pole);
        leg.lower.getWorldPosition(knee);
        leg.foot.getWorldPosition(ankle);
        aim(leg.lower, knee, ankle, wish);
        leg.foot.parent.getWorldQuaternion(parentRotation).invert();
        actorRotation
          .copy(parentRotation)
          .multiply(facing)
          .multiply(leg.shoeRotation);
        leg.foot.quaternion.slerp(actorRotation, blend);
        leg.toes.quaternion.slerp(leg.toesRotation, blend);

        leg.arm.parent.getWorldQuaternion(parentRotation).invert();
        turnTo
          .copy(alongX)
          .applyQuaternion(facing)
          .applyQuaternion(parentRotation);
        delta.setFromAxisAngle(
          turnTo,
          0.32 * Math.cos(p * 2 * Math.PI) * blend,
        );
        leg.arm.quaternion.premultiply(delta);
      }
    },
    state: () => ({
      phase: (travelled / cycle) * Math.PI * 2,
      phaseOffset: 0,
      clipCycle: (travelled / cycle) % 1,
      blend,
    }),
  };
}
