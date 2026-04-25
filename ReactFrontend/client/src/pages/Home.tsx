/*
Design reminder for this file — CoughNet / Bioluminescent Clinical Interface:
This page must feel like a premium diagnostic instrument rather than a generic marketing site.
Favor asymmetry, cinematic depth, telemetry-driven motion, sharp evidence framing, and clinical credibility.
Ask of every section: does this feel measured, computational, and trustworthy?
*/

import { useEffect, useMemo, useRef, useState } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import * as THREE from "three";
import {
  Accessibility,
  Activity,
  ArrowRight,
  AudioLines,
  BarChart3,
  BrainCircuit,
  Database,
  Download,
  Github,
  Globe2,
  Linkedin,
  Menu,
  Mic,
  Microscope,
  Phone,
  ShieldCheck,
  Stethoscope,
} from "lucide-react";

const HERO_BG =
  "https://d2xsxph8kpxj0f.cloudfront.net/310519663573989122/H7jnXrQGPUzwK2gemz8xEH/coughnet-hero-diagnostic-core-UhLuQS7ZqcFin2vNXhiBGp.webp";
const PROBLEM_BG =
  "https://d2xsxph8kpxj0f.cloudfront.net/310519663573989122/H7jnXrQGPUzwK2gemz8xEH/coughnet-problem-signal-field-JEVWHnYby4CMaob8fqQJYP.webp";
const PIPELINE_BG =
  "https://d2xsxph8kpxj0f.cloudfront.net/310519663573989122/H7jnXrQGPUzwK2gemz8xEH/coughnet-pipeline-atmosphere-Esp9gYHSdDhy9kVi2q3fKg.webp";
const FOOTER_BG =
  "https://d2xsxph8kpxj0f.cloudfront.net/310519663573989122/H7jnXrQGPUzwK2gemz8xEH/coughnet-footer-particle-field-FtP6j6jKn4TAC3e7jZeR2P.webp";

const navItems = [
  { id: "home", label: "Home" },
  { id: "how-it-works", label: "How It Works" },
  { id: "live-demo", label: "Live Demo" },
  { id: "research", label: "Research" },
  { id: "team", label: "Team" },
];

const stats = [
  {
    label: "People at risk from TB globally",
    end: 1.8,
    suffix: "B",
    decimals: 1,
    icon: Stethoscope,
    description:
      "A surveillance gap at this scale demands screening that works without equipment-heavy deployment.",
  },
  {
    label: "COVID-19 cases missed by conventional screening",
    end: 45,
    suffix: "M+",
    decimals: 0,
    icon: Activity,
    description:
      "Symptom-led pathways fail quietly. Passive cough analysis creates another chance to detect risk earlier.",
  },
  {
    label: "Marginal deployment cost with commodity phones",
    end: 0,
    prefix: "$",
    suffix: "",
    decimals: 0,
    icon: Phone,
    description:
      "CoughNet is architected for low-resource settings where hardware simplicity matters as much as model quality.",
  },
];

const pipelineSteps = [
  {
    title: "Mic Input",
    meta: "Web Audio API / 16kHz / 3s capture",
    detail:
      "Captures a short cough clip directly from the browser using phone or laptop microphones, preserving a lightweight, no-clinic intake flow.",
    accent: "#00E5FF",
    icon: Mic,
  },
  {
    title: "Waveform Capture",
    meta: "AnalyserNode / time-domain trace",
    detail:
      "Streams real-time time-domain amplitude into a medical-monitor style waveform so judges can see the signal become measurable immediately.",
    accent: "#3CE8FF",
    icon: AudioLines,
  },
  {
    title: "MFCC Extraction",
    meta: "40 cepstral coefficients / frame",
    detail:
      "Transforms raw cough energy into compact acoustic fingerprints suitable for downstream classification and longitudinal comparison.",
    accent: "#7B2FBE",
    icon: BarChart3,
  },
  {
    title: "CNN/RNN Model",
    meta: "In-browser inference / TF.js-ready",
    detail:
      "Demonstrates the architecture for running inference locally, keeping the privacy story strong and the deployment model simple.",
    accent: "#8B5CF6",
    icon: BrainCircuit,
  },
  {
    title: "Classification Output",
    meta: "6-class probabilities / confidence score",
    detail:
      "Surfaces interpretable probability bands and escalation logic so the product reads like a triage tool rather than a black box.",
    accent: "#00FF94",
    icon: ShieldCheck,
  },
];

const researchCards = [
  {
    title: "Cambridge COVID Cough Study",
    source: "Cambridge University",
    year: "2021",
    abstract:
      "Explored asymptomatic COVID-19 detection from cough sounds using deep learning and demonstrated that acoustic biomarkers can encode clinically relevant respiratory signals.",
    href: "https://www.repository.cam.ac.uk/items/482de9ea-8881-4c3f-aa7f-f08f30f7bbfa",
    icon: Microscope,
  },
  {
    title: "Coswara Dataset",
    source: "Indian Institute of Science",
    year: "2020",
    abstract:
      "Open-access cough, breathing, and voice dataset designed for machine-learning workflows in COVID-19 audio screening research.",
    href: "https://github.com/iiscleap/Coswara-Data",
    icon: Database,
  },
  {
    title: "FluSense",
    source: "Carnegie Mellon University",
    year: "2020",
    abstract:
      "A contactless syndromic surveillance platform combining microphone-derived cough signals and edge intelligence for population-level monitoring.",
    href: "https://www.nature.com/articles/s41591-020-0844-9",
    icon: AudioLines,
  },
];

const teamMembers = [
  {
    name: "Srijayan Pallerla",
    role: "Audio Pipeline & MFCC",
    bio: "Builds the browser-side acquisition, signal conditioning, and feature extraction flow for low-friction respiratory capture.",
    href: "https://www.linkedin.com/",
    palette: ["#00E5FF", "#7B2FBE"],
  },
  {
    name: "Siddharth Lakshmi Narayanan",
    role: "ML Model Training & API Integration",
    bio: "Focuses on classifier architecture, dataset alignment, confidence calibration for interpretable respiratory screening, and backend to frontend connection",
    href: "https://www.linkedin.com/",
    palette: ["#7B2FBE", "#00FF94"],
  },
  {
    name: "Soumil Voona",
    role: "Frontend & Visualization",
    bio: "Designs the interface layer that translates waveforms, inference states, and scientific credibility into a judge-ready experience.",
    href: "https://www.linkedin.com/",
    palette: ["#00E5FF", "#00FF94"],
  },
];

gsap.registerPlugin(ScrollTrigger);

function LogoMark() {
  return (
    <svg
      aria-hidden="true"
      viewBox="0 0 140 64"
      className="h-9 w-auto"
      fill="none"
    >
      <path
        d="M6 33C14 33 14 17 22 17C30 17 30 47 38 47C46 47 46 21 54 21C62 21 62 43 70 43C78 43 78 11 86 11C94 11 94 53 102 53C110 53 110 28 118 28C126 28 126 33 134 33"
        stroke="url(#cn-wave)"
        strokeWidth="4"
        strokeLinecap="round"
      />
      <path
        d="M49 20C41 15 29 19 24 28C19 37 22 50 33 54C44 58 53 50 57 42"
        stroke="rgba(232,244,248,0.85)"
        strokeWidth="2"
        opacity="0.7"
      />
      <path
        d="M91 20C99 15 111 19 116 28C121 37 118 50 107 54C96 58 87 50 83 42"
        stroke="rgba(232,244,248,0.85)"
        strokeWidth="2"
        opacity="0.7"
      />
      <defs>
        <linearGradient id="cn-wave" x1="6" y1="8" x2="134" y2="56">
          <stop stopColor="#00E5FF" />
          <stop offset="0.58" stopColor="#73F2FF" />
          <stop offset="1" stopColor="#7B2FBE" />
        </linearGradient>
      </defs>
    </svg>
  );
}

type CounterProps = {
  end: number;
  prefix?: string;
  suffix?: string;
  decimals?: number;
};

function MetricCounter({ end, prefix = "", suffix = "", decimals = 0 }: CounterProps) {
  const ref = useRef<HTMLSpanElement | null>(null);

  useEffect(() => {
    if (!ref.current) return;
    const target = ref.current;
    const value = { amount: 0 };

    target.textContent = `${prefix}${end.toFixed(decimals)}${suffix}`;

    const trigger = ScrollTrigger.create({
      trigger: target,
      start: "top 90%",
      once: true,
      onEnter: () => {
        gsap.fromTo(
          value,
          { amount: 0 },
          {
            amount: end,
            duration: 1.8,
            ease: "power3.out",
            onUpdate: () => {
              target.textContent = `${prefix}${value.amount.toFixed(decimals)}${suffix}`;
            },
          },
        );
      },
    });

    return () => trigger.kill();
  }, [decimals, end, prefix, suffix]);

  return <span ref={ref} />;
}

function HeroScene({ highContrast }: { highContrast: boolean }) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const container = containerRef.current;
    const canvas = canvasRef.current;
    if (!container || !canvas) return;

    const scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2("#040c12", 0.16);

    const camera = new THREE.PerspectiveCamera(46, container.clientWidth / container.clientHeight, 0.1, 100);
    camera.position.set(0, 0, 10);

    const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.8));
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.outputColorSpace = THREE.SRGBColorSpace;

    const group = new THREE.Group();
    scene.add(group);

    const lungMaterial = new THREE.MeshBasicMaterial({
      color: new THREE.Color(highContrast ? "#7AF6FF" : "#00E5FF"),
      wireframe: true,
      transparent: true,
      opacity: highContrast ? 0.46 : 0.27,
    });

    const leftLung = new THREE.Mesh(new THREE.SphereGeometry(1.6, 26, 26), lungMaterial.clone());
    leftLung.scale.set(0.92, 1.28, 0.78);
    leftLung.position.set(-1.22, -0.16, 0.05);

    const rightLung = new THREE.Mesh(new THREE.SphereGeometry(1.6, 26, 26), lungMaterial.clone());
    rightLung.scale.set(0.92, 1.28, 0.78);
    rightLung.position.set(1.22, -0.16, 0.05);

    const trachea = new THREE.Mesh(
      new THREE.CylinderGeometry(0.34, 0.46, 2.4, 18, 1, true),
      new THREE.MeshBasicMaterial({
        color: new THREE.Color(highContrast ? "#9AF7FF" : "#00E5FF"),
        wireframe: true,
        transparent: true,
        opacity: highContrast ? 0.42 : 0.22,
      }),
    );
    trachea.position.set(0, 2.05, 0.08);

    group.add(leftLung, rightLung, trachea);

    const helixGroup = new THREE.Group();
    for (let i = 0; i < 2; i += 1) {
      const points: THREE.Vector3[] = [];
      for (let step = 0; step < 120; step += 1) {
        const t = step / 16;
        const angle = t * Math.PI * 1.8 + (i === 0 ? 0 : Math.PI);
        points.push(new THREE.Vector3(Math.cos(angle) * 0.45, -2 + step * 0.038, Math.sin(angle) * 0.45));
      }
      const curve = new THREE.CatmullRomCurve3(points);
      const tube = new THREE.Mesh(
        new THREE.TubeGeometry(curve, 180, 0.06, 10, false),
        new THREE.MeshBasicMaterial({
          color: new THREE.Color(i === 0 ? "#C58CFF" : "#7B2FBE"),
          transparent: true,
          opacity: 0.85,
        }),
      );
      helixGroup.add(tube);
    }

    for (let rung = 0; rung < 14; rung += 1) {
      const y = -1.75 + rung * 0.32;
      const geo = new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(-0.35, y, 0),
        new THREE.Vector3(0.35, y, 0),
      ]);
      const line = new THREE.Line(
        geo,
        new THREE.LineBasicMaterial({ color: new THREE.Color(rung % 2 === 0 ? "#E8B8FF" : "#AE7AFF"), transparent: true, opacity: 0.4 }),
      );
      helixGroup.add(line);
    }

    group.add(helixGroup);

    const spectrogramCanvas = document.createElement("canvas");
    spectrogramCanvas.width = 512;
    spectrogramCanvas.height = 64;
    const spectrogramContext = spectrogramCanvas.getContext("2d");
    if (spectrogramContext) {
      const gradient = spectrogramContext.createLinearGradient(0, 0, 512, 0);
      gradient.addColorStop(0, "#0a102a");
      gradient.addColorStop(0.28, "#00E5FF");
      gradient.addColorStop(0.68, "#FFF27A");
      gradient.addColorStop(1, "#FF5C5C");
      spectrogramContext.fillStyle = "#06141d";
      spectrogramContext.fillRect(0, 0, 512, 64);
      for (let x = 0; x < 512; x += 10) {
        const h = 18 + Math.sin(x * 0.035) * 12 + Math.random() * 18;
        spectrogramContext.fillStyle = gradient;
        spectrogramContext.globalAlpha = 0.8;
        spectrogramContext.fillRect(x, 32 - h / 2, 8, h);
      }
      spectrogramContext.globalAlpha = 1;
    }
    const spectrogramTexture = new THREE.CanvasTexture(spectrogramCanvas);
    spectrogramTexture.needsUpdate = true;

    const ring = new THREE.Mesh(
      new THREE.TorusGeometry(3.24, 0.22, 24, 180),
      new THREE.MeshBasicMaterial({ map: spectrogramTexture, transparent: true, opacity: 0.95 }),
    );
    ring.rotation.x = Math.PI / 2.4;
    group.add(ring);

    const particlesGeometry = new THREE.BufferGeometry();
    const particleCount = 900;
    const particlePositions = new Float32Array(particleCount * 3);
    for (let i = 0; i < particleCount; i += 1) {
      particlePositions[i * 3] = (Math.random() - 0.5) * 16;
      particlePositions[i * 3 + 1] = (Math.random() - 0.5) * 10;
      particlePositions[i * 3 + 2] = (Math.random() - 0.5) * 12;
    }
    particlesGeometry.setAttribute("position", new THREE.BufferAttribute(particlePositions, 3));
    const particles = new THREE.Points(
      particlesGeometry,
      new THREE.PointsMaterial({
        color: new THREE.Color("#7edfff"),
        size: 0.03,
        transparent: true,
        opacity: 0.7,
      }),
    );
    scene.add(particles);

    const ambient = new THREE.AmbientLight("#77eaff", 0.8);
    const violet = new THREE.PointLight("#7b2fbe", 9, 25, 2);
    violet.position.set(0.8, 0.7, 3.4);
    const cyan = new THREE.PointLight("#00e5ff", 10, 30, 2);
    cyan.position.set(-2.4, 1.4, 2.8);
    scene.add(ambient, violet, cyan);

    gsap.to(group.scale, {
      x: 1.04,
      y: 1.07,
      z: 1.04,
      duration: 2.4,
      repeat: -1,
      yoyo: true,
      ease: "sine.inOut",
    });

    gsap.to(helixGroup.rotation, {
      y: Math.PI * 2,
      duration: 12,
      repeat: -1,
      ease: "none",
    });

    gsap.to(ring.rotation, {
      z: Math.PI * 2,
      duration: 16,
      repeat: -1,
      ease: "none",
    });

    const section = container.closest("section");
    const scrub = section
      ? ScrollTrigger.create({
          trigger: section,
          start: "top top",
          end: "bottom top",
          scrub: true,
          onUpdate: ({ progress }) => {
            group.rotation.y = progress * 1.4;
            group.rotation.x = progress * 0.35;
            group.position.z = progress * -1.8;
            group.position.x = progress * 1.3;
            group.position.y = progress * -0.8;
            group.scale.setScalar(1 - progress * 0.22);
            (particles.material as THREE.PointsMaterial).opacity = 0.45 + progress * 0.35;
          },
        })
      : null;

    const clock = new THREE.Clock();
    let frame = 0;

    const onResize = () => {
      const width = container.clientWidth;
      const height = container.clientHeight;
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      renderer.setSize(width, height);
    };

    const animate = () => {
      frame = requestAnimationFrame(animate);
      const elapsed = clock.getElapsedTime();
      group.rotation.z = Math.sin(elapsed * 0.5) * 0.06;
      particles.rotation.y = elapsed * 0.02;
      particles.rotation.x = Math.sin(elapsed * 0.14) * 0.03;
      renderer.render(scene, camera);
    };

    onResize();
    window.addEventListener("resize", onResize);
    animate();

    return () => {
      cancelAnimationFrame(frame);
      window.removeEventListener("resize", onResize);
      scrub?.kill();
      renderer.dispose();
      leftLung.geometry.dispose();
      rightLung.geometry.dispose();
      trachea.geometry.dispose();
      ring.geometry.dispose();
      spectrogramTexture.dispose();
      particlesGeometry.dispose();
      lungMaterial.dispose();
      scene.clear();
    };
  }, [highContrast]);

  return (
    <div ref={containerRef} className="absolute inset-0 overflow-hidden">
      <div
        className="absolute inset-0 opacity-45"
        style={{
          backgroundImage: `radial-gradient(circle at center, rgba(0,229,255,0.14), transparent 36%), linear-gradient(180deg, rgba(4,12,18,0.06), rgba(4,12,18,0.85)), url(${HERO_BG})`,
          backgroundPosition: "center",
          backgroundSize: "cover",
        }}
      />
      <canvas ref={canvasRef} className="absolute inset-0 h-full w-full" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,transparent_36%,rgba(4,12,18,0.68)_80%)]" />
    </div>
  );
}

function GeometricAvatar({ palette }: { palette: string[] }) {
  return (
    <div className="relative h-24 w-24 overflow-hidden rounded-full border border-white/10 bg-[#08121a] shadow-[0_0_40px_rgba(0,229,255,0.1)]">
      <div
        className="absolute inset-0 opacity-80"
        style={{
          background: `radial-gradient(circle at 35% 30%, ${palette[0]}55, transparent 34%), radial-gradient(circle at 70% 65%, ${palette[1]}66, transparent 28%), linear-gradient(160deg, rgba(8,18,26,0.4), rgba(4,12,18,0.95))`,
        }}
      />
      <div className="absolute left-3 top-4 h-8 w-8 rounded-lg border border-white/20 rotate-12" style={{ background: `${palette[0]}22` }} />
      <div className="absolute right-4 top-8 h-10 w-10 rounded-full border border-white/15" style={{ background: `${palette[1]}28` }} />
      <div className="absolute bottom-3 left-6 h-12 w-12 rounded-[1.2rem] border border-white/10 rotate-[28deg]" style={{ background: `${palette[0]}18` }} />
      <div className="absolute inset-x-4 bottom-5 h-px bg-white/25" />
    </div>
  );
}

function LiveDemo({ highContrast }: { highContrast: boolean }) {
  const waveformRef = useRef<HTMLCanvasElement | null>(null);
  const spectrogramRef = useRef<HTMLCanvasElement | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const sourceRef = useRef<MediaStreamAudioSourceNode | null>(null);
  const animationRef = useRef<number>(0);
  const timeoutRef = useRef<number | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [remaining, setRemaining] = useState(3);
  const [status, setStatus] = useState("Awaiting microphone input.");
  const [downloadUrl, setDownloadUrl] = useState("");
  const [predictions, setPredictions] = useState<Record<string, number> | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isMock, setIsMock] = useState(false);
  const [topPrediction, setTopPrediction] = useState<string | null>(null);

  // Backend URL — configurable via VITE_API_URL environment variable
  // Default: http://127.0.0.1:8000 (local FastAPI server)
  const API_BASE = (import.meta.env.VITE_API_URL as string | undefined) ?? "http://127.0.0.1:8000";

  useEffect(() => {
    const waveformCanvas = waveformRef.current;
    const spectrogramCanvas = spectrogramRef.current;
    if (!waveformCanvas || !spectrogramCanvas) return;

    const waveformContext = waveformCanvas.getContext("2d");
    const spectrogramContext = spectrogramCanvas.getContext("2d");
    if (!waveformContext || !spectrogramContext) return;

    const resize = () => {
      const waveformRect = waveformCanvas.getBoundingClientRect();
      waveformCanvas.width = waveformRect.width * Math.min(window.devicePixelRatio, 2);
      waveformCanvas.height = waveformRect.height * Math.min(window.devicePixelRatio, 2);
      waveformContext.setTransform(Math.min(window.devicePixelRatio, 2), 0, 0, Math.min(window.devicePixelRatio, 2), 0, 0);

      const spectrogramRect = spectrogramCanvas.getBoundingClientRect();
      spectrogramCanvas.width = spectrogramRect.width * Math.min(window.devicePixelRatio, 2);
      spectrogramCanvas.height = spectrogramRect.height * Math.min(window.devicePixelRatio, 2);
      spectrogramContext.setTransform(Math.min(window.devicePixelRatio, 2), 0, 0, Math.min(window.devicePixelRatio, 2), 0, 0);
    };

    const drawIdle = () => {
      const width = waveformCanvas.clientWidth;
      const height = waveformCanvas.clientHeight;
      waveformContext.clearRect(0, 0, width, height);
      waveformContext.fillStyle = "rgba(4, 12, 18, 0.9)";
      waveformContext.fillRect(0, 0, width, height);
      waveformContext.strokeStyle = highContrast ? "rgba(122, 246, 255, 0.9)" : "rgba(0, 229, 255, 0.7)";
      waveformContext.lineWidth = 2;
      waveformContext.beginPath();
      waveformContext.moveTo(0, height / 2);
      for (let x = 0; x <= width; x += 10) {
        waveformContext.lineTo(x, height / 2 + Math.sin(x * 0.02) * 2);
      }
      waveformContext.stroke();

      const sWidth = spectrogramCanvas.clientWidth;
      const sHeight = spectrogramCanvas.clientHeight;
      spectrogramContext.clearRect(0, 0, sWidth, sHeight);
      spectrogramContext.fillStyle = "rgba(4,12,18,0.92)";
      spectrogramContext.fillRect(0, 0, sWidth, sHeight);
      const gradient = spectrogramContext.createLinearGradient(0, 0, sWidth, 0);
      gradient.addColorStop(0, "rgba(10,22,60,0.5)");
      gradient.addColorStop(0.5, "rgba(0,229,255,0.16)");
      gradient.addColorStop(1, "rgba(123,47,190,0.22)");
      spectrogramContext.fillStyle = gradient;
      spectrogramContext.fillRect(0, sHeight / 2 - 6, sWidth, 12);
    };

    resize();
    drawIdle();
    window.addEventListener("resize", resize);
    return () => window.removeEventListener("resize", resize);
  }, [highContrast]);

  const stopVisuals = () => {
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
      animationRef.current = 0;
    }
    if (timeoutRef.current) {
      window.clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
  };

  const cleanupAudio = () => {
    stopVisuals();
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
    sourceRef.current?.disconnect();
    analyserRef.current?.disconnect();
    sourceRef.current = null;
    analyserRef.current = null;
    audioContextRef.current?.close().catch(() => undefined);
    audioContextRef.current = null;
  };

  const drawActiveFrames = () => {
    const waveformCanvas = waveformRef.current;
    const spectrogramCanvas = spectrogramRef.current;
    const analyser = analyserRef.current;
    if (!waveformCanvas || !spectrogramCanvas || !analyser) return;
    const waveformContext = waveformCanvas.getContext("2d");
    const spectrogramContext = spectrogramCanvas.getContext("2d");
    if (!waveformContext || !spectrogramContext) return;

    const waveformData = new Uint8Array(analyser.fftSize);
    const frequencyData = new Uint8Array(analyser.frequencyBinCount);

    const render = () => {
      const width = waveformCanvas.clientWidth;
      const height = waveformCanvas.clientHeight;
      analyser.getByteTimeDomainData(waveformData);
      waveformContext.clearRect(0, 0, width, height);
      waveformContext.fillStyle = "rgba(4, 12, 18, 0.95)";
      waveformContext.fillRect(0, 0, width, height);
      waveformContext.strokeStyle = highContrast ? "#8EF8FF" : "#00E5FF";
      waveformContext.lineWidth = 2;
      waveformContext.beginPath();
      const sliceWidth = width / waveformData.length;
      let x = 0;
      for (let i = 0; i < waveformData.length; i += 1) {
        const v = waveformData[i] / 128.0;
        const y = (v * height) / 2;
        if (i === 0) waveformContext.moveTo(x, y);
        else waveformContext.lineTo(x, y);
        x += sliceWidth;
      }
      waveformContext.stroke();

      const sWidth = spectrogramCanvas.clientWidth;
      const sHeight = spectrogramCanvas.clientHeight;
      analyser.getByteFrequencyData(frequencyData);
      const image = spectrogramContext.getImageData(1, 0, sWidth - 1, sHeight);
      spectrogramContext.putImageData(image, 0, 0);
      for (let y = 0; y < sHeight; y += 1) {
        const idx = Math.floor((y / sHeight) * frequencyData.length);
        const intensity = frequencyData[idx] / 255;
        const r = Math.floor(255 * Math.max(0, intensity - 0.48) * 1.9);
        const g = Math.floor(230 * Math.min(1, intensity * 1.2));
        const b = Math.floor(255 * (0.35 + intensity * 0.7));
        spectrogramContext.fillStyle = `rgb(${r}, ${g}, ${b})`;
        spectrogramContext.fillRect(sWidth - 1, sHeight - y, 1, 1);
      }

      animationRef.current = requestAnimationFrame(render);
    };

    render();
  };

  const stopRecording = () => {
    if (!isRecording) return;
    setIsRecording(false);
    setRemaining(3);
      setStatus("Recording complete. Sending to classifier...");
    mediaRecorderRef.current?.stop();
    cleanupAudio();
  };

  const startRecording = async () => {
    if (isRecording) return;
    try {
      setStatus("Recording… hold for 3 seconds.");
      setIsMock(false);
      setTopPrediction(null);
      if (downloadUrl) URL.revokeObjectURL(downloadUrl);
      setDownloadUrl("");
      setPredictions(null);
      setIsProcessing(false);
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      const audioContext = new window.AudioContext();
      const source = audioContext.createMediaStreamSource(stream);
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 2048;
      analyser.smoothingTimeConstant = 0.84;
      source.connect(analyser);
      sourceRef.current = source;
      analyserRef.current = analyser;
      audioContextRef.current = audioContext;

      const recorder = new MediaRecorder(stream);
      mediaRecorderRef.current = recorder;
      chunksRef.current = [];
      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) chunksRef.current.push(event.data);
      };
      recorder.onstop = async () => {
        const blob = new Blob(chunksRef.current, { type: recorder.mimeType || "audio/webm" });
        const url = URL.createObjectURL(blob);
        setDownloadUrl(url);
        
        // Send to FastAPI backend
        setIsProcessing(true);
        setStatus("Analyzing audio...");
        const startTime = Date.now();
        console.log("Recording blob size:", blob.size, "type:", blob.type);
        
        try {
          const formData = new FormData();
          formData.append("audio", blob, "recording.webm");
          
          const apiUrl = `${API_BASE}/predict`;
          console.log("Sending to", apiUrl);
          
          // Update status every second while waiting
          const statusInterval = setInterval(() => {
            const elapsedSeconds = Math.round((Date.now() - startTime) / 1000);
            setStatus(`Analyzing audio... (${elapsedSeconds}s)`);
          }, 1000);
          
          const response = await fetch(apiUrl, {
            method: "POST",
            body: formData,
          });
          
          clearInterval(statusInterval);
          const elapsedSeconds = ((Date.now() - startTime) / 1000).toFixed(2);
          console.log("Response status:", response.status, response.statusText, `(${elapsedSeconds}s)`);
          
          const data = await response.json();
          console.log("Response data:", data);
          
          if (response.ok) {
            if (data.prediction && data.prediction.all_probabilities) {
              // Extract probabilities from response
              const predDict = data.prediction.all_probabilities;
              console.log("Probabilities:", predDict);
              setPredictions(predDict);
              setTopPrediction(data.prediction.predicted_disease);
              setIsMock(data.prediction.mock === true);
              const processingTime = data.processing_time ? data.processing_time.toFixed(2) : elapsedSeconds;
              setStatus(`✓ ${data.prediction.predicted_disease} — ${(data.prediction.confidence * 100).toFixed(1)}% confidence (${processingTime}s)`);
            } else {
              setStatus("Received response but no predictions found");
              console.error("Invalid response format:", data);
            }
          } else {
            const errorMsg = data.detail || data.error || response.statusText;
            setStatus(`Error: ${errorMsg}`);
            console.error("API error response:", data);
          }
        } catch (error) {
          const errorMsg = error instanceof Error ? error.message : "Unknown error";
          setStatus(`Connection error: ${errorMsg}. Make sure the backend is running on ${API_BASE}`);
          console.error("Full API error:", error);
        } finally {
          setIsProcessing(false);
        }
      };

      recorder.start();
      setIsRecording(true);
      setRemaining(3);
      drawActiveFrames();

      const startedAt = Date.now();
      const tick = () => {
        const elapsed = (Date.now() - startedAt) / 1000;
        const left = Math.max(0, 3 - elapsed);
        setRemaining(Number(left.toFixed(1)));
        if (left > 0 && isRecording) {
          timeoutRef.current = window.setTimeout(tick, 100);
        }
      };
      tick();

      timeoutRef.current = window.setTimeout(() => stopRecording(), 3000);
    } catch (error: any) {
      let errorMsg = "Microphone access was blocked. Allow access to test the capture pipeline.";
      
      if (error.name === "NotAllowedError") {
        errorMsg = "Microphone permission denied. Check: 1) Browser site permissions 2) macOS System Settings > Privacy & Security > Microphone";
      } else if (error.name === "NotFoundError") {
        errorMsg = "No microphone found on this device.";
      } else if (error.name === "NotReadableError") {
        errorMsg = "Microphone is in use by another app. Close other audio apps and retry.";
      }
      
      setStatus(errorMsg);
      cleanupAudio();
      setIsRecording(false);
    }
  };

  useEffect(() => {
    return () => {
      if (downloadUrl) URL.revokeObjectURL(downloadUrl);
      cleanupAudio();
    };
  }, [downloadUrl]);

  return (
    <div className="diagnostic-card diag-border overflow-hidden p-5 sm:p-7 lg:p-8">
      <div className="grid gap-8 xl:grid-cols-[1.2fr_0.8fr]">
        <div className="space-y-6">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="mono-label text-xs">Interactive intake module</p>
              <h3 className="mt-2 text-3xl font-bold text-white">Hear It for Yourself</h3>
            </div>
            <div className="rounded-full border border-cyan-400/20 bg-cyan-400/8 px-4 py-2 font-mono text-xs text-cyan-100/75">
              Browser microphone · local capture · no upload required
            </div>
          </div>

          <div className="grid gap-7 xl:grid-cols-[0.74fr_1fr]">
            <div className="rounded-[1.5rem] border border-cyan-300/14 bg-[#05111a]/90 p-6 shadow-[0_24px_80px_rgba(0,0,0,0.25)] xl:p-7">
              <div className="flex min-h-[260px] flex-col items-center justify-center gap-4 text-center">
                <button
                  aria-label={isRecording ? "Recording in progress" : "Hold to record a cough sample"}
                  className={`relative flex h-40 w-40 items-center justify-center rounded-full border text-center transition-transform ${
                    isRecording
                      ? "border-red-400/50 bg-red-500/12 text-red-100"
                      : "border-cyan-300/30 bg-cyan-400/8 text-cyan-50"
                  }`}
                  onPointerDown={startRecording}
                  onPointerUp={stopRecording}
                  onPointerLeave={stopRecording}
                  onKeyDown={(event) => {
                    if ((event.key === " " || event.key === "Enter") && !isRecording) {
                      event.preventDefault();
                      startRecording();
                    }
                  }}
                  onKeyUp={(event) => {
                    if (event.key === " " || event.key === "Enter") {
                      event.preventDefault();
                      stopRecording();
                    }
                  }}
                >
                  <span
                    className={`absolute inset-0 rounded-full ${
                      isRecording ? "animate-ping bg-red-500/16" : "animate-pulse bg-cyan-400/10"
                    }`}
                  />
                  <span className="relative z-10 flex flex-col items-center gap-3">
                    <Mic className={`h-8 w-8 ${isRecording ? "text-red-200" : "text-cyan-200"}`} />
                    <span className="font-[Space_Grotesk] text-lg font-bold">
                      {isRecording ? `Recording… ${remaining.toFixed(1)}s` : "Hold to Record"}
                    </span>
                  </span>
                </button>

                <p className="font-mono text-sm text-[#00FF94]">{status}</p>

                {downloadUrl ? (
                  <div className="flex flex-col items-center gap-2">
                    <a
                      href={downloadUrl}
                      download="coughnet-recording.webm"
                      className="inline-flex items-center gap-2 rounded-full border border-cyan-300/20 bg-white/4 px-4 py-2 font-[Space_Grotesk] text-sm font-bold text-cyan-50"
                    >
                      <Download className="h-4 w-4" />
                      Download Recording
                    </a>
                    {predictions && (
                      <button
                        onClick={() => {
                          URL.revokeObjectURL(downloadUrl);
                          setDownloadUrl("");
                          setPredictions(null);
                          setTopPrediction(null);
                          setIsMock(false);
                          setStatus("Awaiting microphone input.");
                        }}
                        className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/4 px-4 py-2 font-[Space_Grotesk] text-sm font-bold text-slate-200"
                      >
                        &#8635; Re-record
                      </button>
                    )}
                  </div>
                ) : null}
              </div>
            </div>

            <div className="space-y-5">
              <div className="canvas-frame overflow-hidden p-4">
                <div className="mb-3 flex items-center justify-between">
                  <p className="mono-label text-[11px]">Waveform capture</p>
                  <span className="font-mono text-xs text-cyan-100/65">time-domain / analyser node</span>
                </div>
                <canvas ref={waveformRef} className="h-36 w-full" />
              </div>
              <div className="canvas-frame overflow-hidden p-4">
                <div className="mb-3 flex items-center justify-between">
                  <p className="mono-label text-[11px]">Spectrogram display</p>
                  <span className="font-mono text-xs text-cyan-100/65">frequency-domain / real-time scroll</span>
                </div>
                <canvas ref={spectrogramRef} className="h-40 w-full" />
              </div>
            </div>
          </div>
        </div>

        <div className="rounded-[1.5rem] border border-white/10 bg-white/[0.03] p-5 sm:p-6 xl:p-7">
          <div className="space-y-4">
            <div>
              <p className="mono-label text-xs">{isProcessing ? "Processing..." : "Inference output"}</p>
              <h4 className="mt-2 text-2xl font-bold text-white">Probability distribution</h4>
              <p className="mt-2 font-mono text-sm text-slate-300/70">
                {status}
              </p>
            </div>

            {predictions
              ? [
                  { label: "COVID-19", color: "#FF4D4D" },
                  { label: "Tuberculosis", color: "#FF8A3D" },
                  { label: "Pneumonia", color: "#C084FC" },
                  { label: "Bronchitis", color: "#FFB82F" },
                  { label: "Asthma", color: "#FDE047" },
                  { label: "Cold Cough", color: "#87CEEB" },
                  { label: "Healthy", color: "#00FF94" },
                ]
                  .map((item) => {
                    const value = predictions[item.label] ?? 0;
                    const isTop = item.label === topPrediction;
                    return (
                      <div key={item.label} className="space-y-2">
                        <div className="flex items-center justify-between font-mono text-xs text-slate-200/80">
                          <span className={isTop ? "font-bold text-white" : ""}>
                            {item.label}{isTop ? " ★" : ""}
                          </span>
                          <span>{Math.round(value * 100)}%</span>
                        </div>
                        <div className="progress-track h-3">
                          <div
                            className="progress-fill h-full"
                            style={{ width: `${value * 100}%`, backgroundColor: item.color, color: item.color }}
                          />
                        </div>
                      </div>
                    );
                  })
              : [
                  { label: "Healthy", value: 0.21, color: "#00FF94" },
                  { label: "Cold Cough", value: 0.16, color: "#87CEEB" },
                  { label: "COVID-19", value: 0.15, color: "#FF4D4D" },
                  { label: "Tuberculosis", value: 0.16, color: "#FF8A3D" },
                  { label: "Bronchitis", value: 0.16, color: "#FFB82F" },
                  { label: "Asthma", value: 0.16, color: "#FDE047" },
                ].map((item) => (
                  <div key={item.label} className="space-y-2">
                    <div className="flex items-center justify-between font-mono text-xs text-slate-200/80">
                      <span>{item.label}</span>
                      <span>{Math.round(item.value * 100)}%</span>
                    </div>
                    <div className="progress-track h-3">
                      <div
                        className="progress-fill h-full"
                        style={{ width: `${item.value * 100}%`, backgroundColor: item.color, color: item.color }}
                      />
                    </div>
                  </div>
                ))}

            {/* Dynamic escalation banner — shown when a high-risk class exceeds 50% confidence */}
            {predictions && (() => {
              const highRisk = ["COVID-19", "Tuberculosis", "Pneumonia"];
              const riskClass = highRisk.find((cls) => (predictions[cls] ?? 0) > 0.50);
              return riskClass ? (
                <div className="rounded-2xl border border-red-400/20 bg-red-500/10 px-4 py-3 text-sm text-red-100">
                  <div className="flex items-start gap-3">
                    <span className="mt-0.5 inline-flex h-2.5 w-2.5 rounded-full bg-red-400 shadow-[0_0_18px_rgba(255,77,77,0.9)]" />
                    <div>
                      <p className="font-[Space_Grotesk] font-bold">Consult a healthcare provider</p>
                      <p className="mt-1 text-red-100/80">
                        {riskClass} probability exceeds the 50% escalation threshold. This is not a medical diagnosis.
                      </p>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="rounded-2xl border border-green-400/20 bg-green-500/10 px-4 py-3 text-sm text-green-100">
                  <div className="flex items-start gap-3">
                    <span className="mt-0.5 inline-flex h-2.5 w-2.5 rounded-full bg-green-400" />
                    <p>No high-risk indicators detected above the 50% threshold.</p>
                  </div>
                </div>
              );
            })()}

            {/* Mock mode disclaimer */}
            {isMock && predictions && (
              <div className="rounded-2xl border border-yellow-400/20 bg-yellow-500/8 px-4 py-3 text-sm text-yellow-100/80">
                ⚠️ Demo mode — results are simulated. Load <code className="font-mono text-xs">cough_classifier.pt</code> for real inference.
              </div>
            )}

            {!predictions && (
              <div className="rounded-2xl border border-cyan-300/10 bg-cyan-400/[0.04] p-4 text-sm text-slate-200/75">
                Hold the record button, cough for 3 seconds, then release to see the probability distribution.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function Home() {
  const [activeSection, setActiveSection] = useState("home");
  const [scrollProgress, setScrollProgress] = useState(0);
  const [navOpen, setNavOpen] = useState(false);
  const [language, setLanguage] = useState("EN");
  const [highContrast, setHighContrast] = useState(false);
  const logoPathRef = useRef<SVGPathElement | null>(null);

  const sections = useMemo(() => navItems.map((item) => item.id), []);

  useEffect(() => {
    const onScroll = () => {
      const total = document.documentElement.scrollHeight - window.innerHeight;
      setScrollProgress(total > 0 ? (window.scrollY / total) * 100 : 0);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    const visibility = new Map<string, number>();
    sections.forEach((id) => visibility.set(id, 0));

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          visibility.set(entry.target.id, entry.isIntersecting ? entry.intersectionRatio : 0);
        });

        let bestSection: string | null = null;
        let bestRatio = 0;
        visibility.forEach((ratio, id) => {
          if (ratio > bestRatio) {
            bestRatio = ratio;
            bestSection = id;
          }
        });

        if (bestSection) setActiveSection(bestSection);
      },
      {
        threshold: [0, 0.2, 0.4, 0.6],
        rootMargin: "-15% 0px -25% 0px",
      },
    );

    sections.forEach((id) => {
      const section = document.getElementById(id);
      if (section) observer.observe(section);
    });

    return () => observer.disconnect();
  }, [sections]);

  useEffect(() => {
    document.documentElement.classList.toggle("contrast-more", highContrast);
  }, [highContrast]);

  useEffect(() => {
    const ctx = gsap.context(() => {
      const logoPath = logoPathRef.current;
      if (logoPath) {
        const length = logoPath.getTotalLength();
        gsap.set(logoPath, { strokeDasharray: length, strokeDashoffset: length });
        gsap.to(logoPath, { strokeDashoffset: 0, duration: 1.2, ease: "power2.out" });
      }

      gsap.from("[data-hero-item]", {
        opacity: 0,
        y: 36,
        duration: 0.9,
        ease: "power3.out",
        stagger: 0.12,
        delay: 0.35,
      });

      gsap.utils.toArray<HTMLElement>("[data-reveal]").forEach((element) => {
        gsap.from(element, {
          opacity: 0,
          y: 40,
          duration: 0.85,
          ease: "power3.out",
          scrollTrigger: {
            trigger: element,
            start: "top 80%",
          },
        });
      });

      gsap.utils.toArray<HTMLElement>("[data-stagger-group]").forEach((group) => {
        gsap.from(group.children, {
          opacity: 0,
          y: 24,
          duration: 0.7,
          stagger: 0.12,
          ease: "power3.out",
          scrollTrigger: {
            trigger: group,
            start: "top 80%",
          },
        });
      });

      gsap.utils.toArray<HTMLElement>("[data-hover-lift]").forEach((element) => {
        const enter = () =>
          gsap.to(element, {
            y: -8,
            scale: 1.015,
            borderColor: "rgba(0,229,255,0.32)",
            boxShadow: "0 22px 70px rgba(0,229,255,0.14)",
            duration: 0.28,
            ease: "power2.out",
          });
        const leave = () =>
          gsap.to(element, {
            y: 0,
            scale: 1,
            borderColor: "rgba(0,229,255,0.14)",
            boxShadow: "0 28px 70px rgba(0,0,0,0.24)",
            duration: 0.28,
            ease: "power2.out",
          });

        element.addEventListener("mouseenter", enter);
        element.addEventListener("mouseleave", leave);

        return () => {
          element.removeEventListener("mouseenter", enter);
          element.removeEventListener("mouseleave", leave);
        };
      });
    });

    return () => {
      ctx.revert();
      ScrollTrigger.getAll().forEach((trigger) => trigger.kill());
    };
  }, []);

  const scrollTo = (id: string) => {
    const section = document.getElementById(id);
    if (section) {
      section.scrollIntoView({ behavior: "smooth", block: "start" });
      setNavOpen(false);
    }
  };

  return (
    <div className={`${highContrast ? "[--contrast-glow:0_0_0_1px_rgba(122,246,255,0.34)]" : ""} relative min-h-screen overflow-hidden`}>
      <header className="fixed inset-x-0 top-0 z-50 px-3 pt-3 sm:px-5">
        <div className="mx-auto max-w-[1380px] overflow-hidden rounded-[1.4rem] border border-cyan-300/10 bg-[#07121aaa] shadow-[0_10px_50px_rgba(0,0,0,0.28)] backdrop-blur-2xl">
          <div className="h-[2px] w-full bg-white/5">
            <div className="h-full bg-cyan-300 shadow-[0_0_16px_rgba(0,229,255,0.9)]" style={{ width: `${scrollProgress}%` }} />
          </div>
          <div className="flex items-center justify-between gap-4 px-4 py-3 lg:px-6">
            <button aria-label="Go to home section" className="flex items-center gap-3" onClick={() => scrollTo("home")}>
              <div className="shrink-0">
                <svg viewBox="0 0 140 64" className="h-10 w-auto" fill="none">
                  <path
                    ref={logoPathRef}
                    d="M6 33C14 33 14 17 22 17C30 17 30 47 38 47C46 47 46 21 54 21C62 21 62 43 70 43C78 43 78 11 86 11C94 11 94 53 102 53C110 53 110 28 118 28C126 28 126 33 134 33"
                    stroke="url(#nav-wave)"
                    strokeWidth="4"
                    strokeLinecap="round"
                  />
                  <path d="M49 20C41 15 29 19 24 28C19 37 22 50 33 54C44 58 53 50 57 42" stroke="rgba(232,244,248,0.8)" strokeWidth="2" opacity="0.72" />
                  <path d="M91 20C99 15 111 19 116 28C121 37 118 50 107 54C96 58 87 50 83 42" stroke="rgba(232,244,248,0.8)" strokeWidth="2" opacity="0.72" />
                  <defs>
                    <linearGradient id="nav-wave" x1="6" y1="8" x2="134" y2="56">
                      <stop stopColor="#00E5FF" />
                      <stop offset="1" stopColor="#7B2FBE" />
                    </linearGradient>
                  </defs>
                </svg>
              </div>
              <div className="text-left">
                <div className="font-[Space_Grotesk] text-lg font-bold tracking-[-0.05em] text-white">
                  Cough<span className="text-cyan-300">Net</span>
                </div>
                <div className="font-mono text-[10px] uppercase tracking-[0.24em] text-slate-300/55">Passive respiratory screening</div>
              </div>
            </button>

            <nav className="hidden items-center gap-7 lg:flex">
              {navItems.map((item) => (
                <button
                  key={item.id}
                  aria-label={`Go to ${item.label}`}
                  className={`relative font-[Space_Grotesk] text-sm font-medium tracking-[-0.02em] ${
                    activeSection === item.id ? "text-cyan-200" : "text-slate-200/76"
                  }`}
                  onClick={() => scrollTo(item.id)}
                >
                  {item.label}
                  <span
                    className={`absolute -bottom-2 left-0 h-px bg-cyan-300 shadow-[0_0_14px_rgba(0,229,255,0.8)] transition-all ${
                      activeSection === item.id ? "w-full" : "w-0"
                    }`}
                  />
                </button>
              ))}
            </nav>

            <div className="hidden items-center gap-3 lg:flex">
              <label className="flex items-center gap-2 rounded-full border border-white/10 bg-white/4 px-3 py-2 text-xs text-slate-200/75">
                <Globe2 className="h-4 w-4 text-cyan-300" />
                <select
                  name="language"
                  id="language-selector"
                  aria-label="Language selector"
                  value={language}
                  onChange={(event) => setLanguage(event.target.value)}
                  className="bg-transparent font-mono outline-none"
                >
                  <option className="bg-[#07121a]" value="EN">EN</option>
                  <option className="bg-[#07121a]" value="ES">ES</option>
                  <option className="bg-[#07121a]" value="FR">FR</option>
                  <option className="bg-[#07121a]" value="HI">HI</option>
                </select>
              </label>
              <button
                aria-label="Toggle accessibility contrast mode"
                className={`rounded-full border px-3 py-2 ${
                  highContrast ? "border-cyan-300/40 bg-cyan-400/12 text-cyan-100" : "border-white/10 bg-white/4 text-slate-200/75"
                }`}
                onClick={() => setHighContrast((value) => !value)}
              >
                <Accessibility className="h-4 w-4" />
              </button>
              <button aria-label="Try the demo" className="cyan-button px-5 py-3 text-sm" onClick={() => scrollTo("live-demo")}>
                Try the Demo
              </button>
            </div>

            <button
              aria-label="Open navigation"
              className="rounded-full border border-white/10 bg-white/4 p-3 text-slate-100 lg:hidden"
              onClick={() => setNavOpen((value) => !value)}
            >
              <Menu className="h-4 w-4" />
            </button>
          </div>

          {navOpen ? (
            <div className="border-t border-white/8 px-4 py-4 lg:hidden">
              <div className="grid gap-3">
                {navItems.map((item) => (
                  <button
                    key={item.id}
                    aria-label={`Go to ${item.label}`}
                    className="rounded-2xl border border-white/8 bg-white/4 px-4 py-3 text-left font-[Space_Grotesk] text-slate-100"
                    onClick={() => scrollTo(item.id)}
                  >
                    {item.label}
                  </button>
                ))}
                <div className="flex items-center gap-3 pt-2">
                  <button className="ghost-button flex-1 px-4 py-3 text-sm" onClick={() => setHighContrast((value) => !value)}>
                    Contrast
                  </button>
                  <button className="cyan-button flex-1 px-4 py-3 text-sm" onClick={() => scrollTo("live-demo")}>
                    Try the Demo
                  </button>
                </div>
              </div>
            </div>
          ) : null}
        </div>
      </header>

      <main className="relative z-10">
        <section id="home" className="section-shell relative min-h-screen overflow-hidden pt-28 lg:pt-32">
          <HeroScene highContrast={highContrast} />
          <div className="container relative z-10 flex min-h-[calc(100vh-8rem)] items-center py-10">
            <div className="grid w-full items-center gap-20 xl:grid-cols-[0.96fr_1.04fr]">
              <div className="max-w-2xl">
                <div data-hero-item className="eyebrow">
                  <span className="inline-flex h-2 w-2 rounded-full bg-cyan-300 shadow-[0_0_14px_rgba(0,229,255,0.9)]" />
                  Clinical AI / Edge-ready / Phone-native
                </div>
                <div data-hero-item className="mt-6 inline-flex items-center gap-3 rounded-full border border-white/10 bg-white/[0.035] px-4 py-2 font-mono text-xs uppercase tracking-[0.18em] text-slate-300/68">
                  respiratory screening narrative
                </div>
                <h1 data-hero-item className="section-title text-balance mt-6 max-w-3xl text-white">
                  CoughNet
                  <span className="mt-3 block text-cyan-200/95">Your cough tells a story.</span>
                  <span className="mt-2 block text-slate-100/88">We listen.</span>
                </h1>
                <p data-hero-item className="section-subtitle mt-7 max-w-xl">
                  AI-powered respiratory screening via microphone. No equipment. No clinic. Just a phone. CoughNet turns a short cough into a technically legible intake moment with audio telemetry, feature extraction logic, and model-ready outputs.
                </p>
                <div data-hero-item className="mt-9 flex flex-col gap-4 sm:flex-row">
                  <button aria-label="Try the demo" className="cyan-button px-6 py-4 text-base" onClick={() => scrollTo("live-demo")}>
                    Try the Demo
                  </button>
                  <button aria-label="Read the research" className="ghost-button px-6 py-4 text-base" onClick={() => scrollTo("research")}>
                    Read the Research
                  </button>
                </div>
                <div data-hero-item className="mt-10 grid gap-4 sm:grid-cols-3 lg:max-w-2xl">
                  {[
                    ["Signal", "Real-time waveform + spectrogram"],
                    ["Model", "TF.js-ready inference handoff"],
                    ["Deployment", "Designed for low-resource settings"],
                  ].map(([label, value]) => (
                    <div key={label} className="rounded-[1.2rem] border border-white/10 bg-white/[0.03] p-4 backdrop-blur-xl">
                      <div className="mono-label text-[10px]">{label}</div>
                      <div className="mt-2 text-sm leading-6 text-slate-200/78">{value}</div>
                    </div>
                  ))}
                </div>
              </div>

              <div data-hero-item className="hidden lg:block">
                <div className="ml-auto max-w-lg rounded-[2rem] border border-cyan-300/12 bg-[#07141d]/68 p-6 backdrop-blur-xl xl:translate-y-8">
                  <div className="mb-5 flex items-center justify-between">
                    <div>
                      <p className="mono-label text-[11px]">System posture</p>
                      <h2 className="mt-2 text-2xl font-bold text-white">Built to feel credible in the room</h2>
                    </div>
                    <div className="rounded-full border border-cyan-300/16 bg-cyan-400/8 px-4 py-2 font-mono text-xs text-cyan-100/70">
                      live concept interface
                    </div>
                  </div>
                  <div className="grid gap-4 sm:grid-cols-2">
                    {[
                      {
                        label: "Input",
                        value: "audio capture",
                        detail: "On-device microphone intake",
                      },
                      {
                        label: "Features",
                        value: "MFCC heatmaps",
                        detail: "Interpretable acoustic vectors",
                      },
                      {
                        label: "Inference",
                        value: "CNN / RNN compatible",
                        detail: "Private-by-default browser path",
                      },
                      {
                        label: "Output",
                        value: "Risk triage bands",
                        detail: "Confidence-aware class scores",
                      },
                    ].map((item) => (
                      <div key={item.label} className="rounded-[1.35rem] border border-white/8 bg-white/[0.03] p-4">
                        <div className="mono-label text-[10px]">{item.label}</div>
                        <div className="mt-3 font-[Space_Grotesk] text-xl font-bold text-white">{item.value}</div>
                        <div className="mt-2 text-sm leading-6 text-slate-300/70">{item.detail}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section id="problem" className="section-shell relative overflow-hidden">
          <div
            className="absolute inset-0 opacity-60"
            style={{
              backgroundImage: `linear-gradient(180deg, rgba(4,12,18,0.92), rgba(4,12,18,0.86)), url(${PROBLEM_BG})`,
              backgroundPosition: "center",
              backgroundSize: "cover",
            }}
          />
          <div className="container section-pad relative z-10">
            <div className="relative overflow-hidden rounded-[2rem] border border-white/8 bg-[#06131d]/80 px-6 py-10 shadow-[0_26px_90px_rgba(0,0,0,0.32)] backdrop-blur-xl lg:px-12 lg:py-14">
              <div className="pointer-events-none absolute left-0 top-0 hidden text-[clamp(8rem,24vw,18rem)] font-bold leading-none tracking-[-0.1em] text-white/[0.035] lg:block">
                1.8B
              </div>
              <div className="grid gap-12 lg:grid-cols-[0.88fr_1.12fr] lg:gap-16">
                <div data-reveal className="relative z-10">
                  <div className="eyebrow">The problem</div>
                  <h2 className="mt-6 text-[clamp(2.4rem,5vw,4.6rem)] font-bold leading-[0.94] text-white">
                    Screening bottlenecks still leave entire communities invisible.
                  </h2>
                  <p className="mt-6 max-w-xl text-lg leading-8 text-slate-200/72">
                    Respiratory disease surveillance still depends on physical access, trained staff, and slow pathways that often miss the earliest, most scalable moment of signal capture. CoughNet reframes the phone microphone as a passive triage sensor.
                  </p>
                </div>
                <div data-stagger-group className="relative z-10 grid gap-4">
                  {stats.map((stat) => {
                    const Icon = stat.icon;
                    return (
                      <div key={stat.label} className="diagnostic-card p-5 sm:p-6" data-hover-lift>
                        <div className="grid gap-4 sm:grid-cols-[auto_1fr] sm:items-start">
                          <div className="flex h-14 w-14 items-center justify-center rounded-2xl border border-cyan-300/14 bg-cyan-400/8">
                            <Icon className="h-6 w-6 text-cyan-200" />
                          </div>
                          <div>
                            <div className="metric-value text-[clamp(2.6rem,6vw,4.6rem)] text-white">
                              <MetricCounter
                                end={stat.end}
                                prefix={stat.prefix}
                                suffix={stat.suffix}
                                decimals={stat.decimals}
                              />
                            </div>
                            <div className="mt-3 text-base font-semibold text-slate-100">{stat.label}</div>
                            <p className="mt-2 max-w-xl text-sm leading-7 text-slate-300/72">{stat.description}</p>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>
        </section>

        <section id="how-it-works" className="section-shell relative overflow-hidden">
          <div
            className="absolute inset-0 opacity-65"
            style={{
              backgroundImage: `linear-gradient(180deg, rgba(4,12,18,0.95), rgba(4,12,18,0.85)), url(${PIPELINE_BG})`,
              backgroundPosition: "center",
              backgroundSize: "cover",
            }}
          />
          <div className="container section-pad relative z-10">
            <div className="max-w-3xl" data-reveal>
              <div className="eyebrow">How it works</div>
              <h2 className="mt-6 text-[clamp(2.6rem,5vw,4.8rem)] font-bold leading-[0.96] text-white">
                From Cough to Diagnosis
              </h2>
              <p className="mt-6 text-lg leading-8 text-slate-200/72">
                The product story is simple: capture a cough, translate it into features, run inference, and return interpretable probabilities. The interface makes each stage auditable so the pipeline looks engineered rather than magical.
              </p>
            </div>

            <div className="mt-12 overflow-hidden rounded-[2rem] border border-white/8 bg-[#07131c]/78 p-5 shadow-[0_28px_90px_rgba(0,0,0,0.3)] backdrop-blur-xl sm:p-7 lg:p-10" data-reveal>
              <div className="relative">
                <div className="pointer-events-none absolute left-0 right-0 top-10 hidden h-px bg-[linear-gradient(90deg,rgba(0,229,255,0.18),rgba(123,47,190,0.42),rgba(0,255,148,0.18))] lg:block" />
                <div className="grid gap-5 lg:grid-cols-3 xl:grid-cols-5" data-stagger-group>
                  {pipelineSteps.map((step, index) => {
                    const Icon = step.icon;
                    return (
                      <div
                        key={step.title}
                        className="diagnostic-card relative min-h-[260px] p-5 transition-transform xl:min-h-[280px]"
                        data-hover-lift
                      >
                        <div className="absolute left-5 top-5 font-mono text-[11px] uppercase tracking-[0.24em] text-white/35">0{index + 1}</div>
                        <div className="mt-8 flex h-14 w-14 items-center justify-center rounded-2xl border border-white/10" style={{ backgroundColor: `${step.accent}18`, color: step.accent }}>
                          <Icon className="h-6 w-6" />
                        </div>
                        <h3 className="mt-6 text-2xl font-bold text-white">{step.title}</h3>
                        <p className="mt-2 font-mono text-xs uppercase tracking-[0.18em] text-slate-300/60">{step.meta}</p>
                        <p className="mt-5 text-[15px] leading-7 text-slate-300/74">{step.detail}</p>
                        <div className="mt-6 h-1.5 rounded-full bg-white/6">
                          <div
                            className="h-full rounded-full shadow-[0_0_16px_currentColor]"
                            style={{ width: `${38 + index * 14}%`, backgroundColor: step.accent, color: step.accent }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              <div className="mt-10 flex flex-col gap-4 rounded-[1.5rem] border border-white/8 bg-white/[0.03] p-5 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="font-[Space_Grotesk] text-lg font-bold text-white">
                    Based on published research from Cambridge University & Carnegie Mellon University
                  </p>
                  <p className="mt-2 text-sm text-slate-300/70">
                    Dataset-first design, clear inference handoff, and interface cues that make the science legible to judges.
                  </p>
                </div>
                <div className="flex flex-wrap gap-2 font-mono text-[11px] uppercase tracking-[0.18em] text-cyan-100/72">
                  <span className="rounded-full border border-cyan-300/14 bg-cyan-400/8 px-3 py-2">Cambridge</span>
                  <span className="rounded-full border border-violet-300/14 bg-violet-400/8 px-3 py-2">Carnegie Mellon</span>
                  <span className="rounded-full border border-emerald-300/14 bg-emerald-400/8 px-3 py-2">IISc Coswara</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section id="live-demo" className="section-shell relative overflow-hidden">
          <div className="container section-pad relative z-10">
            <div className="mb-8 max-w-3xl" data-reveal>
              <div className="eyebrow">Live demo</div>
              <h2 className="mt-6 text-[clamp(2.6rem,5vw,4.8rem)] font-bold leading-[0.96] text-white">
                Demo the intake layer judges can actually touch.
              </h2>
              <p className="mt-6 text-lg leading-8 text-slate-200/72">
                This section focuses on the most persuasive product handoff: a tangible microphone interaction paired with waveform and spectrogram feedback, followed by a transparent placeholder inference panel that shows where the model connects.
              </p>
            </div>
            <div data-reveal>
              <LiveDemo highContrast={highContrast} />
            </div>
          </div>
        </section>

        <section id="research" className="section-shell relative overflow-hidden">
          <div className="container section-pad relative z-10">
            <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between" data-reveal>
              <div className="max-w-3xl">
                <div className="eyebrow">Research & credibility</div>
                <h2 className="mt-6 text-[clamp(2.5rem,5vw,4.6rem)] font-bold leading-[0.96] text-white">
                  Grounded in Peer-Reviewed Science
                </h2>
              </div>
              <p className="max-w-xl text-base leading-8 text-slate-300/72">
                CoughNet is presented as an auditable screening interface rooted in open-access research, not an opaque black-box claim.
              </p>
            </div>

            <div className="mt-12 grid gap-5 lg:grid-cols-3" data-stagger-group>
              {researchCards.map((card) => {
                const Icon = card.icon;
                return (
                  <article key={card.title} className="diagnostic-card flex h-full flex-col p-6" data-hover-lift>
                    <div className="flex items-center justify-between gap-4">
                      <div className="flex h-14 w-14 items-center justify-center rounded-2xl border border-cyan-300/14 bg-cyan-400/8 text-cyan-200">
                        <Icon className="h-6 w-6" />
                      </div>
                      <div className="font-mono text-[11px] uppercase tracking-[0.18em] text-slate-300/58">{card.year}</div>
                    </div>
                    <h3 className="mt-6 text-2xl font-bold text-white">{card.title}</h3>
                    <p className="mt-2 font-mono text-xs uppercase tracking-[0.16em] text-cyan-100/62">{card.source}</p>
                    <p className="mt-5 flex-1 text-sm leading-7 text-slate-300/74">{card.abstract}</p>
                    <a
                      className="mt-6 inline-flex items-center gap-2 font-[Space_Grotesk] font-bold text-cyan-200"
                      href={card.href}
                      target="_blank"
                      rel="noreferrer"
                    >
                      View Paper <ArrowRight className="h-4 w-4" />
                    </a>
                  </article>
                );
              })}
            </div>

            <div className="mt-8 rounded-[1.5rem] border border-white/8 bg-white/[0.03] px-5 py-4 text-center text-sm text-slate-300/70" data-reveal>
              CoughNet&apos;s classifier is trained on open-access datasets. No proprietary data. Fully auditable.
            </div>
          </div>
        </section>

        <section id="team" className="section-shell relative overflow-hidden">
          <div className="container section-pad relative z-10">
            <div className="max-w-3xl" data-reveal>
              <div className="eyebrow">Team</div>
              <h2 className="mt-6 text-[clamp(2.5rem,5vw,4.6rem)] font-bold leading-[0.96] text-white">Built by Team CoughNet</h2>
              <p className="mt-6 text-lg leading-8 text-slate-200/72">
                A deliberately cross-functional team spanning signal processing, model design, and the interface layer that makes technical systems legible in the room.
              </p>
            </div>

            <div className="mt-12 grid gap-5 lg:grid-cols-3" data-stagger-group>
              {teamMembers.map((member) => (
                <article key={member.name} className="diagnostic-card p-6" data-hover-lift>
                  <div className="flex items-start justify-between gap-4">
                    <GeometricAvatar palette={member.palette} />
                    <a
                      aria-label={`Open LinkedIn profile for ${member.name}`}
                      href={member.href}
                      target="_blank"
                      rel="noreferrer"
                      className="rounded-full border border-white/10 bg-white/4 p-3 text-slate-100"
                    >
                      <Linkedin className="h-4 w-4" />
                    </a>
                  </div>
                  <h3 className="mt-6 text-2xl font-bold text-white">{member.name}</h3>
                  <p className="mt-2 inline-flex rounded-full border border-cyan-300/16 bg-cyan-400/10 px-3 py-1 font-mono text-[11px] uppercase tracking-[0.18em] text-cyan-100/72">
                    {member.role}
                  </p>
                  <p className="mt-5 text-sm leading-7 text-slate-300/74">{member.bio}</p>
                </article>
              ))}
            </div>
          </div>
        </section>
      </main>

      <footer className="section-shell relative overflow-hidden border-t border-white/8">
        <div
          className="absolute inset-0 opacity-90"
          style={{
            backgroundImage: `linear-gradient(180deg, rgba(4,12,18,0.88), rgba(4,12,18,0.98)), url(${FOOTER_BG})`,
            backgroundPosition: "center",
            backgroundSize: "cover",
          }}
        />
        <div className="container section-pad relative z-10">
          <div className="mx-auto max-w-4xl text-center" data-reveal>
            <div className="eyebrow">Deployable public-health interface</div>
            <h2 className="mt-6 text-[clamp(2.8rem,6vw,5.8rem)] font-bold leading-[0.94] text-white">
              A phone is all it takes.
              <span className="mt-3 block text-cyan-200">Deploy CoughNet to your community today.</span>
            </h2>
            <div className="mt-8 flex flex-col justify-center gap-4 sm:flex-row">
              <button className="cyan-button px-6 py-4 text-base" onClick={() => scrollTo("live-demo")}>Try the Demo</button>
              <a className="ghost-button px-6 py-4 text-base" href="mailto:team@coughnet.health">
                Contact Us
              </a>
            </div>
          </div>

          <div className="mt-14 grid gap-8 rounded-[2rem] border border-white/8 bg-[#07131ca8] p-6 backdrop-blur-xl lg:grid-cols-[1fr_auto_auto] lg:items-end">
            <div>
              <div className="flex items-center gap-3">
                <LogoMark />
                <div>
                  <div className="font-[Space_Grotesk] text-xl font-bold text-white">
                    Cough<span className="text-cyan-300">Net</span>
                  </div>
                  <div className="font-mono text-[11px] uppercase tracking-[0.2em] text-slate-300/55">Respiratory screening interface</div>
                </div>
              </div>
              <p className="mt-5 max-w-xl text-sm leading-7 text-slate-300/72">
                Designed for community health workers in low-resource settings worldwide. The goal is not to replace clinicians, but to shorten the path between signal and escalation.
              </p>
            </div>
            <div>
              <div className="mono-label text-[11px]">Navigation</div>
              <div className="mt-3 grid gap-2 text-sm text-slate-200/80">
                {navItems.map((item) => (
                  <button key={item.id} className="text-left" onClick={() => scrollTo(item.id)}>
                    {item.label}
                  </button>
                ))}
              </div>
            </div>
            <div>
              <div className="mono-label text-[11px]">Connect</div>
              <div className="mt-3 flex gap-3">
                <a aria-label="Open GitHub" href="https://github.com/" target="_blank" rel="noreferrer" className="rounded-full border border-white/10 bg-white/4 p-3 text-slate-100">
                  <Github className="h-4 w-4" />
                </a>
                <a aria-label="Open LinkedIn" href="https://www.linkedin.com/" target="_blank" rel="noreferrer" className="rounded-full border border-white/10 bg-white/4 p-3 text-slate-100">
                  <Linkedin className="h-4 w-4" />
                </a>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
