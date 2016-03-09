# confapplet

基于[云通讯](http://yuntongxun.com)的简单电话会议小应用**DEMO**程序。

**注意: 只是DEMO！**

## 服务器/浏览器 API

采用 [JSON-RPC](http://www.jsonrpc.org/specification) over WebSocket，但是：
* 不支持批处理请求
* 同一时间点不并发执行同一个客户端的多个请求。

### 服务器提供的 RPC
用户进行会议/呼叫控制。

#### 创建会议

`int CreateConf()`

- `return` 新建的会议ID。一个由4－8位数字组成标识符。

#### 解散会议
`void DismissConf(string confid)`

- `params`
    - `confid` 要解散的会议ID。一个由4－8位数字组成标识符。

#### 邀请加入会议
`int InviteJoinConf(string confid, string number)`

- `params`
    - `confid` 会议ID。一个由4－8位数字组成标识符。
    - `number` 被邀请者电话号码
- `return` 此次邀请过程的呼叫ID。一个由32位数字、字符组成的唯一通话标识符。

#### 退出会议
`void QuitConf(string confid, string callid)`

- `params`
    - `confid` 会议ID。一个由4－8位数字组成标识符。
    - `callid` 退出者的呼叫ID

#### 会议状态查询
`pair<map<string, int>, map<string, int> QueryConfState(string confid)`

- `params`
    - `confid` 会议ID
- `return` 会议状态元组数据：
    - `state` 状态枚举值
    - `count` 会议参与者数量

### 浏览器器提供的 RPC
用于接收来自服务器的会议/会叫状态变化通知。

#### 会议创建通知
会议创建成功会发送此请求

`void OnConfCreate(string confid, string callid, string createtime)`

- `params`
    - `confid` 一个由4－8位数字组成标识符。
    - `callid` 创建会议的用户callid， 一个由32位数字、字符组成的唯一通话标识符。
    - `createtime` 会议创建时间，格式yyyymmddhhmiss

#### 加入会议通知
`void OnConfInviteJoin(string confid, string callid, string jointime, int result, string number)`

- `confid` 加入会议的会议id。
- `callid` 一个由32位数字、字符组成的唯一标识符。
- `jointime` 加入会议时间，格式yyyymmddhhmiss
- `result` 操作结果。　0成功 ，其它值为失败。
- `number` 手机号

#### 会议邀请结果通知
`void OnConfInviteJoin(string confid, string callid, string jointime, string number)`

- `confid` 加入会议的会议id。
- `callid` 一个由32位数字、字符组成的唯一标识符。
- `jointime` 加入会议时间，格式yyyymmddhhmiss
- `number` 手机号

#### 退出会议通知
`void OnConfQuit(string confid, string callid, string jointime, string number)`

- `confid` 加入会议的会议id。
- `callid` 一个由32位数字、字符组成的唯一标识符。
- `jointime` 加入会议时间，格式yyyymmddhhmiss
- `number` 手机号

#### 会议被删除通知
当会议中的最一个人退出会议后，会议被自动删除

`void OnConfDel(string confid, string deltime)`

- `confid` 一个由4-8位数字组成的标识符。
- `deltime` 会议被删除时间，格式yyyymmddhhmiss。

### 解散会议操作结果通知
执行解散会议命令后的操作结果回调通知。

`void OnConfDismiss(string confid, int status)`

- `confid` 一个由4-8位数字组成的标识符。
- `status` 结果值0成功，其它值为失败。
