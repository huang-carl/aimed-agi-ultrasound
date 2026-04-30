// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.6.10;

/**
 * @title EvidenceStore - 数据存证合约
 * @author AIMED 充盈视界
 * @notice 用于医疗数据上链存证和验证
 */
contract EvidenceStore {
    
    struct Evidence {
        string evidenceId;
        string dataHash;
        string metadata;
        uint256 blockNumber;
        uint256 timestamp;
        address storedBy;
    }
    
    // 存证映射
    mapping(string => Evidence) public evidences;
    // 用户存证列表
    mapping(string => string[]) public userEvidences;
    // 所有存证列表
    string[] public evidenceList;
    // 存证总数
    uint256 public totalEvidences;
    
    // 事件
    event EvidenceStored(
        string evidenceId,
        string dataHash,
        address storedBy,
        uint256 timestamp
    );
    
    event EvidenceVerified(
        string evidenceId,
        bool valid,
        uint256 timestamp
    );
    
    /**
     * @notice 存储数据存证
     * @param _evidenceId 存证 ID
     * @param _dataHash 数据哈希（SHA-256）
     * @param _metadata 元数据（JSON 格式）
     */
    function storeEvidence(
        string memory _evidenceId,
        string memory _dataHash,
        string memory _metadata
    ) public {
        require(bytes(evidences[_evidenceId].evidenceId).length == 0, "Evidence already exists");
        require(bytes(_evidenceId).length > 0, "EvidenceId cannot be empty");
        require(bytes(_dataHash).length > 0, "DataHash cannot be empty");
        
        evidences[_evidenceId] = Evidence({
            evidenceId: _evidenceId,
            dataHash: _dataHash,
            metadata: _metadata,
            blockNumber: block.number,
            timestamp: block.timestamp,
            storedBy: msg.sender
        });
        
        // 从 metadata 中提取 userId（简化处理）
        string memory userId = "system";
        userEvidences[userId].push(_evidenceId);
        evidenceList.push(_evidenceId);
        totalEvidences++;
        
        emit EvidenceStored(_evidenceId, _dataHash, msg.sender, block.timestamp);
    }
    
    /**
     * @notice 验证存证是否存在
     * @param _evidenceId 存证 ID
     * @return 是否存在
     */
    function verifyEvidence(string memory _evidenceId) public view returns (bool) {
        return bytes(evidences[_evidenceId].evidenceId).length > 0;
    }
    
    /**
     * @notice 查询存证详情
     * @param _evidenceId 存证 ID
     * @return evidenceId 存证 ID
     * @return dataHash 数据哈希
     * @return metadata 元数据
     * @return blockNumber 区块高度
     * @return timestamp 时间戳
     * @return storedBy 存储地址
     */
    function queryEvidence(string memory _evidenceId) public view returns (
        string memory evidenceId,
        string memory dataHash,
        string memory metadata,
        uint256 blockNumber,
        uint256 timestamp,
        address storedBy
    ) {
        Evidence storage ev = evidences[_evidenceId];
        return (
            ev.evidenceId,
            ev.dataHash,
            ev.metadata,
            ev.blockNumber,
            ev.timestamp,
            ev.storedBy
        );
    }
    
    /**
     * @notice 获取存证总数
     * @return 存证总数
     */
    function getTotalEvidences() public view returns (uint256) {
        return totalEvidences;
    }
    
    /**
     * @notice 获取用户的存证列表
     * @param _userId 用户 ID
     * @return 存证 ID 列表
     */
    function getUserEvidences(string memory _userId) public view returns (string[] memory) {
        return userEvidences[_userId];
    }
}
