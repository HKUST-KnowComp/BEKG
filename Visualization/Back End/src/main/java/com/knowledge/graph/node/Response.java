package com.knowledge.graph.node;

import lombok.Data;

import java.util.HashMap;
import java.util.Map;

/*
返回到前端的统一数据格式
*/

public class Response {
    private Integer status; //状态码
    private String message;
    private HashMap data; //返回数据

    public Response(Integer status, String message, HashMap data) {
        this.status = status;
        this.message = message;
        this.data = data;
    }

    public static  Response Ok(String message, HashMap data){
        return new Response(200, message, data);
    }

    public static Response Error(String message){
        return new Response(500,message,null);
    }

    public Response() {
    }

    public Integer getStatus() {
        return status;
    }

    public void setStatus(Integer status) {
        this.status = status;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public Map getData() {
        return data;
    }

    public void setData(HashMap data) {
        this.data = data;
    }

    @Override
    public String toString() {
        return "Response{" +
                "status=" + status +
                ", message='" + message + '\'' +
                ", data=" + data +
                '}';
    }
}
