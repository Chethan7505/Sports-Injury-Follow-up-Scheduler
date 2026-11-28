import React, { useRef, useMemo, useEffect } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import * as THREE from 'three';

/* ── Thread using imperative Three.js Line ────────────── */
function Thread({ offset, spread, frequency, color1, color2 }) {
  const groupRef = useRef();
  const lineRef = useRef();
  const segments = 200;

  const { scene } = useThree();

  const geometry = useMemo(() => {
    const pts = [];
    const progArr = [];
    for (let i = 0; i <= segments; i++) {
      const t = i / segments;
      pts.push(new THREE.Vector3((t - 0.5) * 4, 0, 0));
      progArr.push(t);
    }
    const geo = new THREE.BufferGeometry().setFromPoints(pts);
    geo.setAttribute('aProgress', new THREE.Float32BufferAttribute(progArr, 1));
    return geo;
  }, []);

  const material = useMemo(
    () =>
      new THREE.ShaderMaterial({
        vertexShader: `
          uniform float uTime;
          uniform float uFrequency;
          uniform float uSpread;
          uniform float uOffset;
          attribute float aProgress;
          varying float vProgress;
          varying float vAlpha;

          void main() {
            vProgress = aProgress;
            vec3 pos = position;

            float wave1 = sin(aProgress * uFrequency + uTime * 0.8 + uOffset) * uSpread;
            float wave2 = cos(aProgress * uFrequency * 0.7 + uTime * 0.5 + uOffset * 1.3) * uSpread * 0.6;
            pos.y += wave1 + wave2;
            pos.x += sin(aProgress * uFrequency * 0.3 + uTime * 0.3 + uOffset * 0.7) * uSpread * 0.4;

            vAlpha = smoothstep(0.0, 0.1, aProgress) * smoothstep(1.0, 0.9, aProgress);

            gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
          }
        `,
        fragmentShader: `
          uniform vec3 uColor1;
          uniform vec3 uColor2;
          varying float vProgress;
          varying float vAlpha;

          void main() {
            vec3 color = mix(uColor1, uColor2, vProgress);
            gl_FragColor = vec4(color, vAlpha * 0.35);
          }
        `,
        transparent: true,
        depthWrite: false,
        uniforms: {
          uTime: { value: 0 },
          uFrequency: { value: frequency },
          uSpread: { value: spread },
          uOffset: { value: offset },
          uColor1: { value: new THREE.Color(color1) },
          uColor2: { value: new THREE.Color(color2) },
        },
      }),
    [offset, spread, frequency, color1, color2]
  );

  useEffect(() => {
    const line = new THREE.Line(geometry, material);
    lineRef.current = line;
    if (groupRef.current) {
      groupRef.current.add(line);
    }
    return () => {
      if (groupRef.current) {
        groupRef.current.remove(line);
      }
      geometry.dispose();
      material.dispose();
    };
  }, [geometry, material]);

  useFrame(({ clock }) => {
    if (lineRef.current) {
      lineRef.current.material.uniforms.uTime.value = clock.elapsedTime;
    }
  });

  return <group ref={groupRef} />;
}

function CoreGlow({ color }) {
  return (
    <mesh>
      <sphereGeometry args={[0.03, 32, 32]} />
      <meshBasicMaterial color={color} transparent opacity={0.7} />
    </mesh>
  );
}

function ThreadScene({ colors, coreColor, threadCount, spread, frequency }) {
  const c1 = colors[0] || '#27c8ff';
  const c2 = colors[1] || '#9fffda';

  return (
    <>
      <CoreGlow color={coreColor} />
      {Array.from({ length: threadCount }, (_, i) => (
        <Thread
          key={i}
          offset={i * 1.8}
          spread={spread}
          frequency={frequency}
          color1={c1}
          color2={c2}
        />
      ))}
    </>
  );
}

export default function WebThreads({
  colors = ['#27c8ff', '#9fffda'],
  coreColor = '#FFFFFF',
  threadCount = 5,
  spread = 0.18,
  frequency = 3.8,
}) {
  return (
    <Canvas
      camera={{ position: [0, 0, 2], fov: 50 }}
      style={{ width: '100%', height: '100%' }}
      gl={{ alpha: true, antialias: true }}
    >
      <ThreadScene
        colors={colors}
        coreColor={coreColor}
        threadCount={threadCount}
        spread={spread}
        frequency={frequency}
      />
    </Canvas>
  );
}
