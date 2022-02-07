package com.knowledge.graph.node;

import java.util.List;
import java.util.Map;

public class BIMNode {

    private Long id; //节点ID

    private Map<String, Object> properties; //将所有属性组合成一个map类型


    @Override
    public String toString() {
        return "BIMNode{" +
                "id=" + id +
                ", properties=" + properties +
                '}';
    }

    public Map<String, Object> getProperties() {
        return properties;
    }

    public void setProperties(Map<String, Object> properties) {
        this.properties = properties;
    }

    public BIMNode(Long id, Map<String, Object> properties) {
        this.id = id;
        this.properties = properties;
    }


    public BIMNode() {
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

}
