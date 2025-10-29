import streamlit as st
import streamlit.components.v1 as components

# ----------------------------------------------------------------------
#  Internal – expand the latest <iframe> so the canvas can fill 50 vh.
#  We inject this CSS only once per session.
# ----------------------------------------------------------------------
def _expand_iframe():
    # in utilities/animations.py -> _expand_iframe()
    st.markdown(
    """
    <style>
      /* match any Streamlit component iframe */
      iframe[src*="component"] {
        position: fixed !important;
        top: 0; left: 0;
        width: 100vw !important;
        height: 100vh !important;
        z-index: -1;
      }
    </style>
    """,
    unsafe_allow_html=True,
)


# ----------------------------------------------------------------------
#  Public – call this in any Streamlit page to add the neon stock line.
# ----------------------------------------------------------------------
def add_half_screen_stock_glow():
    """Injects the half-screen glowing stock-style background once."""
    _expand_iframe()          # make sure iframe can stretch

    html = """
    <canvas id="bgCanvas"></canvas>

    <style>
      /* Half-screen neon-glow chart anchored at bottom */
      #bgCanvas {
        position: fixed;
        bottom: -18; left: 0;
        width: 100vw;
        height: 100vh;          /* half the viewport height             */
        z-index: -1;           /* behind all Streamlit elements         */
        pointer-events: none;  /* clicks pass through                   */
        opacity: 0.70;         /* same as your original “10” but valid  */
      }
      body { margin: 0; }
    </style>

    <script>
    (function(){
      const canvas = document.getElementById('bgCanvas');
      const ctx    = canvas.getContext('2d');

      function resize(){
        canvas.width  = window.innerWidth;
        canvas.height = window.innerHeight * 0.5;  // match 50 vh
      }
      window.addEventListener('resize', resize);
      resize();

      /* ------- Generate upward random-walk line ------------------------ */
      const POINTS     = 600;
      const volatility = 30;
      const drift      = canvas.height / POINTS * 0.3;
      const topLimit   = canvas.height * 0.10;     // keep top 10 % clear
      let   y          = canvas.height;            // start at bottom
      const points     = [];

      for (let i = 0; i < POINTS; i++) {
        y = y - drift + (Math.random() - 0.5) * volatility;
        y = Math.max(topLimit, Math.min(canvas.height, y));
        const x = (i / (POINTS - 1)) * canvas.width;
        points.push([x, y]);
      }

      /* ------- Animation loop ----------------------------------------- */
      const FPS        = 80;
      const FRAME_TIME = 1000 / FPS;
      const speedPx    = 2;
      let offset       = 0;
      let lastTime     = 0;

      function draw(now){
      if (now - lastTime < FRAME_TIME){
        requestAnimationFrame(draw); return;
      }
      lastTime = now;

      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.save();
      ctx.translate(-offset, 0);

      /* Glow pass */
      ctx.beginPath();
      ctx.shadowColor = "rgba(0,255,0,0.95)";   // neon green glow
      ctx.shadowBlur  = 60;
      ctx.lineWidth   = 2;
      ctx.strokeStyle = "#39FF14";              // neon green line
      points.forEach(([x, y], i) => i ? ctx.lineTo(x, y) : ctx.moveTo(x, y));
      ctx.stroke();

      /* Crisp centre line */
      ctx.shadowBlur = 0;
      ctx.lineWidth  = 2;
      ctx.strokeStyle = "#39FF14";              // neon green line
      ctx.stroke();

      ctx.restore();

      offset += speedPx;
      if (offset > canvas.width) offset = 0;
      requestAnimationFrame(draw);
      }
      requestAnimationFrame(draw);
    })();
    </script>
    """

    # height=0 keeps layout flow compact; CSS + _expand_iframe handles sizing
    components.html(html, height=150, width=0)
