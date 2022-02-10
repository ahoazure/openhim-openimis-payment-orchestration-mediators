# Dockerized OpenIMIS Payment Layer Orchestration Mediators

The code contains Python-based OpenHIM mediators created for GIZ and renamed using Jembi (https://www.jembi.org/) naming convention. Dr. Stephen Mburu is a python developers based in School of Computing and Informatics, University of Nairobi. The mediators expose FHIR R4 APIs for exchange of data between openIMIS and Mifos via openHIM.

---

# Installation Guide

This guide assumes successful installation of OpenIMIS (http://openimis.org/), OpenHIM (https://openhim.org), docker and docker-compose.

To install the dockerized instance of payment mediators, proceed as follows:
    
1. Replace default configuration vaiables in .conf/mediatorsConfig.json with your server configs
2. Run `docker-compose build`
3. Create Super User
    `docker-compose run paymentmediators python manage.py  createsuperuser`
    
4. Run `docker-compose up -d` to spin the containers in detatched mode
5. Load login page using https:baseurl/admin/ to confirn configurations are properly configured
6. Click configurations link to update server configuration variables for openIMIS, openHIM and Mifos  
7. Load openHIM console https:baseurl/ to login using credentials loaded in step 1 above
8. Confirm whether the mediators are registered with their default clients, channels and enpoints 
