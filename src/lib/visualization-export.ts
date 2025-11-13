/**
 * Visualization Export Utilities
 * Provides export functionality for PNG, SVG, and interactive HTML formats
 */

export interface ExportOptions {
  filename?: string;
  width?: number;
  height?: number;
  backgroundColor?: string;
  scale?: number;
}

export interface HTMLExportOptions extends ExportOptions {
  includeControls?: boolean;
  includeData?: boolean;
  title?: string;
  description?: string;
}

/**
 * Export canvas element to PNG using canvas.toBlob
 */
export async function exportCanvasToPNG(
  canvas: HTMLCanvasElement,
  options: ExportOptions = {}
): Promise<void> {
  const {
    filename = `visualization_${Date.now()}.png`,
    width,
    height,
    scale = 2
  } = options;

  return new Promise((resolve, reject) => {
    try {
      // Create a temporary canvas for high-resolution export
      const exportCanvas = document.createElement('canvas');
      const ctx = exportCanvas.getContext('2d');
      
      if (!ctx) {
        reject(new Error('Failed to get canvas context'));
        return;
      }

      // Set dimensions
      const exportWidth = width || canvas.width;
      const exportHeight = height || canvas.height;
      exportCanvas.width = exportWidth * scale;
      exportCanvas.height = exportHeight * scale;

      // Scale context for high-resolution
      ctx.scale(scale, scale);

      // Draw original canvas
      ctx.drawImage(canvas, 0, 0, exportWidth, exportHeight);

      // Convert to blob and download
      exportCanvas.toBlob(
        (blob) => {
          if (!blob) {
            reject(new Error('Failed to create blob'));
            return;
          }

          downloadBlob(blob, filename);
          resolve();
        },
        'image/png',
        1.0
      );
    } catch (error) {
      reject(error);
    }
  });
}

/**
 * Export SVG element to SVG file
 */
export function exportSVG(
  svgElement: SVGElement,
  options: ExportOptions = {}
): void {
  const {
    filename = `visualization_${Date.now()}.svg`,
    width,
    height,
    backgroundColor = 'white'
  } = options;

  try {
    // Clone the SVG element
    const clonedSvg = svgElement.cloneNode(true) as SVGElement;

    // Set dimensions if provided
    if (width) clonedSvg.setAttribute('width', width.toString());
    if (height) clonedSvg.setAttribute('height', height.toString());

    // Add background if specified
    if (backgroundColor && backgroundColor !== 'transparent') {
      const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
      rect.setAttribute('width', '100%');
      rect.setAttribute('height', '100%');
      rect.setAttribute('fill', backgroundColor);
      clonedSvg.insertBefore(rect, clonedSvg.firstChild);
    }

    // Add XML declaration and DOCTYPE
    const svgString = new XMLSerializer().serializeToString(clonedSvg);
    const svgBlob = new Blob(
      [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">',
        svgString
      ],
      { type: 'image/svg+xml;charset=utf-8' }
    );

    downloadBlob(svgBlob, filename);
  } catch (error) {
    console.error('Failed to export SVG:', error);
    throw error;
  }
}

/**
 * Export Three.js scene to PNG
 */
export async function exportThreeSceneToPNG(
  renderer: any,
  scene: any,
  camera: any,
  options: ExportOptions = {}
): Promise<void> {
  const {
    filename = `3d_visualization_${Date.now()}.png`,
    width = 1920,
    height = 1080,
    scale = 1
  } = options;

  try {
    // Store original size
    const originalSize = renderer.getSize(new (await import('three')).Vector2());

    // Set export size
    renderer.setSize(width * scale, height * scale);

    // Render scene
    renderer.render(scene, camera);

    // Get canvas and export
    const canvas = renderer.domElement;
    await exportCanvasToPNG(canvas, { filename, scale: 1 }); // Scale already applied

    // Restore original size
    renderer.setSize(originalSize.x, originalSize.y);
  } catch (error) {
    console.error('Failed to export Three.js scene:', error);
    throw error;
  }
}

/**
 * Export Plotly chart to PNG
 */
export async function exportPlotlyToPNG(
  plotElement: HTMLElement,
  options: ExportOptions = {}
): Promise<void> {
  const {
    filename = `plot_${Date.now()}.png`,
    width = 1920,
    height = 1080
  } = options;

  try {
    // Dynamically import Plotly
    const Plotly = await import('plotly.js');

    await Plotly.downloadImage(plotElement, {
      format: 'png',
      width,
      height,
      filename: filename.replace('.png', '')
    });
  } catch (error) {
    console.error('Failed to export Plotly chart:', error);
    throw error;
  }
}

/**
 * Export Plotly chart to SVG
 */
export async function exportPlotlyToSVG(
  plotElement: HTMLElement,
  options: ExportOptions = {}
): Promise<void> {
  const {
    filename = `plot_${Date.now()}.svg`,
    width = 1920,
    height = 1080
  } = options;

  try {
    const Plotly = await import('plotly.js');

    await Plotly.downloadImage(plotElement, {
      format: 'svg',
      width,
      height,
      filename: filename.replace('.svg', '')
    });
  } catch (error) {
    console.error('Failed to export Plotly chart to SVG:', error);
    throw error;
  }
}

/**
 * Create interactive HTML export with embedded data and controls
 */
export function exportInteractiveHTML(
  content: {
    title: string;
    description?: string;
    htmlContent: string;
    scripts?: string[];
    styles?: string[];
    data?: any;
  },
  options: HTMLExportOptions = {}
): void {
  const {
    filename = `interactive_visualization_${Date.now()}.html`,
    includeControls = true,
    includeData = true
  } = options;

  const { title, description, htmlContent, scripts = [], styles = [], data } = content;

  // Build HTML document
  const html = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${escapeHtml(title)}</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        h1 {
            margin-top: 0;
            color: #333;
        }
        .description {
            color: #666;
            margin-bottom: 20px;
        }
        .visualization {
            margin: 20px 0;
        }
        ${includeControls ? `
        .controls {
            margin: 20px 0;
            padding: 15px;
            background: #f9f9f9;
            border-radius: 4px;
        }
        .controls button {
            padding: 8px 16px;
            margin-right: 10px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        .controls button:hover {
            background: #0056b3;
        }
        ` : ''}
        ${styles.join('\n')}
    </style>
</head>
<body>
    <div class="container">
        <h1>${escapeHtml(title)}</h1>
        ${description ? `<p class="description">${escapeHtml(description)}</p>` : ''}
        
        ${includeControls ? `
        <div class="controls">
            <button onclick="resetView()">Reset View</button>
            <button onclick="exportImage()">Export as PNG</button>
            <button onclick="toggleFullscreen()">Fullscreen</button>
        </div>
        ` : ''}
        
        <div class="visualization">
            ${htmlContent}
        </div>
    </div>

    ${includeData && data ? `
    <script>
        // Embedded data
        window.visualizationData = ${JSON.stringify(data)};
    </script>
    ` : ''}

    ${scripts.map(script => `<script src="${script}"></script>`).join('\n')}

    ${includeControls ? `
    <script>
        function resetView() {
            if (window.resetVisualization) {
                window.resetVisualization();
            }
        }

        function exportImage() {
            const canvas = document.querySelector('canvas');
            if (canvas) {
                canvas.toBlob(blob => {
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'visualization.png';
                    a.click();
                    URL.revokeObjectURL(url);
                });
            }
        }

        function toggleFullscreen() {
            if (!document.fullscreenElement) {
                document.documentElement.requestFullscreen();
            } else {
                document.exitFullscreen();
            }
        }
    </script>
    ` : ''}
</body>
</html>`;

  // Create and download HTML file
  const blob = new Blob([html], { type: 'text/html;charset=utf-8' });
  downloadBlob(blob, filename);
}

/**
 * Export NGL Viewer scene to interactive HTML
 */
export async function exportNGLToHTML(
  pdbContent: string,
  representation: string,
  colorScheme: string,
  options: HTMLExportOptions = {}
): Promise<void> {
  const {
    filename = `protein_structure_${Date.now()}.html`,
    title = 'Protein Structure Visualization',
    description = 'Interactive 3D protein structure viewer'
  } = options;

  const htmlContent = `
    <div id="viewport" style="width: 100%; height: 600px;"></div>
    <script src="https://unpkg.com/ngl@2.0.0-dev.37/dist/ngl.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            var stage = new NGL.Stage('viewport', { backgroundColor: 'white' });
            
            var pdbContent = ${JSON.stringify(pdbContent)};
            var stringBlob = new Blob([pdbContent], { type: 'text/plain' });
            
            stage.loadFile(stringBlob, { ext: 'pdb' }).then(function(component) {
                component.addRepresentation('${representation}', {
                    colorScheme: '${colorScheme}'
                });
                stage.autoView();
                
                window.resetVisualization = function() {
                    stage.autoView();
                };
            });
            
            window.addEventListener('resize', function() {
                stage.handleResize();
            });
        });
    </script>
  `;

  exportInteractiveHTML(
    {
      title,
      description,
      htmlContent,
      scripts: [],
      styles: []
    },
    { filename, includeControls: true, includeData: false }
  );
}

/**
 * Export Three.js Force Graph to interactive HTML
 */
export async function exportForceGraphToHTML(
  graphData: { nodes: any[]; links: any[] },
  options: HTMLExportOptions = {}
): Promise<void> {
  const {
    filename = `network_graph_${Date.now()}.html`,
    title = '3D Network Graph',
    description = 'Interactive 3D force-directed network visualization'
  } = options;

  const htmlContent = `
    <div id="3d-graph" style="width: 100%; height: 600px;"></div>
    <script src="https://unpkg.com/three"></script>
    <script src="https://unpkg.com/three-spritetext"></script>
    <script src="https://unpkg.com/3d-force-graph"></script>
    <script>
        const graphData = ${JSON.stringify(graphData)};
        
        const Graph = ForceGraph3D()
            (document.getElementById('3d-graph'))
            .graphData(graphData)
            .nodeLabel('label')
            .nodeAutoColorBy('type')
            .linkDirectionalParticles(2)
            .linkDirectionalParticleWidth(1)
            .backgroundColor('#ffffff');
        
        window.resetVisualization = function() {
            Graph.zoomToFit(400);
        };
    </script>
  `;

  exportInteractiveHTML(
    {
      title,
      description,
      htmlContent,
      data: graphData
    },
    { filename, includeControls: true, includeData: true }
  );
}

/**
 * Export Plotly chart to interactive HTML
 */
export async function exportPlotlyToHTML(
  plotData: any[],
  plotLayout: any,
  options: HTMLExportOptions = {}
): Promise<void> {
  const {
    filename = `plot_${Date.now()}.html`,
    title = 'Interactive Plot',
    description = 'Interactive data visualization'
  } = options;

  const htmlContent = `
    <div id="plotly-chart" style="width: 100%; height: 600px;"></div>
    <script src="https://cdn.plot.ly/plotly-2.26.0.min.js"></script>
    <script>
        const data = ${JSON.stringify(plotData)};
        const layout = ${JSON.stringify(plotLayout)};
        
        Plotly.newPlot('plotly-chart', data, layout, {
            responsive: true,
            displayModeBar: true,
            displaylogo: false
        });
        
        window.resetVisualization = function() {
            Plotly.relayout('plotly-chart', {
                'scene.camera': {
                    eye: { x: 1.5, y: 1.5, z: 1.5 }
                }
            });
        };
    </script>
  `;

  exportInteractiveHTML(
    {
      title,
      description,
      htmlContent,
      data: { plotData, plotLayout }
    },
    { filename, includeControls: true, includeData: true }
  );
}

/**
 * Helper function to download blob
 */
function downloadBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

/**
 * Helper function to escape HTML
 */
function escapeHtml(text: string): string {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

/**
 * Export multiple formats at once
 */
export async function exportMultipleFormats(
  exportFunctions: Array<() => Promise<void>>,
  onProgress?: (completed: number, total: number) => void
): Promise<void> {
  const total = exportFunctions.length;
  let completed = 0;

  for (const exportFn of exportFunctions) {
    await exportFn();
    completed++;
    if (onProgress) {
      onProgress(completed, total);
    }
  }
}
