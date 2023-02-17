# Forest Conservation Evaluation Tool (FCET)

The FCET is a web tool that aids the evaluation of forest conservation policy. The tool can be accessed online at https://fcet.servirglobal.net and stored on a NASA server as a CapRover application. Troubleshooting is best done by looking at deployment and application logs in the CapRover admin interface. and operates using a web tier and database tier. The web application itself is built using using HTML, CSS, and JavaScript on the front-end to render a page that users can see. We use several JavaScript libraries to help render the page. For the overall page, we use ExtJS 4.2. To enable GIS controls on the page we use Openlayers. To get map tiles we use either the Google Maps API or MapBox.

## Overview

The web application has a database and back-end to perform analytical operations and keep track of user sessions. The application layer is written in Python using the back-end framework, Django. The best way to understand the major features of the application layer is to read a Django tutorial. 

We access a single database running on PostgreSQL from the application. There is a second server in the application layer, Geoserver running on Apache Tomcat. This is our mapserver that renders map tiles and sends them to the client. Our maptiles are not static images and change frequently based on user actions. Geoserver reads geospatial data from the database and renders maptiles based on this data.

The front-end and back-end communicate using an adhoc RPC-like API.

## Front-end: JavaScript Single Page App 

The JavaScript files that are served to the front-end can be found in Evaluator/templates/app. The most relevant code can be found under Evaluator/templates/views. The files correspond to individual menu components on the rendered page. Views is a misnomer because these files also contain models and logic. Even though ExtJS is an MVC framework, there is little reliance on the built-in MVC features. 

The major menu sections are:

- Define Study Area
- Define Outcome Period
- Limit Point Types
- Select Treatment Points
- Select Control Points
- Select Matched Control Points
- Check Balance Statistics
- View Results
- Check Sensitivity
- Download Report

We maintain sessions using cookies, but there are no true user accounts.

## Database: PostgreSQL 

The username and password can be found in the Evaluator settings file. The best way to find the table schemas is to look at the models.py files of each application. We have several extensions installed:

-postgis
-postgis_topology
-fuzzystrmatch
-postgis_tiger_geocoder
-hstore

The database configuration is sensitive since the analytical workload can be quite heavy.

## Back-end: Django

A Django project is composed of several applications. In this project custom applications can be found in `/Evaluator`. They are:

- **Evaluator**: Handles overall application settings and initial routing.
- **first_page**: Handles proxying request to geoserver and static content.
- **jobs**: Handles the running and storage of statistical matching routines.
- **layers**: Handles the storage and creation of map layers and their data.
- **map**: Handles user iteractions with the main map interface.
- **PSM**: A module to perform propensity score matching.
- **regions**: Handles geospatial area designations.
- **tables**: Uses job data to report analytics about the job performed.
- **upload**: Handles user file uploads which are always shapefiles.

Inside each application there are the following Python files:

- `urls.py`: Exposes TCP endpoints to call functionality.
- `view.py`: The presentation end of what a response to a request looks like. Typically JSON.
- `services.py`: The logic and helper functions needed to manipulate application data.
- `models.py`: Data models that are used to create schemas in the database and defined objects maniulated in services.

You will also see the following folders:

- Data: Any data in the form of a shapefile that needs to be dissolved into the database for the app to run.
- Management: Useful Python scripts to automate tasks when working with the applications.

Common commands are:

- To precalculate region lookups (current stored in the database so does not need to be run): 

```$ python manage.py warmcache```

- To load in new regions: 

```$ python manage.py load_region [polygon shapefile location in EPSG:4326]```

- To load in new point feature to fill a region: 

```$ python manage.py upload_features [point shapefile location] [number of points to load; None for all points]```

As well as other common Django commands.

> Regions and points are not directly associated. Instead we find all points that fall within a regional designation on request. This is precalculated as it takes a few minutes to find all needed points. 

> All database tables are automatically created and follow the same naming convention that can be infered from the application models.
  
### Evaluator

Handles overall application settings and initial routing. 
In this location we specify where all other apps reside. We also specify where to find and how to connect to the database and cache. The specifics of the settings can be found in the online Django documentation. There is an Evaluator.wsgi file that is needed to run the application. This is read by Gunicorn.

### first_page

Handles proxying request to geoserver and static content. As a backup the application layer can serve the JavaScript files, but this should be handled by Nginx. There are two request types that are proxied through the application serves and passed through to Geoserver. We modify these two requests in order to make them compatible with other maptiles and allow PDF printing.    

### jobs

Handles the running and storage of statistical matching routines. We only store the results and metadata of the run. This is highly aggregated information and takes little space.

### layers

The layer management is probably the most complicated part of the application. The layers data schema imitates a shapefile. We store features in one table, we store attribute metadata in another table, and we store actual attributes in another table. All point feature shapefiles are dissolved into this format.

Geoserver is then able to read the feature table to render the points as needed. The attributes are stored
as an Entity Attribute Value schema. This is from a legacy requirement that forced the schema to be flexible.

There is one more complexity in rendering maptiles and retrieves the appropriate features. Since this is a central store, all users will retrieve a subset of this store. Writing 50k points for every user would be far too slow so we use Hstore, a PostgreSQL key-value store to record which points a user has selected. 

Geoserver has no way to access an outside key-value store, but by using hstore we can join a key-value store to our features table and allow Geoserver to quickly render the result. 

### map

Handles user iteractions with the main map interface. Most user requests go through this application. We also keep the print PDF functionality here.For the most part this is simple logic code, but there is a lot of it.

### PSM

A module to perform propensity score matching. Unfortunately, there *is* no library to perform Propensity Score Matching in Python. So we made our own. The performance is comparable to STATA and we can complete a match in less than a second. From the user perspective, matches feel slower because most of the time is spent loading data. We considered using a routine from R, but the most well known routines used O(n^2) algorithms and ran too slowly.

### regions

Handles geospatial area designations. We use country and state regions to allow the users to select a working space rather than attempting to render all 10 million at once. This application handles the loading of regions into the database so that they can be read by geoserver. They are also made known to the rest of the application to allow modification of the correct menus.

### tables

Uses job data to report analytics about the job performed. The tables are based on the results from a Propensity Score Matching run. Overall these are simple to build and amount to converting database enteries to JSON.

### upload

Handles user file uploads which are always shapefiles. In some interactions users upload shapefiles, we automatically reproject these to EPSG:4326. The shapefile itself is stored on disk and the file location is stored in the database.
