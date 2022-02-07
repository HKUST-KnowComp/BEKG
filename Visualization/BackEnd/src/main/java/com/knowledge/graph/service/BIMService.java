package com.knowledge.graph.service;

import com.knowledge.graph.mapper.BIMMapper;
import com.knowledge.graph.mapper.RelationshipMapper;
import com.knowledge.graph.node.BIMNode;
import com.knowledge.graph.node.AnotherNodeWithRelationship;
import com.knowledge.graph.node.RelationshipNode;
import com.knowledge.graph.node.Response;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class BIMService {

    @Autowired
    private BIMMapper bimMapper;

    @Autowired
    private RelationshipMapper relationshipMapper;

    public Response getAllNode(){
        List<BIMNode> bimNodes =  bimMapper.getAllNode();
        HashMap hashMap = new HashMap();
        hashMap.put("nodes",bimNodes);
        return Response.Ok("查询所有结点成功",hashMap);
    }

    public Response getAllRelationship(){
        List<RelationshipNode> relationships = relationshipMapper.getAllRelationship();
        HashMap hashMap = new HashMap();
        hashMap.put("relationships",relationships);
        return Response.Ok("查询所有联系成功",hashMap);
    }
    public Map<String, Object> getProperties(Long id){
        return bimMapper.getPropertiesById(id);
    }

    public Response getNodeByName(String name){
        List<BIMNode> bimNodes = bimMapper.getNodeByName(name);
        HashMap hashMap = new HashMap();
        hashMap.put("nodes",bimNodes);
        return Response.Ok("模糊查询结点成功",hashMap);
    }

    public Response getAnotherNodeWithRelationshipById(Long id){
        AnotherNodeWithRelationship endNodes = new AnotherNodeWithRelationship();
        List<BIMNode> AnotherNodes = new ArrayList<>();
        AnotherNodes.addAll(bimMapper.getEndNodes(id));
        AnotherNodes.addAll(bimMapper.getStartNodes(id));
        endNodes.setAnotherNodes(AnotherNodes);
        endNodes.setRelationshipNodes(relationshipMapper.getRelationshipByStartId(id));
        HashMap hashMap = new HashMap();
        hashMap.put("endNodesWithRelationship",endNodes);
        return Response.Ok("查询某结点以及其联系成功", hashMap);
    }

    public Response getNodeById(Long id){
        BIMNode node = bimMapper.getBIMById(id);
        HashMap hashMap = new HashMap();
        hashMap.put("node",node);
        return Response.Ok("根据结点id查找结点成功", hashMap);
    }
}
