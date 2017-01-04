#EVOLUTIONARY MULTI-CRITERION OPTIMIZATION

- obj: identify approximate Pareto-optimal set for multiple objectives

##Key Issues
- how to formalize what a good Pareto set approximation
- How to use this information provided by an approximation

##4 Lessons
1. EMO provides information about a problem search space exploration)
2. EMO can help in a single obj scenarios
3. EMO is part of decision-making process
4. EMO for large n is different from n = 2

##General Scheme of dominance-based MOEA
- multi-objective evolutionary algorithms
- mating selection is stochastic
- environmental selection (greedy heuristic): problem solving heuristic of making the locally optimal choice at each stage[1] with the hope of finding a global optimum.
###Dominance
- Ranking of popilation using dominance (pareto dominant set?)
	- dominance rank: by how many individuals is an individual dominated?
	- domininace count: how many individuals does an individual dominate
	- dominance depth: at which front is an individual located
Goal: rank incomparable solutions within a dominance class
###Density information (good for search)
- rank incomparable solutions within a dominance class
- Kernel Method
* density = function of the distances
- k-th nearest neighbor
* density = function of distance to k-th neighbor
- histogram method
* density = number of elements within box

###EMO Value
- one EMO run can be more effective then aggretgation + multiple runs

###EMO helps in single objective scenarios
- "Multiobjectivatzation" - transform a single-objective problem in a multi-objective one
- solve it using MOEA
- approach 1: decompose objective function in tseveral functions
* convert constraints into objectives
* MOEA outperformed single-objective counterpart
- approcah 2: leave problem as is, but add further objective functions
* multiobjective genetic programming
* trees grow rapidly, premature convergence, overfitting of training data
* commonly dealt w/ by: constraints, penalties, objective ranking

###QUALITY OF PARETO SET APPROXIMATION
- incomparability does not give search direction
- need: total orderin of set of Pareto set approximation
- unary indicator: assign each approx real number (A)
- binary indicator: assign each approx pair a real number (A,B)

###Incorporate preferences during Search
- preference adaptive search

###Two Objectives vs N objectives
- multiple objcivest result in more incomparable solutions
- average runtime is more

###Dimensionality Reduction
- reduce objectives to make deciison-making easier

##OCTOPUS

###DEFINE
#### 1. Parameters/genes: 
- connect to multiple genePool and NumberSlider components
- octopus will explore possible values of connected sliders according to their individual range settings

####2. Parametric model/mapping:
- take input parameters and does calculations/analysis/generation

####3. Objectives/phenotypes:
- number objective values: Fitness value of a solution, min 2, max inf
- textual objectives: simple short names descrbing objective dimensions
- (optional) boolean hard constraints: boolean param to be connected. Octopus exects true value for every valid solution otherwise solution is thrown away
- (optional) 3d mesh represntation of solution can be fed into octopus for visual assessment

###SOLUTIONS VIEWER\
####Main viewport shows:
- non-dominated pareto-front (opaque cubes)
- transparent cubes (dominated solutions still belonging to the Elite
- Transparent yellow cubes elite solutions from previous generations - the more transparent the older
- Transparent yellow spherese indicate simpe marking
####Context menu
- 'reinstate solution' = resptores solution parameters
- 'mark' = adds yellow sphere around solution to keep it alive and visible
- 'Mark prefered (obj)' adds user preference at this region in the objective space: meaning weighting of objectives is aid to be preferred
- 'Toggle show mesh' toggles between cube and mesh view of single solutuon
- 'Delete' deletes the solutions

####History Slider
- scroll through the history of the search process
- all history except last geneartion can be deleted with the 'X' button
- search can be resumed from any point in history
- marking and preferences can be done in history

####PROCESS CONTROL
- 'Start' - starts process with 2 x Population size of soltuions in beginning
- 'Start w/ presets' used to incorporate slider setup currently in GH
- 'Stop' stops a search, can be resumable
- 'Reset' resets solutions

####ALGO SETTINGS
- 'Elitism' gives percentage fo new solutions that are bred out of elite instad of the entire pool, when set high more local optimization is performaed
- 'Mut. PRobability' probability each paraetmer to become mutated with the 'Mutation Rate'
- 'Mut. Rate' low mean little changes to parameter values, high meas big changes
- 'Crossover rate' probability of two subsequently generated solutions to exchange parameter values
- 'Population Size' - number of solutions per generation, total of 2 x populationsize number is number of soltuions in each generations poll
- 'Record INterval' - interval of generations in which history record is stored 
- 'Max evaluation time (ms)': if solution takes longer to compute, added to collection to debug
- 'Minim. RHino on Start' - minimizes rhino and GH to optimize screen updates (min manually as well!)
- 'Diversify Parameters' introduces additional obj dimension favors solutions different from others
- 'Record solution meshes' mesh rep stored for history solution greatly increases memory usage
- 'Display settings' = ParetoFront, Elite, Histort - determines which set to show
- hypervoluume graph: mathematical measure for spread of oslutions
- genetic distance graph: each row repsresntes paraetmer gene where corenrs of polyline rep values for parmaeters, this shows you CONVERGENCE of search
- Objectives - list of objectives and order of how they are supplioed to cotopus, can toggle on and off with use 
- COnvergence graph - one graph for each objective dimension showing upper and lower bounds of pareto front (dark greay), elite (light gray) for number of history soltuions


 










 






  