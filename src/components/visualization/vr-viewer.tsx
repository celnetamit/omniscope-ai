"use client";

import React, { useEffect, useRef, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Loader2, Glasses, XCircle, Info, Download, FileImage, FileCode, Globe } from 'lucide-react';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuSeparator } from '@/components/ui/dropdown-menu';
import { toast } from 'sonner';
import { exportThreeSceneToPNG, exportInteractiveHTML } from '@/lib/visualization-export';

interface VRViewerProps {
  scene?: any; // Three.js scene
  onVRSessionStart?: () => void;
  onVRSessionEnd?: () => void;
  enableControllers?: boolean;
  enableTeleportation?: boolean;
}

interface VRCapabilities {
  supported: boolean;
  immersiveVR: boolean;
  inlineVR: boolean;
  controllers: boolean;
}

export function VRViewer({
  scene: externalScene,
  onVRSessionStart,
  onVRSessionEnd,
  enableControllers = true,
  enableTeleportation = true
}: VRViewerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const rendererRef = useRef<any>(null);
  const sceneRef = useRef<any>(null);
  const cameraRef = useRef<any>(null);
  const vrSessionRef = useRef<any>(null);
  const controllersRef = useRef<any[]>([]);
  const animationFrameRef = useRef<number | null>(null);

  const [vrCapabilities, setVRCapabilities] = useState<VRCapabilities>({
    supported: false,
    immersiveVR: false,
    inlineVR: false,
    controllers: false
  });
  const [vrActive, setVRActive] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [controllerStatus, setControllerStatus] = useState<string[]>([]);

  // Check WebXR capabilities
  useEffect(() => {
    checkVRCapabilities();
  }, []);

  const checkVRCapabilities = async () => {
    if (!('xr' in navigator)) {
      setVRCapabilities({
        supported: false,
        immersiveVR: false,
        inlineVR: false,
        controllers: false
      });
      return;
    }

    try {
      const xr = (navigator as any).xr;
      
      const immersiveVR = await xr.isSessionSupported('immersive-vr');
      const inlineVR = await xr.isSessionSupported('inline');
      
      setVRCapabilities({
        supported: immersiveVR || inlineVR,
        immersiveVR,
        inlineVR,
        controllers: immersiveVR // Controllers typically available with immersive VR
      });
    } catch (err) {
      console.error('Error checking VR capabilities:', err);
      setVRCapabilities({
        supported: false,
        immersiveVR: false,
        inlineVR: false,
        controllers: false
      });
    }
  };

  // Initialize Three.js scene and renderer
  useEffect(() => {
    const initScene = async () => {
      if (!containerRef.current) return;

      try {
        const THREE = await import('three');
        const { VRButton } = await import('three/examples/jsm/webxr/VRButton.js');
        const { XRControllerModelFactory } = await import('three/examples/jsm/webxr/XRControllerModelFactory.js');

        // Create or use external scene
        const scene = externalScene || new THREE.Scene();
        sceneRef.current = scene;

        // Add default lighting if no external scene
        if (!externalScene) {
          const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
          scene.add(ambientLight);

          const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
          directionalLight.position.set(1, 1, 1);
          scene.add(directionalLight);

          // Add a simple grid for reference
          const gridHelper = new THREE.GridHelper(10, 10);
          scene.add(gridHelper);

          // Add some demo objects
          const geometry = new THREE.BoxGeometry(0.5, 0.5, 0.5);
          const material = new THREE.MeshStandardMaterial({ color: 0x00ff00 });
          const cube = new THREE.Mesh(geometry, material);
          cube.position.set(0, 1.5, -2);
          scene.add(cube);
        }

        // Create camera
        const camera = new THREE.PerspectiveCamera(
          75,
          containerRef.current.clientWidth / containerRef.current.clientHeight,
          0.1,
          1000
        );
        camera.position.set(0, 1.6, 3); // Average human eye height
        cameraRef.current = camera;

        // Create renderer with WebXR support
        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(containerRef.current.clientWidth, containerRef.current.clientHeight);
        renderer.setPixelRatio(window.devicePixelRatio);
        renderer.xr.enabled = true;
        containerRef.current.appendChild(renderer.domElement);
        rendererRef.current = renderer;

        // Setup VR controllers if enabled
        if (enableControllers && vrCapabilities.controllers) {
          setupVRControllers(THREE, scene, renderer, XRControllerModelFactory);
        }

        // Setup teleportation if enabled
        if (enableTeleportation) {
          setupTeleportation(THREE, scene);
        }

        // Handle window resize
        const handleResize = () => {
          if (!containerRef.current || !cameraRef.current || !rendererRef.current) return;
          
          const width = containerRef.current.clientWidth;
          const height = containerRef.current.clientHeight;
          
          cameraRef.current.aspect = width / height;
          cameraRef.current.updateProjectionMatrix();
          rendererRef.current.setSize(width, height);
        };
        window.addEventListener('resize', handleResize);

        // Start animation loop
        renderer.setAnimationLoop(() => {
          animate();
        });

        return () => {
          window.removeEventListener('resize', handleResize);
          if (animationFrameRef.current) {
            cancelAnimationFrame(animationFrameRef.current);
          }
          renderer.dispose();
          if (containerRef.current && renderer.domElement) {
            containerRef.current.removeChild(renderer.domElement);
          }
        };
      } catch (err) {
        console.error('Failed to initialize VR scene:', err);
        setError('Failed to initialize VR viewer');
      }
    };

    initScene();
  }, [externalScene, enableControllers, enableTeleportation, vrCapabilities]);

  const setupVRControllers = async (THREE: any, scene: any, renderer: any, XRControllerModelFactory: any) => {
    try {
      const controllerModelFactory = new XRControllerModelFactory();

      // Controller 0 (typically right hand)
      const controller0 = renderer.xr.getController(0);
      controller0.addEventListener('selectstart', onSelectStart);
      controller0.addEventListener('selectend', onSelectEnd);
      controller0.addEventListener('connected', (event: any) => {
        controller0.add(buildController(THREE, event.data));
        updateControllerStatus(0, 'connected');
      });
      controller0.addEventListener('disconnected', () => {
        updateControllerStatus(0, 'disconnected');
      });
      scene.add(controller0);

      const controllerGrip0 = renderer.xr.getControllerGrip(0);
      controllerGrip0.add(controllerModelFactory.createControllerModel(controllerGrip0));
      scene.add(controllerGrip0);

      // Controller 1 (typically left hand)
      const controller1 = renderer.xr.getController(1);
      controller1.addEventListener('selectstart', onSelectStart);
      controller1.addEventListener('selectend', onSelectEnd);
      controller1.addEventListener('connected', (event: any) => {
        controller1.add(buildController(THREE, event.data));
        updateControllerStatus(1, 'connected');
      });
      controller1.addEventListener('disconnected', () => {
        updateControllerStatus(1, 'disconnected');
      });
      scene.add(controller1);

      const controllerGrip1 = renderer.xr.getControllerGrip(1);
      controllerGrip1.add(controllerModelFactory.createControllerModel(controllerGrip1));
      scene.add(controllerGrip1);

      controllersRef.current = [controller0, controller1];
    } catch (err) {
      console.error('Failed to setup VR controllers:', err);
    }
  };

  const buildController = (THREE: any, data: any) => {
    let geometry, material;

    switch (data.targetRayMode) {
      case 'tracked-pointer':
        geometry = new THREE.BufferGeometry();
        geometry.setAttribute('position', new THREE.Float32BufferAttribute([0, 0, 0, 0, 0, -1], 3));
        geometry.setAttribute('color', new THREE.Float32BufferAttribute([0.5, 0.5, 0.5, 0, 0, 0], 3));
        material = new THREE.LineBasicMaterial({ vertexColors: true, blending: THREE.AdditiveBlending });
        return new THREE.Line(geometry, material);

      case 'gaze':
        geometry = new THREE.RingGeometry(0.02, 0.04, 32).translate(0, 0, -1);
        material = new THREE.MeshBasicMaterial({ opacity: 0.5, transparent: true });
        return new THREE.Mesh(geometry, material);

      default:
        return new THREE.Object3D();
    }
  };

  const setupTeleportation = (THREE: any, scene: any) => {
    // Create teleportation marker
    const markerGeometry = new THREE.RingGeometry(0.25, 0.3, 32);
    markerGeometry.rotateX(-Math.PI / 2);
    const markerMaterial = new THREE.MeshBasicMaterial({ color: 0x00ff00, opacity: 0.5, transparent: true });
    const marker = new THREE.Mesh(markerGeometry, markerMaterial);
    marker.visible = false;
    scene.add(marker);
  };

  const onSelectStart = (event: any) => {
    const controller = event.target;
    controller.userData.isSelecting = true;
  };

  const onSelectEnd = (event: any) => {
    const controller = event.target;
    controller.userData.isSelecting = false;
  };

  const updateControllerStatus = (index: number, status: string) => {
    setControllerStatus(prev => {
      const newStatus = [...prev];
      newStatus[index] = status;
      return newStatus;
    });
  };

  const animate = () => {
    if (!rendererRef.current || !sceneRef.current || !cameraRef.current) return;

    // Update controller interactions
    if (controllersRef.current.length > 0) {
      controllersRef.current.forEach(controller => {
        if (controller.userData.isSelecting) {
          // Handle selection/interaction logic
        }
      });
    }

    rendererRef.current.render(sceneRef.current, cameraRef.current);
  };

  const startVRSession = async () => {
    if (!vrCapabilities.immersiveVR) {
      toast.error('Immersive VR not supported on this device');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const xr = (navigator as any).xr;
      const session = await xr.requestSession('immersive-vr', {
        requiredFeatures: ['local-floor'],
        optionalFeatures: ['hand-tracking', 'layers']
      });

      vrSessionRef.current = session;

      session.addEventListener('end', () => {
        setVRActive(false);
        vrSessionRef.current = null;
        if (onVRSessionEnd) onVRSessionEnd();
        toast.info('VR session ended');
      });

      if (rendererRef.current) {
        await rendererRef.current.xr.setSession(session);
      }

      setVRActive(true);
      if (onVRSessionStart) onVRSessionStart();
      toast.success('VR session started');
    } catch (err: any) {
      console.error('Failed to start VR session:', err);
      setError(err.message || 'Failed to start VR session');
      toast.error('Failed to start VR session');
    } finally {
      setLoading(false);
    }
  };

  const endVRSession = async () => {
    if (vrSessionRef.current) {
      await vrSessionRef.current.end();
    }
  };

  // Export functions
  const exportToPNG = async () => {
    if (!rendererRef.current || !sceneRef.current || !cameraRef.current) {
      toast.error('No scene to export');
      return;
    }

    try {
      await exportThreeSceneToPNG(
        rendererRef.current,
        sceneRef.current,
        cameraRef.current,
        {
          filename: 'vr_scene.png',
          width: 1920,
          height: 1080
        }
      );
      toast.success('PNG exported successfully');
    } catch (error) {
      console.error('Failed to export PNG:', error);
      toast.error('Failed to export PNG');
    }
  };

  const exportToSVG = async () => {
    if (!rendererRef.current) {
      toast.error('No scene to export');
      return;
    }

    try {
      const canvas = rendererRef.current.domElement;
      
      // Create SVG with embedded canvas image
      const svgNS = 'http://www.w3.org/2000/svg';
      const svg = document.createElementNS(svgNS, 'svg');
      svg.setAttribute('width', canvas.width.toString());
      svg.setAttribute('height', canvas.height.toString());
      svg.setAttribute('viewBox', `0 0 ${canvas.width} ${canvas.height}`);
      
      const dataURL = canvas.toDataURL('image/png');
      const image = document.createElementNS(svgNS, 'image');
      image.setAttribute('href', dataURL);
      image.setAttribute('width', canvas.width.toString());
      image.setAttribute('height', canvas.height.toString());
      svg.appendChild(image);
      
      const { exportSVG } = await import('@/lib/visualization-export');
      await exportSVG(svg, {
        filename: 'vr_scene.svg',
        width: canvas.width,
        height: canvas.height
      });
      
      toast.success('SVG exported successfully');
    } catch (error) {
      console.error('Failed to export SVG:', error);
      toast.error('Failed to export SVG');
    }
  };

  const exportToHTML = async () => {
    try {
      const htmlContent = `
        <div id="vr-container" style="width: 100%; height: 600px;"></div>
        <script src="https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js"></script>
        <script type="module">
          import { VRButton } from 'https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/webxr/VRButton.js';
          
          const scene = new THREE.Scene();
          const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
          camera.position.set(0, 1.6, 3);
          
          const renderer = new THREE.WebGLRenderer({ antialias: true });
          renderer.setSize(window.innerWidth, window.innerHeight);
          renderer.xr.enabled = true;
          document.getElementById('vr-container').appendChild(renderer.domElement);
          
          // Add lighting
          const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
          scene.add(ambientLight);
          const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
          directionalLight.position.set(1, 1, 1);
          scene.add(directionalLight);
          
          // Add grid
          const gridHelper = new THREE.GridHelper(10, 10);
          scene.add(gridHelper);
          
          // Add demo cube
          const geometry = new THREE.BoxGeometry(0.5, 0.5, 0.5);
          const material = new THREE.MeshStandardMaterial({ color: 0x00ff00 });
          const cube = new THREE.Mesh(geometry, material);
          cube.position.set(0, 1.5, -2);
          scene.add(cube);
          
          // Add VR button
          document.body.appendChild(VRButton.createButton(renderer));
          
          // Animation loop
          renderer.setAnimationLoop(() => {
            renderer.render(scene, camera);
          });
          
          // Handle resize
          window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
          });
          
          window.resetVisualization = () => {
            camera.position.set(0, 1.6, 3);
            camera.lookAt(0, 0, 0);
          };
        </script>
      `;

      await exportInteractiveHTML(
        {
          title: 'VR Scene Visualization',
          description: 'Interactive WebXR-enabled 3D scene',
          htmlContent,
          scripts: [],
          styles: []
        },
        {
          filename: 'vr_scene.html',
          includeControls: true,
          includeData: false
        }
      );
      
      toast.success('Interactive HTML exported successfully');
    } catch (error) {
      console.error('Failed to export HTML:', error);
      toast.error('Failed to export HTML');
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Glasses className="h-5 w-5" />
          VR Viewer
        </CardTitle>
        <CardDescription>
          Immersive virtual reality visualization using WebXR
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* VR Capabilities Status */}
        <div className="flex flex-wrap gap-2">
          <Badge variant={vrCapabilities.supported ? "default" : "secondary"}>
            {vrCapabilities.supported ? '✓' : '✗'} WebXR Supported
          </Badge>
          <Badge variant={vrCapabilities.immersiveVR ? "default" : "secondary"}>
            {vrCapabilities.immersiveVR ? '✓' : '✗'} Immersive VR
          </Badge>
          <Badge variant={vrCapabilities.controllers ? "default" : "secondary"}>
            {vrCapabilities.controllers ? '✓' : '✗'} Controllers
          </Badge>
          {vrActive && (
            <Badge variant="default" className="bg-green-500">
              VR Active
            </Badge>
          )}
        </div>

        {/* Error Display */}
        {error && (
          <Alert variant="destructive">
            <XCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Info Alert */}
        {!vrCapabilities.supported && (
          <Alert>
            <Info className="h-4 w-4" />
            <AlertDescription>
              WebXR is not supported on this device or browser. Try using a VR headset with a compatible browser (Chrome, Edge, Firefox).
            </AlertDescription>
          </Alert>
        )}

        {/* VR Controls */}
        <div className="flex gap-2">
          {!vrActive ? (
            <Button
              onClick={startVRSession}
              disabled={!vrCapabilities.immersiveVR || loading}
              className="flex items-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Starting VR...
                </>
              ) : (
                <>
                  <Glasses className="h-4 w-4" />
                  Enter VR
                </>
              )}
            </Button>
          ) : (
            <Button
              onClick={endVRSession}
              variant="destructive"
              className="flex items-center gap-2"
            >
              <XCircle className="h-4 w-4" />
              Exit VR
            </Button>
          )}
          
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" className="flex items-center gap-2">
                <Download className="h-4 w-4" />
                Export
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={exportToPNG}>
                <FileImage className="mr-2 h-4 w-4" />
                Export as PNG
              </DropdownMenuItem>
              <DropdownMenuItem onClick={exportToSVG}>
                <FileCode className="mr-2 h-4 w-4" />
                Export as SVG
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={exportToHTML}>
                <Globe className="mr-2 h-4 w-4" />
                Export Interactive HTML
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        {/* Controller Status */}
        {enableControllers && controllerStatus.length > 0 && (
          <div className="space-y-2">
            <div className="text-sm font-medium">Controller Status:</div>
            <div className="flex gap-2">
              {controllerStatus.map((status, index) => (
                <Badge
                  key={index}
                  variant={status === 'connected' ? 'default' : 'secondary'}
                >
                  Controller {index}: {status || 'not detected'}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* 3D Scene Container */}
        <div
          ref={containerRef}
          className="w-full h-[600px] border rounded-lg bg-gray-900"
          style={{ position: 'relative' }}
        />

        {/* Instructions */}
        <div className="text-sm text-muted-foreground space-y-1">
          <div className="font-medium">Instructions:</div>
          <ul className="list-disc list-inside space-y-1">
            <li>Click "Enter VR" to start an immersive VR session</li>
            <li>Use VR controllers to interact with objects in the scene</li>
            {enableTeleportation && <li>Point and click to teleport to different locations</li>}
            <li>Press the menu button on your controller to exit VR</li>
          </ul>
        </div>
      </CardContent>
    </Card>
  );
}
