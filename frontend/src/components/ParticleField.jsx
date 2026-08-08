import { useEffect, useRef } from 'react';

export default function ParticleField({ className = '' }) {
  const hostRef = useRef(null);

  useEffect(() => {
    const host = hostRef.current;
    if (!host) return undefined;
    let cancelled = false;
    let cleanup = () => {};

    import('three').then((THREE) => {
      if (cancelled) return;
      const scene = new THREE.Scene();
      const camera = new THREE.PerspectiveCamera(38, window.innerWidth / window.innerHeight, 0.1, 100);
      camera.position.z = 12;
      const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
      renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.4));
      renderer.setSize(window.innerWidth, window.innerHeight);
      renderer.setClearColor(0x000000, 0);
      renderer.domElement.className = 'particle-canvas';
      host.appendChild(renderer.domElement);

      const count = 520;
      const positions = new Float32Array(count * 3);
      for (let index = 0; index < count; index += 1) {
        positions[index * 3] = (Math.random() - 0.5) * 18;
        positions[index * 3 + 1] = (Math.random() - 0.5) * 11;
        positions[index * 3 + 2] = (Math.random() - 0.5) * 8;
      }
      const geometry = new THREE.BufferGeometry();
      geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
      const material = new THREE.PointsMaterial({ color: 0xffa63d, size: 0.018, transparent: true, opacity: 0.5, depthWrite: false, blending: THREE.AdditiveBlending });
      const points = new THREE.Points(geometry, material);
      scene.add(points);
      const pointer = { x: 0, y: 0 };
      let frame = 0;
      const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      const onPointer = (event) => {
        pointer.x = (event.clientX / Math.max(window.innerWidth, 1) - 0.5) * 0.32;
        pointer.y = (event.clientY / Math.max(window.innerHeight, 1) - 0.5) * 0.2;
      };
      const resize = () => {
        camera.aspect = window.innerWidth / Math.max(window.innerHeight, 1);
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
      };
      const render = (time) => {
        points.rotation.y += (pointer.x - points.rotation.y) * 0.012;
        points.rotation.x += (-pointer.y - points.rotation.x) * 0.012;
        if (!reduced) points.rotation.z = Math.sin(time * 0.00008) * 0.05;
        renderer.render(scene, camera);
        if (!reduced) frame = window.requestAnimationFrame(render);
      };
      window.addEventListener('resize', resize, { passive: true });
      window.addEventListener('pointermove', onPointer, { passive: true });
      render(0);
      if (!reduced) frame = window.requestAnimationFrame(render);
      cleanup = () => {
        window.removeEventListener('resize', resize);
        window.removeEventListener('pointermove', onPointer);
        window.cancelAnimationFrame(frame);
        geometry.dispose();
        material.dispose();
        renderer.dispose();
        renderer.domElement.remove();
      };
    }).catch(() => {});

    return () => {
      cancelled = true;
      cleanup();
    };
  }, []);

  return <div ref={hostRef} className={`particle-field ${className}`} aria-hidden="true" />;
}
