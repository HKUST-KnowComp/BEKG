package com.knowledge.graph.node;

public class RelationshipNode {

    private Long id;

    private Long source; //连线开始ID

    private Long target; //连线结束ID

    private String type; //连线的类型

    public Long getSource() {
        return source;
    }

    public void setSource(Long source) {
        this.source = source;
    }

    public Long getTarget() {
        return target;
    }

    public void setTarget(Long target) {
        this.target = target;
    }

    public String getType() {
        return type;
    }

    public void setType(String type) {
        this.type = type;
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public RelationshipNode(Long id, Long source, Long target, String type) {
        this.id = id;
        this.source = source;
        this.target = target;
        this.type = type;
    }

    public RelationshipNode() {
    }
}
