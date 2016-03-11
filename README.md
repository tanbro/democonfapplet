# confapplet

基于[云通讯](http://yuntongxun.com)的简单电话会议小应用**DEMO**程序

**注意: 只是DEMO！**

## 服务器/浏览器 API

采用 [JSON-RPC](http://www.jsonrpc.org/specification) over WebSocket，但是：
* 不支持批处理请求
* 同一时间点不并发执行同一个客户端的多个请求。

**注意：**

由于时间关系，只实现这4个接口：
* 创建会议
* 解散会议
* 邀请加入会议
* 退出会议

所以，浏览器将**不会**收到任何通知性质的消息！


### 服务器提供的 RPC
用户进行会议/呼叫控制。

#### 创建会议

`Object CreateConf()`

- `return` 一个`JSON`对象，包括新建的会议ID`confid`，一个由4－8位数字组成标识符。

#### 解散会议
`void DismissConf(String confid)`

- `params`
    - `confid` 要解散的会议ID。一个由4－8位数字组成标识符。

#### 邀请加入会议
`Object InviteJoinConf(String confid, String number)`

- `params`
    - `confid` 会议ID。一个由4－8位数字组成标识符。
    - `number` 被邀请者电话号码
- `return` 一个`JSON`对象，包括此次邀请过程的呼叫ID`callid`，一个由32位数字、字符组成的唯一通话标识符。

#### 退出会议
`void QuitConf(String confid, String callid)`

- `params`
    - `confid` 会议ID。一个由4－8位数字组成标识符。
    - `callid` 退出者的呼叫ID

#### 会议状态查询
`Object QueryConfState(string confid)`

- `params`
    - `confid` 会议ID
- `return` 一个`JSON`对象，包括的属性有：
    - `state` 状态枚举值
    - `count` 会议参与者数量

### 浏览器提供的 RPC
用于接收来自服务器的会议/会叫状态变化通知。

#### 会议创建通知
会议创建成功会发送此请求

`void OnConfCreate(String confid, String callid, String createtime)`

- `params`
    - `confid` 一个由4－8位数字组成标识符。
    - `callid` 创建会议的用户callid， 一个由32位数字、字符组成的唯一通话标识符。
    - `createtime` 会议创建时间，格式yyyymmddhhmiss

#### 加入会议通知
`void OnConfInviteJoin(String confid, String callid, String jointime, Number result, String number)`

- `confid` 加入会议的会议id。
- `callid` 一个由32位数字、字符组成的唯一标识符。
- `jointime` 加入会议时间，格式yyyymmddhhmiss
- `result` 操作结果。　0成功 ，其它值为失败。
- `number` 手机号

#### 会议邀请结果通知
`void OnConfInviteJoin(String confid, String callid, String jointime, String number)`

- `confid` 加入会议的会议id。
- `callid` 一个由32位数字、字符组成的唯一标识符。
- `jointime` 加入会议时间，格式yyyymmddhhmiss
- `number` 手机号

#### 退出会议通知
`void OnConfQuit(String confid, String callid, String jointime, String number)`

- `confid` 加入会议的会议id。
- `callid` 一个由32位数字、字符组成的唯一标识符。
- `jointime` 加入会议时间，格式yyyymmddhhmiss
- `number` 手机号

#### 会议被删除通知
当会议中的最一个人退出会议后，会议被自动删除

`void OnConfDel(String confid, String deltime)`

- `confid` 一个由4-8位数字组成的标识符。
- `deltime` 会议被删除时间，格式yyyymmddhhmiss。

#### 解散会议操作结果通知
执行解散会议命令后的操作结果回调通知。

`void OnConfDismiss(String confid, Number status)`

- `confid` 一个由4-8位数字组成的标识符。
- `status` 结果值0成功，其它值为失败。
