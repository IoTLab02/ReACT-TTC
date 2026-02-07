# ReACT-TTC: Capacity-Aware Top Trading Cycles for Post-Choice Reassignment in Shared CPS

 

## Folder Structure
--------------------------------------------
```
data/           # input datasets
results/        # experiment outputs (generated)
src/            # experiment code
test/           # test to run
tools/          # plotting scripts
README.md
requirements.txt
```


## Run test script and generate all results  
-------------------------------------------- 
Install all dependencies:  
```
pip install -r requirements.txt
``` 

Run test script:  
```
python test/test_main.py
```

All results will be generated in results folder.  



## Run Individually (Run from src folder)
--------------------------------------------  
To run experiments varying non-compliant EV agents:    
```
python run_varying_EV.py
```


To run experiments varying queue size of charging point resources:      

```
python run_varying_q.py
```


