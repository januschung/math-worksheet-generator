"""
main.py
-------
FastAPI web API for generating math worksheet PDFs. Exposes endpoints for worksheet generation, serving PDFs, and providing default problem ranges. Also serves a modern web UI for interactive worksheet creation.
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from uuid import uuid4
import worksheet_core

app = FastAPI(title="Math Worksheet Web API")

# ---------------------------------------------------------------------------
# Configuration & helpers
# ---------------------------------------------------------------------------
OUTPUT_DIR = Path(__file__).parent / "generated"
OUTPUT_DIR.mkdir(exist_ok=True)

PROBLEM_CLASS_MAP = {
    "multiplication": worksheet_core.MultiplicationProblem,
    "addition": worksheet_core.AdditionProblem,
    "subtraction": worksheet_core.SubtractionProblem,
    "division": worksheet_core.DivisionProblem,
    "missingfactor": worksheet_core.MissingFactorProblem,
    "fractioncompare": worksheet_core.FractionComparisonProblem,
}


def parse_range(txt: str):
    """Parse 'min..max' as (min, max) or raise HTTPException on error."""
    try:
        return worksheet_core.parse_range(txt)
    except ValueError:
        raise HTTPException(status_code=400, detail="Ranges must be in 'min..max' format with min ≤ max")


def clean_old_files(limit: int = 50):
    """Delete oldest PDFs to prevent unbounded storage growth."""
    pdfs = sorted(OUTPUT_DIR.glob("*.pdf"), key=lambda p: p.stat().st_mtime)
    for p in pdfs[:-limit]:
        p.unlink(missing_ok=True)

# ---------------------------------------------------------------------------
# API routes
# ---------------------------------------------------------------------------

@app.post("/generate")
async def generate_worksheet(payload: dict):
    """
    Create a worksheet PDF and return its URL.
    Request body:
      {
        "problem_types": ["multiplication", ...],
        "n": 100,
        "term1": "2..12",          # optional, single-type only
        "term2": "2..12",          # optional, single-type only
        "defaults": {               # optional per-type overrides
          "multiplication": {"term1": "3..12", "term2": "2..15"}
        }
      }
    Response:
      {"url": "/pdf/worksheet_xxx.pdf"}
    """
    types = payload.get("problem_types")
    if not types or not isinstance(types, list):
        raise HTTPException(status_code=400, detail="'problem_types' must be a non‑empty list")

    classes = []
    for t in types:
        cls = PROBLEM_CLASS_MAP.get(t.lower())
        if not cls:
            raise HTTPException(status_code=400, detail=f"Unknown problem type: {t}")
        classes.append(cls)

    try:
        n = int(payload.get("n", worksheet_core.DEFAULT_N))
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="'n' must be an integer")
    if n <= 0:
        raise HTTPException(status_code=400, detail="'n' must be positive")

    try:
        chunk = int(payload.get("chunk", 25))
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="'chunk' must be an integer")
    if chunk <= 0 or chunk > 50:
        raise HTTPException(status_code=400, detail="'chunk' must be between 1 and 50")

    # Parse per-type default overrides
    overrides_raw = payload.get("defaults", {})
    per_type_ranges = {}
    for name, rng in overrides_raw.items():
        cls = PROBLEM_CLASS_MAP.get(name.lower())
        if not cls:
            raise HTTPException(status_code=400, detail=f"Unknown problem type in defaults: {name}")
        try:
            t1 = parse_range(rng["term1"])
            t2 = parse_range(rng["term2"])
        except KeyError:
            raise HTTPException(status_code=400, detail=f"Both term1 and term2 must be provided for {name}")
        per_type_ranges[cls] = (t1, t2)

    file_id = uuid4().hex
    out_path = OUTPUT_DIR / f"worksheet_{file_id}.pdf"

    if len(classes) == 1:
        # Single-type worksheet (optionally supports term1/term2)
        cls = classes[0]
        term1_txt = payload.get("term1")
        term2_txt = payload.get("term2")
        if (term1_txt is None) ^ (term2_txt is None):
            raise HTTPException(status_code=400, detail="Provide BOTH term1 and term2 or neither")
        if term1_txt:
            term1_range = parse_range(term1_txt)
            term2_range = parse_range(term2_txt)
        elif cls in per_type_ranges:
            term1_range, term2_range = per_type_ranges[cls]
        else:
            term1_range, term2_range = worksheet_core.PROBLEM_DEFAULTS[cls]
        gen = worksheet_core.WorksheetGenerator(cls, n, term1_range, term2_range, str(out_path))
        gen.generate_problems()
        gen.create_pdf()
    else:
        # Multi-type worksheet (no term1/term2 allowed, only per-type defaults)
        if payload.get("term1") or payload.get("term2"):
            raise HTTPException(status_code=400, detail="term1/term2 not allowed with multiple types")
        problems_by_type = []
        for cls in classes:
            if cls in per_type_ranges:
                t1, t2 = per_type_ranges[cls]
            else:
                t1, t2 = worksheet_core.PROBLEM_DEFAULTS[cls]
            plist = worksheet_core.make_problems(cls, n, t1, t2)
            problems_by_type.append((cls, plist))
        gen = worksheet_core.MixedWorksheetGenerator(problems_by_type, str(out_path), chunk_size=chunk)
        gen.create_pdf()

    clean_old_files()
    return {"url": f"/pdf/{out_path.name}"}


@app.get("/pdf/{filename}")
async def serve_pdf(filename: str):
    """Serve a generated PDF for inline display or download."""
    path = OUTPUT_DIR / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    # Inline display so <iframe> can render it instead of forcing download
    headers = {"Content-Disposition": f"inline; filename=\"{filename}\""}
    return FileResponse(path, media_type="application/pdf", headers=headers)


@app.get("/")
async def index():
    """
    Serve the interactive web UI for worksheet generation and preview.
    The UI fetches /defaults to prepopulate term ranges and provides a modern, user-friendly experience.
    """
    html = """
    <!doctype html>
    <html lang='en'>
    <head>
      <meta charset='utf-8'>
      <meta name='viewport' content='width=device-width, initial-scale=1'>
      <title>Math Worksheet Generator</title>
      <style>
        body{font-family:sans-serif;max-width:800px;margin:2rem auto;padding:0 1rem;line-height:1.4;background:#f9f9fb}
        fieldset{border:1px solid #ccc;margin-bottom:1rem;background:#fff;padding:1rem 1.5rem;border-radius:8px;box-shadow:0 2px 8px #0001}
        .row{display:flex;flex-wrap:wrap;align-items:center;margin:0.5rem 0}
        .row label{min-width:160px;font-weight:500}
        .row input[type=text]{width:90px;margin-left:0.25rem}
        .row input[type=text]:disabled{background:#eee}
        .default-hint{color:#888;font-size:0.95em;margin-left:0.5em}
        .reset-btn{margin-left:0.5em;font-size:0.9em;padding:0.1em 0.5em;border-radius:4px;border:1px solid #ccc;background:#f3f3f3;cursor:pointer}
        .reset-btn:disabled{color:#aaa;border-color:#eee;background:#fafafa;cursor:default}
        .range-help{margin:0.3rem 0 0.8rem;color:#555;font-size:0.95em}
        .desc{color:#555;font-size:0.9em;margin-left:0.5em}
        .example{color:#777;font-size:0.9em;margin-left:0.5em;font-style:italic}
        input[type=number]{width:80px}
        button[type=submit]{margin-left:0.5rem;padding:0.4em 1.2em;font-size:1.1em;border-radius:6px;border:1px solid #888;background:#4a90e2;color:#fff;cursor:pointer}
        button[type=submit]:hover{background:#357ab8}
        iframe{border:1px solid #ccc;margin-top:1rem}
      </style>
    </head>
    <body>
      <h1>Math Worksheet Generator</h1>

      <form id='cfg'>
        <fieldset>
          <legend>Problem Types &amp; Optional Term Ranges</legend>
          <p class="range-help">Ranges use <code>min..max</code> format (e.g. <code>3..12</code>). Term1 is the first number and term2 the second. For division they set the divisor and quotient. Fraction comparison uses them as denominators.</p>

          <div class='row' data-type='multiplication'>
            <label><input type='checkbox' name='ptype' value='multiplication'>Multiplication</label>
            term1 <input type='text' id='multiplication_term1'>
            term2 <input type='text' id='multiplication_term2'>
            <span class="default-hint" id="multiplication_hint"></span>
            <button type="button" class="reset-btn" id="multiplication_reset">Reset</button>
            <span class="desc">term1 × term2</span>
            <span class="example" id="multiplication_example"></span>
          </div>
          <div class='row' data-type='addition'>
            <label><input type='checkbox' name='ptype' value='addition'>Addition</label>
            term1 <input type='text' id='addition_term1'>
            term2 <input type='text' id='addition_term2'>
            <span class="default-hint" id="addition_hint"></span>
            <button type="button" class="reset-btn" id="addition_reset">Reset</button>
            <span class="desc">term1 + term2</span>
            <span class="example" id="addition_example"></span>
          </div>
          <div class='row' data-type='subtraction'>
            <label><input type='checkbox' name='ptype' value='subtraction'>Subtraction</label>
            term1 <input type='text' id='subtraction_term1'>
            term2 <input type='text' id='subtraction_term2'>
            <span class="default-hint" id="subtraction_hint"></span>
            <button type="button" class="reset-btn" id="subtraction_reset">Reset</button>
            <span class="desc">term1 - term2</span>
            <span class="example" id="subtraction_example"></span>
          </div>
          <div class='row' data-type='division'>
            <label><input type='checkbox' name='ptype' value='division'>Division</label>
            term1 <input type='text' id='division_term1'>
            term2 <input type='text' id='division_term2'>
            <span class="default-hint" id="division_hint"></span>
            <button type="button" class="reset-btn" id="division_reset">Reset</button>
            <span class="desc">dividend ÷ term1 (divisor) = term2 (quotient)</span>
            <span class="example" id="division_example"></span>
          </div>
          <div class='row' data-type='missingfactor'>
            <label><input type='checkbox' name='ptype' value='missingfactor'>Missing&nbsp;Factor</label>
            term1 <input type='text' id='missingfactor_term1'>
            term2 <input type='text' id='missingfactor_term2'>
            <span class="default-hint" id="missingfactor_hint"></span>
            <button type="button" class="reset-btn" id="missingfactor_reset">Reset</button>
            <span class="desc">term1 × term2 with one blank</span>
            <span class="example" id="missingfactor_example"></span>
          </div>
          <div class='row' data-type='fractioncompare'>
            <label><input type='checkbox' name='ptype' value='fractioncompare'>Fraction&nbsp;Compare</label>
            term1 <input type='text' id='fractioncompare_term1'>
            term2 <input type='text' id='fractioncompare_term2'>
            <span class="default-hint" id="fractioncompare_hint"></span>
            <button type="button" class="reset-btn" id="fractioncompare_reset">Reset</button>
            <span class="desc">compare 1/term1 and 1/term2</span>
            <span class="example" id="fractioncompare_example"></span>
          </div>
        </fieldset>

        <label>Problems per type: <input type='number' name='n' id='n' value='100' min='1'></label>
        <label>Problems per section: <input type='number' name='chunk' id='chunk' value='25' min='1' max='50'></label>
        <button type='submit'>Generate</button>
      </form>

      <h2>Preview</h2>
      <iframe id='preview' style='width:100%;height:80vh'></iframe>

<script>
(async function(){
  const form = document.getElementById('cfg');
  const frame = document.getElementById('preview');
  const defaults = await fetch('/defaults').then(r => r.json());
  const types = Object.keys(defaults);

  function parseRange(txt){
    const [a,b] = txt.split('..').map(Number);
    return [a,b];
  }

  function exampleFor(type, r1, r2){
    const [a1,a2] = parseRange(r1);
    const [b1,b2] = parseRange(r2);
    switch(type){
      case 'multiplication':
        return `${a1} × ${b2}`;
      case 'addition':
        return `${a1} + ${b2}`;
      case 'subtraction':
        return `${a2} - ${b1}`;
      case 'division':
        return `${a1*b2} ÷ ${a1}`;
      case 'missingfactor':
        return `${a1} × __ = ${a1*b2}`;
      case 'fractioncompare':
        return `1/${a1} ? 1/${b2}`;
      default:
        return '';
    }
  }

  // Prepopulate and set up UI for each type
  for(const t of types){
    const t1 = document.getElementById(`${t}_term1`);
    const t2 = document.getElementById(`${t}_term2`);
    const hint = document.getElementById(`${t}_hint`);
    const reset = document.getElementById(`${t}_reset`);
    const ex = document.getElementById(`${t}_example`);
    const update = () => {
      try{
        ex.textContent = 'e.g. ' + exampleFor(t, t1.value, t2.value);
      }catch{ ex.textContent = ''; }
    };
    t1.value = defaults[t].term1;
    t2.value = defaults[t].term2;
    t1.placeholder = defaults[t].term1;
    t2.placeholder = defaults[t].term2;
    hint.textContent = `(default: ${defaults[t].term1}, ${defaults[t].term2})`;
    t1.disabled = true;
    t2.disabled = true;
    reset.disabled = true;
    reset.addEventListener('click', () => {
      t1.value = defaults[t].term1;
      t2.value = defaults[t].term2;
      update();
    });
    t1.addEventListener('input', update);
    t2.addEventListener('input', update);
    update();
    // Enable/disable term fields based on checkbox
    const cb = document.querySelector(`input[name='ptype'][value='${t}']`);
    cb.addEventListener('change', () => {
      t1.disabled = t2.disabled = reset.disabled = !cb.checked;
      if(!cb.checked){
        t1.value = defaults[t].term1;
        t2.value = defaults[t].term2;
        update();
      }
    });
  }

  form.addEventListener('submit', async (ev) => {
    ev.preventDefault();
    const checked = Array.from(document.querySelectorAll('input[name="ptype"]:checked'));
    if(!checked.length){ alert('Choose at least one problem type'); return; }
    const problem_types = checked.map(cb => cb.value);
    const n = parseInt(document.getElementById('n').value, 10) || 0;
    if(n <= 0){ alert('N must be positive'); return; }
    const chunk = parseInt(document.getElementById('chunk').value, 10) || 0;
    if(chunk <= 0 || chunk > 50){ alert('Chunk must be 1-50'); return; }
    const defaultsPayload = {};
    for(const t of problem_types){
      const t1 = document.getElementById(`${t}_term1`).value.trim();
      const t2 = document.getElementById(`${t}_term2`).value.trim();
      if(t1 !== defaults[t].term1 || t2 !== defaults[t].term2){
        if(!(t1 && t2)){
          alert(`Fill BOTH term ranges for ${t} or reset both`);
          return;
        }
        defaultsPayload[t] = {term1:t1, term2:t2};
      }
    }
    const payload = {problem_types, n, chunk};
    if(Object.keys(defaultsPayload).length) payload.defaults = defaultsPayload;
    try{
      const res = await fetch('/generate', {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify(payload)
      });
      if(!res.ok){
        const msg = await res.text();
        alert(msg);
        return;
      }
      const {url} = await res.json();
      frame.src = url;
      frame.focus();
    }catch(err){
      alert('Network error: '+err);
    }
  });
})();
</script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

@app.get("/defaults")
async def get_defaults():
    """Return the default term1/term2 ranges for each problem type as a JSON object."""
    return {
        name: {
            "term1": f"{rng[0][0]}..{rng[0][1]}",
            "term2": f"{rng[1][0]}..{rng[1][1]}"
        }
        for name, cls in PROBLEM_CLASS_MAP.items()
        for rng in [worksheet_core.PROBLEM_DEFAULTS[cls]]
    }

# Expose generated PDFs via /pdf/* so direct links work too.
app.mount("/pdf", StaticFiles(directory=OUTPUT_DIR), name="pdf")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

