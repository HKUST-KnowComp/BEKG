package com.knowledge.graph.controller;

import com.knowledge.graph.node.BIMNode;
import com.knowledge.graph.node.RelationshipNode;
import com.knowledge.graph.node.Response;
import com.knowledge.graph.service.BIMService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
public class BIMController {

    @Autowired
    private BIMService bimService;

    @GetMapping("/getAllNode")
    public Response getAllNode(){
        return bimService.getAllNode();
    }

    @GetMapping("/getAllRelationship")
    public Response getAllRelationship(){
        return bimService.getAllRelationship();
    }

    @PostMapping("/getNodeByName/{name}")
    public Response getNodeByName(@PathVariable("name") String name){
        return bimService.getNodeByName(name);
    }

    @GetMapping("/getAnotherNodeById/{id}")
    public Response getNodeWithRelationshipById(@PathVariable("id") Long id){
        return bimService.getAnotherNodeWithRelationshipById(id);
    }

    @GetMapping("/getNodeById/{id}")
    public Response getNodeById(@PathVariable("id") Long id){
        return bimService.getNodeById(id);
    }
}
