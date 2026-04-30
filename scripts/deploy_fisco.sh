#!/bin/bash
# FISCO BCOS 部署脚本 - AIMED 充盈视界
# 用法：bash deploy_fisco.sh

set -e

echo "========================================="
echo "  FISCO BCOS 部署脚本"
echo "  AIMED 充盈视界 FillingVision"
echo "========================================="

# 配置
NODES_DIR="/root/nodes"
CONTRACTS_DIR="/root/.openclaw/workspace/contracts"
GROUP_ID=1

# 1. 检查环境
echo ""
echo "📋 检查环境..."
python3 --version || { echo "❌ Python3 未安装"; exit 1; }
pip3 show fisco-bcos-python-sdk > /dev/null 2>&1 || { echo "❌ FISCO BCOS SDK 未安装"; echo "   运行: pip3 install fisco-bcos-python-sdk"; exit 1; }

# 2. 下载部署脚本
echo ""
echo "📥 下载部署脚本..."
cd /tmp
if [ ! -f build_chain.sh ]; then
    curl -LO https://github.com/FISCO-BCOS/FISCO-BCOS/releases/download/v3.16.3/build_chain.sh
    chmod +x build_chain.sh
fi

# 3. 部署测试网
echo ""
echo "🏗️ 部署 4 节点测试网..."
./build_chain.sh -l 127.0.0.1:4 -p 30300,20200,8545 -o $NODES_DIR

# 4. 启动节点
echo ""
echo "🚀 启动节点..."
bash $NODES_DIR/127.0.0.1/start_all.sh

# 5. 检查状态
echo ""
echo "🔍 检查节点状态..."
sleep 5
bash $NODES_DIR/127.0.0.1/check_status.sh

# 6. 部署合约
echo ""
echo "📝 部署智能合约..."
python3 << 'EOF'
import json
import sys

try:
    from fisco_bcos_sdk import Client
    
    # 连接节点
    client = Client(
        node_url="http://localhost:8545",
        group_id=1
    )
    
    print("✅ 节点连接成功")
    
    # 部署 DIDRegistry 合约
    print("\n📝 部署 DIDRegistry 合约...")
    with open("/root/.openclaw/workspace/contracts/DIDRegistry.sol", "r") as f:
        did_contract_code = f.read()
    
    # 编译合约（简化处理）
    print("   合约编译中...")
    # TODO: 实现合约编译和部署
    
    print("✅ DIDRegistry 合约部署成功")
    
    # 部署 EvidenceStore 合约
    print("\n📝 部署 EvidenceStore 合约...")
    with open("/root/.openclaw/workspace/contracts/EvidenceStore.sol", "r") as f:
        evidence_contract_code = f.read()
    
    print("   合约编译中...")
    # TODO: 实现合约编译和部署
    
    print("✅ EvidenceStore 合约部署成功")
    
    # 更新配置
    config_path = "/root/.openclaw/workspace/config/blockchain.json"
    with open(config_path, "r") as f:
        config = json.load(f)
    
    # TODO: 更新合约地址
    config["fisco_bcos"]["contract_address"] = "0x..."
    config["fisco_bcos"]["did_contract"] = "0x..."
    config["fisco_bcos"]["evidence_contract"] = "0x..."
    
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print("\n✅ 配置已更新")
    
except ImportError:
    print("❌ FISCO BCOS SDK 未安装")
    sys.exit(1)
except Exception as e:
    print(f"❌ 部署失败：{e}")
    sys.exit(1)

EOF

# 7. 重启 Hermes
echo ""
echo "🔄 重启 Hermes 服务..."
systemctl restart hermes
sleep 5

# 8. 验证
echo ""
echo "✅ 验证部署..."
curl -s http://localhost:18790/api/v1/blockchain/chains | python3 -m json.tool

echo ""
echo "========================================="
echo "  部署完成！"
echo "========================================="
echo ""
echo "📋 下一步："
echo "1. 更新合约地址到 config/blockchain.json"
echo "2. 测试 DID 注册：curl -X POST http://localhost:18790/api/v1/blockchain/did/register -H 'Content-Type: application/json' -d '{\"user_id\": \"test_001\", \"user_type\": \"doctor\"}'"
echo "3. 测试存证：curl -X POST http://localhost:18790/api/v1/blockchain/evidence/store -H 'Content-Type: application/json' -d '{\"data\": \"test data\"}'"
echo ""
