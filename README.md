# Bike Predict - Machine Learning in Python with RStudio Connect

This repository contains an example of using [pins](https://github.com/rstudio/pins), [vetiver](https://vetiver.tidymodels.org), [Shiny for Python](https://shiny.rstudio.com/py/) to create a machine learning project in Python. Everything is deployable on [RStudio Connect](https://rstudio.com/products/connect/). 

![](img/bikeshare_python.png)

## Who This is For

1. Python data scientists who want to build machine learning projects with existing interoperable data assets from R processes scheduled to run on [RStudio Connect](https://rstudio.com/products/connect/).
2. Multilingual data scientists who want to utilize both R and Python in their data science workflow. It can also be used as an example for multilingual data science teams to colloborate with open source tools like pins, vetiver, and Shiny.

## Individual Content

| Content                                   | Description                                                  | Code                                                         | Content Deployed to Connect (not public yet)                                  |
| ----------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| **Model** - Train and Deploy Model | From *Content DB* get the *bike_model_data* table and then train a model. The model is saved to Connect as a pin, and then deployed to Connect as a plumber API using vetiver. | [model/01-train-and-deploy-model/model_training_deployment.ipynb](model/01-train-and-deploy-model/model_training_deployment.ipynb) | [Jupyter Notebook](https://colorado.rstudio.com/rsc/bikeshare-model-retraining/), [Pin](https://colorado.rstudio.com/rsc/bikeshare-rf-model-python-pin/), [Vetiver API](https://colorado.rstudio.com/rsc/new-bikeshare-model/) |
| **App** - Client App                      | Use the API endpoint to interactively serve predictions to a shiny app.| [app/app.py](app/app.py)                                           | [Shiny app](https://colorado.rstudio.com/rsc/bike-share-python-app/)                                                                                                                                                              |
| **App** - Dev Client App                  | A development version of the client app.                                | [app-dev/app.py](app-dev/app.py)                                   | [Shiny app](https://colorado.rstudio.com/rsc/bike-share-python-dev/)                                                                                                                                                              |

## Contributing

See a problem or want to contribute? Please refer to the [contributing page](./CONTRBUTING.md).
