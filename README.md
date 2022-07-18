# Bike Predict - Machine Learning in Python with RStudio Connect

This repository contains an example of using [pins](https://github.com/rstudio/pins), [vetiver](https://vetiver.tidymodels.org), [Shiny for Python](https://github.com/rstudio/py-shiny) to create a machine learning project in Python. Everything is deployable on [RStudio Connect](https://rstudio.com/products/connect/). 

![](img/bikeshare_python.png)

## Who This is For

1. Python data scientists who want to build machine learning projects with or without [RStudio Connect](https://rstudio.com/products/connect/).
2. People who describe *production-izing* or *deploying* content as pain points may find this helpful.
This repository is aimed for bilingual data scientists who want to utilize both and R python in their data science workflow. It can also be used as an example for bilingual data science teams (Python and R) to colloborate with open source tools like pins, vetiver, and Shiny.

### WIP

add more details on the workflow.

## What doesn't it do

TBD

## Individual Content

| Content                                   | Description                                                  | Code                                                         | Content Deployed to Connect                                  |
| ----------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| **Model** Step 1 - Train and Deploy Model | From *Content DB* get the *bike_model_data* table and then train a model. The model is saved to Connect as a pin, and then deployed to Connect as a plumber API using vetiver. | [content/02-model/01-train-and-deploy-model/document.qmd](content/02-model/01-train-and-deploy-model/document.qmd) | [Quarto document](https://colorado.rstudio.com/rsc/bike-predict-r-train-and-deploy-model/), [Pin](https://colorado.rstudio.com/rsc/bike-predict-r-pinned-model/), [Plumber API](https://colorado.rstudio.com/rsc/bike-predict-r-api/) |
| **Model** Step 2 - Model Metrics          | Use vetiver to document the model performance. Model performance metrics are calculated and then written to pin using vetiver. | [add quarto file]() | [add page from RSC](), [add model pin]() |
| **App** - Client App                      | Use the API endpoint to interactively server predictions to a shiny app.| [app/app.py](app/app.py)                                           | [Shiny app](https://colorado.rstudio.com/rsc/bike-share-python/)                                                                                                                                                              |
| **App** - Dev Client App                  | A development version of the client app.                                | [app-dev/app.py](app-dev/app.py)                                   | [Shiny app](https://colorado.rstudio.com/rsc/bike-share-python-dev/)                                                                                                                                                              |
| **App** - Content Homepage               | A page that contains links to all of the bike predict content.     | [add quarto file]()           | [add rendered Quarto document on RSC](https://colorado.rstudio.com/rsc/bike-predict-r-dashboard/)                                                                                                                                                         |

## Contributing

See a problem or want to contribute? Please refer to the [contributing page](./CONTRBUTING.md).
