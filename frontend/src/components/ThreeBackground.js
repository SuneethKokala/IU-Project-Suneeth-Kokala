import React, { useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import * as THREE from 'three';

const AnimatedSprites = () => {
  const groupRef = useRef();

  useFrame(() => {
    if (groupRef.current) {
      groupRef.current.rotation.y += 0.005;
    }
  });

  const sprites = [];
  for (let i = 0; i < 20; i++) {
    sprites.push(
      <sprite
        key={i}
        position={[
          (Math.random() - 0.5) * 30,
          (Math.random() - 0.5) * 30,
          (Math.random() - 0.5) * 30
        ]}
        scale={[Math.random() * 2 + 0.5, Math.random() * 2 + 0.5, 1]}
      >
        <spriteMaterial 
          color={new THREE.Color().setHSL(Math.random(), 0.7, 0.6)}
          transparent
          opacity={0.6}
        />
      </sprite>
    );
  }

  return (
    <group ref={groupRef}>
      {sprites}
      <sprite position={[6, 5, 5]} scale={[2, 5, 1]}>
        <spriteMaterial color="#69f" />
      </sprite>
      <sprite position={[8, -2, 2]} scale={[0.1, 0.5, 0.1]}>
        <spriteMaterial color="#69f" sizeAttenuation={false} />
      </sprite>
    </group>
  );
};

const ThreeBackground = () => {
  return (
    <div style={{ 
      position: 'fixed', 
      top: 0, 
      left: 0, 
      width: '100%', 
      height: '100%', 
      zIndex: -1 
    }}>
      <Canvas camera={{ position: [15, 15, 15], fov: 50 }}>
        <color attach="background" args={['#ffffff']} />
        <AnimatedSprites />
      </Canvas>
    </div>
  );
};

export default ThreeBackground;