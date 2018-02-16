# kibosh-sample-tile

![](resources/kibosh.png)

1. Install [tile-generator](https://github.com/cf-platform-eng/tile-generator/)
1. Build [kibosh.linux](https://github.com/cf-platform-eng/kibosh) and put the binary into the project root
    - `make linux` from the kibosh project root
1. Run `./package.sh`

The example uses [MySQL](https://github.com/kubernetes/charts/tree/master/stable/mysql) with minimal changes. MySQL service is exposed to external traffic via loadbalancer. To see the changeset,
run
```
diff src/my_charts/values.yaml =(curl -s https://raw.githubusercontent.com/kubernetes/charts/master/stable/mysql/values.yaml)
# `=(` is for zsh users; replace with `<(` if using bash
```


