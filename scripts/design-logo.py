"""Original canvas-design identity: supersampled transparent PNGs and a brand board."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'apps/web-preview/public/brand'
OUT.mkdir(parents=True,exist_ok=True)
INK='#204d3d'
SAGE='#85987c'
FONTS=Path('C:/Users/izayo/.codex/skills/canvas-design/canvas-fonts')

def mark(size=512, color=INK):
    scale=4
    im=Image.new('RGBA',(512*scale,512*scale))
    d=ImageDraw.Draw(im)
    # An open courtyard: architectural C, with a detached coordinate/block.
    d.rounded_rectangle((72*scale,72*scale,440*scale,440*scale),radius=94*scale,fill=color)
    d.rounded_rectangle((139*scale,139*scale,373*scale,373*scale),radius=35*scale,fill=(0,0,0,0))
    d.rectangle((334*scale,70*scale,450*scale,281*scale),fill=(0,0,0,0))
    d.rounded_rectangle((373*scale,72*scale,440*scale,139*scale),radius=10*scale,fill=SAGE)
    return im.resize((size,size),Image.Resampling.LANCZOS)

mark().save(OUT/'opencampus-mark.png')
mark(64).save(OUT/'favicon.png')
font=ImageFont.truetype(str(FONTS/'BricolageGrotesque-Bold.ttf'),172)
lockup=Image.new('RGBA',(1700,360));lockup.alpha_composite(mark(320),(0,20))
d=ImageDraw.Draw(lockup);d.text((355,82),'OpenCampus',font=font,fill=INK,stroke_width=0)
lockup.save(OUT/'opencampus-logo.png')
board=Image.new('RGB',(2200,1500),'#f3f2ea');d=ImageDraw.Draw(board)
mono=ImageFont.truetype(str(FONTS/'DMMono-Regular.ttf'),19)
d.text((120,100),'OPENCAMPUS / VISUAL IDENTITY 01',font=mono,fill=INK)
board.paste(lockup.resize((1530,324),Image.Resampling.LANCZOS),(320,470),lockup.resize((1530,324),Image.Resampling.LANCZOS))
d.line((120,1265,2080,1265),fill='#c5cbc1',width=2)
d.text((120,1310),'OPEN COURTYARD',font=mono,fill=INK)
d.text((1460,1310),'FOREST INK / MINERAL GREY',font=mono,fill=INK)
design=ROOT/'design';design.mkdir(exist_ok=True)
board.save(design/'opencampus-identity.png')
import pymupdf
pdf=pymupdf.open()
page=pdf.new_page(width=1100,height=750)
page.insert_image(page.rect,stream=(design/'opencampus-identity.png').read_bytes())
pdf.save(design/'opencampus-identity.pdf',deflate=True,garbage=4)
print('Created mark, lockup, favicon, PNG identity board and PDF.')
