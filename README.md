# Civil Engineering Estimation App

Excel-workflow based estimation system with BOQ, Abstract, Material Statement, carriage cost, CP deduction and GST addition.

## Run Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

## Run Frontend
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:5173

## Features
- Upload Excel template and preview sheets.
- Multi-item table entry.
- Feet to meter conversion: 1 ft = 0.3048 m.
- Quantity units: cum, sqm, rmt.
- Amount = quantity × rate.
- Material breakup for PCC/RCC/brick masonry/plaster.
- Carriage by percentage or distance basis.
- CP 9.09% deduction and GST 5.36% addition.
- BOQ, Material Statement and Abstract Excel export.
- PFM/PDF export.
- Save and load project by ID.

## Notes
Uploaded template reading is included. Exact cell-by-cell template replication needs mapping rules for your specific Excel format. The export currently preserves an Excel-like structured format with BOQ, Material Statement, and Abstract sheets.
