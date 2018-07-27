# bazaar-tile

Bazaar is a [Kibosh](https://github.com/cf-platform-eng/kibosh/)
experiment around dynamically managing charts. 

### Installation

* Download [bazaar-chart-0.0.3.pivotal](https://storage.googleapis.com/kibosh-public/bazaar-chart-0.0.3.pivotal)
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
./bazaarcli.mac -t http://bazaar.$SYSTEM_DOMAIN -u admin -p 'monkey123' list
./bazaarcli.mac -t http://bazaar.$SYSTEM_DOMAIN -u admin -p 'monkey123' save ~/workspace/kibosh-sample/sample-charts/mysql-0.8.2.tgz

./bazaarcli.mac -t http://bazaar.$SYSTEM_DOMAIN -u admin -p 'monkey123' list

cf enable-service-access mysql
cf marketplace

./bazaarcli.mac -t http://bazaar.$SYSTEM_DOMAIN -u admin -p 'monkey123' delete mysql
cf marketplace
```
