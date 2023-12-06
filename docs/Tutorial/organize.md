# First step: organizing your data

This step is not necessary, as you can customize a your pipeline `extract` method as much as you need. However, in order to simplify this, entropic works best with a nested structure, which we'll explain further in this page.

For this tutorial we'll be building a data pipeline for a kinematic experiment involving data for position, velocity and time.

## Understanding `Iteration` and `Sample`
Entropic's `Iteration` and `Sample` are deeply connected with an experiment. Broadly speaking they refer to:

* An `Iteration` represents a fixed set of initial conditions for which you make at least one run.
* Each of this runs would represent a `Sample`, which have at least one measurement.

In our case, lets say we have a incline plane experiment in which a ball is dropped from the top, and position in the $x$ and $y$ axis. Three sets of initial conditions were recorded: with the plane at $30^o$, $45^o$ and at $60^o$. For each initial condition two measurements were done, one for the $x$ axis and one for the $y$ axis, and each measurement was repeated three times. This would be thought of as three iterations, each with three samples (one for each repetition), and each repetition having two data sources, one for the $x$ axis and one for the $y$ axis. The ideal file structure would the be:
```
results/
|-- thirty_degrees
|   |-- sample1
|   |   |-- x_axis_data.csv
|   |   `-- y_axis_data.csv
|   |-- sample2
|   |   |-- x_axis_data.csv
|   |   `-- y_axis_data.csv
|   `-- sample3
|   |   |-- x_axis_data.csv
|   |   `-- y_axis_data.csv
|-- forty_five_degrees
|   |-- sample1
|   |   |-- x_axis_data.csv
|   |   `-- y_axis_data.csv
|   |-- sample2
|   |   |-- x_axis_data.csv
|   |   `-- y_axis_data.csv
|   `-- sample3
|   |   |-- x_axis_data.csv
|   |   `-- y_axis_data.csv
`-- sixty_degrees
    |-- sample1
    |   |-- x_axis_data.csv
    |   `-- y_axis_data.csv
    |-- sample2
    |   |-- x_axis_data.csv
    |   `-- y_axis_data.csv
    `-- sample3
        |-- x_axis_data.csv
        `-- y_axis_data.csv
```
