#!/usr/bin/env python3

import uvicorn
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
import ipaddress

app = FastAPI()

# 设置正确的 API 密钥
API_KEY = "your-secret-api-key"


@app.middleware("http")
async def verify_client_ip(request, call_next):
    # 提取客户端 IP 地址
    client_ip = request.client.host
    try:
        ip = ipaddress.ip_address(client_ip)
        # 检查是否为局域网地址
        if not ip.is_private:
            raise HTTPException(status_code=403, detail="Forbidden: Only local network allowed")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid IP address")
    
    response = await call_next(request)
    return response


@app.get("/photo")
async def get_photo(x_api_key: str = Header(...)):
    # 验证 API 密钥
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    file_path = "./photo.jpg"
    try:
        return FileResponse(file_path, media_type="image/jpeg", filename="photo.jpg")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=1270)  # 替换为实际局域网 IP 地址
