from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
class Base(DeclarativeBase): pass
class Pond(Base):
 __tablename__='ponds'
 id:Mapped[int]=mapped_column(Integer,primary_key=True)
 name:Mapped[str]=mapped_column(String(100)); location:Mapped[str]=mapped_column(String(160),default='')
 area_ha:Mapped[float]=mapped_column(Float,default=1.0); species:Mapped[str]=mapped_column(String(80),default='L. vannamei')
 stocking_date:Mapped[str]=mapped_column(String(10),default=''); stage:Mapped[str]=mapped_column(String(40),default='Grow-out')
 readings:Mapped[list['Reading']]=relationship(back_populates='pond',cascade='all, delete-orphan')
class Reading(Base):
 __tablename__='readings'
 id:Mapped[int]=mapped_column(Integer,primary_key=True); pond_id:Mapped[int]=mapped_column(ForeignKey('ponds.id'))
 recorded_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow); do_mg_l:Mapped[float]=mapped_column(Float)
 temperature_c:Mapped[float]=mapped_column(Float); ph:Mapped[float]=mapped_column(Float); salinity_ppt:Mapped[float]=mapped_column(Float); tan_mg_l:Mapped[float]=mapped_column(Float)
 simulated:Mapped[bool]=mapped_column(Boolean,default=True); pond:Mapped[Pond]=relationship(back_populates='readings')
class Incident(Base):
 __tablename__='incidents'
 id:Mapped[int]=mapped_column(Integer,primary_key=True); pond_id:Mapped[int]=mapped_column(ForeignKey('ponds.id'))
 created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow); description:Mapped[str]=mapped_column(Text)
 language:Mapped[str]=mapped_column(String(20),default='English'); image_name:Mapped[str|None]=mapped_column(String(255),nullable=True)
 status:Mapped[str]=mapped_column(String(40),default='Open'); risk:Mapped[str]=mapped_column(String(40),default='Needs review'); report:Mapped[str]=mapped_column(Text,default='')
 pond:Mapped[Pond]=relationship()
