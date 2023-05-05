# Flatr

Flatr is a webscraping python package developed to aid flat hunting in the UK. It provides functionality to extract the details of the latest properties posted on some of the more popular sites in the UK. For each listing the listing title, rent/month, availability and link are extracted. The listing title is composed from the number of bedrooms and the location of the flat.

## Supported sites

**Note: Webscraping on some of the supported sites is restricted. To view allowed activiteis, check `<site-url-root>/robots.txt`.**

* <a href="https://www.grantproperty.com/tenants/properties/" target="_blank">Grant Property</a>
* <a href="https://www.gumtree.com/search?search_category=property-to-rent" target="_blank">Gumtree</a>
* <a href="https://www.onthemarket.com/to-rent/property/edinburgh/" target="_blank">On The Market</a>
* <a href="https://www.rightmove.co.uk/property-to-rent" target="_blank">Rightmove</a>
* <a href="https://www.spareroom.co.uk/flatshare/" target="_blank">Spareroom</a>
* <a href="https://zonegroup.co.uk/search-property/rent" target="_blank">Zoneletting</a>
* <a href="https://www.zoopla.co.uk/to-rent/" target="_blank">(Zoopla)</a>

## Usage

**Note: Given the restrictions of the supported sites, the package was developed for personal use only and not meant to cause harm or distrupt the operation of the sites. Please make sure to not spam the sites with requests (used in the package to retrieve data). Checking for new flats every 5 minutes or so should be sufficient in most cases.**

### Getting started

Make sure to have `Python 3.8 or higher` installed on your machine or the environment you are using.

```console
// Clone this repository
git clone https://github.com/MarioMihaly/flatr.git
// Change directory
cd flatr
// Install the flatr package
pip install .
```

If you wish to continue developemnt, install the `development requirements`. This way the `flatr` package is installed using the `editable` flag with `pip`.

```console
// Clone this repository
git clone https://github.com/MarioMihaly/flatr.git
// Change directory
cd flatr
// Install requirements for development
pip install -r requirements_dev.txt
```

To check installation, open a `Python interactive session` in a terminal and run the following code. You should see the details of the most recent listings of the site printed.

```python
from flatr.sites import Gumtree

link = 'https://www.gumtree.com/search?search_category=property-to-rent'
listings = Gumtree(link).get_listings()

for listing in listings:
    print(f'{listing}\n')
```

### Adding custom `sites`

Custom sites can be added using [this template](./templates/site_temp.py). Replace `ClassName` with your custom site's name and add it to the [sites directory](./src/flatr/sites/). Edit the [\_\_init\_\_.py](./src/flatr/sites/__init__.py) file in the same directory to allow access to your custom site in the package. If you installed the package for development, you should be able to access your custom site just like any other.

## Example application

**Note: The provided example is for personal usage only.**

The example provided in the [examples folder](./examples/) is an adaption of my original script ran on a `Linux VM` every 5 minutes to find new flats, save them in a `Google Sheet` for later reference and send an email with the new flats.

The script allowed the review of over `1200` listings over a period of 1 month with minimal effort.
