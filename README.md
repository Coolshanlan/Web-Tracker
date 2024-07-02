# How to run
```shell
python website_tracker.py
```
**debug mode (-d)** will not send email
```shell
python website_tracker.py -d
```
**Specify debug config (-t idx)** will not send email
```shell
python website_tracker.py -d -t <config index>
```

# Config arguments
## Common arguments
```json
{
    "enable":true,
    "target_URL":"https://www.google.com/finance/quote/TWD-JPY?sa=X&ved=2ahUKEwiI__fnooOAAxV0hMYKHYPhBNQQmY0JegQIDRAc",
    "website_name":"日幣匯率",
    "email_messages":"匯率已降低！",
    "to_emails":["joey0201020123@gmail.com"],
    "update_second":300,
    "extract_all":false,
    "filtering":[",","自 NT$ "],
    "find_element":
    {
        "tag":"div",
        "class_name":"kf1m0",
        "id":"id"
    },
    "tracker":
    {
        "tracker_name": ["BasicTracker","DynamicTracker","NumberTracker","NewTracker"],
        "mode":["Basic","Dynamic"],
        "dynamic_delay": 5, (dynamic only)
        "scorll_times": 3, (dynamic only)
    }
}
```
- enable: 起動狀態
- website_name: custom website name
- email_messages: email content
- extract_all: 根據 find element 所找到的所有 elements 都抓下來轉成文字，if false 只拿第一個找到的
- filtering: 過濾文字
- find_element: `class_name`, `id` 二選一
- tracker: 跟 tracker 相關的參數
  - tracker_name: ["BasicTracker","NumberTracker","ListNewTracker"] 擇一
  - mode: 動態會開啟 web driver
  - **dynamic_delay**: dynamic mode only, 每次 scroll 中間等待內容載入的時間
  - **scorll_times**: dynamic mode only, scroll 次數

## Tracker
- BasicTracker
- DynamicTracker
- NumberTracker
- ListNewTracker
  
### BasicTracker
抓出 element 中的文字

**trigger condition**: element 中的文字改變

### NumberTracker
抓出 element 中的文字，並轉成 int

**trigger condition**: element number 越過 `number`，接下來每超過 `remind_diff` 也會觸發
```json
{
    "target_number":
      {
        "mode":"bigger",
        "number":4.6, (擇一 or both)
        "remind_diff":0.01 (擇一 or both)
      }
}
```
- mode: ['bigger', 'lower'] 看是要 > target number 還是 <
- number: target number
- remind_diff: 超過 target number 後，每差多少繼續提醒

### ListNewTracker
**extract_all need be `True`**

**trigger condition**: element 透過 "\n" 轉成 set(List<str>) 只要有新項目就會觸發，減少擇不會



