from html import escape

GEOMETRY = (
 (1,"300,0 450,150 300,300 150,150",300,55,300,175),(2,"0,0 300,0 150,150",150,28,150,88),(3,"0,0 150,150 0,300",28,150,88,150),
 (4,"0,300 150,150 300,300 150,450",70,300,170,300),(5,"0,300 150,450 0,600",28,450,88,450),(6,"0,600 300,600 150,450",150,570,150,512),
 (7,"300,300 450,450 300,600 150,450",300,542,300,425),(8,"300,600 600,600 450,450",450,570,450,512),(9,"600,600 600,300 450,450",572,450,512,450),
 (10,"300,300 450,150 600,300 450,450",528,300,430,300),(11,"600,300 600,0 450,150",572,150,512,150),(12,"300,0 600,0 450,150",450,28,450,88),
)
ABBR={"sun":"Su","moon":"Mo","mars":"Ma","mercury":"Me","jupiter":"Ju","venus":"Ve","saturn":"Sa","rahu":"Ra","ketu":"Ke"}

def kundli_svg(chart: dict, title: str) -> str:
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600" role="img"><title>{escape(title)}</title>',
           '<rect width="600" height="600" fill="#fffdf7"/>']
    planets={h["house_number"]:[p for p in chart["planets"] if p["house"]==h["house_number"]] for h in chart["houses"]}
    for number,polygon,lx,ly,px,py in GEOMETRY:
        house=chart["houses"][number-1]
        parts.append(f'<polygon points="{polygon}" fill="none" stroke="#7d2d2d" stroke-width="2"/>')
        parts.append(f'<text x="{lx}" y="{ly}" text-anchor="middle" font-size="18" fill="#6b625b">{house["rashi_number"]}</text>')
        labels=[]
        if number==1: labels.append("Lagna")
        for planet in planets[number]: labels.append(ABBR[planet["identifier"]]+(" (R)" if planet.get("retrograde") else ""))
        for index,label in enumerate(labels):
            y=py+(index-(len(labels)-1)/2)*24
            parts.append(f'<text x="{px}" y="{y:.1f}" text-anchor="middle" font-size="18" font-weight="600" fill="#29231f">{escape(label)}</text>')
    parts.append('</svg>')
    return ''.join(parts)
