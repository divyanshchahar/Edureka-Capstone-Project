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
# CSV file with results of the operation
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
# CSV file with output of the operation
def count_unwanted(dataframe_name, file_name):

    df_temp = spark.read.csv(dataframe_name, header=True)

    nan_count = []
    null_count = []
    q_count = []
    zero_count = []
    column_index = []

    for i in df_temp.columns:
        column_index.append(i)
        nan_count.append(df_temp.where(df_temp[i].isNull()).count())
        null_count.append(df_temp.filter(df_temp[i] == 'NaN').count())
        q_count.append(df_temp.filter(df_temp[i] == '?').count())
        zero_count.append(df_temp.filter(df_temp[i] == 0).count())

    unwanted_data = {"nan_count": nan_count, "null_count": null_count, "q_count": q_count, "zero_count": zero_count}

    pd.DataFrame(unwanted_data, index=column_index).to_csv(file_name)



##############################
##############################
## MAIN BODY OF THE PROGRAM ##
##############################
##############################

# Importing Libraries and functionality
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import pandas as pd

spark = SparkSession.builder.getOrCreate() # Creating Spark Session

# #######
# # EDA #
# #######

# ALLERGIES #

df_temp = spark.read.csv("dataset_project_1/allergies.csv", header=True)

unique_writer(df_temp, "DESCRIPTION", "eda/allergies_DESCRIPTION.csv") # Unique Values in the the DESCRIPTION column
unique_writer(df_temp, "PATIENT", "eda/allergies_PATIENT.csv") # Unique Values in the patient column

# Determining if there are patients with multiple ongoing allergies
df_temp = df_temp.where(df_temp["STOP"].isNull())
unique_writer(df_temp, "PATIENT", "eda/allergies_ongoing.csv")

# Unwanted Data
count_unwanted("dataset_project_1/allergies.csv", "eda/allergies_unwanted.csv")

###############################################################################

# CAREPLANS #

df_temp = spark.read.csv("dataset_project_1/careplans.csv", header=True)

unique_writer(df_temp, "PATIENT", "eda/careplans_PATIENT.csv") # Unique Values in the Patient Column

# Determining if a patient can have multiple ongoing care plans
df_temp1 = df_temp.where(df_temp["STOP"].isNull()) # Filtering the data by null values
unique_writer(df_temp1, "PATIENT", "eda/careplans_ongoing.csv") # unique values count on PATIENT column

unique_writer(df_temp, "DESCRIPTION", "eda/careplans_DESCRIPTION.csv") # Unique values in the DESCRIPTION column
unique_writer(df_temp, "REASONDESCRIPTION", "eda/careplans_REASONDESCRIPTION.csv") # Unique Values in the REASONDESCRIPTION column

# Determining the DESCRIPTION value when the REASONDESCRIPTION column is empty
df_temp2 = df_temp.where(df_temp["REASONDESCRIPTION"].isNull()) # Filtering the dat by null values
unique_writer(df_temp2, "DESCRIPTION", "eda/careplans_REASONDESCRIPTION_null.csv") # Unique values in the REASONDESCRITION column

count_unwanted("dataset_project_1/careplans.csv", "eda/careplans_unwanted.csv") # Unwanted Data
###############################################################################################

# CONDITIONS #

df_temp = spark.read.csv("dataset_project_1/conditions.csv", header=True)

unique_writer(df_temp, "DESCRIPTION", "eda/conditions_DESCRIPTIONS.csv") # Unique Values in the DESCRIPTION Column

# Determining Conditions with no STOP date i.e. chronic conditions
df_temp1 = df_temp.where(df_temp["STOP"].isNull())
unique_writer(df_temp1, "DESCRIPTION", "eda/conditions_STOP_null.csv") # The conditions in this file will be called "Assumed chronic"

# Dtermining if any of the conditions which do not have a stop date has stop dates in any of the enteries
chronic_conditions = set(df_temp1.toPandas()["DESCRIPTION"].tolist()) # Set of all the conditions which do not have a STOP date
df_temp2 = df_temp.where(df_temp["DESCRIPTION"].isin(chronic_conditions)) # Filtering the dataframe with the above setd
df_temp3 = df_temp2.where(df_temp2["STOP"].isNotNull()) # Filtering the dataset again to have non Null Values
unique_writer(df_temp3, "DESCRIPTION", "eda/conditions_psudo_chroninc.csv") # Writing the results to a file

# NOTE: Psudo Chronic Conditions is self coined term which represents conditions which were classsified as chroninic(i.e.
# having no stop date ) in some enteries but actually have STOP dates in some other enteries.

# Making a list of chronic situations
df_temp1 = spark.read.csv("eda/conditions_STOP_null.csv", header=True) # File with conditions from enteris which have no STOP date
df_temp2 = spark.read.csv("eda/conditions_psudo_chroninc.csv", header=True) # File with enteries with psudo chronic conditions
assumed_chronic = set(df_temp1.toPandas()["DESCRIPTION"].tolist()) # set of conditions which have no STOP dates
psudo_chronic = set(df_temp2.toPandas()["DESCRIPTION"].tolist()) # set of psudo chronic conditions
real_chronic = assumed_chronic - psudo_chronic # chronic conditions
df_chronic = pd.Series(list(chronic_conditions)) # Crearing a dataframe of chronic conditions
df_chronic.to_csv("preprocessed/conditions_chronic.csv", index=False, header=False) # writing chronic conditions to a file

####################################################################################

# ENCOUNTER #

df_temp = spark.read.csv("dataset_project_1/encounters.csv", header=True)

unique_writer(df_temp, "REASONDESCRIPTION", "eda/encounters_REASONDESCRIPTION.csv") # Unique Value Count on REASONDESCRIPTION column
unique_writer(df_temp, "DESCRIPTION", "eda/encounters_DESCRIPTION.csv") # Unique Value Count on DESCRIPTION column
unique_writer(df_temp, "ENCOUNTERCLASS", "eda/encounters_ENCOUNTERCLASS.csv") # Unique Value Count on ENCOUNTERCLASS column

count_unwanted("dataset_project_1/encounters.csv", "eda/encounters_unwanted.csv") # Unwanted Data

# Determining the ENCOUNTERCLASS and DESCRIPTION when REASONDESCRIPTION column is null
df_temp1 = df_temp.where(df_temp["REASONDESCRIPTION"].isNull()) # Filtering the dataset by null values in REASONDECRIPTION column
unique_writer(df_temp1, "DESCRIPTION", "eda/encounters_REASONDESCRIPTION_null_DESCRIPTION.csv") # Unique Value Count on DESCRIPTION column
unique_writer(df_temp1, "ENCOUNTERCLASS", "eda/encounters_REASONDESCRIPTION_null_ENCOUNTERCLASS.csv") # Unique Value Count on ENCOUNTERCLASS column

# Cross Tabulation operations
df_temp.crosstab("REASONDESCRIPTION", "ENCOUNTERCLASS").toPandas().to_csv("eda/encounters_crosstab_REASONDESCRIPTION_ENCOUNTERCLASS.csv", index=False) # REASONDESCRIPTION and ENCOUNTERCLASS
df_temp.crosstab("DESCRIPTION", "ENCOUNTERCLASS").toPandas().to_csv("eda/encounters_crosstab_DESCRIPTION_ENCOUNTERCLASS.csv", index=False) # DESCRIPTION and ENCOUNTERCLASS

# Cross Tabulation operation when on enteries where REASONDESCRIPTION is null
df_temp1 = df_temp.where(df_temp["REASONDESCRIPTION"].isNull())
df_temp1.crosstab("DESCRIPTION", "ENCOUNTERCLASS").toPandas().to_csv("eda/encounters_REASONDESCRIPTION_null_crosstab.csv", index=False)

########################################################################################################################################

# IMAGING STUDIES #

df_temp = spark.read.csv("dataset_project_1/imaging_studies.csv", header=True)

# Performing Unique Value Count
unique_writer(df_temp, "BODYSITE_DESCRIPTION", "eda/imaging_studies_BODYSITE_DESCRIPTION.csv") # BODYSITE_DESCRIPTION
# unique_writer(df_temp, "MODALITY_DESCRIPTION", "eda/imaging_studies_MODALITY_DESCRIPTION.csv") # MODATLITY_DESCRIPTION
unique_writer(df_temp, "SOP_DESCRIPTION", "eda/imaging_studies_SOP_DESCRIPTION.csv") # SOP_DESCRIPTION

# Perfoming Cross Tabulation Operation
# df_temp.crosstab("BODYSITE_DESCRIPTION", "MODALITY_DESCRIPTION").toPandas().to_csv("eda/imaging_studies_crosstab_BODYSITE_DESCRIPTION_MODALITY_DESCRIPTION.csv", index=False)
df_temp.crosstab("BODYSITE_DESCRIPTION", "SOP_DESCRIPTION").toPandas().to_csv("eda/imaging_studies_crosstab_BODYSITE_DESCRIPTION_SOP_DESCRIPTION.csv", index=False)
df_temp.crosstab("MODALITY_DESCRIPTION", "SOP_DESCRIPTION").toPandas().to_csv("eda/imaging_studies_crosstab_MODALITY_DESCRIPTION_SOP_DESCRIPTION.csv", index=False)

count_unwanted("dataset_project_1/imaging_studies.csv", "eda/imaging_studies_unwanted.csv")

###############################################################################################################################

# IMMUNIZATION #

df_temp = spark.read.csv("dataset_project_1/immunizations.csv", header=True)

# Performing Unique Value Counts
unique_writer(df_temp, "DESCRIPTION", "eda/imunization_DESCRIPTION.csv")

count_unwanted("dataset_project_1/immunizations.csv", "eda/immunization_unwanted.csv") # Unwanted Data

############################################################################

# MEDICATION #

df_temp = spark.read.csv("dataset_project_1/medications.csv", header=True)

# Unique Value Counts
unique_writer(df_temp, "DESCRIPTION", "eda/medications_DESCRIPTION.csv") # DESCRIPTION
unique_writer(df_temp, "REASONDESCRIPTION", "eda/medications_REASONDESCRIPTION.csv") # REASONDECRIPTION

# Cross Tabulation Operation
df_temp.crosstab("DESCRIPTION", "REASONDESCRIPTION").toPandas().to_csv("eda/medications_crosstab_DESCRIPTION_REASONDESCRIPTION.csv", index=False)

# Unique Values Count(filtered by null values in REASONDESCRIPTION)
df_temp1 = df_temp.where(df_temp["REASONDESCRIPTION"].isNull())
unique_writer(df_temp1, "DESCRIPTION", "eda/medications_REASONDESCRIPTION_null_DESCRIPTION.csv")

###########################################################################################

# OBSERVATION #

df_temp = spark.read.csv("dataset_project_1/observations.csv", header=True)

# Unique Value Counts
unique_writer(df_temp, "DESCRIPTION", "eda/observation_DESCRIPTION.csv")

############################################################################

# Procedures

df_temp = spark.read.csv("dataset_project_1/procedures.csv", header=True)

# Unique Value Counts
unique_writer(df_temp, "DESCRIPTION", "eda/procedures_DESCRIPTION.csv")
unique_writer(df_temp, "REASONDESCRIPTION", "eda/procedures_REASONDESCRIPTION.csv")

# Cross Tabulation Operation
df_temp.crosstab("DESCRIPTION", "REASONDESCRIPTION").toPandas().to_csv("eda/procedures_crosstab_DESCRIPTION_REASONDESCRIPTION.csv", index=False)