# ----------------------------------------------------------------------------
# Stormwater QA/QC: SW_QAQC_DB.py
# Written by: Jennifer McCall
# Description: Calculates coded values as domain description, and performs other QA/QC on Stormwater data.
# ----------------------------------------------------------------------------

import arcpy, os 
from datetime import date, datetime, timedelta

arcpy.env.overwriteOutput = True
times1 = list()
times1.append(time.time())

def dbPath():
        #parameters for database
        Folder = "Sample Folder"
        databasename = "Database Name"
        platform = "SQL_Server"
        instance = "Instance"
        authentication = "OPERATING_SYSTEM_AUTH"
        dbname = "DBName"
        #Connect to database
        arcpy.CreateDatabaseConnection_management(Folder, databasename, platform, instance, authentication, "","","",dbname)
        #print("Done!!")

        times1 = list()
        times1.append(time.time())

        # ArcPro PROD SDE connection file to target DB
        dbPath = Folder +  "\\" + databasename + ".sde" 
        
        return dbPath

path = dbPath()
path2 = "C:\\Path"
featureClass = [os.path.join(path, "Stormwater_Culvert"),os.path.join(path, "Stormwater_Inlet"),
os.path.join(path, "Line_Gen"),os.path.join(path, "Stormwater_Manhole"),os.path.join(path, "Stormwater_Outfalls"),os.path.join(path, "Stormwater_Pipe_Marker"),os.path.join(path, "Stormwater_Point_gen"),
os.path.join(path, "Sign"),os.path.join(path, "StormwaterChannel"),os.path.join(path, "StormwaterArea"), os.path.join(path, "Stormwater_Area_Gen"), os.path.join(path, "Stormwater_Control_Structure")]
domains = arcpy.da.ListDomains(path)
cvList = []
descList = []



def timestamp():
    #Timestamp for printing on output, formatted as m/d h:m:s e.g. 3/4 13:58:24 
    times1.append(time.time())  # float format; datetime.now() is datetime format
    return " ["+"{dt.month}/{dt.day} {dt:%H}:{dt:%M}:{dt:%S}".format(dt=datetime.now())+"] "

def addMsg(msg, ts=True, warning=False): 
    """Print time-stamped message to results and to log file. """
    """(Can use 2nd parameter to optionally turn off timestamp.)"""
    if ts: msg = timestamp() + msg
    # arcpy.AddMessage(msg) for running as a Python Toolbox; print(msg) for standalone
    
    arcpy.AddWarning(msg) if warning else arcpy.AddMessage(msg)
     # Print to logFile also if it exists
     # Set log folder to contain log files
    logFldr = path2
    logFile = logFldr + "\\Log_"+time.strftime("%Y%m%d")+".log"
    if not os.path.exists(logFldr):  
        addMsg("Creating folder to contain script results logs,\n  {0}...".format(logFldr))
        os.makedirs(logFldr)

    try: logFile
    except NameError: logFile_exists = False
    else: logFile_exists = True
    if logFile_exists:
        with open(logFile, "a") as myFile: myFile.write (msg+"\n")

# Creates list of domain names
for domain in domains:
    cvList.append(domain.name)

for dom in cvList:
    print(dom)
    new_domTable = dom +"_1"
    code = "Code"
    description = "Description"
    descList = []
    view = "View"
    domTable = os.path.join(path,"DomTable" + dom[:3])
    # Exports domain to table for calculation
    addMsg("Exporting " + dom + " domain to table")
    arcpy.DomainToTable_management(path, dom, domTable, code, description)
    # Calculates coded value as description for each domain in DB
    addMsg("Calculating coded value as description")
    try: 
        arcpy.CalculateField_management(domTable, code, "!description!", "PYTHON")
    except arcpy.ExecuteError:    
        arcpy.AddError(arcpy.GetMessages(2))    
        continue
    # Imports new recalculated domain
    addMsg("Importing new domain")
    try: 
        arcpy.TableToDomain_management(domTable, code, description, path, new_domTable)
    except arcpy.ExecuteError:    
        arcpy.AddError(arcpy.GetMessages(2))    
        continue    
    for fc in featureClass:
        fieldList = arcpy.ListFields(fc)  
        for fld in fieldList:
            if fld.domain == dom:
                # Removes the old domain from each field 
                addMsg("Removing old domain from " + fld.name)
                arcpy.RemoveDomainFromField_management(fc, fld.name)

                # Clean up common input errors
                
                addMsg("Cleaning common input errors") 
                with arcpy.da.SearchCursor(fc, fld.name) as cursor: 
                    for row in cursor:
                        strRow = str(row)
                        rStrip   = strRow.strip("('',)")
                        
                        if rStrip == "N":
                            View1="View1"
                            addMsg("Recalculating {} field from {}".format(fld.name, fc)) 
                            arcpy.MakeTableView_management(fc, "View1", "{} = 'N'".format(fld.name))
                            arcpy.CalculateField_management(View1, fld.name, "'No'", "PYTHON")
                        if rStrip == "Y":
                            View2="View2"
                            addMsg("Recalculating {} field from {}".format(fld.name, fc)) 
                            arcpy.MakeTableView_management(fc, "View2", "{} = 'Y'".format(fld.name))
                            arcpy.CalculateField_management(View2, fld.name, "'Yes'", "PYTHON")    
                        if rStrip == "O":
                            View3="View3"
                            addMsg("Recalculating {} field from {}".format(fld.name, fc)) 
                            arcpy.MakeTableView_management(fc, "View3", "{} = 'O'".format(fld.name))
                            arcpy.CalculateField_management(View3, fld.name, "'Other'", "PYTHON")
                        if rStrip == "OP":
                            View4="View4"
                            addMsg("Recalculating {} field from {}".format(fld.name, fc)) 
                            arcpy.MakeTableView_management(fc, "View4", "{} = 'OP'".format(fld.name))
                            arcpy.CalculateField_management(View4, fld.name, "'Open Pipe'", "PYTHON")    
                        if rStrip == "POS":
                            View5="View5"
                            addMsg("Recalculating {} field from {}".format(fld.name, fc)) 
                            arcpy.MakeTableView_management(fc, "View5", "{} = 'POS'".format(fld.name))
                            arcpy.CalculateField_management(View5, fld.name, "'Pond Outlet Structure'", "PYTHON")    
                        if rStrip == "Pond Outlet Structur":
                            View6="View6"
                            addMsg("Recalculating {} field from {}".format(fld.name, fc)) 
                            arcpy.MakeTableView_management(fc, "View6", "{} = 'Pond Outlet Structur'".format(fld.name))
                            arcpy.CalculateField_management(View6, fld.name, "'Pond Outlet Structure'", "PYTHON")    
                        if rStrip == " Pond Outlet Structure":
                            View7="View7"
                            addMsg("Recalculating {} field from {}".format(fld.name, fc)) 
                            arcpy.MakeTableView_management(fc, "View7", "{} = ' Pond Outlet Structure'".format(fld.name))
                            arcpy.CalculateField_management(View7, fld.name, "'Pond Outlet Structure'", "PYTHON")
                        if rStrip == "VG":
                            View8="View8"
                            addMsg("Recalculating {} field from {}".format(fld.name, fc)) 
                            arcpy.MakeTableView_management(fc, "View8", "{} = 'VG'".format(fld.name))
                            arcpy.CalculateField_management(View8, fld.name, "'Vane Grate'", "PYTHON")    
                        if rStrip == "C":
                            View9="View9"
                            addMsg("Recalculating {} field from {}".format(fld.name, fc)) 
                            arcpy.MakeTableView_management(fc, "View9", "{} = 'C'".format(fld.name))
                            arcpy.CalculateField_management(View9, fld.name, "'Type C'", "PYTHON")
                        if rStrip == "R":
                            View10="View10"
                            addMsg("Recalculating {} field from {}".format(fld.name, fc)) 
                            arcpy.MakeTableView_management(fc, "View10", "{} ='R'".format(fld.name))
                            arcpy.CalculateField_management(View10, fld.name, "'Type R'", "PYTHON") 
                        if rStrip == "D":
                            View11="View11"
                            addMsg("Recalculating {} field from {}".format(fld.name, fc)) 
                            arcpy.MakeTableView_management(fc, "View11", "{} = 'D'".format(fld.name))
                            arcpy.CalculateField_management(View11, fld.name, "'Type D'", "PYTHON")                        
                        if rStrip == "13":
                            View12="View12"
                            addMsg("Recalculating {} field from {}".format(fld.name, fc)) 
                            arcpy.MakeTableView_management(fc, "View12", "{} = '13'".format(fld.name))
                            arcpy.CalculateField_management(View12, fld.name, "'Type 13'", "PYTHON")    
                        if rStrip == "13C":
                            View13="View13"
                            addMsg("Recalculating {} field from {}".format(fld.name, fc)) 
                            arcpy.MakeTableView_management(fc, "View13", "{} = '13C'".format(fld.name))
                            arcpy.CalculateField_management(View13, fld.name, "'Type 13 Combo'", "PYTHON")
                        if rStrip == "NS":
                            View14="View14"
                            addMsg("Recalculating {} field from {}".format(fld.name, fc)) 
                            arcpy.MakeTableView_management(fc, "View14", "{} = 'NS'".format(fld.name))
                            arcpy.CalculateField_management(View14, fld.name, "'Non-standard'", "PYTHON")    
                        if rStrip == "MFES":
                            View15="View15"
                            addMsg("Recalculating {} field from {}".format(fld.name, fc)) 
                            arcpy.MakeTableView_management(fc, "View15", "{} = 'MFES'".format(fld.name))
                            arcpy.CalculateField_management(View15, fld.name, "'Metal Flared End Section'", "PYTHON")
                        if rStrip == "CFES":
                            View16="View16"
                            addMsg("Recalculating {} field from {}".format(fld.name, fc)) 
                            arcpy.MakeTableView_management(fc, "View16", "{} = 'CFES'".format(fld.name))
                            arcpy.CalculateField_management(View16, fld.name, "'Concrete Flared End Section'", "PYTHON") 
                        if rStrip == "RR":
                            View17="View17"
                            addMsg("Recalculating {} field from {}".format(fld.name, fc)) 
                            arcpy.MakeTableView_management(fc, "View17", "{} = 'RR'".format(fld.name))
                            arcpy.CalculateField_management(View17, fld.name, "'Rip Rap'", "PYTHON")                        
                        if rStrip == "HW":
                            View18="View18"
                            addMsg("Recalculating {} field from {}".format(fld.name, fc)) 
                            arcpy.MakeTableView_management(fc, "View18", "{} = 'HW'".format(fld.name))
                            arcpy.CalculateField_management(View18, fld.name, "'Headwall'", "PYTHON")    
                        if rStrip == "NET":
                            View19="View19"
                            addMsg("Recalculating {} field from {}".format(fld.name, fc)) 
                            arcpy.MakeTableView_management(fc, "View19", "{} = 'NET'".format(fld.name))
                            arcpy.CalculateField_management(View19, fld.name, "'No End treatment (Open Pipe)'", "PYTHON")
                        if rStrip == "OET":
                            View20="View20"
                            addMsg("Recalculating {} field from {}".format(fld.name, fc)) 
                            arcpy.MakeTableView_management(fc, "View20", "{} = 'OET'".format(fld.name))
                            arcpy.CalculateField_management(View20, fld.name, "'Other End treatment (Plastic, Non-Standard)'", "PYTHON")
                        if rStrip == "LA":
                            View21="View21"
                            addMsg("Recalculating {} field from {}".format(fld.name, fc)) 
                            arcpy.MakeTableView_management(fc, "View21", "{} = 'LA'".format(fld.name))
                            arcpy.CalculateField_management(View21, fld.name, "'Local Agency'", "PYTHON")                        
                        if rStrip == "UN":
                            View22="View22"
                            addMsg("Recalculating {} field from {}".format(fld.name, fc)) 
                            arcpy.MakeTableView_management(fc, "View22", "{} = 'UN'".format(fld.name))
                            arcpy.CalculateField_management(View22, fld.name, "'Unknown'", "PYTHON")                                              
                        if rStrip == "C":
                            View23="View23"
                            addMsg("Recalculating {} field from {}".format(fld.name, fc)) 
                            arcpy.MakeTableView_management(fc, "View23", "{} = 'C'".format(fld.name))
                            if fld.name == "Culvert_Sh":
                                arcpy.CalculateField_management(View23, fld.name, "'Circular'", "PYTHON")
                            if fld.name == "Material":
                                arcpy.CalculateField_management(View23, fld.name, "'Concrete'", "PYTHON")    
                            if fld.name == "Structural":
                                arcpy.CalculateField_management(View23, fld.name, "'Critical'", "PYTHON")      
                            else:    
                                arcpy.CalculateField_management(View23, fld.name, "'Type C'", "PYTHON")
                        if rStrip == "F":
                            View24="View24"
                            addMsg("Recalculating {} field from {}".format(fld.name, fc)) 
                            arcpy.MakeTableView_management(fc, "View24", "{} = 'F'".format(fld.name))
                            arcpy.CalculateField_management(View24, fld.name, "'Fair'", "PYTHON")
                        if rStrip == "G":
                            View25="View25"
                            addMsg("Recalculating {} field".format(fld.name))
                            arcpy.MakeTableView_management(fc, "View25", "{} = 'G'".format(fld.name))
                            arcpy.CalculateField_management(View25, fld.name, "'Good'", "PYTHON")                        
                        if rStrip == "P":
                            View26="View26"
                            addMsg("Recalculating {} field from {}".format(fld.name, fc)) 
                            arcpy.MakeTableView_management(fc, "View26", "{} = 'P'".format(fld.name))
                            if fld.name == "Drains_To_":
                                arcpy.CalculateField_management(View26, fld.name, "'Pond or Control Measure'", "PYTHON")           
                            else:    
                                arcpy.CalculateField_management(View26, fld.name, "'Poor'", "PYTHON")               
                        if rStrip == "D/C":
                            View25="View25"
                            addMsg("Recalculating {} field from {}".format(fld.name, fc)) 
                            arcpy.MakeTableView_management(fc, "View25", "{} = 'D/C'".format(fld.name))
                            arcpy.CalculateField_management(View25, fld.name, "'Ditch or Conveyance'", "PYTHON")
                        if fld.name == "SW":
                            View26="View26"
                            addMsg("Recalculating {} field from {}".format(fld.name, fc)) 
                            arcpy.MakeTableView_management(fc, "View26", "{} = 'SW'".format(fld.name))
                            arcpy.CalculateField_management(View26, fld.name, "'State Waters'", "PYTHON")                        
                        if rStrip == "YG":
                            View27="View27"
                            addMsg("Recalculating {} field from {}".format(fld.name, fc)) 
                            arcpy.MakeTableView_management(fc, "View27", "{} = 'YG'".format(fld.name))
                            arcpy.CalculateField_management(View27, fld.name, "'Yes >50% sediment/water'", "PYTHON")                                           
                        if rStrip == "YL":
                            View28="View28"
                            addMsg("Recalculating {} field from {}".format(fld.name, fc)) 
                            arcpy.MakeTableView_management(fc, "View28", "{} = 'YL'".format(fld.name))
                            arcpy.CalculateField_management(View28, fld.name, "'Yes <50% sediment/water'", "PYTHON")            
                        if fld.name == "RCP":
                            View29="View29"
                            addMsg("Recalculating {} field from {}".format(fld.name, fc)) 
                            arcpy.MakeTableView_management(fc, "View29", "{} = 'RCP'".format(fld.name))
                            arcpy.CalculateField_management(View29, fld.name, "'Reinforced Concrete Pipe'", "PYTHON")                        
                        if rStrip == "CMP":
                            View30="View30"
                            addMsg("Recalculating {} field from {}".format(fld.name, fc)) 
                            arcpy.MakeTableView_management(fc, "View30", "{} = 'CMP'".format(fld.name))
                            arcpy.CalculateField_management(View30, fld.name, "'Corrugated Metal Pipe'", "PYTHON")                                           
                        if rStrip == "PVC":
                            View31="View31"
                            addMsg("Recalculating {} field from {}".format(fld.name, fc)) 
                            arcpy.MakeTableView_management(fc, "View31", "{} = 'PVC'".format(fld.name))
                            arcpy.CalculateField_management(View31, fld.name, "'Plastic Pipe'", "PYTHON")          
                        if rStrip == "FES":
                            View32="View32"
                            addMsg("Recalculating {} field from {}".format(fld.name, fc)) 
                            arcpy.MakeTableView_management(fc, "View32", "{} = 'FES'".format(fld.name))
                            arcpy.CalculateField_management(View32, fld.name, "'Flared End Section'", "PYTHON")     
                        if rStrip == "NL":
                            View33="View33"
                            addMsg("Recalculating {} field from {}".format(fld.name, fc)) 
                            arcpy.MakeTableView_management(fc, "View33", "{} = 'NL'".format(fld.name, fld.name))
                            arcpy.CalculateField_management(View33, fld.name, "'No'", "PYTHON")         
                        if rStrip == "E":
                            View34="View34"
                            addMsg("Recalculating {} field from {}".format(fld.name, fc)) 
                            arcpy.MakeTableView_management(fc, "View34", "{} ='E'".format(fld.name))
                            arcpy.CalculateField_management(View34, fld.name, "'Elliptical'", "PYTHON")                      
                        if rStrip == "US":
                            View35="View35"
                            addMsg("Recalculating {} field from {}".format(fld.name, fc)) 
                            arcpy.MakeTableView_management(fc, "View35", "{} ='US'".format(fld.name))
                            arcpy.CalculateField_management(View35, fld.name, "'Unspecified'", "PYTHON")  
                        if rStrip == "B":
                            View36="View36"
                            addMsg("Recalculating {} field from {}".format(fld.name, fc)) 
                            arcpy.MakeTableView_management(fc, "View36", "{} ='B'".format(fld.name))
                            arcpy.CalculateField_management(View36, fld.name, "'Box'", "PYTHON")           
                        if rStrip == "Ellyptical":
                            View37="View37"
                            addMsg("Recalculating {} field from {}".format(fld.name, fc)) 
                            arcpy.MakeTableView_management(fc, "View37", "{} ='Ellyptical'".format(fld.name))
                            arcpy.CalculateField_management(View37, fld.name, "'Elliptical'", "PYTHON")             
                        if rStrip == "Plastic":
                            View38="View38"
                            addMsg("Recalculating {} field from {}".format(fld.name, fc)) 
                            arcpy.MakeTableView_management(fc, "View38", "{} ='Plastic'".format(fld.name))
                            arcpy.CalculateField_management(View38, fld.name, "'Plastic Pipe'", "PYTHON")               
                        if rStrip == "S/EF":
                            View39="View39"
                            addMsg("Recalculating {} field from {}".format(fld.name, fc)) 
                            arcpy.MakeTableView_management(fc, "View39", "{} ='S/EF'".format(fld.name))
                            arcpy.CalculateField_management(View39, fld.name, "'Spillway/Emergency Overflow'", "PYTHON")               
                        if rStrip == "CD":
                            View40="View40"
                            addMsg("Recalculating {} field from {}".format(fld.name, fc)) 
                            arcpy.MakeTableView_management(fc, "View40", "{} ='CD'".format(fld.name))
                            arcpy.CalculateField_management(View40, fld.name, "'Check Dam'", "PYTHON")               
                        if rStrip == "BP":
                            View41="View41"
                            addMsg("Recalculating {} field from {}".format(fld.name, fc)) 
                            arcpy.MakeTableView_management(fc, "View41", "{} ='BP'".format(fld.name))
                            arcpy.CalculateField_management(View41, fld.name, "'Bank Protection'", "PYTHON")                                                                   
                        if rStrip == "FB":
                            View42="View42"
                            addMsg("Recalculating {} field from {}".format(fld.name, fc)) 
                            arcpy.MakeTableView_management(fc, "View42", "{} ='FB'".format(fld.name))
                            arcpy.CalculateField_management(View42, fld.name, "'Forebay'", "PYTHON")                                                                   
                        if rStrip == "M":
                            View43="View43"
                            addMsg("Recalculating {} field from {}".format(fld.name, fc)) 
                            arcpy.MakeTableView_management(fc, "View43", "{} ='M'".format(fld.name))
                            arcpy.CalculateField_management(View43, fld.name, "'Micropool'", "PYTHON")                                      
                        if rStrip == "R":
                            View44="View44"
                            addMsg("Recalculating {} field from {}".format(fld.name, fc)) 
                            arcpy.MakeTableView_management(fc, "View44", "{} ='R'".format(fld.name))
                            arcpy.CalculateField_management(View44, fld.name, "'Micropool'", "PYTHON")     
                        if rStrip == " ":
                            View45="View45"
                            addMsg("Recalculating {} field from {}".format(fld.name, fc)) 
                            arcpy.MakeTableView_management(fc, "View45", "{} = ' '".format(fld.name))
                            arcpy.CalculateField_management(View45, fld.name, "None", "PYTHON")
                        if rStrip == "  ":
                            View46="View46"
                            addMsg("Recalculating {} field from {}".format(fld.name, fc)) 
                            arcpy.MakeTableView_management(fc, "View46", "{} = '  '".format(fld.name))
                            arcpy.CalculateField_management(View46, fld.name, "None", "PYTHON")                                                                      
                
        
                # Assigns new recalculated domain to field
                addMsg("Assigning new domain to " + fld.name)
                arcpy.AssignDomainToField_management(fc,fld.name,new_domTable)                 
    addMsg("Deleting unneeded domain output table")
    arcpy.Delete_management(domTable)       
   
    # Deletes the old domain
    addMsg("Deleting old domain")
    try: 
        arcpy.DeleteDomain_management(path, dom)
    except arcpy.ExecuteError:    
        arcpy.AddError(arcpy.GetMessages(2))    
        continue
    
    # Domain is reassigned its old name
    addMsg("Reasigning old domain name to " + dom)
    arcpy.AlterDomain_management(path, new_domTable, dom)   
    
addMsg("QA/QC script complete")

