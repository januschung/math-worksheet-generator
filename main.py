from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from uuid import uuid4
import run  # reuse CLI module as a library

app = FastAPI(title="Math Worksheet Web API")

# ---------------------------------------------------------------------------
# Configuration & helpers
# ---------------------------------------------------------------------------
OUTPUT_DIR = Path(__file__).parent / "generated"
OUTPUT_DIR.mkdir(exist_ok=True)

PROBLEM_CLASS_MAP = {
    "multiplication": run.MultiplicationProblem,
    "addition": run.AdditionProblem,
    "subtraction": run.SubtractionProblem,
    "division": run.DivisionProblem,
    "missingfactor": run.MissingFactorProblem,
    "fractioncompare": run.FractionComparisonProblem,
}


def parse_range(txt: str):
    """Parse "min..max" → (min, max)."""
    try:
        lo, hi = map(int, txt.split(".."))
        if lo > hi:
            raise ValueError
        return lo, hi
    except ValueError:
        raise HTTPException(status_code=400, detail="Ranges must be in 'min..max' format with min ≤ max")


def clean_old_files(limit: int = 50):
    """Prevent unbounded storage growth (delete oldest PDFs)."""
    pdfs = sorted(OUTPUT_DIR.glob("*.pdf"), key=lambda p: p.stat().st_mtime)
    for p in pdfs[:-limit]:
        p.unlink(missing_ok=True)

# ---------------------------------------------------------------------------
# API routes
# ---------------------------------------------------------------------------

@app.post("/generate")
async def generate_worksheet(payload: dict):
    """Create a worksheet PDF and return its URL.

    Expected body:
    {
      "problem_types": ["multiplication", ...],
      "n": 100,
      "term1": "2..12",          # optional, single‑type only
      "term2": "2..12",          # optional, single‑type only
      "defaults": {               # optional per‑type overrides
        "multiplication": {"term1": "3..12", "term2": "2..15"}
      }
    }
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
        n = int(payload.get("n", run.DEFAULT_N))
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="'n' must be an integer")
    if n <= 0:
        raise HTTPException(status_code=400, detail="'n' must be positive")

    # ---------- Per‑request default overrides ----------
    overrides_raw = payload.get("defaults", {})
    overrides = {}
    for name, rng in overrides_raw.items():
        cls = PROBLEM_CLASS_MAP.get(name.lower())
        if not cls:
            raise HTTPException(status_code=400, detail=f"Unknown problem type in defaults: {name}")
        try:
            t1 = parse_range(rng["term1"])
            t2 = parse_range(rng["term2"])
        except KeyError:
            raise HTTPException(status_code=400, detail=f"Both term1 and term2 must be provided for {name}")
        overrides[cls] = (t1, t2)

    original_defaults = {}
    try:
        # Apply overrides
        for cls, rng in overrides.items():
            original_defaults[cls] = run.PROBLEM_DEFAULTS[cls]
            run.PROBLEM_DEFAULTS[cls] = rng

        # ---------- PDF generation ----------
        file_id = uuid4().hex
        out_path = OUTPUT_DIR / f"worksheet_{file_id}.pdf"

        if len(classes) == 1:
            # Single‑type worksheet (still supports term1/term2)
            cls = classes[0]
            term1_txt = payload.get("term1")
            term2_txt = payload.get("term2")
            if (term1_txt is None) ^ (term2_txt is None):
                raise HTTPException(status_code=400, detail="Provide BOTH term1 and term2 or neither")
            if term1_txt:
                term1_range = parse_range(term1_txt)
                term2_range = parse_range(term2_txt)
            else:
                term1_range, term2_range = run.PROBLEM_DEFAULTS[cls]
            gen = run.WorksheetGenerator(cls, n, term1_range, term2_range, str(out_path))
            gen.generate_problems()
            gen.create_pdf()
        else:
            if payload.get("term1") or payload.get("term2"):
                raise HTTPException(status_code=400, detail="term1/term2 not allowed with multiple types")

            problems_by_type = []
            for cls in classes:
                t1, t2 = run.PROBLEM_DEFAULTS[cls]
                plist, recent = [], []
                for _ in range(n):
                    for _ in range(50):
                        a = run.random.randint(*t1)
                        b = run.random.randint(*t2)
                        if (a, b) not in recent:
                            plist.append(cls(a, b))
                            recent.append((a, b))
                            if len(recent) > 10:
                                recent.pop(0)
                            break
                    else:
                        plist.append(cls(run.random.randint(*t1), run.random.randint(*t2)))
                problems_by_type.append((cls, plist))
            gen = run.MixedWorksheetGenerator(problems_by_type, str(out_path))
            gen.create_pdf()

        clean_old_files()
        return {"url": f"/pdf/{out_path.name}"}
    finally:
        # Restore globals so overrides don't leak between requests
        for cls, rng in original_defaults.items():
            run.PROBLEM_DEFAULTS[cls] = rng


@app.get("/pdf/{filename}")
async def serve_pdf(filename: str):
    path = OUTPUT_DIR / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    # Inline display so <iframe> can render it instead of forcing download
    headers = {"Content-Disposition": f"inline; filename=\"{filename}\""}
    return FileResponse(path, media_type="application/pdf", headers=headers)


@app.get("/", response_class=HTMLResponse)
async def index():
    """Simple vanilla‑JS page to create worksheets and preview PDFs inline."""
    html = """
    <!doctype html>
    <html lang='en'>
    <head>
      <meta charset='utf-8'>
      <meta name='viewport' content='width=device-width, initial-scale=1'>
      <title>Math Worksheet Generator</title>
      <style>
        body{font-family:sans-serif;max-width:800px;margin:2rem auto;padding:0 1rem;line-height:1.4}
        fieldset{border:1px solid #ccc;margin-bottom:1rem}
        .row{display:flex;flex-wrap:wrap;align-items:center;margin:0.25rem 0}
        .row label{min-width:160px}
        .row input[type=text]{width:90px;margin-left:0.25rem}
        input[type=number]{width:80px}
        iframe{border:1px solid #ccc;margin-top:1rem}
      </style>
    </head>
    <body>
      <h1>Math Worksheet Generator</h1>

      <form id='cfg'>
        <fieldset>
          <legend>Problem Types &amp; Optional Term Ranges</legend>

          <div class='row' data-type='multiplication'>
            <label><input type='checkbox' name='ptype' value='multiplication'>Multiplication</label>
            term1 <input type='text' id='multiplication_term1' placeholder='min..max'>
            term2 <input type='text' id='multiplication_term2' placeholder='min..max'>
          </div>
          <div class='row' data-type='addition'>
            <label><input type='checkbox' name='ptype' value='addition'>Addition</label>
            term1 <input type='text' id='addition_term1' placeholder='min..max'>
            term2 <input type='text' id='addition_term2' placeholder='min..max'>
          </div>
          <div class='row' data-type='subtraction'>
            <label><input type='checkbox' name='ptype' value='subtraction'>Subtraction</label>
            term1 <input type='text' id='subtraction_term1' placeholder='min..max'>
            term2 <input type='text' id='subtraction_term2' placeholder='min..max'>
          </div>
          <div class='row' data-type='division'>
            <label><input type='checkbox' name='ptype' value='division'>Division</label>
            term1 <input type='text' id='division_term1' placeholder='min..max'>
            term2 <input type='text' id='division_term2' placeholder='min..max'>
          </div>
          <div class='row' data-type='missingfactor'>
            <label><input type='checkbox' name='ptype' value='missingfactor'>Missing&nbsp;Factor</label>
            term1 <input type='text' id='missingfactor_term1' placeholder='min..max'>
            term2 <input type='text' id='missingfactor_term2' placeholder='min..max'>
          </div>
          <div class='row' data-type='fractioncompare'>
            <label><input type='checkbox' name='ptype' value='fractioncompare'>Fraction&nbsp;Compare</label>
            term1 <input type='text' id='fractioncompare_term1' placeholder='min..max'>
            term2 <input type='text' id='fractioncompare_term2' placeholder='min..max'>
          </div>
        </fieldset>

        <label>Problems per type: <input type='number' name='n' id='n' value='100' min='1'></label>
        <button type='submit' style='margin-left:0.5rem'>Generate</button>
      </form>

      <h2>Preview</h2>
      <iframe id='preview' style='width:100%;height:80vh'></iframe>

<script>
(function(){
  const form = document.getElementById('cfg');
  const frame = document.getElementById('preview');

  form.addEventListener('submit', async (ev) => {
    ev.preventDefault();

    const checked = Array.from(document.querySelectorAll('input[name="ptype"]:checked'));
    if(!checked.length){ alert('Choose at least one problem type'); return; }

    const problem_types = checked.map(cb => cb.value);
    const n = parseInt(document.getElementById('n').value, 10) || 0;
    if(n <= 0){ alert('N must be positive'); return; }

    const defaults = {};
    for(const t of problem_types){
      const t1 = document.getElementById(`${t}_term1`).value.trim();
      const t2 = document.getElementById(`${t}_term2`).value.trim();
      if(t1 || t2){
        if(!(t1 && t2)){
          alert(`Fill BOTH term ranges for ${t} or clear both`);
          return;
        }
        defaults[t] = {term1:t1, term2:t2};
      }
    }

    const payload = {problem_types, n};
    if(Object.keys(defaults).length) payload.defaults = defaults;

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
    return html

# Expose generated PDFs via /pdf/* so direct links work too.
app.mount("/pdf", StaticFiles(directory=OUTPUT_DIR), name="pdf")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


