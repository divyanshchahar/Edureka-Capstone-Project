##########################
##########################
## FUNCTION DECLARATION ##
##########################
##########################

###################################
# FUNCTION TO WRITE UNIQUE VALUES #
###################################

# Function to count frquency of values in the rows of a dataset
# INPUT:
# df_temp [pyspark-dataframe] Dataframe on which operation needs to be performed
# rowname [string] name of the string whose values need to counted
# filename [string] name of the file which will store the result
# OUTPUT:
# csv file with results of the operation
def unique_writer(df_temp, rowname, filename):
    df_unique = df_temp.groupby(rowname).count().sort(col("count").desc())
    df_unique.toPandas().to_csv(filename, index=False)

#####################################################
# FUNCTION TO COUNT UNWANTED VALUES IN EVERY COLUMN #
#####################################################

# INPUT :
# dataframe_name [string] name of the the dataframe on which operation needs to be preformed
# file_name [string] name of the the file in which results need to be stored in csv format
# OUTPUT:
# csv file with output of the operation
def count_unwanted(dataframe_address, file_name):

    df_temp = spark.read.csv(dataframe_address, header=True)

    # unique_count = []
    nan_count = []
    null_count = []
    q_count = []
    zero_count = []
    column_index = []

    for i in df_temp.columns:
        column_index.append(i)
        # unique_count.append(df_temp.select(i).distinct().count())
        nan_count.append(df_temp.where(df_temp[i].isNull()).count())
        null_count.append(df_temp.filter(df_temp[i] == 'NaN').count())
        q_count.append(df_temp.filter(df_temp[i] == '?').count())
        zero_count.append(df_temp.filter(df_temp[i] == 0).count())

    # unwanted_data = {"unique":unique_count, "nan_count": nan_count, "null_count": null_count, "q_count": q_count, "zero_count": zero_count}
    unwanted_data = {"nan_count": nan_count, "null_count": null_count, "q_count": q_count, "zero_count": zero_count}

    pd.DataFrame(unwanted_data, index=column_index).to_csv(file_name)

############################
# FUNCTION TO GROUP VALUES #
############################
# INPUT:
# df [pyspak dataframe] Dataframe containing groups and values
# grouping_column [string] column of the dataframe which will form groups
# values_column [string] column which contains the values
# file_name [string] name of the file which will store the results
# OUTPUT:
# text file containing the results of grouping operation
def group_values(df, grouping_clmn, values_column, file_name):

    df1 = df.where(df[grouping_clmn].isNull())

    nvls= set(df1.toPandas()[values_column].tolist())

    f = open(file_name, "w")
    f.write("GROUPED BY: " + str(grouping_clmn) + "\n")
    f.write("VALUES: " + str(values_column) + "\n")
    f.write("___________________________________________________________" + "\n")
    f.write("\n")

    f.write("NONE \n")
    for nvl in nvls:
        f.write(nvl.lower())
        f.write("\n")

    df2 = df.where(df[grouping_clmn].isNotNull())
    grps = set(df2.toPandas()[grouping_clmn].tolist())

    for grp in grps:
        f.write(str(grp).upper())
        f.write("\n")
        df_temp1 = df_temp.where(df_temp[grouping_clmn] == grp)
        vlus = set(df_temp1.toPandas()[values_column].tolist())
        for vls in vlus:
            f.write(str(vls).lower())
            f.write("\n")
        f.write("\n")
    f.close()





##############################
##############################
## MAIN BODY OF THE PROGRAM ##
##############################
##############################

# Importing Libraries and functionality
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, countDistinct
import pandas as pd
from datetime import datetime

spark = SparkSession.builder.getOrCreate() # Creating Spark Session

###############################
# EDA - UNDERSTANDING ENTRIES #
###############################

now = datetime.now()
dt_string = now.strftime("%d-%m-%Y %H:%M:%S")
print("EDA - UNDERSTANDING ENTRIES started at:",dt_string)


# ALLERGIES #

df_temp = spark.read.csv("dataset_project_1/allergies.csv", header=True)

unique_writer(df_temp, "DESCRIPTION", "eda/understanding_entries/allergies_uvc1.csv") # Unique Values in the the DESCRIPTION column
unique_writer(df_temp, "PATIENT", "eda/understanding_entries/allergies_uvc2.csv") # Unique Values in the patient column

# Determining if there are patients with multiple ongoing allergies
df_temp = df_temp.where(df_temp["STOP"].isNull())
unique_writer(df_temp, "PATIENT", "eda/understanding_entries/allergies_nuvc1.csv")

# Unwanted Data
count_unwanted("dataset_project_1/allergies.csv", "eda/understanding_entries/allergies_unwanted.csv")

###############################################################################

# CAREPLANS #

df_temp = spark.read.csv("dataset_project_1/careplans.csv", header=True)

# Unique Values Count
unique_writer(df_temp, "PATIENT", "eda/understanding_entries/careplans_uvc1.csv") # PATIENT Column
unique_writer(df_temp, "DESCRIPTION", "eda/understanding_entries/careplans_uvc2.csv") # DESCRIPTION column
unique_writer(df_temp, "REASONDESCRIPTION", "eda/understanding_entries/careplans_uvc3.csv") # REASONDESCRIPTION column

# Unique Values Count on Datafarem filtered by NaN values
df_temp1 = df_temp.where(df_temp["STOP"].isNull()) # Filtering the data by null values in STOP column
unique_writer(df_temp1, "PATIENT", "eda/understanding_entries/careplans_nuvc1.csv") # unique values count on PATIENT column

df_temp2 = df_temp.where(df_temp["REASONDESCRIPTION"].isNull()) # Filtering the data by NaN values in REASONDESCRIPTION column
unique_writer(df_temp2, "DESCRIPTION", "eda/understanding_entries/careplans_nuvc2.csv") # Unique values on the DESCRITION column


count_unwanted("dataset_project_1/careplans.csv", "eda/understanding_entries/careplans_unwanted.csv") # Unwanted Data

###############################################################################################

# CONDITIONS #

df_temp = spark.read.csv("dataset_project_1/conditions.csv", header=True) # Reading the dataframe

# Unique Values Count
unique_writer(df_temp, "DESCRIPTION", "eda/understanding_entries/conditions_uvc1.csv") # DESCRIPTION Column

# Unique Values Count on null filtered Dataframe
df_temp1 = df_temp.where(df_temp["STOP"].isNull()) # Filtering by NaN values in STOP ccolumn
unique_writer(df_temp1, "DESCRIPTION", "eda/understanding_entries/conditions_nuvc1.csv") # performing unique values count - The conditions in this file will be called "Assumed chronic"

# Dtermining if any of the conditions which do not have a stop date has stop dates in any of the enteries
chronic_conditions = set(df_temp1.toPandas()["DESCRIPTION"].tolist()) # Set of all the conditions which do not have a STOP date
df_temp2 = df_temp.where(df_temp["DESCRIPTION"].isin(chronic_conditions)) # Filtering the dataframe with the above set
df_temp3 = df_temp2.where(df_temp2["STOP"].isNotNull()) # Filtering the dataset again to have non Null Values
unique_writer(df_temp3, "DESCRIPTION", "eda/understanding_entries/conditions_psudo_chroninc.csv") # Writing the results to a file

# NOTE: Psudo Chronic Conditions is self coined term which represents conditions which were classsified as chroninic(i.e.
# having no stop date ) in some enteries but actually have STOP dates in some other enteries.

# Making a list of chronic situations
df_temp1 = spark.read.csv("eda/understanding_entries/conditions_nuvc1.csv", header=True) # File with conditions from enteris which have no STOP date
df_temp2 = spark.read.csv("eda/understanding_entries/conditions_psudo_chroninc.csv", header=True) # File with enteries with psudo chronic conditions
assumed_chronic = set(df_temp1.toPandas()["DESCRIPTION"].tolist()) # set of conditions which have no STOP dates
psudo_chronic = set(df_temp2.toPandas()["DESCRIPTION"].tolist()) # set of psudo chronic conditions
real_chronic = assumed_chronic - psudo_chronic # chronic conditions
df_chronic = pd.Series(list(chronic_conditions)) # Crearing a dataframe of chronic conditions
df_chronic.to_csv("preprocessed/conditions_chronic.csv", index=False, header=False) # writing chronic conditions to a file

####################################################################################

# ENCOUNTER #

df_temp = spark.read.csv("dataset_project_1/encounters.csv", header=True)

# Unique Values Count
unique_writer(df_temp, "REASONDESCRIPTION", "eda/understanding_entries/encounters_uvc1.csv") # REASONDESCRIPTION column
unique_writer(df_temp, "DESCRIPTION", "eda/understanding_entries/encounters_uvc2.csv") # DESCRIPTION column
unique_writer(df_temp, "ENCOUNTERCLASS", "eda/understanding_entries/encounters_uvc3.csv") #  ENCOUNTERCLASS column

count_unwanted("dataset_project_1/encounters.csv", "eda/understanding_entries/encounters_unwanted.csv") # Unwanted Data

# Unique Values Count on Dataframe filtered by NaN values
df_temp1 = df_temp.where(df_temp["REASONDESCRIPTION"].isNull()) # Filtering the dataset by NaN values in REASONDECRIPTION column
unique_writer(df_temp1, "DESCRIPTION", "eda/understanding_entries/encounters_nuvc1.csv") # Unique Value Count on DESCRIPTION column
unique_writer(df_temp1, "ENCOUNTERCLASS", "eda/understanding_entries/encounters_nuvc2.csv") # Unique Value Count on ENCOUNTERCLASS column

# Cross Tabulation operations
df_temp.crosstab("REASONDESCRIPTION", "ENCOUNTERCLASS").toPandas().to_csv("eda/understanding_entries/encounters_ct1.csv", index=False) # REASONDESCRIPTION and ENCOUNTERCLASS
df_temp.crosstab("DESCRIPTION", "ENCOUNTERCLASS").toPandas().to_csv("eda/understanding_entries/encounters_ct2.csv", index=False) # DESCRIPTION and ENCOUNTERCLASS
df_temp.crosstab("DESCRIPTION", "REASONDESCRIPTION").toPandas().to_csv("eda/understanding_entries/encounters_ct3.csv", index=False) # DESCRIPTION and REASONDECSRIPTION

# Cross Tabulation operation on Dataframe filtered by NaN operations
# df_temp1 = df_temp.where(df_temp["REASONDESCRIPTION"].isNull())
# df_temp1.crosstab("DESCRIPTION", "ENCOUNTERCLASS").toPandas().to_csv("eda/encounters_REASONDESCRIPTION_null_crosstab.csv", index=False)

########################################################################################################################################

# IMAGING STUDIES #

df_temp = spark.read.csv("dataset_project_1/imaging_studies.csv", header=True)

# Unique Values Count
unique_writer(df_temp, "BODYSITE_DESCRIPTION", "eda/understanding_entries/imaging_studies_uvc1.csv") # BODYSITE_DESCRIPTION
# unique_writer(df_temp, "MODALITY_DESCRIPTION", "eda/imaging_studies_MODALITY_DESCRIPTION.csv") # MODATLITY_DESCRIPTION
unique_writer(df_temp, "SOP_DESCRIPTION", "eda/understanding_entries/imaging_studies_uvc2.csv") # SOP_DESCRIPTION

count_unwanted("dataset_project_1/imaging_studies.csv", "eda/understanding_entries/imaging_studies_unwanted.csv")

# Cross Tabulation Operation
# df_temp.crosstab("BODYSITE_DESCRIPTION", "MODALITY_DESCRIPTION").toPandas().to_csv("eda/imaging_studies_crosstab_BODYSITE_DESCRIPTION_MODALITY_DESCRIPTION.csv", index=False)
df_temp.crosstab("BODYSITE_DESCRIPTION", "SOP_DESCRIPTION").toPandas().to_csv("eda/understanding_entries/imaging_studies_ct1.csv", index=False) # BODYSITE_DESCRIPTION and SOP_DESCRIPTION
df_temp.crosstab("MODALITY_DESCRIPTION", "SOP_DESCRIPTION").toPandas().to_csv("eda/understanding_entries/imaging_studies_ct2.csv", index=False) # MODALITY_DESCRIPTION and SOP_DESCRIPTION

###############################################################################################################################

# IMMUNIZATION #

df_temp = spark.read.csv("dataset_project_1/immunizations.csv", header=True)

# Unique Values Count
unique_writer(df_temp, "DESCRIPTION", "eda/understanding_entries/imunization_uvc1.csv")

count_unwanted("dataset_project_1/immunizations.csv", "eda/understanding_entries/immunization_unwanted.csv") # Unwanted Data

############################################################################

# MEDICATION #

df_temp = spark.read.csv("dataset_project_1/medications.csv", header=True)

# Unique Values Count
unique_writer(df_temp, "DESCRIPTION", "eda/understanding_entries/medications_uvc1.csv") # DESCRIPTION
unique_writer(df_temp, "REASONDESCRIPTION", "eda/understanding_entries/medications_uvc2.csv") # REASONDECRIPTION

count_unwanted("dataset_project_1/medications.csv", "eda/understanding_entries/medications_unwanted.csv")

# # Cross Tabulation Operation
df_temp.crosstab("DESCRIPTION", "REASONDESCRIPTION").toPandas().to_csv("eda/understanding_entries/medications_ct1.csv", index=False)

# Unique Values Count on Dataframe filtered by null values
df_temp1 = df_temp.where(df_temp["REASONDESCRIPTION"].isNull()) # filtering by NaN values in REASONDESCRIPTION column
unique_writer(df_temp1, "DESCRIPTION", "eda/understanding_entries/medications_nuvc1.csv") #unique values count on DESCRIPTION

###########################################################################################

# OBSERVATION #

df_temp = spark.read.csv("dataset_project_1/observations.csv", header=True)

# Unique Value Counts
unique_writer(df_temp, "DESCRIPTION", "eda/understanding_entries/observation_DESCRIPTION.csv")

count_unwanted("dataset_project_1/observations.csv", "eda/understanding_entries/observations_unwanted.csv")

############################################################################

# PROCEDURES #

df_temp = spark.read.csv("dataset_project_1/procedures.csv", header=True)

# Unique Values Count
unique_writer(df_temp, "DESCRIPTION", "eda/understanding_entries/procedures_uvc1.csv") # DESCRIPTION column
unique_writer(df_temp, "REASONDESCRIPTION", "eda/understanding_entries/procedures_uvc2.csv") # REASONDESCRIPTION column

count_unwanted("dataset_project_1/procedures.csv", "eda/understanding_entries/procedures_unwabted.csv") # Unwanted Data

# Unique Values Count on Dataframe filtered by Null Values
df_temp1 = df_temp.where(df_temp["REASONDESCRIPTION"].isNull()) # Filtering by null values in REASONDESCRIPTION
unique_writer(df_temp1, "DESCRIPTION", "eda/understanding_entries/procedures_nuvc1.csv") # counting unique values in DESCRIPTION column

# Cross Tabulation Operation
df_temp.crosstab("DESCRIPTION", "REASONDESCRIPTION").toPandas().to_csv("eda/understanding_entries/procedures_ct1.csv", index=False) # DESCRIPTION and REASONDESCRIPTION


now = datetime.now()
dt_string = now.strftime("%d-%m-%Y %H:%M:%S")
print("EDA - UNDERSTANDING ENTRIES finished at:",dt_string)

#########################################################################################################################################################################

############################
# EDA - UNDERSTANDING DATA #
############################

# CAREPLANS #

df_temp = spark.read.csv("dataset_project_1/careplans.csv", header=True)

group_values(df_temp, "DESCRIPTION", "REASONDESCRIPTION", r"eda/understanding_data/careplans_1.txt")
group_values(df_temp, "REASONDESCRIPTION", "DESCRIPTION", r"eda/understanding_data/careplans_2.txt")

########################################################################################################################





