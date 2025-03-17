# QWQ AI Agent Bash 集成
# 添加到 ~/.bashrc 来启用 ag 命令

# 核心脚本路径
QWQ_AGENT_CORE="$HOME/bin/qwq-agent-core.sh"

# 历史记录
QWQ_HISTORY_FILE="$HOME/.qwq_agent_history"
touch "$QWQ_HISTORY_FILE"

# 颜色设置
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

# 直接与Bash交互的AI助手函数
ag() {
    # 不带参数时显示帮助
    if [ $# -eq 0 ]; then
        echo -e "${CYAN}QWQ AI Agent Bash 集成${NC}"
        echo -e "${BLUE}用法:${NC}"
        echo -e "  ${GREEN}ag${NC} <问题或命令> - 询问AI或执行增强命令"
        echo -e "  ${GREEN}ag exec${NC} <命令>  - 执行命令并让AI分析结果"
        echo -e "  ${GREEN}ag run${NC} <描述>   - 通过自然语言生成并执行命令"
        echo -e "  ${GREEN}ag explain${NC} <命令> - 解释命令的功能"
        echo -e "  ${GREEN}ag help${NC}         - 显示此帮助信息"
        return 0
    fi
    
    # 检查核心脚本是否存在
    if [ ! -f "$QWQ_AGENT_CORE" ]; then
        echo -e "${RED}错误: 找不到AI核心脚本: $QWQ_AGENT_CORE${NC}"
        return 1
    fi
    
    # 处理特殊命令
    case "$1" in
        help)
            echo -e "${CYAN}ly61 AI Agent Bash 集成 - 详细帮助${NC}"
            echo -e "${BLUE}==================================${NC}"
            echo -e "基础命令:"
            echo -e "  ${GREEN}ag${NC} <问题>      - 向AI提问任何问题"
            echo -e "  ${GREEN}ag explain${NC} <命令> - 解释命令的功能"
            echo -e "  ${GREEN}ag help${NC}      - 显示此帮助信息"
            echo -e ""
            echo -e "命令执行:"
            echo -e "  ${GREEN}ag exec${NC} <命令>  - 执行命令并让AI分析结果"
            echo -e "  ${GREEN}ag run${NC} <描述>   - 通过自然语言描述生成并执行命令"
            echo -e "  ${GREEN}ag sudo${NC} <描述>  - 以sudo方式执行AI生成的命令 (需谨慎!)"
            echo -e ""
            echo -e "文件操作:"
            echo -e "  ${GREEN}ag read${NC} <文件>  - 读取文件并让AI分析内容"
            echo -e "  ${GREEN}ag write${NC} <文件> <描述> - 让AI生成内容并写入文件"
            echo -e ""
            echo -e "工作流程:"
            echo -e "  ${GREEN}ag pipe${NC} <命令>  - 将命令输出传递给AI分析"
            echo -e "  ${GREEN}ag save${NC} <名称>  - 保存最后一次交互到笔记"
            echo -e "  ${GREEN}ag hist${NC}        - 显示历史记录"
            echo -e "${BLUE}==================================${NC}"
            ;;
            
        exec|execute)
            if [ -z "$2" ]; then
                echo -e "${RED}错误: 请提供要执行的命令${NC}"
                return 1
            fi
            shift
            CMD="$*"
            echo -e "${BLUE}执行命令:${NC} $CMD"
            
            # 执行命令并捕获输出
            OUTPUT=$(eval "$CMD" 2>&1)
            EXIT_CODE=$?
            
            echo -e "${YELLOW}命令输出:${NC}"
            echo "$OUTPUT"
            echo -e "${BLUE}退出代码:${NC} $EXIT_CODE"
            
            # 收集Shell上下文
            SHELL_CONTEXT="当前用户: $(whoami)\n当前目录: $(pwd)\n当前时间: $(date)\n操作系统: $(uname -a)\n命令: $CMD\n命令输出: $OUTPUT\n退出代码: $EXIT_CODE\n\n作为一名Linux专家，请分析上述命令的结果，包括解释命令的作用、对输出的解读，以及可能的后续操作建议。请直接给出分析，不要重复命令和输出内容。"
            
            # 将命令和输出传递给AI进行分析
            "$QWQ_AGENT_CORE" --shell-context "$SHELL_CONTEXT" "请分析这个命令及其输出: $CMD"
            
            # 记录到历史
            echo "时间: $(date)" >> "$QWQ_HISTORY_FILE"
            echo "命令: ag exec $CMD" >> "$QWQ_HISTORY_FILE"
            echo "输出: $OUTPUT" >> "$QWQ_HISTORY_FILE"
            echo "---" >> "$QWQ_HISTORY_FILE"
            ;;
            
        run)
            if [ -z "$2" ]; then
                echo -e "${RED}错误: 请提供命令描述${NC}"
                return 1
            fi
            shift
            DESC="$*"
            
            # 收集Shell上下文
            SHELL_CONTEXT="当前用户: $(whoami)\n当前目录: $(pwd)\n当前时间: $(date)\n操作系统: $(uname -a)\n请根据以下描述生成一条bash命令，只返回命令本身，不要包含任何解释: $DESC"
            
            # 请求AI生成命令
            echo -e "${BLUE}基于描述生成命令:${NC} $DESC"
            CMD=$("$QWQ_AGENT_CORE" --shell-context "$SHELL_CONTEXT" "$DESC")
            
            # 显示生成的命令
            echo -e "${YELLOW}生成的命令:${NC} $CMD"
            echo -n -e "${CYAN}是否执行此命令? [y/N] ${NC}"
            read -r CONFIRM
            
            if [[ "$CONFIRM" == "y" || "$CONFIRM" == "Y" ]]; then
                # 执行命令
                echo -e "${BLUE}执行命令:${NC}"
                eval "$CMD"
                EXIT_CODE=$?
                echo -e "${BLUE}退出代码:${NC} $EXIT_CODE"
            else
                echo -e "${BLUE}已取消执行${NC}"
            fi
            ;;
            
        explain)
            if [ -z "$2" ]; then
                echo -e "${RED}错误: 请提供要解释的命令${NC}"
                return 1
            fi
            shift
            CMD="$*"
            
            # 收集Shell上下文
            SHELL_CONTEXT="当前用户: $(whoami)\n当前目录: $(pwd)\n当前时间: $(date)\n操作系统: $(uname -a)\n请详细解释这个bash命令的作用: $CMD"
            
            # 请求AI解释命令
            "$QWQ_AGENT_CORE" --shell-context "$SHELL_CONTEXT" "请详细解释这个命令的功能、选项和可能的用途: $CMD"
            ;;
            
        read)
            if [ -z "$2" ]; then
                echo -e "${RED}错误: 请提供文件路径${NC}"
                return 1
            fi
            FILE="$2"
            
            if [ ! -f "$FILE" ]; then
                echo -e "${RED}错误: 文件不存在: $FILE${NC}"
                return 1
            fi
            
            # 读取文件内容
            echo -e "${BLUE}读取文件:${NC} $FILE"
            CONTENT=$(cat "$FILE")
            
            # 收集Shell上下文
            SHELL_CONTEXT="当前用户: $(whoami)\n当前目录: $(pwd)\n当前时间: $(date)\n文件路径: $FILE\n请分析这个文件内容"
            
            # 将文件内容传递给AI分析
            "$QWQ_AGENT_CORE" --shell-context "$SHELL_CONTEXT" "请分析这个文件的内容:\n\n$CONTENT"
            ;;
            
        write)
            if [ -z "$2" ] || [ -z "$3" ]; then
                echo -e "${RED}错误: 用法: ag write <文件名> <内容描述>${NC}"
                return 1
            fi
            FILE="$2"
            shift 2
            DESC="$*"
            
            # 收集Shell上下文
            SHELL_CONTEXT="当前用户: $(whoami)\n当前目录: $(pwd)\n当前时间: $(date)\n文件路径: $FILE\n请根据以下描述生成文件内容: $DESC"
            
            # 请求AI生成内容
            echo -e "${BLUE}为文件生成内容:${NC} $FILE"
            CONTENT=$("$QWQ_AGENT_CORE" --shell-context "$SHELL_CONTEXT" "请根据以下描述生成内容: $DESC")
            
            # 显示生成的内容
            echo -e "${YELLOW}生成的内容:${NC}"
            echo "$CONTENT"
            
            # 确认是否写入
            echo -n -e "${CYAN}是否保存到文件? [y/N] ${NC}"
            read -r CONFIRM
            
            if [[ "$CONFIRM" == "y" || "$CONFIRM" == "Y" ]]; then
                # 写入文件
                echo "$CONTENT" > "$FILE"
                echo -e "${GREEN}内容已保存到:${NC} $FILE"
            else
                echo -e "${BLUE}已取消保存${NC}"
            fi
            ;;
            
        pipe)
            if [ -z "$2" ]; then
                echo -e "${RED}错误: 请提供要执行的命令${NC}"
                return 1
            fi
            shift
            CMD="$*"
            
            # 执行命令并捕获输出
            echo -e "${BLUE}执行命令:${NC} $CMD"
            OUTPUT=$(eval "$CMD" 2>&1)
            EXIT_CODE=$?
            
            # 收集Shell上下文
            SHELL_CONTEXT="当前用户: $(whoami)\n当前目录: $(pwd)\n当前时间: $(date)\n命令: $CMD\n以下是命令输出，请分析这些信息:"
            
            # 将输出传递给AI分析
            "$QWQ_AGENT_CORE" --shell-context "$SHELL_CONTEXT" "$OUTPUT"
            ;;
            
        hist|history)
            # 显示历史记录
            if [ -f "$QWQ_HISTORY_FILE" ]; then
                echo -e "${BLUE}AI交互历史:${NC}"
                cat "$QWQ_HISTORY_FILE"
            else
                echo -e "${YELLOW}没有历史记录${NC}"
            fi
            ;;
            
        save)
            if [ -z "$2" ]; then
                echo -e "${RED}错误: 请提供笔记名称${NC}"
                return 1
            fi
            NAME="$2"
            FILE="$HOME/qwq_notes_${NAME}_$(date +%Y%m%d).md"
            
            # 读取最后一次交互
            LAST_INTERACTION=$(tail -n 10 "$QWQ_HISTORY_FILE" | sed -n '/---/,/---/p')
            
            # 写入笔记
            echo "# QWQ AI 笔记: $NAME" > "$FILE"
            echo "日期: $(date)" >> "$FILE"
            echo "" >> "$FILE"
            echo "## 交互内容" >> "$FILE"
            echo "```" >> "$FILE"
            echo "$LAST_INTERACTION" >> "$FILE"
            echo "```" >> "$FILE"
            
            echo -e "${GREEN}笔记已保存到:${NC} $FILE"
            ;;
            
        sudo)
            if [ -z "$2" ]; then
                echo -e "${RED}错误: 请提供命令描述${NC}"
                return 1
            fi
            shift
            DESC="$*"
            
            # 警告
            echo -e "${RED}警告: 您正在使用sudo权限执行AI生成的命令!${NC}"
            echo -e "${RED}这可能会修改系统配置或造成数据损失.${NC}"
            
            # 收集Shell上下文
            SHELL_CONTEXT="当前用户: $(whoami)\n当前目录: $(pwd)\n当前时间: $(date)\n操作系统: $(uname -a)\n请根据以下描述生成一条需要sudo权限的bash命令，只返回命令本身，不要包含任何解释: $DESC"
            
            # 请求AI生成命令
            echo -e "${BLUE}基于描述生成sudo命令:${NC} $DESC"
            CMD=$("$QWQ_AGENT_CORE" --shell-context "$SHELL_CONTEXT" "$DESC")
            
            # 显示生成的命令
            echo -e "${YELLOW}生成的sudo命令:${NC} $CMD"
            echo -n -e "${CYAN}是否执行此sudo命令? [y/N] ${NC}"
            read -r CONFIRM
            
            if [[ "$CONFIRM" == "y" || "$CONFIRM" == "Y" ]]; then
                # 再次确认
                echo -n -e "${RED}再次确认执行sudo命令? [y/N] ${NC}"
                read -r CONFIRM2
                
                if [[ "$CONFIRM2" == "y" || "$CONFIRM2" == "Y" ]]; then
                    # 执行sudo命令
                    echo -e "${BLUE}执行sudo命令:${NC}"
                    sudo bash -c "$CMD"
                    EXIT_CODE=$?
                    echo -e "${BLUE}退出代码:${NC} $EXIT_CODE"
                else
                    echo -e "${BLUE}已取消执行${NC}"
                fi
            else
                echo -e "${BLUE}已取消执行${NC}"
            fi
            ;;
            
        *)
            # 默认处理: 向AI提问
            QUERY="$*"
            SHELL_CONTEXT="当前用户: $(whoami)\n当前目录: $(pwd)\n当前时间: $(date)\n操作系统: $(uname -a)"
            
            # 将问题传递给AI
            echo -e "${YELLOW}AI思考中...${NC}"
            RESPONSE=$("$QWQ_AGENT_CORE" --shell-context "$SHELL_CONTEXT" "$QUERY")
            EXIT_CODE=$?

            # 检查命令是否执行成功
            if [ $EXIT_CODE -ne 0 ]; then
                echo -e "${RED}错误: AI请求失败${NC}"
                return 1
            fi

            # 确保输出正确显示
            echo -e "${GREEN}AI回答:${NC}"
            printf "%s\n" "$RESPONSE"

            # 更新历史
            echo "回答: $RESPONSE" >> "$QWQ_HISTORY_FILE"
            echo "---" >> "$QWQ_HISTORY_FILE"
            ;;
    esac
}

# 函数别名 - 方便访问特定功能
ag_exec() {
    ag exec "$@"
}

ag_run() {
    ag run "$@"
}

ag_read() {
    ag read "$@"
}

# 自动补全设置
_ag_complete() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    case "${prev}" in
        ag)
            opts="help exec run explain read write pipe hist save sudo"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        read|explain|write)
            COMPREPLY=( $(compgen -f ${cur}) )
            return 0
            ;;
        *)
            ;;
    esac
}

# 启用自动补全
complete -F _ag_complete ag
