#!/bin/bash

# 通义 QWQ-32B API Agent - 核心组件
# 日期：2025-03-15

# 配置文件路径
CONFIG_FILE="$HOME/.qwq_agent_config"

# 加载配置
if [[ -f "$CONFIG_FILE" ]]; then
    source "$CONFIG_FILE"
else
    echo "首次运行设置"
    echo "请输入您的通义 QWQ-32B API 密钥 (DashScope API Key):"
    read -r API_KEY
    
    echo "API_KEY=\"$API_KEY\"" > "$CONFIG_FILE"
    echo "API_URL=\"https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions\"" >> "$CONFIG_FILE"
    echo "MODEL=\"qwq-32b\"" >> "$CONFIG_FILE"
    
    chmod 600 "$CONFIG_FILE"
    source "$CONFIG_FILE"
    
    echo "配置已保存"
fi

# 替换核心AI脚本中的query_ai函数
query_ai() {
    local prompt="$1"
    local system_msg="$2"
    local temp_file=$(mktemp)
    local output_file=$(mktemp)
    
    # 默认系统消息
    if [[ -z "$system_msg" ]]; then
        system_msg="你是一个在bash环境中运行的AI助手，可以通过'ag'命令调用。当前用户是liuy616161，当前时间是$(date '+%Y-%m-%d %H:%M:%S')，请尽量简洁、实用地回答问题。"
    fi
    
    # 转义引号和特殊字符
    prompt=$(echo "$prompt" | sed 's/"/\\"/g' | sed 's/\\/\\\\/g')
    system_msg=$(echo "$system_msg" | sed 's/"/\\"/g' | sed 's/\\/\\\\/g')
    
    # 构建请求体 - 包含系统消息
    local data="{\"model\": \"$MODEL\", \"messages\": [{\"role\": \"system\", \"content\": \"$system_msg\"}, {\"role\": \"user\", \"content\": \"$prompt\"}], \"stream\": true}"
    
    # 发送请求
    echo "AI思考中..."
    curl -s -X POST "$API_URL" \
         -H "Authorization: Bearer $API_KEY" \
         -H "Content-Type: application/json" \
         -d "$data" > "$temp_file"
         
    # 处理响应
    echo "AI回答:"
    local content=""
    
    # 使用更安全可靠的方式处理输出
    while IFS= read -r line; do
        [[ -z "$line" ]] && continue
        line=${line#data: }
        [[ "$line" == "[DONE]" ]] && break
        
        if echo "$line" | grep -q '{"choices"'; then
            # 提取内容更可靠的方法
            local chunk=$(echo "$line" | grep -o '"content":"[^"]*"' | cut -d'"' -f4)
            if [[ -n "$chunk" && "$chunk" != "null" ]]; then
                printf "%s" "$chunk" | tee -a "$output_file"
            fi
        fi
    done < "$temp_file"
    
    printf "\n"
    
    # 读取完整输出
    content=$(cat "$output_file")
    
    # 清理临时文件
    rm -f "$temp_file" "$output_file"
    
    # 返回结果
    echo "$content"
}

# 执行程序
if [[ "$1" == "--query" ]]; then
    shift
    PROMPT="$*"
    query_ai "$PROMPT"
elif [[ "$1" == "--shell-context" ]]; then
    shift
    CONTEXT="$1"
    shift
    PROMPT="$*"
    query_ai "$PROMPT" "$CONTEXT"
else
    echo "用法: $0 --query <问题文本>"
    echo "  或: $0 --shell-context <上下文信息> <问题文本>"
fi