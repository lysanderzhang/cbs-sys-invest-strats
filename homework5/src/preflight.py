"""Submission checks: source evidence, fresh numbers, PDF structure and TeX diagnostics."""
import hashlib,json,re
from pypdf import PdfReader
from .config import ROOT
from .data import load

def main():
    load()
    verification=json.loads((ROOT/"results/verification/independent.json").read_text())
    for p,digest in verification["output_sha256"].items():
        assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==digest,f"Stale verification: {p}"
    source=(ROOT/"report/main.tex").read_text()
    evidence=json.loads((ROOT/"results/verification/report_evidence.json").read_text())
    assert hashlib.sha256(source.encode()).hexdigest()==evidence["main_tex_sha256"]
    for meta in evidence["narrative"].values():assert f"{meta['value']:.5f}" in source
    pdf=ROOT/"report/main.pdf"
    assert pdf.stat().st_mtime >= (ROOT/"report/main.tex").stat().st_mtime
    pages=PdfReader(pdf).pages
    assert len(pages)==12
    first=pages[0].extract_text()
    for part in ["(a)","(b)","(c)","(d)"]: assert part in first
    text="\n".join(p.extract_text() for p in pages)
    assert not re.search(r"validation|checked|no errors|placeholder|coding agent|AI workflow",text,re.I)
    assert source.count("includegraphics")==5
    for figure in ["composite","modules","allocations","distributions","buffer"]:assert figure+".pdf" in source
    log=(ROOT/"report/main.log").read_text()
    for forbidden in ["Overfull","Underfull","undefined references"]:assert forbidden not in log
    assert "Section 8." not in source
    assert re.search(r"\b20 passed\b",(ROOT/"results/verification/pytest.txt").read_text())
    out={"pages":12,"figures":5,"tests_passed":20,"independent_comparisons":verification["scalar_comparisons"],"maximum_return_difference":verification["maximum_return_difference"],"narrative_quantities_bound":len(evidence["narrative"]),"numerical_output_files":len(verification["output_sha256"]),"pdf_sha256":hashlib.sha256(pdf.read_bytes()).hexdigest(),"limitations":["ETF history prevents a full 2000-2009 comparison","SHV is a low-duration Treasury proxy, not a zero-risk account","One adjusted-price vendor; historical revisions possible","Frictionless month-end boundary; extra-month lag is not measured next-open slippage","Extension and switching buffer are historical analyses, not prospective records","Costs are scenarios; no taxes, capacity or measured spreads"]}
    (ROOT/"results/verification/preflight.json").write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out,indent=2))
if __name__=="__main__":main()
