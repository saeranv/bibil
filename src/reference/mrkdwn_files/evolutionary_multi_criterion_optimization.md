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
- transfparent cubes (dominated solutions still belonging to the Elite
- Transparent yellow cubes elite solutions from previous generations - the more transparent the older
- Transparent yellow spherese indicate simpe marking
####Context menu
- 'reinstate solution' = resptores solution parameters
- 'mark' = adds yellow sphere around solution to keep it alive and visible
- 'totally different parameters of two solutions' = 

 






  