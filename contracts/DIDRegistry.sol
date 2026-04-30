// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.6.10;

/**
 * @title DIDRegistry - 数字身份注册合约
 * @author AIMED 充盈视界
 * @notice 用于注册和管理区块链数字身份（DID）
 */
contract DIDRegistry {
    
    struct DIDDocument {
        string did;
        string userId;
        string userType;
        string metadata;
        uint256 createdAt;
        uint256 updatedAt;
        bool active;
    }
    
    // DID 映射
    mapping(string => DIDDocument) public dids;
    // 用户 DID 列表
    mapping(string => string[]) public userDids;
    // 所有 DID 列表
    string[] public didList;
    // DID 总数
    uint256 public totalDIDs;
    
    // 事件
    event DIDRegistered(
        string did,
        string userId,
        string userType,
        uint256 timestamp
    );
    
    event DIDUpdated(
        string did,
        string metadata,
        uint256 timestamp
    );
    
    event DIDRevoked(
        string did,
        uint256 timestamp
    );
    
    /**
     * @notice 注册新的数字身份
     * @param _did 数字身份标识
     * @param _userId 用户 ID
     * @param _userType 用户类型（patient/doctor/developer/admin）
     * @param _metadata 元数据（JSON 格式）
     */
    function registerDID(
        string memory _did,
        string memory _userId,
        string memory _userType,
        string memory _metadata
    ) public {
        require(!dids[_did].active, "DID already exists");
        require(bytes(_did).length > 0, "DID cannot be empty");
        require(bytes(_userId).length > 0, "UserID cannot be empty");
        require(bytes(_userType).length > 0, "UserType cannot be empty");
        
        dids[_did] = DIDDocument({
            did: _did,
            userId: _userId,
            userType: _userType,
            metadata: _metadata,
            createdAt: block.timestamp,
            updatedAt: block.timestamp,
            active: true
        });
        
        userDids[_userId].push(_did);
        didList.push(_did);
        totalDIDs++;
        
        emit DIDRegistered(_did, _userId, _userType, block.timestamp);
    }
    
    /**
     * @notice 更新 DID 元数据
     * @param _did 数字身份标识
     * @param _metadata 新的元数据
     */
    function updateDID(string memory _did, string memory _metadata) public {
        require(dids[_did].active, "DID does not exist");
        
        dids[_did].metadata = _metadata;
        dids[_did].updatedAt = block.timestamp;
        
        emit DIDUpdated(_did, _metadata, block.timestamp);
    }
    
    /**
     * @notice 撤销 DID
     * @param _did 数字身份标识
     */
    function revokeDID(string memory _did) public {
        require(dids[_did].active, "DID does not exist");
        
        dids[_did].active = false;
        dids[_did].updatedAt = block.timestamp;
        
        emit DIDRevoked(_did, block.timestamp);
    }
    
    /**
     * @notice 验证 DID 是否有效
     * @param _did 数字身份标识
     * @return 是否有效
     */
    function verifyDID(string memory _did) public view returns (bool) {
        return dids[_did].active;
    }
    
    /**
     * @notice 查询 DID 详情
     * @param _did 数字身份标识
     * @return did DID 标识
     * @return userId 用户 ID
     * @return userType 用户类型
     * @return metadata 元数据
     * @return createdAt 创建时间
     * @return updatedAt 更新时间
     * @return active 是否活跃
     */
    function queryDID(string memory _did) public view returns (
        string memory did,
        string memory userId,
        string memory userType,
        string memory metadata,
        uint256 createdAt,
        uint256 updatedAt,
        bool active
    ) {
        DIDDocument storage doc = dids[_did];
        return (
            doc.did,
            doc.userId,
            doc.userType,
            doc.metadata,
            doc.createdAt,
            doc.updatedAt,
            doc.active
        );
    }
    
    /**
     * @notice 获取用户的所有 DID
     * @param _userId 用户 ID
     * @return DID 列表
     */
    function getUserDIDs(string memory _userId) public view returns (string[] memory) {
        return userDids[_userId];
    }
    
    /**
     * @notice 获取 DID 总数
     * @return DID 总数
     */
    function getTotalDIDs() public view returns (uint256) {
        return totalDIDs;
    }
}
