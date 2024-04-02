import os
import dotenv

import uvicorn
from fastapi import APIRouter, FastAPI

dotenv.load_dotenv()

router = APIRouter()

@router.get("/printer/status/time")
async def printer_get_time() -> dict:
    print("Received Request")
    return {"time": 10}


@router.get("/printer/status/percentage")
async def printer_get_percentage():
    return {"percentage": 90}


@router.get("/printer/status/state")
async def printer_get_state():
    return {"state": "IDLE"}


@router.get("/printer/status/print_speed")
async def get_print_speed():
    return {"print_speed": 1000}


@router.get("/printer/status/file_name")
async def get_file_name():
    return {"file_name": "test.gcode"}

@router.get("/printer/camera")
async def printer_get_camera():
    try:
        last_frame = bytes()
    except Exception as e:
        print(str(e))
        return {"error": str(e)}
    return {"frame": frame} if (frame := last_frame
                                ) is not None else {}

app = FastAPI()
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("debug_printers:app", host="localhost", port=6000, reload=True)