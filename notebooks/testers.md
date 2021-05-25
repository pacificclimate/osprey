# Welcome Testers

Thank you for helping us test `Osprey`, we appreciate it! By now you should have received a username/password combination that will give you access to the [PCIC-DACCS Jupyter Hub](https://docker-dev03.pcic.uvic.ca/jupyter/hub/login). In this hub you can create private notebooks that will persist with your account. Below are some instructions to help you get oriented.

## Creating a Notebook

Once you have logged in you will be prompted with a "Launcher" tab (if there is no prompt use the `+` in the top right corner to open a new tab). It is recommended that you use the `birdy` notebook as it has some important items pre-installed.

## Using the Bird

We have a number of demonstration notebooks available [here](https://github.com/pacificclimate/osprey/tree/master/notebooks/tests). Each will detail how to use the different processes available in `Osprey` and how to use it. In general though, you just need the bird `url` and that will allow you to connect to the bird:
```
osprey = WPSClient(url="https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/osprey/wps")
```

If you anticipate your request may take a long time, you can use the bird in asynchronous mode:
```
osprey = WPSClient(url="https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/osprey/wps", progress=True)
```

## Reporting Feedback

It is preferred that feedback is reported directly on the [github page](https://github.com/pacificclimate/osprey/issues). If this is not possible please send feedback in an email to nrados@uvic.ca.