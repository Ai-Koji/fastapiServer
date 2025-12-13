# fastapiServer

## guide to start:

### server install

fastapi:
```bash
# compile on win10-11
cd src/device
py compile.py

# here compiled files -> build/ 
```

```bash
apt install uvicron
cd src/server/apiServer/
python -m venv venv
source venv/bin/activate

pip install -r requirements.txt

# put compiled exes to uploads/

uvicorn main:app --reload --port 4545 --host "0.0.0.0"
```

door
```bash
cd src/server/door/
npm install
npm start
```

react-client
```bash
cd src/server/react-client
npm install
npm start
```