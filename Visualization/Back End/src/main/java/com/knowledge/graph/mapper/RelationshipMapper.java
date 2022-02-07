package com.knowledge.graph.mapper;

import com.knowledge.graph.node.RelationshipNode;
import org.apache.ibatis.annotations.Param;

import java.util.List;

public interface RelationshipMapper {

    public List<RelationshipNode> getAllRelationship();

    public List<RelationshipNode> getRelationshipByStartId(@Param("sid") Long id);
}
