"""Render every PDF page and prepare visual review sheets; no performance generation."""
from pathlib import Path
import json
import pymupdf
from PIL import Image,ImageOps,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'build/qa';out.mkdir(parents=True,exist_ok=True)
qa=[]
for label,name in [('report','HW2_Momentum_Research_Report.pdf'),('slides','HW2_Investor_Presentation.pdf')]:
    doc=pymupdf.open(ROOT/'deliverables'/name);renders=[]
    for i,page in enumerate(doc,1):
        pix=page.get_pixmap(matrix=pymupdf.Matrix(1.5,1.5),alpha=False)
        p=out/f'{label}_{i:02d}.png';pix.save(p);renders.append(p)
        clipped=[]
        for b in page.get_text('dict')['blocks']:
            for line in b.get('lines',[]):
                for span in line.get('spans',[]):
                    r=pymupdf.Rect(span['bbox'])
                    if r.x0<0 or r.y0<0 or r.x1>page.rect.width+.5 or r.y1>page.rect.height+.5:clipped.append(span['text'])
        qa.append({'artifact':name,'page':i,'render':'build/qa/'+p.name,'text_outside_page':clipped,'text_characters':len(page.get_text()),'status':'rendered; visual review pending'})
    batch=4
    for base in range(0,len(renders),batch):
        w,h=(1100,650) if label=='slides' else (850,1120)
        canvas=Image.new('RGB',(2*w,2*h),'#e8ebee');draw=ImageDraw.Draw(canvas)
        for j,p in enumerate(renders[base:base+batch]):
            im=Image.open(p);im.thumbnail((w-24,h-40))
            x=(j%2)*w+(w-im.width)//2;y=(j//2)*h+28
            canvas.paste(im,(x,y));draw.text(((j%2)*w+15,(j//2)*h+6),p.name,fill='black')
        canvas.save(out/f'{label}_sheet_{base//batch+1}.jpg',quality=92)
(ROOT/'outputs/audits/artifact_qa.json').write_text(json.dumps(qa,indent=2))
print('Rendered',len(qa),'pages; text outside page',sum(bool(x['text_outside_page']) for x in qa))
