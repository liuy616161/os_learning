# bash ai agent

##  get started

### 1.

    mkdir -p $HOME/bin
    vim $HOME/bin/qwq-agent-core.sh   # 复制上面的核心脚本内容
    chmod +x $HOME/bin/qwq-agent-core.sh


### 2.
    vim $HOME/bin/ag-bash-integration.sh  # 复制上面的集成脚本内容

##### 然后添加到.bashrc
    echo "source $HOME/bin/ag-bash-integration.sh" >> ~/.bashrc

### 3.
    source ~/.bashrc


功能完全不详尽，需要后续补充