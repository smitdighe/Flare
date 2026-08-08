import { useEffect, useRef } from 'react';

const VERTEX = `attribute vec2 position; void main(){ gl_Position = vec4(position, 0.0, 1.0); }`;
const FRAGMENT = `precision mediump float;
uniform float uTime;
uniform vec2 uResolution;
uniform vec2 uPointer;
float hash(vec2 p){ return fract(sin(dot(p, vec2(127.1,311.7))) * 43758.5453); }
float noise(vec2 p){ vec2 i=floor(p), f=fract(p); f=f*f*(3.0-2.0*f); return mix(mix(hash(i),hash(i+vec2(1.0,0.0)),f.x),mix(hash(i+vec2(0.0,1.0)),hash(i+vec2(1.0,1.0)),f.x),f.y); }
void main(){
  vec2 uv=gl_FragCoord.xy/uResolution.xy; vec2 p=uv-0.5; p.x*=uResolution.x/uResolution.y;
  float t=uTime*0.06; float n=noise(p*4.0+vec2(t,-t));
  float flow=sin(p.x*3.0+p.y*2.0+t*5.0)+cos(p.y*5.0-t*3.0);
  float glow=1.0-smoothstep(0.0,0.72,length(p-vec2(uPointer.x*0.15,uPointer.y*0.12)));
  vec3 base=mix(vec3(0.012,0.012,0.012),vec3(0.055,0.037,0.018),smoothstep(-0.5,1.0,flow+n*0.38));
  base += vec3(0.42,0.16,0.015)*glow*0.075;
  base += vec3(0.24,0.08,0.01)*smoothstep(0.74,0.2,abs(p.y+sin(p.x*4.0+t)*0.08))*0.025;
  float scan=sin(uv.y*780.0+uTime*2.0)*0.008;
  gl_FragColor=vec4(base+scan,0.62);
}`;

function compile(gl, type, source) {
  const shader = gl.createShader(type);
  gl.shaderSource(shader, source);
  gl.compileShader(shader);
  if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
    gl.deleteShader(shader);
    return null;
  }
  return shader;
}

export default function ShaderBackdrop() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return undefined;
    const gl = canvas.getContext('webgl', { alpha: true, antialias: false });
    if (!gl) return undefined;
    const vertex = compile(gl, gl.VERTEX_SHADER, VERTEX);
    const fragment = compile(gl, gl.FRAGMENT_SHADER, FRAGMENT);
    if (!vertex || !fragment) return undefined;
    const program = gl.createProgram();
    gl.attachShader(program, vertex);
    gl.attachShader(program, fragment);
    gl.linkProgram(program);
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) return undefined;

    const buffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
    const position = gl.getAttribLocation(program, 'position');
    const time = gl.getUniformLocation(program, 'uTime');
    const resolution = gl.getUniformLocation(program, 'uResolution');
    const pointer = gl.getUniformLocation(program, 'uPointer');
    const pointerRef = { x: 0, y: 0 };
    let frame = 0;
    let started = false;
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    const onPointer = (event) => {
      pointerRef.x = event.clientX / Math.max(window.innerWidth, 1) - 0.5;
      pointerRef.y = event.clientY / Math.max(window.innerHeight, 1) - 0.5;
    };
    const resize = () => {
      const dpr = Math.min(window.devicePixelRatio || 1, 1.5);
      canvas.width = Math.floor(window.innerWidth * dpr);
      canvas.height = Math.floor(window.innerHeight * dpr);
      canvas.style.width = '100%';
      canvas.style.height = '100%';
      gl.viewport(0, 0, canvas.width, canvas.height);
    };
    const render = (now) => {
      frame = window.requestAnimationFrame(render);
      gl.useProgram(program);
      gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
      gl.enableVertexAttribArray(position);
      gl.vertexAttribPointer(position, 2, gl.FLOAT, false, 0, 0);
      gl.uniform1f(time, reduced ? 0 : now * 0.001);
      gl.uniform2f(resolution, canvas.width, canvas.height);
      gl.uniform2f(pointer, pointerRef.x, pointerRef.y);
      gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
      if (reduced && started) window.cancelAnimationFrame(frame);
      started = true;
    };

    resize();
    window.addEventListener('resize', resize, { passive: true });
    window.addEventListener('pointermove', onPointer, { passive: true });
    frame = window.requestAnimationFrame(render);
    return () => {
      window.removeEventListener('resize', resize);
      window.removeEventListener('pointermove', onPointer);
      window.cancelAnimationFrame(frame);
      gl.deleteBuffer(buffer);
      gl.deleteProgram(program);
      gl.deleteShader(vertex);
      gl.deleteShader(fragment);
    };
  }, []);

  return <canvas ref={canvasRef} className="shader-backdrop" aria-hidden="true" />;
}
