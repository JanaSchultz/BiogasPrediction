# Model code - continuous anaerobic digestion

### Related publications
The code published via this directory is a model for predicting continuous anerobic digestion processes based on feedstock charactersitcs. It contains the code which was used for modeling in the publication "Long-term continuous anaerobic co-digestion of residual biomass – Model validation and model-based investigation of different carbon-to-nitrogen ratios" [1]. It is an adapted version of the model code by Scherzinger et al. [2]. It is strongly recommended to get familiar with both publications prior to using the model. 

### Model description 
The presented model can be used for predicting the biogas production of fermenters given a set of input parameters is known. The model will calculate the expercted biogas and biomethane production when operating a fermenter with the given operating parameters and substrate charactersitcs.
Scherzinger et al. [2] developed and published this model that uses simple means to check the viability of the proposed substrate mix and predict the respective biogas yield in a continuous biogas production process. Their model is characterized by an easy approach using the degradation kinetics of the substrates determined via batch experiments. It checks for an appropriate C/N ratio and takes some framework conditions (e.g., the maximum organic loading rate) into account. Because it uses basic characteristics, it is easily transferable and adaptable for a large share of substrates. The proposed model has been validated by continuous anaerobic digestion experiments by Schultz et al. [1]. The conducted model validation was regarded as valid for favorable framework conditions - in terms of feedstock C/N ratio, but showed improper prediction at C/N ratios exceeding the defined limit of 35. Seen from another angle, the model (or more precisely, the deviation from the model's prediction) can indicate a process inhibition at an early stage, which could enable rapid intervention in practice. To make use of this feature, Schultz et al. [1] suggested a rRMSE of >10% between predicted and actual biogas production as a threshold for intervention.  
For a detailed description and understanding users are referred to the original prublications.

### Structure of the code
Currently, the model is designed to predict the biogas production of a defined substrate mixture based on the data stored in a csv file. In the code, a change in substrate is implemented. The provided code consists of 3 substrate changes, hence 4 different substrate mixtures which themselves may be composed of different substrates.
The model code consists roughly of the following: 
1. Input data
the input data section needs to be costomized according to your needs. These parameters are the representation of your reactor and you have to adujst those to your needs. The model will calcualte the absolute biogas production of your reactor, hence the parameters given as input here will largely impact your modeling result. Here you will also import the database of substrates. Either choose to add your own substrates to the database or choose substrates already given in the input. Make yourself familiar with the structure of the data base prior to using the model.
2. Input processing
The model will then process the given input, prepare the features of your substrate mixture and save certain characteristics in lists or vectors. It also calcualtes the volume flow of the reactor
3. Biogas production of mixtures
The model function is defined (Gompertz function). The cumulative biogas production of each substrate mixture is then calculated based on the biogas production of the individual substrates contained in the mixture and their respective shares.
At the moment 4 different substrate mixtures are implemented. If you dont want to change the substrate, you can simply set tc1...tc3 = tm. Of course you can also implement more changes by yourself. 
4. Mix 1...4: check, characteristics, BGP
For each mix, the model will then perform the following: it prints a check up report (see model output), calculates features of the substrate mixture (such as water content etc.), the amount of feedstock you have to feed every day, the water that you need to add, water that you can recover and feed back to the system. 
The biogas production is calculated as follows: under 3. the biogas production of the substrate mixture was calculated. The model will calculate the daily production over the time (time frame of the model is defined in the input (tm, tc1,tc2, tc3)) based on the feeding regime (semi continuous feeding with one fed portion per day). It can also predict the methane production. 
5. Biogas production of reactor
In this section the total biogas production over time considering the entire time span tm of the model is calculated by adding the time spans for mix 1...4 together.
6. Saving data
Saves the modeling result in a csv file as well as a plot of the modeling result into the folder 'output'


### Requirements to use the model
There are three different application senarios which come with different requirements: 
1. Checking out the model
you can use the given data base and play with the input variables to explore the functioning of the model without any fruther requirements. 
2. Modeling based on literature
If you have a specific use case in mind but do not have the chance to aquire lab data you may base your modeling activity on literature. The required parameters are defined unter Model input below.
3. Modeling based in lab data
If you have the chance to aquire the data needed (susbtrate charactersitics), then you can customize the model to your very specific needs. The required parameters are defined unter Model input below.

### Model input
The model can be costumized in a way so that it will predict the biogas production of a defined use case. Here we present the parameters that can and have to be adapted to your individual application.

#### Reactor and modeling parameters
The following parameters have to be set under ### 1. Input data:

| **Abbreviation**  | **Parameter**  | **Comment**  | **unit**  |
| :------------ | :------------ | :------------ | :------------ |
| VF  | Fermenter volume  |   | m^3  |
| HRT1...HRT4  | Hydraulic residence time | The hydraulic residence time can be constumized for each substrate mixture given to the reactor   | d  |
| tm  | Time span of model  | time span of the entire model: How long do you want to model the biogas production?  | d  |
| tc1...tc3  | day of substrate mixture change  | On which day do you want to change the substrates given to the reactor?  | d |
| BR  | Organic loading rate | recommended be between 1.5 and 3.5 kgVS/m^3/d  | kgVS/m^3/d  |
| Substrates1...Substrates4  | Short names of Substrates in the Mix1...Mix4  | Those need to be defined in the database (description below)  |   |
| ShareSubstrates1...ShareSubstrates4  | Shares of substrates to bi used in Mix1...Mix4  | need to sum up to 1  |   |

#### Data base import
The model relies on the kinetic parameters of anaerobic degradation of the substrates to be used within the substrate mixture. These parameters have to be determined by conducting batch experiments and fitting the Modified Gompertz Model to the data (for further infromation consolidate [1]). In order to fully exploit the models ability to predict your process, it is resommended to add the characteristics of your substrates to be used to the data bank. Therefore, the parameters listed below need to be determined via lab experiments. If the substrate characteristics are unknown you can choose substrates from our data base or consultate literature. However, in this case the predictions can only be seen as a rough estimation since natural substrate charactersitics may largely diviate.

The data base consists of: 
- a *describtion* of the substrate (Type of substrate and region)
- a *short* name 
- the water content *WC* of the substrate
- the volatile solids content *VS* of the substrate
- the experimentally determined kinetic degradation parameters of the Modified Gompertz Model (*P*, *Rm*, *l* (lambda)) of the substrate
- the carbon content *C* of the substrate
- the nitrogen content *N* of the substrate
- the *methane* content of the produced biogas

### Model output
The output folder contains:
- a .csv file with the predicted biogas production 
- a .png file plotting the predicted biogas production

Within your programming environment, the model will print some informations regading the modeling procedure:
- firstly, it prints an overview of all inforamtion given as input. Here, you can verify wheather you have given the correct inputs to your model, e.g., the volume, hydraulic retention time, modelling time spann, substrate change and organic loading rate, as well as the composition of each substrate mixture.

>The biogas production is modeled for:
 a fermenter with a volume of 0.0055 m^3,
 a hydraulic retention time of 25 days,
 a time span of 292 days, and
 a substrace change after 167, 192 and 242 days.
 The organic loading rate is set to 3 kgVS/m^3/d.
The following Substrates are used in Mix 1:
 25.0 % S_R_As
 25.0 % L_P_As
 50.0 % GD
The following Substrates are used in Mix 2:
 25.0 % S_R_Ca
 25.0 % G_P_As
 50.0 % GD
The following Substrates are used in Mix 3:
 40.0 % S_R_Ca
 40.0 % G_P_As
 20.0 % GD
The following Substrates are used in Mix 4:
 50.0 % S_R_Ca
 50.0 % G_P_As
 0.0 % GD

- for each substrate mixture, the program will also print a summary of the process check up and the modeling results, this information should look like: 

> Mix 1

> ✓ Input 1 is correct.
✓ The Loading Rate per Unit Volume of 3.00 lies in the optimum range.
✓ C/N - Ratio (32.97) is in the optimum range
The amount of substrate to be fed daily is 23.08 g FM.
You have to add 196.92 mL water to substrate mix initially.
✓ Water content of the mashed substrate of 90.30 % lies in the optimum range.
175.57 mL water can be recovered per day.
Each day, an amount of 19.62 g water must be supplied externally.
The expected biogas production is 4.34 L per day

### Packages & Versions
The code uses the following packages under the specified version.
| Package  | Version  |
| :------------ | :------------ |
| numpy | 2.2.4  |
| pandas  | 2.2.3  |
| matplotlib  | 3.10.0  |
| scipy  | 1.15.1  |

### References
[1] 
[2] Scherzinger, M., Kaltschmitt, M., & Elbanhawy, A. Y. (2022). Anaerobic biogas formation from crops’ agricultural residues–Modeling investigations. Bioresource technology, 359, 127497.  https://doi.org/10.1016/j.biortech.2022.127497.

### Licence
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/ "CC BY-SA 4.0")

### Authors
