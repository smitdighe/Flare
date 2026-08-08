import { useEffect, useRef } from 'react';

export default function ThreeTopology({ nodes, onFocus }) {
  const hostRef = useRef(null);
  const onFocusRef = useRef(onFocus);
  onFocusRef.current = onFocus;

  useEffect(() => {
    const host = hostRef.current;
    if (!host) return undefined;
    let cancelled = false;
    let cleanup = () => {};
    import('three').then((THREE) => {
      if (cancelled) return;
      const scene = new THREE.Scene();
      const camera = new THREE.PerspectiveCamera(35, 1, 0.1, 50);
      camera.position.z = 9;
      const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
      renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5));
      renderer.setSize(host.clientWidth, host.clientHeight);
      renderer.domElement.className = 'topology-canvas';
      host.appendChild(renderer.domElement);
      const group = new THREE.Group();
      scene.add(group);
      const pointGeometry = new THREE.SphereGeometry(0.085, 8, 8);
      const pointer = { x: 0, y: 0 };
      const meshes = nodes.map((node, index) => {
        const color = node.tone === 'critical' ? 0xff453a : node.tone === 'high' ? 0xff9500 : node.tone === 'medium' ? 0xffd60a : 0x30d158;
        const material = new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.9 });
        const mesh = new THREE.Mesh(pointGeometry, material);
        const angle = (index / Math.max(nodes.length, 1)) * Math.PI * 2;
        mesh.position.set(Math.cos(angle) * 2.25, Math.sin(angle) * 1.05, (index % 3) * 0.25 - 0.25);
        mesh.userData.node = node;
        group.add(mesh);
        return mesh;
      });
      const lineMaterial = new THREE.LineBasicMaterial({ color: 0xff9500, transparent: true, opacity: 0.18 });
      nodes.forEach((node, index) => {
        const next = nodes[(index + 1) % nodes.length];
        const geometry = new THREE.BufferGeometry().setFromPoints([meshes[index].position, meshes[(index + 1) % nodes.length].position]);
        group.add(new THREE.Line(geometry, lineMaterial));
        node.next = next;
      });
      const raycaster = new THREE.Raycaster();
      const mouse = new THREE.Vector2();
      const onPointer = (event) => {
        const rect = renderer.domElement.getBoundingClientRect();
        pointer.x = (event.clientX - rect.left) / Math.max(rect.width, 1) - 0.5;
        pointer.y = (event.clientY - rect.top) / Math.max(rect.height, 1) - 0.5;
      };
      const onClick = (event) => {
        const rect = renderer.domElement.getBoundingClientRect();
        mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
        raycaster.setFromCamera(mouse, camera);
        const hit = raycaster.intersectObjects(meshes)[0];
        if (hit?.object.userData.node) onFocusRef.current?.(hit.object.userData.node);
      };
      const resize = () => { renderer.setSize(host.clientWidth, host.clientHeight); camera.aspect = host.clientWidth / Math.max(host.clientHeight, 1); camera.updateProjectionMatrix(); };
      const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      let frame = 0;
      const render = (time) => {
        group.rotation.y += (pointer.x * 0.18 - group.rotation.y) * 0.04;
        group.rotation.x += (-pointer.y * 0.1 - group.rotation.x) * 0.04;
        if (!reduced) group.rotation.z = Math.sin(time * 0.0005) * 0.02;
        meshes.forEach((mesh, index) => { mesh.scale.setScalar(1 + (Math.sin(time * 0.003 + index) + 1) * 0.12); });
        renderer.render(scene, camera);
        if (!reduced) frame = window.requestAnimationFrame(render);
      };
      renderer.domElement.addEventListener('pointermove', onPointer, { passive: true });
      renderer.domElement.addEventListener('click', onClick);
      window.addEventListener('resize', resize, { passive: true });
      render(0);
      if (!reduced) frame = window.requestAnimationFrame(render);
      cleanup = () => {
        renderer.domElement.removeEventListener('pointermove', onPointer);
        renderer.domElement.removeEventListener('click', onClick);
        window.removeEventListener('resize', resize);
        window.cancelAnimationFrame(frame);
        group.traverse((object) => { if (object.geometry) object.geometry.dispose(); if (object.material) object.material.dispose(); });
        pointGeometry.dispose();
        lineMaterial.dispose();
        renderer.dispose();
        renderer.domElement.remove();
      };
    }).catch(() => {});
    return () => { cancelled = true; cleanup(); };
  }, [nodes]);

  return <div ref={hostRef} className="three-topology-layer" aria-label="Interactive threat topology" role="img" />;
}
