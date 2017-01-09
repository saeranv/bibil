src: https://dspace.mit.edu/handle/1721.1/99261?show=full C.Mackey thesis

####HUMAN COMFORT METRICS
- two main models
- 1) comfort science viewpoint that thermal comfort tied to physical laws that govern human's energy balance
- Predicted Mean Vote (PMV)
- 2) comfort is complex based on physical and social: tests occupants in building occupants within their daily routine and in settings of passive energy
- uses statistical correlations across thousands of surveys to arrive at guidelines for what physical variables are acceptalbe and level of <b>adaptive freedom</b> given to occupants
- PMV is poor estimator of comfort in many cases vs adaptive model in which thermally diverse environment is preferred

####COMPUTATIONAL METHODS
- existing state of the art in energy modeling/comfort:
  - run energy model and output heating/cooling load and compare output to previous METHODS
  - comfort is checked by taking temperature and humidity outputs of model, recorded at center of room, run through PMV model, then extrapolate from single point comfort
  - assumption holds true in case of conditioned spaces where many diffusers and fans included in HVAC mix air well enough
  - Chris' criticism: expend energy/arch space implementing fans, diffusers and ducts extend deep into space to make built form match abstract comfort/energy model, vs robust comfort/energy model that can handle complexity of human behaviour and bldg physics to create simpler, well-desinged building
  - for ex. not sowrk to test passive building operating off adaptive behavour of occupants
    1. Complete passive bldg has no heating/cooling system - impossible to evaluate effect of given design using heating/cooling values
    2. Passive buildings does not include diffusers/fans to enable well-mixed air
    3. Not all spaces will be comfortable all the time
  - soln = reverse traditional energy modeling process:
    - instead of run strategy through model and see heating/cooling values change, with comfort constant
    - see energy remain constant/nonexistent and see effect of given design move spatially in form of a thermal map with areas made warmer/cooler by the given strategy
    - propose: create multi ppoint high resolution thermal map

  1. Operative temperature (To)- usual metric adaptive comfort is measured: average of radiant and air temperature experienced by person
    - air temp = average air temperuater
    - radiant temp = net heat gain/loss in home (i.e can feel warm in sun even though air temp is cold)
    - averaging comes from the fact that human beings tend to lose 1/2 body heat by radiating it and other half through air-related factors (temp and humidity)
  2. Thermal comfort percentage: builds of Rakha (2015) outdoor thermal comfort
    - refers to % of time that given point in space lies inside adaptive comfort range
  3. Adaptive comfort (AC)
    - degree temp delta above/below netural temp for point in space/time
    - assembled from: surface temp, air temp, solar radiation, air stratification
