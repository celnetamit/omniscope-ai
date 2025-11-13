"use client";

import React, { useEffect, useRef, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, Download, RotateCw, ZoomIn, ZoomOut, Glasses, FileImage, FileCode, Globe } from 'lucide-react';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuSeparator } from '@/components/ui/dropdown-menu';
import { toast } from 'sonner';
import { exportCanvasToPNG, exportSVG, exportNGLToHTML } from '@/lib/visualization-export';

interface ProteinViewerProps {
  pdbId?: string;
  pdbContent?: string;
  onLoad?: (data: any) => void;
  enableVR?: boolean;
}

interface ProteinData {
  structure_id: string;
  pdb_content: string;
  atoms: any[];
  residues: any[];
  chains: any[];
  atom_count: number;
  residue_count: number;
  chain_count: number;
}

export function ProteinViewer({ pdbId: initialPdbId, pdbContent, onLoad, enableVR = false }: ProteinViewerProps) {
  const viewerRef = useRef<HTMLDivElement>(null);
  const stageRef = useRef<any>(null);
  const [pdbId, setPdbId] = useState(initialPdbId || '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [proteinData, setProteinData] = useState<ProteinData | null>(null);
  const [representation, setRepresentation] = useState('cartoon');
  const [colorScheme, setColorScheme] = useState('chainname');
  const [vrSupported, setVRSupported] = useState(false);
  const [vrActive, setVRActive] = useState(false);

  // Check VR support
  useEffect(() => {
    const checkVR = async () => {
      if (enableVR && 'xr' in navigator) {
        try {
          const xr = (navigator as any).xr;
          const supported = await xr.isSessionSupported('immersive-vr');
          setVRSupported(supported);
        } catch (err) {
          console.error('Error checking VR support:', err);
        }
      }
    };
    checkVR();
  }, [enableVR]);

  // Initialize NGL Viewer
  useEffect(() => {
    const initViewer = async () => {
      if (!viewerRef.current) return;

      try {
        // Dynamically import NGL to avoid SSR issues
        const NGL = await import('ngl');
        
        // Create stage with VR support if enabled
        const stageConfig: any = {
          backgroundColor: 'white',
        };
        
        if (enableVR && vrSupported) {
          stageConfig.webgl = {
            xr: { enabled: true }
          };
        }
        
        const stage = new NGL.Stage(viewerRef.current, stageConfig);
        
        stageRef.current = stage;

        // Handle window resize
        const handleResize = () => {
          stage.handleResize();
        };
        window.addEventListener('resize', handleResize);

        return () => {
          window.removeEventListener('resize', handleResize);
          stage.dispose();
        };
      } catch (err) {
        console.error('Failed to initialize NGL viewer:', err);
        setError('Failed to initialize 3D viewer');
      }
    };

    initViewer();
  }, [enableVR, vrSupported]);

  // Load protein structure
  const loadProtein = async () => {
    if (!pdbId && !pdbContent) {
      setError('Please provide a PDB ID or upload a PDB file');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/visualization/protein/load', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          pdb_id: pdbId || undefined,
          pdb_content: pdbContent || undefined,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to load protein structure');
      }

      const data: ProteinData = await response.json();
      setProteinData(data);

      // Load structure into NGL viewer
      if (stageRef.current) {
        const NGL = await import('ngl');
        
        // Clear existing structures
        stageRef.current.removeAllComponents();

        // Load structure from string
        const stringBlob = new Blob([data.pdb_content], { type: 'text/plain' });
        const component = await stageRef.current.loadFile(stringBlob, { ext: 'pdb' });

        // Add representation
        component.addRepresentation(representation, {
          colorScheme: colorScheme,
        });

        // Auto-view
        stageRef.current.autoView();
      }

      if (onLoad) {
        onLoad(data);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load protein structure');
      console.error('Error loading protein:', err);
    } finally {
      setLoading(false);
    }
  };

  // Update representation
  const updateRepresentation = async (newRep: string) => {
    setRepresentation(newRep);
    
    if (stageRef.current && proteinData) {
      const components = stageRef.current.compList;
      if (components.length > 0) {
        components[0].removeAllRepresentations();
        components[0].addRepresentation(newRep, {
          colorScheme: colorScheme,
        });
      }
    }
  };

  // Update color scheme
  const updateColorScheme = async (newScheme: string) => {
    setColorScheme(newScheme);
    
    if (stageRef.current && proteinData) {
      const components = stageRef.current.compList;
      if (components.length > 0) {
        components[0].removeAllRepresentations();
        components[0].addRepresentation(representation, {
          colorScheme: newScheme,
        });
      }
    }
  };

  // Control functions
  const resetView = () => {
    if (stageRef.current) {
      stageRef.current.autoView();
    }
  };

  const zoomIn = () => {
    if (stageRef.current) {
      stageRef.current.viewer.zoom(0.8);
    }
  };

  const zoomOut = () => {
    if (stageRef.current) {
      stageRef.current.viewer.zoom(1.2);
    }
  };

  const exportToPNG = async () => {
    if (!stageRef.current) return;

    try {
      const blob = await stageRef.current.makeImage({
        factor: 2,
        antialias: true,
        trim: false,
        transparent: false,
      });
      
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `protein_${pdbId || 'structure'}.png`;
      link.click();
      URL.revokeObjectURL(url);
      
      toast.success('PNG exported successfully');
    } catch (error) {
      console.error('Failed to export PNG:', error);
      toast.error('Failed to export PNG');
    }
  };

  const exportToSVG = async () => {
    if (!stageRef.current) return;

    try {
      // NGL doesn't support direct SVG export, so we'll convert canvas to SVG
      const canvas = stageRef.current.viewer.renderer.domElement;
      
      // Create SVG with embedded image
      const svgNS = 'http://www.w3.org/2000/svg';
      const svg = document.createElementNS(svgNS, 'svg');
      svg.setAttribute('width', canvas.width.toString());
      svg.setAttribute('height', canvas.height.toString());
      svg.setAttribute('viewBox', `0 0 ${canvas.width} ${canvas.height}`);
      
      // Convert canvas to data URL
      const dataURL = canvas.toDataURL('image/png');
      
      // Create image element in SVG
      const image = document.createElementNS(svgNS, 'image');
      image.setAttribute('href', dataURL);
      image.setAttribute('width', canvas.width.toString());
      image.setAttribute('height', canvas.height.toString());
      svg.appendChild(image);
      
      // Export SVG
      await exportSVG(svg, {
        filename: `protein_${pdbId || 'structure'}.svg`,
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
    if (!proteinData) {
      toast.error('No protein data loaded');
      return;
    }

    try {
      await exportNGLToHTML(
        proteinData.pdb_content,
        representation,
        colorScheme,
        {
          filename: `protein_${pdbId || 'structure'}.html`,
          title: `Protein Structure: ${pdbId || 'Custom'}`,
          description: `Interactive 3D visualization with ${proteinData.atom_count} atoms, ${proteinData.residue_count} residues, and ${proteinData.chain_count} chains`
        }
      );
      
      toast.success('Interactive HTML exported successfully');
    } catch (error) {
      console.error('Failed to export HTML:', error);
      toast.error('Failed to export HTML');
    }
  };

  const enterVR = async () => {
    if (!vrSupported) {
      toast.error('VR not supported on this device');
      return;
    }

    try {
      const xr = (navigator as any).xr;
      const session = await xr.requestSession('immersive-vr', {
        requiredFeatures: ['local-floor']
      });

      session.addEventListener('end', () => {
        setVRActive(false);
        toast.info('VR session ended');
      });

      // NGL doesn't have built-in VR support, so we'd need to use Three.js directly
      // For now, show a message
      toast.info('VR mode activated - use VR Viewer component for full VR support');
      setVRActive(true);
    } catch (err: any) {
      console.error('Failed to start VR:', err);
      toast.error('Failed to start VR session');
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Protein Structure Viewer</CardTitle>
        <CardDescription>
          Interactive 3D visualization of protein structures using NGL Viewer
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Input Controls */}
        <div className="flex gap-2">
          <div className="flex-1">
            <Label htmlFor="pdb-id">PDB ID</Label>
            <Input
              id="pdb-id"
              placeholder="e.g., 1ABC"
              value={pdbId}
              onChange={(e) => setPdbId(e.target.value.toUpperCase())}
              disabled={loading}
            />
          </div>
          <div className="flex items-end">
            <Button onClick={loadProtein} disabled={loading || (!pdbId && !pdbContent)}>
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Loading...
                </>
              ) : (
                'Load Structure'
              )}
            </Button>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Visualization Controls */}
        {proteinData && (
          <div className="flex gap-2 flex-wrap">
            <div className="flex-1 min-w-[150px]">
              <Label>Representation</Label>
              <Select value={representation} onValueChange={updateRepresentation}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="cartoon">Cartoon</SelectItem>
                  <SelectItem value="backbone">Backbone</SelectItem>
                  <SelectItem value="ball+stick">Ball & Stick</SelectItem>
                  <SelectItem value="spacefill">Space Fill</SelectItem>
                  <SelectItem value="surface">Surface</SelectItem>
                  <SelectItem value="ribbon">Ribbon</SelectItem>
                  <SelectItem value="licorice">Licorice</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex-1 min-w-[150px]">
              <Label>Color Scheme</Label>
              <Select value={colorScheme} onValueChange={updateColorScheme}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="chainname">By Chain</SelectItem>
                  <SelectItem value="residueindex">By Residue</SelectItem>
                  <SelectItem value="element">By Element</SelectItem>
                  <SelectItem value="bfactor">By B-Factor</SelectItem>
                  <SelectItem value="hydrophobicity">Hydrophobicity</SelectItem>
                  <SelectItem value="sstruc">Secondary Structure</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-end gap-1">
              <Button variant="outline" size="icon" onClick={resetView} title="Reset View">
                <RotateCw className="h-4 w-4" />
              </Button>
              <Button variant="outline" size="icon" onClick={zoomIn} title="Zoom In">
                <ZoomIn className="h-4 w-4" />
              </Button>
              <Button variant="outline" size="icon" onClick={zoomOut} title="Zoom Out">
                <ZoomOut className="h-4 w-4" />
              </Button>
              
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" size="icon" title="Export">
                    <Download className="h-4 w-4" />
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
              
              {enableVR && vrSupported && (
                <Button 
                  variant={vrActive ? "default" : "outline"} 
                  size="icon" 
                  onClick={enterVR} 
                  title="Enter VR"
                >
                  <Glasses className="h-4 w-4" />
                </Button>
              )}
            </div>
          </div>
        )}

        {/* Viewer Container */}
        <div
          ref={viewerRef}
          className="w-full h-[500px] border rounded-lg bg-white"
          style={{ position: 'relative' }}
        />

        {/* Structure Info */}
        {proteinData && (
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div>
              <div className="font-semibold">Atoms</div>
              <div className="text-muted-foreground">{proteinData.atom_count.toLocaleString()}</div>
            </div>
            <div>
              <div className="font-semibold">Residues</div>
              <div className="text-muted-foreground">{proteinData.residue_count.toLocaleString()}</div>
            </div>
            <div>
              <div className="font-semibold">Chains</div>
              <div className="text-muted-foreground">{proteinData.chain_count}</div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
