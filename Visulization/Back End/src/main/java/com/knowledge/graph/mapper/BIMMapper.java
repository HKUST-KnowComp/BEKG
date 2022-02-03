package com.knowledge.graph.mapper;

import com.knowledge.graph.node.BIMNode;
import org.apache.ibatis.annotations.Param;

import java.util.List;
import java.util.Map;

public interface BIMMapper {

    public List<BIMNode> getAllNode();

    public Map<String, Object> getPropertiesById(@Param("id") Long id);

    public BIMNode getBIMById(@Param("id") Long id);

    public List<BIMNode> getNodeByName(@Param("name") String name);

    public List<BIMNode> getEndNodes(@Param("sid") Long id);

    public List<BIMNode> getStartNodes(@Param("eid") Long id);
}
