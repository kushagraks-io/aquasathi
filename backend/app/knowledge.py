"""Small transparent keyword retrieval corpus for this MVP."""
SOURCES = [
 {"id":"mpeda-shaphari","title":"SHAPHARI Guidelines for Certification of Farms","publisher":"MPEDA / Aquaculture Authority","url":"https://mpeda.gov.in/wp-content/uploads/2021/02/Shaphari-C-of-F-guidelines.pdf","summary":"Lists water-quality factors for shrimp farming and example optimal ranges: temperature 28–33 °C, pH 7.5–8.5, DO 5–7 mg/L, salinity 15–25 ppt, ammonia-N below 0.01 ppm. Conditions and species matter.","keywords":"water quality dissolved oxygen temperature ph salinity ammonia tan"},
 {"id":"mpeda-bmp","title":"Better Management Practices (BMPs)","publisher":"MPEDA","url":"https://mpeda.gov.in/?page_id=728","summary":"Describes warning observations associated with shrimp health concerns, including lethargy, reduced appetite, discoloration, and shrimp congregating at pond sides or the surface; recommends attention to pond water quality and trained support.","keywords":"health lethargy appetite discoloration surface sides behavior disease warning"},
 {"id":"mpeda-farmers","title":"Shrimp farming guidance for farmers","publisher":"MPEDA Farmers","url":"https://mpeda.gov.in/farmers/?page_id=1693","summary":"Farmer-facing shrimp culture guidance, including maintaining water quality and seeking appropriate farm management support.","keywords":"shrimp farming pond farmer management water quality"},
 {"id":"icar-ciba","title":"ICAR-CIBA official resources","publisher":"ICAR-Central Institute of Brackishwater Aquaculture","url":"https://www.ciba.icar.gov.in/","summary":"The national research institute's official portal for brackishwater aquaculture research, advisories, and farmer resources. Consult current institute guidance and local experts for pond-specific decisions.","keywords":"icar ciba expert research advisory brackishwater aquaculture"}
]
def search(query: str, limit: int = 3):
 terms=set(query.lower().split()); ranked=[]
 for source in SOURCES:
  text=(source['title']+' '+source['summary']+' '+source['keywords']).lower()
  score=sum(1 for term in terms if len(term)>2 and term in text)
  if score: ranked.append((score,source))
 return [source for _,source in sorted(ranked,key=lambda pair:pair[0],reverse=True)[:limit]]
