# bazaar-tile

Bazaar is a [Kibosh](https://github.com/cf-platform-eng/kibosh/)
experiment around dynamically managing charts. 

### Installation

* Download [bazaar-chart-0.0.4.pivotal](https://storage.googleapis.com/kibosh-public/bazaar-chart-0.0.4.pivotal)
* Upload to an Ops Manager
* Configure tile with PKS cluster creds
    - The PEM encoded Cluster CA certificate
    - K8S API endpoint
    - Cluster JWT token
* Apply changes    

### Use

* Download the latest bazaar cli from  [Kibosh releases](https://github.com/cf-platform-eng/kibosh/releases).
* Get the API user and password from the Bazaar tile credentials tab ("Bazaar API Credentials").

Managing charts:

```bash

./bazaarcli.mac offer list -t http://bazaar.$SYSTEM_DOMAIN -u admin -p 'monkey123'
./bazaarcli.mac offer save -t http://bazaar.$SYSTEM_DOMAIN -u admin -p 'monkey123' ./sample-charts/mysql-0.8.2.tgz

./bazaarcli.mac offer list -t http://bazaar.$SYSTEM_DOMAIN -u admin -p 'monkey123'

cf enable-service-access mysql
cf marketplace

./bazaarcli.mac offer delete -t http://bazaar.$SYSTEM_DOMAIN -u admin -p 'monkey123' mysql
cf marketplace
```

Be sure to visit the [Kibosh readme](https://github.com/cf-platform-eng/kibosh/blob/master/README.md) for more details, taking special note of the details on [setting up Kibosh charts](https://github.com/cf-platform-eng/kibosh#changes-required-in-chart)
