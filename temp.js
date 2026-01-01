        let currentHistory = null;
        let panX = 0;
        let panY = 0;
        let zoom = 1.0;
        let isDragging = false;
        let dragStartX = 0;
        let dragStartY = 0;

        async function compile() {
            let program = document.getElementById('program-input').value.trim();
            // Default to multiply program to show B-gliders
            if (!program) {
                program = '++[>++++++<-]>';
                document.getElementById('program-input').value = program;
            }

const status = document.getElementById('status');
            status.textContent = 'Compiling...';
            status.className = 'status';

try {
                const response = await fetch('http://localhost:5000/compile', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ program })
                });

if (!response.ok) throw new Error(`HTTP ${response.status}`);

const result = await response.json();

// Display INPUT
                document.getElementById('input-display').textContent = program;

// Set history, regions, and gliders for matrix
                currentHistory = result.history || [result.rule110_initial];
                currentRegions = result.regions || {};
                currentGliderTracks = result.glider_tracks || [];

// Display OUTPUT
                const tmTape = result.verification?.tm_tape || '?';
                const tmOutput = result.verification?.tm_output || '';

// For programs without . command, the result is in the tape
                // Tape "11" might represent cell values, but interpretation depends on encoding
                let outputDisplay = `Tape: ${tmTape}`;
                if (tmOutput) {
                    outputDisplay += ` | Changes tracked: ${tmOutput}`;
                } else {
                    outputDisplay += ` | (No output command - result in tape)`;
                }

document.getElementById('output-display').textContent = outputDisplay;

// Update decoding section
                updateDecodingSection(result);

drawMatrix();

status.textContent = 'Ready';
                status.className = 'status success';

} catch (error) {
                console.error('Compilation error:', error);
                status.textContent = `Error: ${error.message}`;
                status.className = 'status error';
            }
        }





        const canvas = document.getElementById('matrix-canvas');
        const ctx = canvas.getContext('2d');
        const container = document.getElementById('matrix-container');

        function resizeCanvas() {
            canvas.width = container.clientWidth;
            canvas.height = container.clientHeight;
        }

        let currentRegions = {};
        let currentGliderTracks = [];


        container.addEventListener('mouseup', () => {
            isDragging = false;
            container.classList.remove('dragging');

        container.addEventListener('mouseleave', () => {
            isDragging = false;
            container.classList.remove('dragging');

        // Visibility toggle function
        function updateVisibility() {
            showInputRegions = document.getElementById('show-input').checked;
            showOutputRegions = document.getElementById('show-output').checked;
            drawMatrix();
        }

        // Zoom handling
        container.addEventListener('wheel', (e) => {
            e.preventDefault();
            const zoomFactor = e.deltaY > 0 ? 0.9 : 1.1;
            zoom = Math.max(0.1, Math.min(5, zoom * zoomFactor));
            drawMatrix();



            const status = document.getElementById('status');
            status.textContent = 'Compiling...';
            status.className = 'status';


                if (!response.ok) throw new Error(`HTTP ${response.status}`);

                const result = await response.json();

                // Display INPUT
                document.getElementById('input-display').textContent = program;

                // Set history, regions, and gliders for matrix
                currentHistory = result.history || [result.rule110_initial];
                currentRegions = result.regions || {};
                currentGliderTracks = result.glider_tracks || [];
                
                // Display OUTPUT
                const tmTape = result.verification?.tm_tape || '?';
                const tmOutput = result.verification?.tm_output || '';
                
                // For programs without . command, the result is in the tape
                // Tape "11" might represent cell values, but interpretation depends on encoding
                let outputDisplay = `Tape: ${tmTape}`;
                if (tmOutput) {
                    outputDisplay += ` | Changes tracked: ${tmOutput}`;
                    outputDisplay += ` | (No output command - result in tape)`;
                
                // Show output region info
                if (currentRegions['output-tape'] && currentRegions['output-tape'].length > 0) {
                    const outputRegion = currentRegions['output-tape'][0];
                    outputDisplay += ` | Output region: cells ${outputRegion.start}-${outputRegion.end}`;
                
                document.getElementById('output-display').textContent = outputDisplay;
                
                // Update decoding section
                updateDecodingSection(result);
                
                // Reset pan/zoom for new data
                panX = 0;
                panY = 0;
                zoom = 1.0;

                resizeCanvas();
                drawMatrix();

                status.textContent = `✅ Computation complete (${currentHistory.length} steps)`;
                status.className = 'status success';

        }

        function loadExample() {
            const select = document.getElementById('examples');
            if (select.value) {
                document.getElementById('program-input').value = select.value;
        }

        // Initialize
        window.addEventListener('resize', () => {
            resizeCanvas();
            drawMatrix();
        resizeCanvas();
        drawMatrix();

        // Auto-compile on page load
        const program = document.getElementById('program-input').value.trim();
        if (program) {
            compile();
        }

        // Auto-compile on input change
        document.getElementById('program-input').addEventListener('input', () => {
            const program = document.getElementById('program-input').value.trim();
            if (program) {
                compile();

        // Also compile on Enter (backup)
        document.getElementById('program-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') compile();
