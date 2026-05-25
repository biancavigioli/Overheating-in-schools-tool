# Overheating-in-schools-tool

### ENG version ###
# Inputs and outputs
This tool allows to evaluate the overheating condition of a school building or of a single classroom, based on these inputs: 
- Location (climate zone: A, B, C, D, E, F)
- Retrofit condition of the building (no retrofit, insulated wall, insulated roof, double window)
- Ventilation rate (high or low)
- Window to floor rate
- Solar heat gain coefficient of the glazings
- Floor and position on the floor (of each classroom)
- Orientation of the window

The results are presented in terms of: 
- Share of hours in the different adaptive comfort bands
- Distribution of temperatures above the thresholds
- Compliance with the TM52 regulations
- Number of heat stress days

# Folder content
The folder contains: 
- 4 python files
   - APP            = the classroom tool (english version)
   - APP-SCHOOL     = the school tool (english version)
   - APP-ITA        = the classroom tool (italian version)
   - APP-SCHOOL-ITA = the school tool (italian version)
- 5 folders that contain the results of the performed simulations
    - base
    - night         = night ventilation
    - sh00          = shadings at 0°
    - sh45          = shadings at 45°
    - FWG           = future weather and UHI results

# How to use
To be able to use the tool, it is necessary to:
1. Download and install Python from python.org/downloads [During installation, check "Add Python to PATH"]
2. Open the "command prompt" from your computer and run
   "pip install streamlit numpy pandas matplotlib seaborn"

To use the tool: 
1. Download the full folder
2. Copy the file directory ("copy as path") of the desired tool (Classroom / School; ENG / ITA)
3. Open the "command prompt" and paste the following line:
   "python -m streamlit run "file directory""
4. A web page will open
