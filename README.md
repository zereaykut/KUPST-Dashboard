# KUPST Dashboard
This dashboard calculates KUPST with imbalance cost for selected powerplant via use of EPIAS Transparency data

## Run Dashboard
Clone the repo
```console
foo@bar:~$ git clone https://github.com/zereaykut/KUPST_dashboard
foo@bar:~$ cd KUPST_dashboard
```

Create python environment
```console
foo@bar:~$ python -m venv env
```

Activate environment in Mac/Linux 
```console
foo@bar:~$ source env/bin/activate
```

Activate environment in Windows 
```console
foo@bar:~$ env\Scripts\activate
```

Install required packages
```console
foo@bar:~$ pip install -r requirements.txt
```

Run dashboard
```console
foo@bar:~$ streamlit run app.py
```

## Example Usage
https://github.com/zereaykut/KUPST_dashboard/assets/102432357/fd9de931-bc7f-4e3b-8399-a29ca3c3c429

## Note
KUDÜP and Real Time Generation data selection sections operate separately. It is not checked in the background whether the switchboards of these two data are matched. For this reason, the user is responsible for ensuring that the parameters selected for KUDÜP and Real Time Production Data match.

## Used Data
MCP: Market Clearing Price [TL/MWh]\n
SMP: System Marginal Price [TL/MWh]\n
Real Time Generation (GRT): Hourly generation of selected powerplant [MWh]\n
KUDÜP: Hourly Finalized Settlement Period Production Plan of selected powerplant [MWh]\n

## Calculation

### Imbalance Cost
![KUPST_Imbalance_Cost](https://github.com/zereaykut/KUPST_dashboard/assets/102432357/3b6b80d6-3328-43bb-9166-9be3913c56b9)

### KUPST
![KUPST_Kupst](https://github.com/zereaykut/KUPST_dashboard/assets/102432357/f73b6d8a-1001-4dfd-9068-5b020356a82e)

## Unit Cost
![KUPST_Unit_Cost](https://github.com/zereaykut/KUPST_dashboard/assets/102432357/502f6808-ccbb-47ff-89a5-090cc55fffc9)

## Source 
[EPIAS Transparency](https://seffaflik.epias.com.tr/home)
