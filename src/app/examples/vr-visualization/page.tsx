'use client';

import React, { useState, useEffect } from 'react';
import { VRViewer } from '@/components/visualization/vr-viewer';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Info } from 'lucide-react';

export default function VRVisualizationExample() {
  const [scene, setScene] = useState<any>(null);
  const [vrSessionActive, setVRSessionActive] = useState(false);

  // Create a custom Three.js scene with sample data
  useEffect(() => {
    const createScene = async () => {
      try {
        const THREE = await import('three');
        
        const newScene = new THREE.Scene();
        newScene.background = new THREE.Color(0x1a1a2e);

        // Add lighting
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
        newScene.add(ambientLight);

        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(5, 10, 5);
        newScene.add(directionalLight);

        // Add a grid for reference
        const gridHelper = new THREE.GridHelper(20, 20, 0x444444, 0x222222);
        newScene.add(gridHelper);

        // Create sample molecular-like structure
        const sphereGeometry = new THREE.SphereGeometry(0.2, 32, 32);
        const colors = [0xff6b6b, 0x4ecdc4, 0x45b7d1, 0xf7b731, 0x5f27cd];

        // Create a cluster of spheres representing atoms
        for (let i = 0; i < 20; i++) {
          const material = new THREE.MeshStandardMaterial({
            color: colors[i % colors.length],
            metalness: 0.3,
            roughness: 0.4
          });
          const sphere = new THREE.Mesh(sphereGeometry, material);
          
          // Position in a spiral pattern
          const angle = (i / 20) * Math.PI * 4;
          const radius = 1 + (i / 20) * 2;
          const height = Math.sin(angle) * 2;
          
          sphere.position.set(
            Math.cos(angle) * radius,
            height + 1.5,
            Math.sin(angle) * radius
          );
          
          newScene.add(sphere);
        }

        // Add connecting lines (bonds)
        const lineMaterial = new THREE.LineBasicMaterial({ color: 0x888888, opacity: 0.6, transparent: true });
        for (let i = 0; i < 19; i++) {
          const points: any[] = [];
          const angle1 = (i / 20) * Math.PI * 4;
          const radius1 = 1 + (i / 20) * 2;
          const height1 = Math.sin(angle1) * 2;
          
          const angle2 = ((i + 1) / 20) * Math.PI * 4;
          const radius2 = 1 + ((i + 1) / 20) * 2;
          const height2 = Math.sin(angle2) * 2;
          
          const point1 = new THREE.Vector3(
            Math.cos(angle1) * radius1,
            height1 + 1.5,
            Math.sin(angle1) * radius1
          );
          const point2 = new THREE.Vector3(
            Math.cos(angle2) * radius2,
            height2 + 1.5,
            Math.sin(angle2) * radius2
          );
          points.push(point1, point2);
          
          const lineGeometry = new THREE.BufferGeometry().setFromPoints(points);
          const line = new THREE.Line(lineGeometry, lineMaterial);
          newScene.add(line);
        }

        // Add some floating particles
        const particleGeometry = new THREE.BufferGeometry();
        const particleCount = 100;
        const positions = new Float32Array(particleCount * 3);
        
        for (let i = 0; i < particleCount * 3; i += 3) {
          positions[i] = (Math.random() - 0.5) * 10;
          positions[i + 1] = Math.random() * 5;
          positions[i + 2] = (Math.random() - 0.5) * 10;
        }
        
        particleGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        const particleMaterial = new THREE.PointsMaterial({
          color: 0x88ccff,
          size: 0.05,
          transparent: true,
          opacity: 0.6
        });
        const particles = new THREE.Points(particleGeometry, particleMaterial);
        newScene.add(particles);

        // Add a platform
        const platformGeometry = new THREE.CylinderGeometry(3, 3, 0.1, 32);
        const platformMaterial = new THREE.MeshStandardMaterial({
          color: 0x2c3e50,
          metalness: 0.5,
          roughness: 0.5
        });
        const platform = new THREE.Mesh(platformGeometry, platformMaterial);
        platform.position.y = 0;
        newScene.add(platform);

        setScene(newScene);
      } catch (err) {
        console.error('Failed to create scene:', err);
      }
    };

    createScene();
  }, []);

  const handleVRSessionStart = () => {
    setVRSessionActive(true);
    console.log('VR session started');
  };

  const handleVRSessionEnd = () => {
    setVRSessionActive(false);
    console.log('VR session ended');
  };

  return (
    <div className="container mx-auto py-8 space-y-6">
      <div>
        <h1 className="text-4xl font-bold mb-2">VR Visualization Example</h1>
        <p className="text-muted-foreground">
          Experience immersive 3D molecular visualization using WebXR technology
        </p>
      </div>

      <Alert>
        <Info className="h-4 w-4" />
        <AlertDescription>
          <strong>Requirements:</strong> This feature requires a WebXR-compatible browser (Chrome, Edge, Firefox) 
          and a VR headset (Meta Quest, HTC Vive, Valve Index, etc.). 
          {!vrSessionActive && ' Click "Enter VR" to start an immersive session.'}
        </AlertDescription>
      </Alert>

      <VRViewer
        scene={scene}
        onVRSessionStart={handleVRSessionStart}
        onVRSessionEnd={handleVRSessionEnd}
        enableControllers={true}
        enableTeleportation={true}
      />

      <Card>
        <CardHeader>
          <CardTitle>About VR Visualization</CardTitle>
          <CardDescription>
            Immersive virtual reality for scientific data exploration
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <h3 className="font-semibold mb-2">Features</h3>
            <ul className="list-disc list-inside space-y-1 text-sm text-muted-foreground">
              <li>Full WebXR support for immersive VR experiences</li>
              <li>6DOF (six degrees of freedom) tracking for natural movement</li>
              <li>VR controller support for interaction with 3D objects</li>
              <li>Teleportation system for easy navigation in large datasets</li>
              <li>Real-time rendering of complex molecular structures</li>
              <li>Compatible with major VR headsets (Meta Quest, HTC Vive, Valve Index)</li>
            </ul>
          </div>

          <div>
            <h3 className="font-semibold mb-2">Use Cases</h3>
            <ul className="list-disc list-inside space-y-1 text-sm text-muted-foreground">
              <li>Explore protein structures in immersive 3D space</li>
              <li>Navigate complex pathway networks with natural movement</li>
              <li>Collaborate with remote team members in shared VR environments</li>
              <li>Present research findings in engaging, interactive formats</li>
              <li>Identify spatial relationships in multi-omics data</li>
            </ul>
          </div>

          <div>
            <h3 className="font-semibold mb-2">Controls</h3>
            <ul className="list-disc list-inside space-y-1 text-sm text-muted-foreground">
              <li><strong>Trigger:</strong> Select and interact with objects</li>
              <li><strong>Grip:</strong> Grab and move objects</li>
              <li><strong>Thumbstick:</strong> Navigate and teleport</li>
              <li><strong>Menu Button:</strong> Access settings and exit VR</li>
            </ul>
          </div>

          <div>
            <h3 className="font-semibold mb-2">Browser Compatibility</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
              <div className="p-2 border rounded">
                <div className="font-medium">Chrome</div>
                <div className="text-xs text-green-600">✓ Supported</div>
              </div>
              <div className="p-2 border rounded">
                <div className="font-medium">Edge</div>
                <div className="text-xs text-green-600">✓ Supported</div>
              </div>
              <div className="p-2 border rounded">
                <div className="font-medium">Firefox</div>
                <div className="text-xs text-green-600">✓ Supported</div>
              </div>
              <div className="p-2 border rounded">
                <div className="font-medium">Safari</div>
                <div className="text-xs text-red-600">✗ Limited</div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
