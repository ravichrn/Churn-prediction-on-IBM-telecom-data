PROC IMPORT OUT= WORK.churn 
            DATAFILE= "H:\Datasets\IBM-Telco-Customer-Churn.xlsx" 
            DBMS=EXCEL REPLACE;
     RANGE="'IBM-Telco-Customer-Churn$'"; 
     GETNAMES=YES;
     MIXED=NO;
     SCANTEXT=YES;
     USEDATE=YES;
     SCANTIME=YES;
RUN;
proc print data=WORK.churn(obs=10);run;
proc contents;run;
proc freq;table gender Partner Dependents PhoneService MultipleLines InternetService OnlineSecurity OnlineBackup DeviceProtection TechSupport StreamingTV StreamingMovies Contract PaperlessBilling PaymentMethod Churn;run;

libname q1 'h:\Datasets';
data q1.churn;
set WORK.churn;run;

/*Encoding Categorical Varibales*/
data q1.churn_en(drop = gender Partner Dependents PhoneService MultipleLines InternetService OnlineSecurity OnlineBackup DeviceProtection TechSupport StreamingTV StreamingMovies Contract PaperlessBilling PaymentMethod Churn);
set q1.churn;
if gender = 'Male' then genderEn = 1;else genderEn = 0;
if Partner = 'Yes' then PartnerEn = 1;else PartnerEn = 0;
if Dependents = 'Yes' then DependentsEn = 1;else DependentsEn = 0;
if PhoneService = 'Yes' then PhoneServiceEn = 1;else PhoneServiceEn = 0;
if MultipleLines='Yes' then MultipleLinesEn=1;else MultipleLinesEn=0;
if InternetService='DSL' or InternetService='Fiber optic' then InternetServiceEn=1;else InternetServiceEn=0;
if OnlineSecurity='No' or OnlineSecurity='No internet service' then OnlineSecurityEn=0; else OnlineSecurityEn=1;
if OnlineBackup='No' or OnlineBackup='No internet service' then OnlineBackupEn=0;else OnlineBackupEn=1;
if DeviceProtection='No' or DeviceProtection='No internet service' then DeviceProtectionEn=0;else DeviceProtectionEn=1;
if TechSupport='No' or TechSupport='No internet service' then TechSupportEn=0;else TechSupportEn=1;
if StreamingTV='No' or StreamingTV='No internet service' then StreamingTVEn=0;else StreamingTVEn=1;
if StreamingMovies='No' or StreamingMovies='No internet service' then StreamingMoviesEn=0;else StreamingMoviesEn=1;
if Contract = 'Month-to-month' then ContractEn = 1; else if Contract = 'One year' then ContractEn = 2;else if Contract = 'Two year' then ContractEn = 3;
if PaperlessBilling='Yes' then PaperlessBillingEn=1;else PaperlessBillingEn=0;
if PaymentMethod='Bank transfer (automatic)' then PaymentEn=1; else if PaymentMethod='Credit card (automatic)' then PaymentEn=2;else if PaymentMethod='Electronic check' then PaymentEn=3;else if PaymentMethod='Mailed check' then PaymentEn=4;
if Churn='Yes' then ChurnEn=1;else ChurnEn=0;
run;

proc print data=q1.churn_en(obs=10);run;

proc contents data=q1.churn_en;run;

/*Creating separate datasets for Churn and Non-Churn*/
data WORK.churn_y(drop = CustomerID);set q1.churn_en;
if ChurnEn = 1;run;
data WORK.churn_n(drop = CustomerID);set q1.churn_en;
if ChurnEn = 0;run;

proc means data=WORK.churn_y mean;
output out = WORK.churn_ym mean= /autoname;
run;

proc means data=WORK.churn_n mean;
output out = WORK.churn_nm mean= /autoname;
run;

data WORK.churn_meanDiff (drop = _TYPE_ _FREQ_);
set WORK.churn_ym WORK.churn_nm;
run;

proc transpose data = WORK.churn_meanDiff out=WORK.chMean_trans;run;

data WORK.perChange;set WORK.chMean_trans(rename =(COL1 = yes COL2 = no));
perChng = abs(((yes - no)/no)*100);run;

proc sort data=WORK.perChange out=q1.chDiff_sorted;by descending perChng;run;
proc print data=q1.chDiff_sorted;run;
/*The top 10 variables to be used for the analysis*/

/*Check for correlation between the variables*/
proc corr data=q1.churn_en;run;

/*Check for multicollinearity*/
proc model data=q1.churn_en;
parms b0 b1 b2 b3 b4 b5 b6 b7 b8 b9 b10;
ChurnEn = b0+b1*SeniorCitizen+b2*ContractEn+b3*MonthlyCharges+b4*OnlineSecurityEn+b5*PaperlessBillingEn+b6*TechSupportEn+b7*DependentsEn+b8*PaymentEn+b9*tenure+b10*PhoneServiceEn;
fit ChurnEn/White;run;

/*Logistic Model*/
proc logistic data=q1.churn outmodel=train_out descending;
class OnlineSecurity TechSupport Dependents PaperlessBilling Contract PaymentMethod PhoneService;
model Churn = SeniorCitizen OnlineSecurity TechSupport Dependents MonthlyCharges PaperlessBilling Contract PaymentMethod PhoneService tenure/expb;
run;

/*Prediction using SCORE*/
PROC LOGISTIC INMODEL=train_out;
SCORE DATA=q1.churn OUT=churn_predicted FITSTAT;
RUN;

proc print data=churn_predicted(obs=10);run;

data churn_predicted;set churn_predicted;
if Churn = I_Churn then prediction = 1; else prediction = 0;run;

proc sql;
select AVG(prediction)*100 as hit_ratio
from churn_predicted
quit;
