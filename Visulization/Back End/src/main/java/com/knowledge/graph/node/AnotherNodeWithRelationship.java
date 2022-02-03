package com.knowledge.graph.node;

import java.util.List;

public class AnotherNodeWithRelationship {
    private List<BIMNode> AnotherNodes;
    private List<RelationshipNode> relationshipNodes;

    public AnotherNodeWithRelationship() {
    }

    public AnotherNodeWithRelationship(List<BIMNode> endNodes, List<RelationshipNode> relationshipNodes) {
        this.AnotherNodes = endNodes;
        this.relationshipNodes = relationshipNodes;
    }

    public List<BIMNode> getAnotherNodes() {
        return AnotherNodes;
    }

    public void setAnotherNodes(List<BIMNode> endNodes) {
        this.AnotherNodes = endNodes;
    }

    public List<RelationshipNode> getRelationshipNodes() {
        return relationshipNodes;
    }

    public void setRelationshipNodes(List<RelationshipNode> relationshipNodes) {
        this.relationshipNodes = relationshipNodes;
    }
}
