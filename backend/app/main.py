import os
from datetime import datetime, timedelta
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session
from .models import Base, Pond, Reading, Incident
from .knowledge import search

DATABASE_URL=os.getenv('DATABASE_URL','sqlite:///./aquasathi.db')
engine=create_engine(DATABASE_URL,connect_args={'check_same_thread':False} if DATABASE_URL.startswith('sqlite') else {})
SessionLocal=sessionmaker(bind=engine,autoflush=False)
Base.metadata.create_all(engine)
app=FastAPI(title='AquaSathi API',version='0.1.0')
def db_session():
 db=SessionLocal()
 try: yield db
 finally: db.close()
def seed():
 with SessionLocal() as db:
  if db.scalar(select(Pond.id).limit(1)): return
  ponds=[Pond(name='Blue Lagoon',location='Bhimavaram, Andhra Pradesh',area_ha=1.8,species='L. vannamei',stocking_date='2026-09-14',stage='Grow-out'),Pond(name='East Creek',location='Bhimavaram, Andhra Pradesh',area_ha=1.2,species='L. vannamei',stocking_date='2026-10-01',stage='Nursery'),Pond(name='Palm Pond',location='Bhimavaram, Andhra Pradesh',area_ha=2.1,species='P. monodon',stocking_date='2026-08-30',stage='Grow-out')]
  db.add_all(ponds); db.flush(); now=datetime.utcnow()
  for index,pond in enumerate(ponds):
   for day in range(7): db.add(Reading(pond_id=pond.id,recorded_at=now-timedelta(days=6-day),do_mg_l=5.8-index*.2-day*.04,temperature_c=29.1+day*.12,ph=7.9+day*.03,salinity_ppt=18+index*2,tan_mg_l=.015 if index==2 else .004+day*.0005,simulated=True))
  db.add(Incident(pond_id=ponds[0].id,description='Feeding response looked slower this morning',language='English',status='Under review',risk='Monitor',report='Demo incident; review current pond conditions with a qualified expert.')); db.commit()
seed()
class PondIn(BaseModel):
 name:str=Field(min_length=1,max_length=100); location:str=Field(default='',max_length=160); area_ha:float=Field(gt=0,le=10000)
 species:str=Field(default='L. vannamei',max_length=80); stocking_date:str=''; stage:str='Grow-out'
class IncidentIn(BaseModel):
 pond_id:int; description:str=Field(min_length=5,max_length=3000); language:str='English'; image_name:str|None=None

def rjson(r): return {'id':r.id,'recorded_at':r.recorded_at.isoformat(),'do_mg_l':r.do_mg_l,'temperature_c':r.temperature_c,'ph':r.ph,'salinity_ppt':r.salinity_ppt,'tan_mg_l':r.tan_mg_l,'simulated':r.simulated}
def pjson(p,db):
 r=db.scalar(select(Reading).where(Reading.pond_id==p.id).order_by(Reading.recorded_at.desc()))
 flags=[]
 if r:
  if r.do_mg_l<5: flags.append('Dissolved oxygen below 5 mg/L screening guide')
  if not 28<=r.temperature_c<=33: flags.append('Temperature outside 28–33 °C example range')
  if not 7.5<=r.ph<=8.5: flags.append('pH outside 7.5–8.5 example range')
  if r.tan_mg_l>=.01: flags.append('Ammonia-N at or above 0.01 mg/L example guide')
 return {'id':p.id,'name':p.name,'location':p.location,'area_ha':p.area_ha,'species':p.species,'stocking_date':p.stocking_date,'stage':p.stage,'health':'Review' if flags else 'Stable','flags':flags,'latest':rjson(r) if r else None}
@app.get('/api/health')
def health(): return {'status':'ok','mode':'demo'}
@app.get('/api/dashboard')
def dashboard(db:Session=Depends(db_session)):
 ponds=db.scalars(select(Pond).order_by(Pond.id)).all(); incidents=db.scalars(select(Incident).order_by(Incident.created_at.desc()).limit(5)).all()
 return {'ponds':[pjson(p,db) for p in ponds],'incidents':[{'id':i.id,'pond_id':i.pond_id,'pond_name':i.pond.name,'description':i.description,'created_at':i.created_at.isoformat(),'status':i.status,'risk':i.risk} for i in incidents],'data_label':'DEMO — SIMULATED READINGS'}
@app.get('/api/ponds')
def ponds(db:Session=Depends(db_session)): return [pjson(p,db) for p in db.scalars(select(Pond).order_by(Pond.id)).all()]
@app.post('/api/ponds',status_code=201)
def create_pond(data:PondIn,db:Session=Depends(db_session)):
 p=Pond(**data.model_dump()); db.add(p); db.commit(); db.refresh(p); return pjson(p,db)
@app.get('/api/ponds/{pond_id}/readings')
def readings(pond_id:int,db:Session=Depends(db_session)):
 if not db.get(Pond,pond_id): raise HTTPException(404,'Pond not found')
 return [rjson(r) for r in db.scalars(select(Reading).where(Reading.pond_id==pond_id).order_by(Reading.recorded_at)).all()]
@app.get('/api/incidents')
def incidents(db:Session=Depends(db_session)):
 return [{'id':i.id,'pond_id':i.pond_id,'pond_name':i.pond.name,'description':i.description,'created_at':i.created_at.isoformat(),'status':i.status,'risk':i.risk,'report':i.report} for i in db.scalars(select(Incident).order_by(Incident.created_at.desc())).all()]
@app.post('/api/incidents',status_code=201)
def create_incident(data:IncidentIn,db:Session=Depends(db_session)):
 if not db.get(Pond,data.pond_id): raise HTTPException(404,'Pond not found')
 i=Incident(**data.model_dump()); db.add(i); db.commit(); db.refresh(i); return {'id':i.id,'status':i.status,'created_at':i.created_at.isoformat()}
@app.get('/api/knowledge/search')
def knowledge(q:str='shrimp pond water quality'):
 return [{k:v for k,v in d.items() if k!='keywords'} for d in search(q)]
@app.post('/api/investigate')
def investigate(data:IncidentIn,db:Session=Depends(db_session)):
 pond=db.get(Pond,data.pond_id)
 if not pond: raise HTTPException(404,'Pond not found')
 r=db.scalar(select(Reading).where(Reading.pond_id==pond.id).order_by(Reading.recorded_at.desc()))
 if not r: raise HTTPException(422,'No readings available for this pond')
 flags=[]
 if r.do_mg_l<5: flags.append(f'DO {r.do_mg_l:.1f} mg/L is below the 5 mg/L example screening guide')
 if not 28<=r.temperature_c<=33: flags.append(f'Temperature {r.temperature_c:.1f} °C is outside the example range')
 if not 7.5<=r.ph<=8.5: flags.append(f'pH {r.ph:.2f} is outside the example range')
 if r.tan_mg_l>=.01: flags.append(f'Ammonia-N {r.tan_mg_l:.3f} mg/L is at/above the example guide')
 visual='Image attached for qualified review; automated image interpretation is not connected.' if data.image_name else 'No image attached.'
 docs=search(data.description+' water quality shrimp health')
 words=['surface','letharg','not eating','eating less','eat less','fed less','feeding','red','dead','mortality','slow']
 risk='Expert review recommended' if flags or any(w in data.description.lower() for w in words) else 'Monitor and record'
 report=(f'Initial screening for {pond.name}. Reported observation: {data.description}\n\nReading source: simulated demonstration data; not a live sensor measurement.\nLatest sample: DO {r.do_mg_l:.1f} mg/L · {r.temperature_c:.1f} °C · pH {r.ph:.2f} · salinity {r.salinity_ppt:.1f} ppt · TAN {r.tan_mg_l:.3f} mg/L.\n'+('Screening flags: '+'; '.join(flags)+'.\n' if flags else 'No screening thresholds flagged in the latest sample. This does not establish that the pond is problem-free.\n')+visual+'\n\nThis is a preliminary evidence summary, not a disease diagnosis or treatment instruction. Recheck readings using a reliable test method, note sampling time and recent changes, and contact a qualified aquaculture professional for serious or worsening signs. Do not apply chemicals based on this report.')
 inc=Incident(**data.model_dump(),status='Expert review recommended' if risk.startswith('Expert') else 'Open',risk=risk,report=report); db.add(inc); db.commit(); db.refresh(inc)
 return {'incident_id':inc.id,'risk':risk,'status':inc.status,'report':report,'flags':flags,'sources':[{k:v for k,v in d.items() if k!='keywords'} for d in docs]}
ROOT=Path(__file__).resolve().parents[2]
DIST=ROOT/'frontend'/'dist'
@app.get('/assets/{asset_path:path}')
def static_asset(asset_path:str):
    asset=(DIST/'assets'/asset_path).resolve()
    if not asset.is_relative_to((DIST/'assets').resolve()) or not asset.is_file(): raise HTTPException(404,'Asset not found')
    return FileResponse(asset)
@app.get('/')
def index(): return FileResponse((DIST/'index.html') if (DIST/'index.html').exists() else ROOT/'frontend'/'index.html')
