from sqlalchemy import create_engine

class Config:
    SECRET_KEY = 'your-secret-key'
    #Line below was changed for my windows setup -Noah
    SQLALCHEMY_DATABASE_URI = "postgresql+pg8000://noah_meduvsky:colortasker@localhost:5432/color_tasker" 
    #SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://lightbringer:colortasker@localhost:5432/color_tasker"
    SQLALCHEMY_TRACK_MODIFICATIONS = False



#TODO: Use this if you want to test local database connection
#SECRET_KEY = 'your-secret-key'
#SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://lightbringer:colortasker@localhost:5432/color_tasker"
#SQLALCHEMY_TRACK_MODIFICATIONS = False
#engine = create_engine(SQLALCHEMY_DATABASE_URI)
#with engine.connect() as connection:
#    print("Connection successful")