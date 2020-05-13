#This document represents functions which will be utilized within the
#HYSPLIT modeling worklflow.

#Greg Lee
#05.13.20
import pandas as pd
import datetime
import os

def HYSPLIT_configure(start_model,
                      num_loc,
                      start_locs,
                      tot_runtime,
                      mod_top,
                      input_data_grids,
                      grid_1_dir,
                      grid_1_name,
                      grid_2_dir,
                      grid_2_name,
                      chem_ident,
                      emis_rate,
                      emis_hours,
                      samp_interval,
                      puff_or_part,
                      particle_num,
                      filename):
    """
    This function is used to configure the hysplit model. If changes need to be made outside of the
    parameters described here, please edit the py file directly.

    Input:
    ----------
    start_model: the date in format year(1990 --> 90), month, day, hour (24 hour). Please fill to two places. Ex-90 01 01 01
    num_loc: The number of starting locations for emmitance. Ex-1
    start_locs: Latitude, Longitude and Height (m) of emission. Ex-40.39 -110.1 0.00
    tot_runtime: Hours of tracking following emission. Ex-48
    mod_top: The model top. Anything beyond this is not calculated. Ex-5000.0
    input_data_grids: The number of atmospheric inputs. Ex-2
    grid_1_dir: The directory of the first atmospheric input. Ex-C:\\Users\\u0890227\\Desktop\\HYSPLIT\\NARR_Weather_Data\\
    grid_1_name: The name of the first atmospheric input. Ex-NARR199001
    grid_2_dir: The directory for the second atmospheric input. See above examples.
    grid_2_name: The name for the second atmospheric input.
    chem_ident: A four digit identifier for the pollutant. Ex. CUMO.
    emis_rate: The emission rate in per hour format. Ex. 0.03427
    emis_hours: The total number of hours of emission. Ex. 3.00
    samp_interval: How often the model should be record and export mappings of the pollutant in days, hours, minutes. Ex: 00 03 00
    puff_or_part: Designation for if the model should use puffs or particles. Several options, see HYSPLIT user manual for details. Ex: 0
    particle_num: The total number of particles or puffs utilized by the model. Ex-1000
    filename: The save name for the files Ex-Jan_1

    """

    import subprocess
    #Create the Batch File
    myBat = open(r'C:\\Users\\u0890227\\Desktop\\HYSPLIT\\batch\\hysplit_temp.bat','w+')

    #Write the Control file
    myBat.write('''@echo off
    setLocal EnableDelayedExpansion

    REM -----------------------------------------------

    REM Set the directories
    set DIR=C:\\Users\\u0890227\\
    set PGM=%DIR%\hysplit4
    cd %PGM%\working

    REM -----------------------------------------------

    REM Checks for existence of ASCDATA file
    IF EXIST ASCDATA.CFG DEL ASCDATA.CFG
    echo -90.0   -180.0  lat/lon of lower left corner   >ASCDATA.CFG
    echo 1.0     1.0     lat/lon spacing in degrees    >>ASCDATA.CFG
    echo 180     360     lat/lon number of data points >>ASCDATA.CFG
    echo 2               default land use category     >>ASCDATA.CFG
    echo 0.2             default roughness length (m)  >>ASCDATA.CFG
    echo '%PGM%\\bdyfiles\\'  directory of files         >>ASCDATA.CFG

    REM -----------------------------------------------

    REM Control file read by the model

    REM Starting Time (year, month, day, hour)
    echo {start_model}             >CONTROL
    REM Number of starting locations
    echo {num_loc}                      >>CONTROL
    REM Enter starting locations (lat, lon, meters)
    echo {start_locs}        >>CONTROL
    REM Enter total run time (hours)
    echo {tot_runtime}                     >>CONTROL
    REM Vertical Motion (0:data 1:isob 3:dens 4:sigma 5:diverg 6:mls2agl 7:average 8: damped)
    echo 0                      >>CONTROL
    REM Top of the model
    echo {mod_top}                >>CONTROL
    REM Number of input data grids
    echo {input_data_grids}                      >>CONTROL
    REM Meteorological data grid #1 directory and file name
    echo {grid_1_dir}       >>CONTROL
    echo {grid_1_name}            >>CONTROL
    REM Meteorological data grid #1 directory and file name
    echo {grid_2_dir}       >>CONTROL
    echo {grid_2_name}            >>CONTROL

    REM Number of different pollutants
    echo 1                      >>CONTROL
    REM Pollutant four character Identifier
    echo {chem_ident}                   >>CONTROL
    REM Emission rate (per hour)
    echo {emis_rate}               >>CONTROL
    REM Hours of emission
    echo {emis_hours}                    >>CONTROL
    REM Release start time: year month day hour minute --- 0s will be start time of the meteorological data file)
    echo 00 00 00 00 00         >>CONTROL


    REM Number of simultaneous concentration grids
    echo 1                      >>CONTROL
    REM Center (Lat, lon in degrees)
    echo 0.0 0.0                >>CONTROL
    REM Grid spacing (Lat,lon in degrees)
    echo 0.05 0.05              >>CONTROL
    REM Grid span (Lat,lon in degrees)
    echo 30.0 30.0              >>CONTROL
    REM Enter grid #1 directory (where things are written)
    echo .\                     >>CONTROL
    REM Enter grid #1 filename
    echo cdump                  >>CONTROL
    REM Number of vertical concentration levels (add 0 if adding treating at ground level)
    echo 1                      >>CONTROL
    REM Height of each level (m)
    echo 100                    >>CONTROL
    REM Sampling start time (year month day hour minute)
    echo 00 00 00 00 00         >>CONTROL
    REM Sampling stop time (year month day hour minute)
    echo 00 00 00 00 00         >>CONTROL
    REM Sampling interval (type hour minute) How often is a map created...
    echo {samp_interval}               >>CONTROL


    REM Number of pullutants depositing
    echo 1                      >>CONTROL
    REM Particle: Diameter(um), Density (g,cc) and Shape
    echo 0.0 0.0 0.0            >>CONTROL
    REM Deposition Velocity (m/s), pollutant molecular weight (gram/mole), surface reactivity ratio, diffusivity ratio, effective henrys constant
    echo 0.0 0.0 0.0 0.0 0.0    >>CONTROL
    REM Wet Removal:Actual Henrys constant (In-cloud, below cloud)
    echo 0.0 0.0 0.0            >>CONTROL
    REM Radioactive decay half-life (days)
    echo 0.0                    >>CONTROL
    REM Pollutant Resuspension (1/m)
    echo 0.0                    >>CONTROL

    REM -----------------------------------------------
    REM ADJUST SETTINGS (https://www.ready.noaa.gov/hysplitusersguide/S410.htm)

    IF EXIST SETUP.CFG DEL SETUP.CFG
    echo ^&SETUP                  >SETUP.CFG
    REM Particle vs Puff (currently only particle)
    echo initd = {puff_or_part}                >>SETUP.CFG
    REM Total number of particles
    echo numpar = {particle_num}           >>SETUP.CFG
    echo /                       >>SETUP.CFG


    REM -----------------------------------------------
    IF EXIST cdump DEL cdump
    REM -----------------------------------------------

    REM Run the model
    %PGM%\\exec\\hycs_std

    REM -----------------------------------------------

    REM execute the plotting
    ECHO 'TITLE^&','### %0 ### ^&' >LABELS.CFG

    REM adding -a2 to imply Arcview generate in value
    REM adding -x1.0E+12 to make the units picopounds
    REM Will need to adjust values..I think..
    %PGM%\exec\concplot -icdump -a2 -c50 -x1.0E+12 -j%PGM%\graphics\arlmap

    REM Open the plotting


    REM --------------------------------------------------
    REM Save all shapefiles into shapefiles
    set /A Counter=0
    set /A file_count = 0

    REM this allows me to print all the GIS files used to create shapefiles
    for %%i in (C:\\Users\\u0890227\\hysplit4\\working\\*GIS_*) do (
      set /A Counter+=1

      if !Counter! ==1 (
      set att=%%i
      )

      if !Counter! ==2 (
      set txt=%%i
      set /A file_count+=3

        echo !att!
        echo !txt!

        %PGM%\\exec\\ascii2shp -d concpolys polygons <!txt!
        %PGM%\\exec\\txt2dbf -C11 -C5 -C9 -C5 -C6../ -C6 -d, !att! concpolys.dbf


        mkdir C:\\Users\\u0890227\\Desktop\\hysplit\\{filename}\\hour_after_start_!file_count!
        move %PGM%\\working\\*concpolys* C:\\Users\\u0890227\\Desktop\\hysplit\\{filename}\\hour_after_start_!file_count!

        set /A Counter=0
      )
    )

    REM concplot.ps

    '''.format(start_model = start_model,
               num_loc = num_loc,
               start_locs = start_locs,
               tot_runtime = tot_runtime,
               mod_top = mod_top,
               input_data_grids = input_data_grids,
               grid_1_dir=grid_1_dir,
               grid_1_name = grid_1_name,
               grid_2_dir = grid_2_dir,
               grid_2_name = grid_2_name,
               chem_ident = chem_ident,
               emis_rate = emis_rate,
               emis_hours = emis_hours,
               samp_interval = samp_interval,
               puff_or_part = puff_or_part,
               particle_num = particle_num,
               filename = filename
              ))

    myBat.close()

    subprocess.call([r'C:\\Users\\u0890227\\Desktop\\HYSPLIT\\batch\\hysplit_temp.bat'])
    print('Script Completed')

def RSEI_merger(RSEI_df,TRI_df):
    """A function which concatenates RSEI data with TRI data based upon the FRSID.

    This function retains the following parameters: 'Date','CAS', 'Daily_Release', 'FRSID', 'Chem', 'MW', 'Half_Life',
    'Solubility','Lat','Long','City','ZIPCode','FacilityName','City','County','StackHeight','StackVelocity',
    'StackDiameter','StackHeightSource','StackVelocitySource','StackDiameterSource.

    Input:
    ----------
    RSEI_df : Stock RSEI dataframe (in csv form)
    TRI_df: Dataframe from TRI derived materials

    Return:
    ----------
    merge: dataframe with the parameters listed above.
    """

    merge = pd.merge(TRI_df.reset_index(),
                 RSEI_df,
                 left_on ='FRSID',
                 right_on = 'FRSID',
                 how='left')[['Date',
                              'CAS',
                              'Daily_Release',
                              'FRSID',
                              'Chem',
                              'MW',
                              'Half_Life',
                              'Solubility',
                              'Lat',
                              'Long',
                              'City',
                              'ZIPCode',
                              'FacilityName',
                              'City',
                              'County',
                              'StackHeight',
                              'StackVelocity',
                              'StackDiameter',
                              'StackHeightSource',
                              'StackVelocitySource',
                              'StackDiameterSource']]
    return merge

def hysplit_input_conversion(data,stack_or_fug):
    """A function to convert the height, lat and lon to a HYSPLIT input.

        Input:
        ----------
        data : input dataframe with a stack height, latitude and longitude with corresponding dataframe names -- 'StackHeight', 'Lat', 'Long'
        stack_or_fug: binary (1 or 0) where 1 designates a stack emission and 0 denotes an fugitive emission

        Return:
        ----------
        data: output dataframe containing a new column HS_loc_input

    """
    if stack_or_fug == 1:
        data["HS_loc_input"] = round(data["Lat"],2).astype(str) + " "+ round(data["Long"],2).astype(str) + " " + data['StackHeight'].astype(str)
    if stack_or_fug == 0:
        data["HS_loc_input"] = round(data["Lat"],2).astype(str) + " "+ round(data["Long"],2).astype(str) + " " + "0.00"

    return data

def chem_date_comb(startdate,enddate,freq,data):
    """A function which takes yearly data and creates an index breakdown of yearly release from start to end date at the desired frequency.

        Input:
        ----------
        startdate: start date in datetime format. Ex-1/1/90 00:00
        enddate: end date in datetime format. Ex-12/31/90 21:00
        freq: Datetime description for how often measurements should be taken. Ex-3H
        data: Input data to perform analysis on. Derived from TRI information.

        Return:
        ----------
        data: returns a dataframe with the datetime and CAS as co-indexes.

    """
    #Set the time dates for analysis:
    calendar = pd.date_range(startdate,enddate, freq=freq)

    #Collect the daily information from the original data
    final_df = pd.DataFrame(columns = ['Daily_Release','FRSID','Chem','CAS','MW','Half_Life','Solubility','Lat','Long'])
    for rows in range(data.shape[0]):

        #Edit if you want more information added to the release
        temp_df = pd.DataFrame({'Daily_Release': [data['51-FUGITIVEAIR'].iloc[rows]/calendar.shape[0]],
                                'FRSID':data['FRSID'].iloc[rows],
                                'Chem':data['CHEMICAL'].iloc[rows],
                                'CAS':data['CAS#/COMPOUNDID'].iloc[rows],
                                'MW':data['MW'].iloc[rows],
                                'Half_Life':data['1/2 Life'].iloc[rows],
                                'Solubility':data['Solubility in H2O'].iloc[rows],
                                'Lat':data['LATITUDE'].iloc[rows],
                                'Long':data['LONGITUDE'].iloc[rows]})

        final_df = final_df.append(temp_df)

    #Add a date-time to each
    final = pd.DataFrame(columns = ['Daily_Release','FRSID','Chem','CAS','MW','Half_Life','Solubility','Lat','Long'] )
    for index in range(calendar.shape[0]):
        final_df['Date_Time'] = calendar[index].strftime("%m/%d/%Y %H:%M:%S")
        temp = final_df.set_index('Date_Time')
        final = final.append(temp)

    #Realign the axis:
    idx = pd.MultiIndex.from_arrays([final.index.array,final['CAS'].array],names = ('Date','CAS'))
    final = final.set_index(idx)

    return final.drop(columns = ['CAS'])