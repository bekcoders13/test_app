from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.for_admin import admin_router
from routes.login import login_router
from routes.test import tests_router
from routes.user import users_router

# Base.metadata.create_all(bind=engine)

app = FastAPI(
    contact={
        'name': "Asilbek Tojialiyev's telegram bot url for questions",
        'url': 'https://t.me/asilbekga_murojaat_bot',
    },
    docs_url='/',
    redoc_url='/redoc',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=["*"],
    allow_methods=["*"],
    allow_headers=["*"], )

app.include_router(login_router)
app.include_router(users_router)
app.include_router(tests_router)
app.include_router(admin_router)
