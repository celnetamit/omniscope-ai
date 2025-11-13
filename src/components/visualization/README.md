# 3D Visualization Components

This directory contains interactive 3D visualization components for OmniScope AI.

## Components

### NetworkGraph3D

Interactive 3D force-directed network graph visualization using three-forcegraph.

**Features:**
- Force-directed 3D layout with physics simulation
- Interactive node and edge styling
- Multiple coloring schemes (degree, type, centrality)
- Real-time interaction (click, hover, drag)
- Centrality metrics calculation
- Export to PNG
- Customizable node size, link width, and opacity

**Usage:**

```tsx
import { NetworkGraph3D } from '@/components/visualization';

const nodes = [
  { id: 'node1', label: 'Node 1', type: 'gene' },
  { id: 'node2', label: 'Node 2', type: 'protein' },
];

const edges = [
  { source: 'node1', target: 'node2', weight: 0.8 },
];

<NetworkGraph3D
  nodes={nodes}
  edges={edges}
  onNodeClick={(node) => console.log('Clicked:', node)}
  onNodeHover={(node) => console.log('Hovered:', node)}
/>
```

**Props:**
- `nodes`: Array of node objects with `id`, `label`, `type`, and optional `metadata`
- `edges`: Array of edge objects with `source`, `target`, `weight`, and optional `type`
- `onNodeClick`: Callback when a node is clicked
- `onNodeHover`: Callback when a node is hovered

**API Endpoint:**
- `POST /api/visualization/network/generate` - Generates network layout and calculates metrics

**Requirements Satisfied:**
- 3.2: Interactive 3D network visualization with force-directed layout
- Supports hover and click handlers
- Node and edge styling options
- Performance optimized for 1000+ nodes

### ProteinViewer

Interactive 3D protein structure viewer using NGL Viewer.

**Features:**
- Load PDB structures by ID or file content
- Multiple representation styles (cartoon, backbone, ball+stick, etc.)
- Multiple color schemes (by chain, residue, element, etc.)
- Interactive controls (rotation, zoom, selection)
- Export to PNG
- Structure statistics display

**Usage:**

```tsx
import { ProteinViewer } from '@/components/visualization';

<ProteinViewer
  pdbId="1ABC"
  onLoad={(data) => console.log('Loaded:', data)}
/>
```

**Requirements Satisfied:**
- 3.1: 3D protein structure rendering from PDB files
- 3.3: Interactive rotation, zoom, and selection controls

### DimensionalityPlot

Interactive 3D dimensionality reduction visualization using Plotly.js.

**Features:**
- Three reduction methods: PCA, t-SNE, and UMAP
- Color coding by metadata (categorical or continuous)
- Interactive 3D scatter plot with rotation and zoom
- Method-specific parameters (perplexity for t-SNE, n_neighbors for UMAP)
- Variance explained display (PCA)
- Export to PNG
- Real-time computation with progress indication

**Usage:**

```tsx
import { DimensionalityPlot } from '@/components/visualization';

const data = [
  [5.1, 3.5, 1.4, 0.2],
  [4.9, 3.0, 1.4, 0.2],
  // ... more samples
];

const metadata = ['Setosa', 'Setosa', /* ... */];

<DimensionalityPlot
  data={data}
  metadata={metadata}
  metadataName="Species"
  method="pca"
  autoCompute={false}
/>
```

**Props:**
- `data`: 2D array of numerical data (samples × features)
- `metadata`: Optional array of metadata values for color coding
- `metadataName`: Name of the metadata field (default: 'group')
- `method`: Reduction method - 'pca', 'tsne', or 'umap' (default: 'pca')
- `autoCompute`: Whether to compute on mount (default: false)
- `onMethodChange`: Callback when method is changed

**Methods:**
- **PCA**: Linear method, fast and deterministic, shows variance explained
- **t-SNE**: Non-linear, preserves local structure, good for clusters
- **UMAP**: Non-linear, preserves both local and global structure

**API Endpoint:**
- `POST /api/visualization/dimensionality-reduction` - Performs dimensionality reduction

**Requirements Satisfied:**
- 3.4: Multi-dimensional data visualization using PCA, t-SNE, and UMAP
- Color coding by metadata
- Interactive 3D scatter plots
- Export functionality

## Examples

See the `examples/` directory for complete working examples:
- `examples/network-graph/page.tsx` - Network graph demonstrations
- `examples/dimensionality-reduction/page.tsx` - Dimensionality reduction with sample datasets
- `examples/websocket/page.tsx` - Real-time collaboration example

## Backend API

All visualization components communicate with the backend API at `/api/visualization/`:

- `POST /api/visualization/protein/load` - Load protein structure
- `POST /api/visualization/network/generate` - Generate network graph
- `POST /api/visualization/dimensionality-reduction` - Perform dimensionality reduction
- `POST /api/visualization/export` - Export visualization

## Dependencies

- `three-forcegraph` - 3D force-directed graph
- `ngl` - Protein structure viewer
- `three` - 3D graphics library
- `@react-three/fiber` - React renderer for Three.js
- `@react-three/drei` - Useful helpers for React Three Fiber
- `plotly.js` - Interactive plotting library
- `react-plotly.js` - React wrapper for Plotly.js

## Performance Notes

- Network graphs are optimized for up to 1000 nodes
- Protein structures handle structures with 10,000+ atoms
- Dimensionality reduction supports datasets with 10,000+ features
- All components use dynamic imports to avoid SSR issues
- WebGL rendering ensures smooth 60 FPS performance
- Backend computation for dimensionality reduction typically completes in <5 seconds


### VRViewer

Immersive virtual reality visualization using WebXR API.

**Features:**
- Full WebXR API integration for immersive VR experiences
- VR controller support with interaction handlers
- Teleportation system for navigation in large scenes
- 6DOF (six degrees of freedom) tracking
- Compatible with major VR headsets (Meta Quest, HTC Vive, Valve Index)
- Real-time 3D scene rendering
- Session management (start/end VR sessions)
- Controller status monitoring
- Automatic capability detection

**Usage:**

```tsx
import { VRViewer } from '@/components/visualization';

<VRViewer
  scene={threeJsScene}
  enableControllers={true}
  enableTeleportation={true}
  onVRSessionStart={() => console.log('VR started')}
  onVRSessionEnd={() => console.log('VR ended')}
/>
```

**Props:**
- `scene`: Optional Three.js scene object (creates default scene if not provided)
- `enableControllers`: Enable VR controller support (default: true)
- `enableTeleportation`: Enable teleportation navigation (default: true)
- `onVRSessionStart`: Callback when VR session starts
- `onVRSessionEnd`: Callback when VR session ends

**VR Requirements:**
- WebXR-compatible browser (Chrome 79+, Edge 79+, Firefox 98+)
- VR headset with WebXR support
- HTTPS connection (required for WebXR API)
- Local development: use `localhost` or enable WebXR flags

**Supported VR Headsets:**
- Meta Quest 2/3/Pro
- HTC Vive/Vive Pro
- Valve Index
- Windows Mixed Reality headsets
- Pico VR headsets

**Controller Interactions:**
- **Trigger**: Select and interact with objects
- **Grip**: Grab and move objects
- **Thumbstick**: Navigate and teleport
- **Menu Button**: Access settings and exit VR

**Requirements Satisfied:**
- 3.6: VR support with WebXR API integration
- VR-compatible scene rendering
- VR controller support with interaction handlers
- Immersive visualization for molecular structures and networks

**Example Page:**
- `examples/vr-visualization/page.tsx` - Complete VR visualization demo

## VR Best Practices

When using the VR components:

1. **Scene Optimization**: Keep polygon count reasonable for VR (target 60-90 FPS)
   - Use level-of-detail (LOD) for complex models
   - Limit draw calls and shader complexity
   - Use instancing for repeated geometry

2. **Controller Interaction**: Provide clear visual feedback
   - Show ray casts from controllers
   - Highlight interactive objects on hover
   - Provide haptic feedback when available

3. **Comfort**: Implement smooth locomotion
   - Avoid rapid camera movements
   - Use teleportation for large distances
   - Provide comfort options (vignetting, snap turning)

4. **Accessibility**: Provide alternative viewing modes
   - Support both VR and non-VR viewing
   - Offer seated and standing experiences
   - Provide adjustable movement speeds

5. **Testing**: Test on multiple VR devices
   - Different headsets have different capabilities
   - Test controller mappings across devices
   - Verify performance on lower-end hardware

## Browser Compatibility

| Browser | 3D Visualization | VR Support |
|---------|-----------------|------------|
| Chrome 79+ | ✓ Full | ✓ Full |
| Edge 79+ | ✓ Full | ✓ Full |
| Firefox 98+ | ✓ Full | ✓ Full |
| Safari 15+ | ✓ Full | ✗ Limited |
| Mobile Chrome | ✓ Full | ✓ AR/VR |
| Mobile Safari | ✓ Full | ✗ Limited |

**Note**: VR features require HTTPS or localhost for security reasons.
