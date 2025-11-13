# Visualization Export Guide

This guide explains how to use the export functionality for all visualization components in OmniScope AI.

## Overview

All visualization components now support exporting in three formats:
- **PNG**: High-resolution raster images using `canvas.toBlob`
- **SVG**: Vector graphics for scalable, publication-quality images
- **Interactive HTML**: Standalone HTML files with embedded data and controls

## Supported Components

### 1. Protein Viewer (`ProteinViewer`)

Exports 3D protein structures visualized with NGL Viewer.

**Export Options:**
- **PNG**: 2x resolution snapshot of the current view
- **SVG**: Vector-based snapshot (canvas embedded in SVG)
- **Interactive HTML**: Standalone viewer with NGL library embedded

**Usage:**
```tsx
import { ProteinViewer } from '@/components/visualization';

<ProteinViewer pdbId="1ABC" />
```

Click the export dropdown button and select your desired format.

**Interactive HTML Features:**
- Fully functional NGL viewer
- All representation and color scheme options
- Rotation, zoom, and pan controls
- Reset view button
- Fullscreen mode

### 2. Network Graph 3D (`NetworkGraph3D`)

Exports 3D force-directed network graphs.

**Export Options:**
- **PNG**: High-resolution snapshot (2x scale)
- **SVG**: Vector snapshot with embedded canvas
- **Interactive HTML**: Standalone 3D force graph with Three.js

**Usage:**
```tsx
import { NetworkGraph3D } from '@/components/visualization';

<NetworkGraph3D nodes={nodes} edges={edges} />
```

**Interactive HTML Features:**
- Full 3D force-directed layout
- Node and edge interactions
- Zoom and rotation controls
- Node selection and highlighting
- Customizable colors and sizes

### 3. Dimensionality Plot (`DimensionalityPlot`)

Exports PCA, t-SNE, and UMAP visualizations.

**Export Options:**
- **PNG**: 1920x1080 high-resolution image
- **SVG**: Vector format for publications
- **Interactive HTML**: Plotly-powered interactive plot

**Usage:**
```tsx
import { DimensionalityPlot } from '@/components/visualization';

<DimensionalityPlot 
  data={data} 
  metadata={metadata} 
  method="pca" 
/>
```

**Interactive HTML Features:**
- Full Plotly interactivity
- Zoom, pan, and rotate
- Hover tooltips
- Legend interactions
- Camera reset

### 4. VR Viewer (`VRViewer`)

Exports WebXR-enabled VR scenes.

**Export Options:**
- **PNG**: Snapshot of the current scene
- **SVG**: Vector snapshot
- **Interactive HTML**: WebXR-enabled scene with VR button

**Usage:**
```tsx
import { VRViewer } from '@/components/visualization';

<VRViewer enableControllers enableTeleportation />
```

**Interactive HTML Features:**
- WebXR VR support
- VR button for immersive mode
- Desktop fallback view
- Scene controls

## Export Utility Functions

The `visualization-export.ts` module provides low-level export functions:

### Canvas Export

```typescript
import { exportCanvasToPNG } from '@/lib/visualization-export';

await exportCanvasToPNG(canvas, {
  filename: 'my-visualization.png',
  width: 1920,
  height: 1080,
  scale: 2
});
```

### SVG Export

```typescript
import { exportSVG } from '@/lib/visualization-export';

exportSVG(svgElement, {
  filename: 'my-visualization.svg',
  width: 1920,
  height: 1080,
  backgroundColor: 'white'
});
```

### Three.js Scene Export

```typescript
import { exportThreeSceneToPNG } from '@/lib/visualization-export';

await exportThreeSceneToPNG(renderer, scene, camera, {
  filename: '3d-scene.png',
  width: 1920,
  height: 1080
});
```

### Plotly Export

```typescript
import { exportPlotlyToPNG, exportPlotlyToSVG } from '@/lib/visualization-export';

// PNG export
await exportPlotlyToPNG(plotElement, {
  filename: 'plot.png',
  width: 1920,
  height: 1080
});

// SVG export
await exportPlotlyToSVG(plotElement, {
  filename: 'plot.svg',
  width: 1920,
  height: 1080
});
```

### Interactive HTML Export

```typescript
import { exportInteractiveHTML } from '@/lib/visualization-export';

exportInteractiveHTML(
  {
    title: 'My Visualization',
    description: 'Interactive data visualization',
    htmlContent: '<div id="viz"></div>',
    scripts: ['https://cdn.example.com/library.js'],
    styles: ['body { margin: 0; }'],
    data: { /* your data */ }
  },
  {
    filename: 'visualization.html',
    includeControls: true,
    includeData: true
  }
);
```

## Specialized Export Functions

### NGL Protein Structure to HTML

```typescript
import { exportNGLToHTML } from '@/lib/visualization-export';

await exportNGLToHTML(
  pdbContent,
  'cartoon',
  'chainname',
  {
    filename: 'protein.html',
    title: 'Protein Structure',
    description: 'Interactive 3D protein viewer'
  }
);
```

### Force Graph to HTML

```typescript
import { exportForceGraphToHTML } from '@/lib/visualization-export';

await exportForceGraphToHTML(
  { nodes, links },
  {
    filename: 'network.html',
    title: '3D Network Graph',
    description: 'Interactive network visualization'
  }
);
```

### Plotly to HTML

```typescript
import { exportPlotlyToHTML } from '@/lib/visualization-export';

await exportPlotlyToHTML(
  plotData,
  plotLayout,
  {
    filename: 'plot.html',
    title: 'Interactive Plot',
    description: 'Data visualization'
  }
);
```

## Export Options Reference

### Common Options

```typescript
interface ExportOptions {
  filename?: string;        // Output filename
  width?: number;          // Export width in pixels
  height?: number;         // Export height in pixels
  backgroundColor?: string; // Background color
  scale?: number;          // Resolution scale factor
}
```

### HTML Export Options

```typescript
interface HTMLExportOptions extends ExportOptions {
  includeControls?: boolean;  // Include control buttons
  includeData?: boolean;      // Embed data in HTML
  title?: string;            // Document title
  description?: string;      // Document description
}
```

## Best Practices

### 1. PNG Exports
- Use `scale: 2` or higher for high-DPI displays
- Default resolution is 1920x1080 for most exports
- PNG is best for presentations and quick sharing

### 2. SVG Exports
- Ideal for publications and print materials
- Scalable without quality loss
- Some 3D visualizations embed raster images in SVG

### 3. Interactive HTML Exports
- Perfect for sharing with collaborators
- No server required - works offline
- Includes all necessary libraries via CDN
- Data can be embedded or loaded separately

### 4. File Sizes
- PNG: 100KB - 5MB depending on complexity
- SVG: 50KB - 2MB (smaller for simple graphics)
- HTML: 10KB - 500KB (larger if data embedded)

## Troubleshooting

### Export Button Not Visible
- Ensure data is loaded before exporting
- Check that the visualization has rendered successfully

### PNG Export Quality Issues
- Increase the `scale` parameter
- Ensure canvas is fully rendered before export

### SVG Export Not Working
- Some 3D visualizations use canvas-to-SVG conversion
- Check browser console for errors

### HTML Export Not Interactive
- Verify CDN links are accessible
- Check browser console for JavaScript errors
- Ensure data is properly serialized

## Requirements Compliance

This implementation satisfies **Requirement 3.5**:

> THE Visualization_Engine SHALL allow Users to export 3D visualizations in at least 3 formats (PNG, SVG, interactive HTML)

All four visualization components support:
- ✅ PNG export using `canvas.toBlob`
- ✅ SVG export for vector graphics
- ✅ Interactive HTML export with embedded controls

## Examples

### Example 1: Export Protein Structure

```typescript
// Load protein
const viewer = <ProteinViewer pdbId="1ABC" />;

// User clicks export dropdown
// Selects "Export as PNG"
// Downloads: protein_1ABC.png (high resolution)

// Selects "Export Interactive HTML"
// Downloads: protein_1ABC.html (standalone viewer)
```

### Example 2: Export Network Graph

```typescript
// Create network
const graph = <NetworkGraph3D nodes={nodes} edges={edges} />;

// Export as SVG for publication
// Downloads: network_graph_3d.svg (vector format)
```

### Example 3: Export Dimensionality Reduction

```typescript
// Compute PCA
const plot = <DimensionalityPlot data={data} method="pca" />;

// Export interactive HTML
// Downloads: pca_plot.html (with Plotly controls)
```

## API Integration

The export functionality integrates with the backend API for data processing but performs exports entirely client-side for security and performance.

No server-side processing is required for exports, ensuring:
- Fast export times
- No data transmission overhead
- Privacy-preserving (data stays in browser)
- Works offline after initial load

## Future Enhancements

Potential future additions:
- PDF export with vector graphics
- Animated GIF export for time-series
- 3D model export (OBJ, STL, GLTF)
- Batch export of multiple visualizations
- Custom export templates
- Cloud storage integration

## Support

For issues or questions about export functionality:
1. Check browser console for errors
2. Verify visualization is fully loaded
3. Try different export formats
4. Check browser compatibility (Chrome, Firefox, Edge recommended)
