from sqlalchemy import create_engine, ForeignKey, DateTime, Integer, String, Column
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

engine = create_engine('sqlite:///game_data.db')
Base = declarative_base()

class Player(Base):
    __tablename__ = 'players'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    personal_best = Column(Integer, default=0)          #This should be automatically the highest score associated with this player

    scores = relationship('Score', backref='player', order_by='Score.score', cascade="save-update, merge, expunge, delete, delete-orphan, refresh-expire")

    def __repr__(self):
        return "<Player: (id={}, name={}, personal_best={})>".format(self.id, self.name, ('0' if not self.scores else self.scores[0]))

    def get_personal_best(self):
        return (0 if not self.scores else self.scores[0].score)
        #return self.personal_best

class Score(Base):
    __tablename__ = 'scores'
    id = Column(Integer, primary_key=True)
    score = Column(Integer(), nullable=False)
    date = Column(DateTime(), default=datetime.now)
    player_id = Column(Integer, ForeignKey('players.id'))

    #player = relationship('Player', backref=backref('scores', order_by=score))
    #player = relationship('Player', back_populates='scores')

    def __repr__(self):
        return "<Score: (id={}, player:{}, played on: {})>".format(self.id, self.player, self.date)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
