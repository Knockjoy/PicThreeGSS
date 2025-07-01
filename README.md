# Welcom to PicThreeGSS

GameSysServerの略です。

このGSSはDocker上で作成されており、配置位置は`/srv/PicThreeGSS/`となっています。
## 使用技術
Python
- FastAPI

# Usage
## move to picthree
```sh
$ cd /srv/PicThreeGSS
```
## boot the GSS API
move to src
```sh
$ cd /src/GameServer
```
boot the api server
```sh
$ uvicorn main:app --reload
```
