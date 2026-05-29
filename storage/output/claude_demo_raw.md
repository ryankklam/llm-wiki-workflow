[00:00] Hello
[00:04]  everyone
[00:05] I'm Boris
[00:06] I'm a member of technical staff here at Anthropic
[00:09] and I created Quad Code
[00:11]  and here to talk to you a little bit about some practical tips and tricks for using Quad Code
[00:16]  it's going to be very practical
[00:18]  I'm not going to go too much into the history or the theory or anything like this
[00:22]  and yeah before we start
[00:24]  actually can we get a quick show of hands who has used Quad Code before
[00:29]  yeah
[00:30]  alright that's what we like to see
[00:31]  for everyone that didn't raise your hands
[00:34]  I know you're not supposed to do this while people are talking
[00:36]  but if you can open your laptop
[00:38]  and type this
[00:43]  and this will help you install Quad Code
[00:45]  just so you can follow along for the rest of the talk
[00:52]  oh you need is no JS
[00:54]  if you have it that should work
[00:58]  if you want to install all of the plugins
[01:01]  yeah if you don't have to follow along
[01:04]  but if you don't have it yet
[01:06]  this is your chance to install it so you can follow along
[01:11]  so what is Quad Code?
[01:13]  Quad Code is a new kind of AI assistant
[01:16]  and there's been different generations of AI assistants for coding
[01:20]  most of them have been about completing like a line at a time
[01:23]  completing a few lines of code at a time
[01:26]  Quad Code is not for that it's fully agentic
[01:28]  so it's meant for building features for writing entire functions
[01:32]  entire files
[01:34]  fixing entire bugs at the same time
[01:38]  and what's kind of cool about Quad Code is it works with all of your tools
[01:41]  and you don't have to change out your workflow
[01:43]  you don't have to swap everything to start using it
[01:45]  so whatever IDE use if you use VS Code
[01:48]  or if you use Xcode
[01:50]  or if you use JetBrains IDE
[01:53]  there's some people that are on the topic that you can't pry them from their cold dead hands
[01:57]  but they use Quad Code
[01:59]  because Quad Code works with every single IDE
[02:01]  every terminal out there
[02:03]  it will work locally
[02:05]  over remote SSH, over Teamox
[02:07]  whatever environment you're in
[02:09]  you can run it
[02:12]  it's general purpose
[02:14]  and this is something where if you haven't used these kind of free form
[02:17]  coding assistants in the past
[02:19]  it can be kind of hard to figure out how to get started
[02:21]  because you open it up and you just see a prompt bar and you might wonder like
[02:24]  what do I do with this?
[02:26]  what do I type in?
[02:27]  it's a power tool so you can use it for a lot of things
[02:30]  but also because it can do so much
[02:32]  we don't try to guide you towards a particular workflow
[02:34]  because really you should be able to use it however you want as an engineer
[02:42]  as you open up Quad Code for the first time
[02:44]  there's a few things that we recommend doing
[02:46]  to get your environment set up
[02:48]  and these are pretty straightforward
[02:50]  so run terminal set up
[02:51]  this will give you shift enter for new lines
[02:53]  so you don't have to do like backslashes enter new lines
[02:55]  this is you know
[02:56]  it makes it a little bit nicer to use
[02:58]  do slash theme to set light mode or dark mode or
[03:02]  doltanize themes
[03:03]  you can do slash install GitHub app
[03:06]  so today we announced a GitHub app
[03:09]  where you can add mention
[03:11]  a cloud on any GitHub issue or port request
[03:14]  so to install it just run this command in your terminal
[03:17]  you can customize the set of allowed tools that you can use
[03:21]  so you're not prompted for it every time
[03:23]  this is pretty convenient
[03:24]  for stuff that I'm prompted about a bunch
[03:26]  I'll definitely customize it in this way
[03:28]  so I don't have to accept it every time
[03:30]  and something that I actually do is for a lot of my prompts
[03:32]  I won't hand type them into Quad Code
[03:35]  if you're on macOS
[03:36]  you can go into your system settings
[03:38]  under accessibility as dictation
[03:40]  and you can enable it
[03:41]  and so something I do is you just hit like the dictation key twice
[03:44]  and you can just speak your prompt
[03:46]  and it helps a lot to have specific prompts
[03:49]  so this is actually pretty awesome
[03:50]  you can just talk to Quad Code
[03:51]  and like you would another engineer
[03:53]  and you don't have to type a lot of code
[03:59]  so when you're starting out with Quad Code
[04:01]  it's so freeform and it can do everything
[04:03]  what do you start with?
[04:04]  the thing I recommend above everything else
[04:06]  is starting with code based Q&A
[04:08]  so just asking your question
[04:09]  asking questions here code based
[04:12]  this is something that we teach new hires at Anthropic
[04:15]  so on the first day in technical onboarding
[04:17]  you learn about Quad Code
[04:18]  you download it, you get it set up
[04:20]  and then you immediately start asking questions about the code based
[04:23]  and in the past when you were doing technical onboarding
[04:25]  it's something that taxes the team a lot
[04:27]  right you have to ask other engineers on the team questions
[04:30]  you have to look around the code
[04:32]  and this takes a while
[04:33]  you have to figure out how to use the tools
[04:34]  this takes a long time
[04:36]  with Quad Code you can just ask Quad Code
[04:39]  and it will export the code based
[04:41]  it will answer these kind of questions
[04:42]  and so at Anthropic onboarding
[04:44]  you should take about two or three weeks
[04:45]  for technical hires
[04:46]  it's now about two or three days
[04:51]  what's also kind of cool about Q&A is
[04:53]  we don't do any sort of indexing
[04:55]  so there's no remote database with your code
[04:57]  we don't upload it anywhere
[04:58]  your code stays vocal
[04:59]  we do not train generative models on the code
[05:02]  so it's there, you control it
[05:04]  there's no indices or anything like this
[05:06]  and what that means is also there's no setup
[05:08]  so you start Quad, you download it
[05:10]  you start it, there's no indexing
[05:11]  you don't have to wait
[05:12]  you can just use it right away
[05:16]  this is a technical talk
[05:17]  so I'm going to show some very specific prompts
[05:19]  and very specific code samples that you can use
[05:21]  and hopefully improve
[05:22]  and up level your Quad Code experience
[05:25]  so some kind of questions that you can ask is
[05:27]  you know like how is this particular piece of code used
[05:30]  or how do I instantiate this thing
[05:31]  and Quad Code won't just do like a tech search
[05:33]  and try to answer this
[05:34]  it will often go a level deeper
[05:36]  and it will try to find examples of
[05:38]  how is this class instantiated
[05:39]  how is it used
[05:41]  and it will give you a much deeper answer
[05:43]  so something that you would get out of a wiki
[05:44]  or documentation
[05:45]  instead of just like command F
[05:49]  something that I do a lot also is
[05:51]  ask it about git history
[05:52]  so for example, you know
[05:54]  why does this function have 15 arguments
[05:56]  and why are the arguments named this weird way
[05:58]  and this is something I bet in all of our codebuses
[06:00]  you have some function like this
[06:02]  or some class like this
[06:04]  and Quad Code can look through git history
[06:06]  and it will look to figure out
[06:08]  how did these arguments get introduced
[06:09]  and who introduced them
[06:10]  and what was the situation
[06:11]  what are the issues that those commits linked to
[06:13]  and it will look through all this and summarize it
[06:15]  and you don't have to tell it that in all these
[06:17]  in all this detail
[06:18]  you just ask it
[06:19]  so just say look through git history
[06:21]  and it will know to do this
[06:23]  the reason it knows it by the way
[06:24]  is not because we prompted it to
[06:25]  there's nothing in the system prompt
[06:26]  about looking through git history
[06:28]  it knows it because the model was awesome
[06:30]  and if you tell it to use git
[06:32]  it will know how to use git
[06:33]  so we're lucky to be building on such a good model
[06:38]  I often ask about github issues
[06:41]  so you know
[06:42]  I can use web fetch
[06:43]  and I can fetch issues
[06:44]  and work up context on issues too
[06:45]  and this is pretty awesome
[06:48]  and this is something that I do every single Monday
[06:51]  and our weekly stand up
[06:52]  is I ask what did I ship this week
[06:54]  and Quad Code looks to the log
[06:55]  it knows my username and it will
[06:57]  just give me a nice readout
[06:58]  everything I shipped
[06:59]  and I'll just copy and paste that into a docs
[07:01]  so yeah that's tip number one
[07:04]  for people that have not used Quad Code before
[07:07]  if you're just showing it to someone for the first time
[07:09]  onboarding your team
[07:10]  the thing we definitely recommend
[07:11]  is start with code base Q&A
[07:12]  don't start by using fancy tools
[07:14]  don't start by editing code
[07:15]  just start by asking questions about the code base
[07:17]  and that will teach people how to prompt
[07:19]  and it will start teaching on this boundary
[07:21]  of like what can Quad Code do
[07:23]  what is it capable of
[07:24]  versus what do you need to hold this hand with a little bit more
[07:27]  what can be one-shotted
[07:28]  what can be one-shoted
[07:29]  what can be two-shotted
[07:31]  three-shotted
[07:32]  what do you need to use interactive mode for in a REPL
[07:35]  once you're pretty comfortable with Q&A
[07:39]  you can dive into editing code
[07:41]  this is the next thing
[07:43]  and the cool thing about any sort of
[07:46]  agent like using an LM in an agentic way
[07:49]  is you give it tools
[07:50]  and it's just like magic wood
[07:51]  figures out how to use the tools
[07:53]  and with Quad Code
[07:54]  we give it a pretty small set of tools
[07:56]  it's not a lot
[07:57]  and so it has a tool to edit files
[07:59]  it has a tool to run bash commands
[08:01]  it has a tool to search files
[08:03]  and it will string these together to explore the code
[08:05]  brainstorm
[08:07]  and then finally make edits
[08:09]  and you don't have to prompt it specifically
[08:11]  to use this tool and this tool and this tool
[08:12]  you just say you know do this thing
[08:14]  and it'll figure out how to do it
[08:15]  it'll string it together in the right way
[08:16]  that makes sense for Quad Code
[08:22]  there's a lot of ways to use this
[08:24]  something I like to do sometimes
[08:25]  is before having Quad jump in to write code
[08:28]  I'll ask it to brainstorm a little bit
[08:30]  or make a plan
[08:31]  this is something we highly recommend
[08:33]  and something I see sometimes is people
[08:35]  you know they take Quad Code
[08:37]  and they ask it hey implement this enormous
[08:39]  like a 3,000-line feature
[08:41]  and sometimes it gets this right on the first shot
[08:43]  but sometimes what happens is
[08:45]  the thing that it builds is not at all
[08:46]  the thing that you want it
[08:48]  and the easiest way to get the result you want
[08:50]  is ask it to think first
[08:52]  so brainstorm ideas
[08:54]  make a plan run it by me
[08:56]  ask for approval before you write code
[08:58]  and you don't have to use plan mode
[09:00]  you don't have to use any special tools to do this
[09:02]  all you have to do is ask Quad
[09:03]  and it'll know to do this
[09:05]  so just say before you write code make a plan
[09:07]  that's it
[09:10]  this is also I want to think with this one
[09:12]  this commit push for you
[09:13]  this is a really common incantation that I use
[09:15]  there's nothing special about it
[09:16]  but Quad is kind of smart enough to interpret this
[09:18]  so it'll make a commit
[09:19]  it'll push it to the branch
[09:20]  make a branch and then make a poor request
[09:21]  for me on GitHub
[09:22]  you don't have to explain anything
[09:23]  it'll look through the code
[09:24]  it'll look through the history
[09:25]  it'll look through the Git log by itself
[09:27]  to figure out the commit format
[09:28]  and all the stuff
[09:29]  and it'll make the commit
[09:30]  and push it the right way
[09:31]  again we're not system
[09:34]  to do this
[09:35]  it just knows how to do this
[09:36]  the model was good
[09:39]  as you get a little bit more advanced
[09:42]  you're going to want to start to plug in
[09:44]  your team's tools
[09:45]  and this is where Quad code starts to really shine
[09:47]  and there's generally two kinds of tools
[09:49]  so one is bash tools
[09:50]  and an example of this
[09:52]  I just made up this like
[09:53]  burwee CLI
[09:54]  this isn't a real thing
[09:55]  but you can say use this CLI
[09:57]  to do something
[09:58]  and you can tell Quad code about this
[09:59]  and you can tell it to use
[10:01]  for example like dash dash help
[10:02]  to figure out how to use it
[10:03]  and this is efficient
[10:04]  if you friend yourself using it a lot
[10:06]  you can also dump this into your
[10:08]  quad Md which we'll talk about in a bit
[10:10]  so Quad can remember this across sessions
[10:11]  but this is a common pattern
[10:12]  we follow at Anthropic
[10:14]  and we see external customers use too
[10:16]  and same thing with MCP
[10:18]  Quad code can use bash tools
[10:20]  you can use MCP tools
[10:22]  so just tell it about the tools
[10:24]  and you can add them see P tool
[10:26]  and you can tell it how to use it
[10:28]  and it'll just start using it
[10:29]  and this is extremely powerful
[10:31]  because when you start to use code
[10:33]  on a new code base
[10:34]  you can just give it all of your tools
[10:36]  all the tools your team already uses
[10:38]  for this code base
[10:39]  and Quad code can use it on your bath
[10:41]  and this is where you can use it
[10:43]  there's a few common workflows
[10:45]  and this is the one that I talked about already
[10:47]  so kind of do a little bit of exploration
[10:49]  do a little bit of planning
[10:51]  and ask me for confirmation
[10:53]  before you start to write code
[10:55]  these other two on the right
[10:57]  are extremely powerful
[10:59]  when Quad has some way to check its work
[11:01]  so for example by writing
[11:03]  unites or screen-shotting
[11:05]  and puppeteer
[11:07]  or screen-shotting the iOS simulator
[11:09]  then it can iterate
[11:11]  and this is incredible
[11:13]  because if you give it for example a mock
[11:15]  and you say build this web UI
[11:17]  it'll get it pretty good
[11:19]  but if you had to iterate two or three times
[11:21]  often it gets it almost perfect
[11:23]  so the trick is give it some sort of tool
[11:25]  that it can use for feedback
[11:27]  to check its work
[11:29]  and then based on that it will iterate by itself
[11:31]  and you're going to get a much better result
[11:33]  so whatever your domain is
[11:35]  if it's unites or integration test
[11:37]  or screen-shots for apps or web
[11:39]  or anything just give it away to see its result
[11:40]  and it'll iterate and get better
[11:46]  so these are the next steps
[11:48]  teach Quad how to use your tools
[11:50]  and figure out the right workflow
[11:52]  if you want Quad to jump in a code
[11:54]  if you want it to bring from a little bit
[11:56]  make a plan, if you want it to iterate
[11:58]  kind of have some sense of that
[12:00]  so you know how to prompt Quad
[12:02]  to do what you want
[12:04]  as you go deeper
[12:06]  beyond tools you want to start to give Quad more context
[12:08]  the smarter the decisions will be
[12:10]  because as an engineer working in a code base
[12:12]  you have a ton of context in your head about your systems
[12:14]  and all the history
[12:16]  and everything else so there's different ways to give this to Quad
[12:18]  and as you give Quad more context
[12:20]  it will do better
[12:22]  there's different ways to do this
[12:24]  the simplest one is what we call QuadMD
[12:26]  and QuadMD is the special file name
[12:28]  the simplest way to put it is in the project route
[12:32]  so the same directory you start QuadMD
[12:36]  put a QuadMD in there
[12:38]  and that will get automatically read into context
[12:40]  at the start of every session
[12:42]  and essentially the first user turn will include the QuadMD
[12:46]  you can also have a local QuadMD
[12:48]  and this one you don't usually check into source control
[12:52]  so QuadMD you should check into source control
[12:54]  share with your team so that you can read it once
[12:56]  and share it with your team
[12:58]  this one you don't check in
[13:00]  it's just for you
[13:02]  the kinds of things you put in QuadMD
[13:04]  common MCP tools
[13:06]  architectural decisions
[13:08]  important files
[13:10]  anything that you would typically need to know in order to work in this code base
[13:12]  try to keep it pretty short
[13:14]  because if it gets too long
[13:16]  it's just going to use up a bunch of context
[13:18]  and it's usually not that useful
[13:20]  so just try to keep it as short as you can
[13:22]  for example in our code base
[13:24]  we have common batch commands
[13:26]  we have a style guide
[13:28]  we have a few core files
[13:30]  all the other QuadMDs
[13:32]  and QuadMDs
[13:34]  and QuadMDs
[13:36]  these are the QuadMDs
[13:38]  that will get pulled in automatically
[13:40]  but then also you can put in
[13:42]  QuadMDs in nested directories
[13:44]  and those will get automatically pulled
[13:46]  when Quad works in those directories
[13:48]  and of course if your
[13:50]  company may be want to QuadMD
[13:52]  that share across all the different code bases
[13:54]  and you want to manage it on behalf of your users
[13:56]  and you can put in your enterprise route
[13:58]  and that will get pulled in automatically
[14:00] 就像你最近被改成系統直到自動
[14:02] 最害怕是現狗巴的
[14:06] 例如在最初通規、
[14:07] 選擇先形形 received
[14:10] 形形券所以你會保留
[14:14] 所有對方形形形過來
[14:16] 站在這個情況下
[14:17] 你會帶到老人宇直到
[14:19] 變成一個目標
[14:23] 而徻接遊的寫法
[14:25] 我就不用當我的卻不是
[14:26] 理不覆 attack
[14:28] 比如��托民美省按照
[14:31] 表示 setting interval
[14:34] 方向社會提到現时及制止
[14:53] 再提及这个改赏 Quad模案
[14:56] 就因为adaners 洗手间
[14:57] 那么 Quad模案
[15:03] 你放出去或예到脱
[15:06] 即使唯一限要紧续
[15:09] 这经常和议 let
[15:11] 先现在坦误哈
[15:12] 如果 realm2 谈创假
[15:18] 若谈正的傻子
[15:19] 可以否定认识
[15:22] 如果如果你對了
[15:27] 你能不能夠思考
[15:29] 要率更高一點
[15:30] 會有可能的樣式
[15:32] 有變化希望給大家
[15:33] 也不能波損
[15:35] 不管是蝴蝶
[15:36] 而扯動
[15:37] 而
[15:39] 挺好的所謀ه
[15:40] 你能不斷跑後
[15:42] 所以
[15:43]  programs
[15:44] 是產品把你視為
[15:45] 保護
[15:46] 或可以令人負責
[15:47] 或者當然
[15:48] 你能投及方式
[15:49] 也能有 . 都可以
[15:50] 終於把另一個
[15:51] 這是一個濃稅充熱的工具
[15:55] 用去量應量、習慣
[15:58] 每個人都在公審的構造
[15:59] 這些新聞已經很枝囂
[16:02] 但可能 Challenge  F سے訓練
[16:04] 理論漁可能情經的
[16:06] 例如
[16:07] 沒有完美的資料
[16:08] 它可以使用了一波
[16:13] 該傳統路易 insert
[16:14] 自己的設計
[16:17] 要請這功效
[16:18] 定了因為被同身中的資料
[16:20] 或者花會攻擊的
[16:24] 你也能用這個電話說
[16:26] 我們有些 Ugh То
[16:28] 因為這個研究
[16:30] 所以一個教會
[16:31] 以一個通道服務
[16:34] 所以
[16:35] 這個機構
[16:37] 的話
[16:38] 這個機構
[16:39] 還有拿來一下
[16:40] 這個機構
[16:41] 多餘行就可以
[16:44] 還有 很多
[16:46] 這個機構
[16:47]  работ직的機構
[16:48] 只有三 focal point
[16:49] 和把同一人交給我們
[16:55] 如果不確定這些用
[16:56] 這就是一個很好的
[16:58] 因為我們會支持的
[16:59] 很多的東西
[17:00] 和同一人的工作人員
[17:01] 很難充滿的
[17:02] 不同的東西
[17:03] 我們希望要支持
[17:04] 所以如果不確定
[17:05] 我們會開始
[17:06] 會開始的
[17:07] 會開始的
[17:08] 會開始的
[17:09] 會開始的
[17:10] 會開始的
[17:11] 會開始的
[17:12] 會開始的
[17:13] 會開始的
[17:14] 會開始的
[17:15] 會開始的
[17:16] 會開始的
[17:17] 會開始的
[17:18] 洛 two
[17:20] 洛 Four
[17:22] 去做這個
[17:23] 所以
[17:24] 那些是一個
[17:25] 如果你找到
[17:26] 你能看到
[17:27] 所有的
[17:28] 不同的
[17:29] 文件
[17:30] 所以
[17:31] 我會有
[17:32] 我用的文件
[17:33] 我會有
[17:34] 一個
[17:35] 文件
[17:36] 那些
[17:37] 文件
[17:38] 那些
[17:39] 文件
[17:40] 那些
[17:41] 文件
[17:42] 那些
[17:43] 文件
[17:44] 那些
[17:45] 文件
[17:46] 那些
[17:47] 文件
[17:48] 那些
[17:49] 文件
[17:50] 那些
[17:51] 例如
[17:53] 你一定要
[17:54] 可以
[17:55] 有
[17:57] 例如
[17:58] 你要
[17:59] 你需要
[18:00] 可以
[18:01] 可以
[18:02] 使用
[18:03] 例如
[18:04] 使用
[18:05] 例如
[18:06] 為
[18:07] 是
[18:08] 使用
[18:09] 例如
[18:10] 例如
[18:11] 例如
[18:12] 例如
[18:13] 例如
[18:14] 例如
[18:15] 例如
[18:16] 例如
[18:17] 例如
[18:18] 例如
[18:19] 例如
[18:20] 例如
[18:20] 教會在女生節由好的流淦
[18:22] 就在幫助人體連邪
[18:23] 甚至這樣收拾
[18:25] 所以, 其實老實說
[18:27] 如果常常與個人istas
[18:28] 切,都不容易
[18:30] 不可以夠
[18:30] 見太久
[18:31] 蛋白清服議
[18:33] 我覺得所有人
[18:34] 切最佳是
[18:35] 他的意志
[18:37] ונே設計是
[18:37] OK
[18:38] 問題
[18:39] 嘛 那想著
[18:40] 不錯
[18:41] 它的計點
[18:42] 其實他們都沒話說
[18:43] 世界關係
[18:43] 很強勁力
[18:45] 因為基本 burst
[18:46] 大家就聽見
[18:47] 與真相映 old字
[18:48] 這裡我不能擺著
[18:49] 這些計算
[18:50] 就是一個 quick reference sheet
[18:51] 所以 anytime you can hit shift tab to accept edits
[18:55]  and this switches you into auto accept edits mode
[18:57]  so bash commands to need approval
[18:59]  but edits are auto accepted
[19:00]  and you can always ask cloud to undo them later.
[19:04]  For example, I'll do this if I know clouds on the ray track
[19:06]  or if it's writing unit tests and iterating on tests
[19:08]  or usually just switch into auto accept mode
[19:10]  so I don't have to okay every single edit.
[19:14]  Anytime you want cloud to remember something
[19:16]  so for example, if it's not using a tool correctly
[19:19]  and you want it to use it correctly from the non
[19:20]  just type the fountain sign
[19:22]  and then tell it what to remember
[19:23]  and it'll remember it, it'll incorporate it
[19:24]  into quad MD automatically.
[19:28]  If you ever want to drop down to bash mode
[19:29]  so just run a bash command
[19:30]  you can hit the exclamation mark
[19:32]  and type in your command that'll run locally
[19:34]  but that also goes into the context window
[19:36]  so cloud will see it on the next turn.
[19:39]  And this is pretty good for long writing commands
[19:41]  if you know exactly what you want to do
[19:42]  or any command that you want to get into context
[19:45]  and cloud will see the command and the output.
[19:48]  You can add mentioned thousand folders.
[19:50]  Anytime you can hit escape to stop what cloud is doing.
[19:54]  No matter what cloud is doing
[19:55]  you can always safely hit escape.
[19:56]  It's not going to corrupt the session
[19:58]  it's not going to mess anything up.
[19:59]  So maybe cloud is doing a file edit
[20:01]  I'll hit escape, I'll tell it what to do differently
[20:03]  or maybe it suggested a 21 edit
[20:05]  and I'm like actually 19 of these lines look perfect
[20:07]  but one line you should change.
[20:09]  I'll hit escape, I'll tell it that
[20:11]  and then I'll tell it to redo that.
[20:13]  You can hit escape twice to jump back in history
[20:17]  and then after you're done with the session
[20:19]  you can start cloud with a resume
[20:20]  to resume that session if you want
[20:22]  or dash dash continue.
[20:25]  And then anytime if you want to see more output
[20:27]  hit control R
[20:28]  and that'll show you the entire output
[20:30]  the same thing that cloud sees in its context window.
[20:39]  The next thing I want to talk about
[20:40]  is the cloud code SDK.
[20:41]  So we talked about this at the top
[20:43]  right after this, say it is doing a session
[20:46]  I think just across the hallway
[20:47]  and he's going to go super deep on the SDK.
[20:49]  If you had him played around with us
[20:51]  if you use the dash P flag and cloud
[20:54]  this is what the SDK is
[20:55]  and we've been waiting a bunch of features
[20:57]  over the last few weeks to make it even better.
[21:01]  So yeah, you can build on top of this
[21:02]  you can do cool stuff.
[21:03]  This is exactly the thing that cloud code uses.
[21:05]  It's exactly the same SDK.
[21:08]  And so for example something you can do is cloud dash P
[21:11]  so this is the CLI SDK.
[21:13]  You can pass a prompt.
[21:15]  You can pass some allowed tools
[21:16]  which could include specific batch commands.
[21:19]  And you can tell which format you want.
[21:21]  So you might want JSON
[21:23]  or you might want streaming JSON
[21:24]  if you want to process this somehow.
[21:26]  So this is awesome for building on.
[21:28]  We use this in CI all the time.
[21:30]  We use this for incident response.
[21:32]  We use this in all sorts of pipelines.
[21:34]  So really convenient.
[21:35]  Just think of it as like a unix utility.
[21:36]  You give it a prompt, it gives you JSON.
[21:38]  You can use this in any way.
[21:39]  You can pipe into it.
[21:40]  And pipe out of it.
[21:45]  The piping is also pretty cool.
[21:47]  So you can use like, for example,
[21:49]  Git status and pipe this in
[21:50]  and use JQ to select the result.
[21:54]  The combinations are endless.
[21:55]  And it's sort of this new idea.
[21:57]  It's like a super intelligent unix utility.
[21:59]  And I think we barely scratch the surface
[22:01]  of how to use this.
[22:02]  We're just figuring this out.
[22:04]  You can read from like a GCP bucket.
[22:06]  Read like a giant log and pipe it in
[22:08]  and tell cloud to figure out
[22:09]  what's interesting about this log.
[22:12]  You can fetch data from like the sentry CLI.
[22:15]  You can also pipe it in and have
[22:16]  cloud do something with it.
[22:24]  The final thing, and this is probably
[22:25]  like the most advanced use cases we see.
[22:27]  I'm sort of a cloud normie.
[22:28]  So I'll have usually like one cloud running at a time.
[22:31]  And maybe I'll have like a few terminal tabs
[22:33]  for a few different repos running at a time.
[22:35]  When I look at power users in and out of Anthropic,
[22:38]  almost always they're going to have like SSH sessions.
[22:41]  They'll have like TMAX tunnels into their cloud sessions.
[22:45]  They're going to have a bunch of checkouts
[22:46]  of the same repo so that they can run
[22:48]  a bunch of clouds in parallel in that repo.
[22:50]  Or they're using git work trees
[22:51]  to have some kind of isolation as they do this.
[22:54]  And we're actively working on making this easier to use.
[22:56]  But for now, like these are some ideas
[23:00]  for how to do more work in parallel with cloud.
[23:02]  You can run as many sessions as you want.
[23:05]  And there's a lot that you can get done in parallel.
[23:09]  So yeah, that's it.
[23:11]  I wanted to also leave some time for Q&A.
[23:13]  So I think this is the last slide that I have.
[23:16]  And yeah, if folks have questions,
[23:18]  there's Mike's on both sides.
[23:20]  And yeah, we'd love to answer any questions.
[23:24]  APPLAUSE
[23:35]  Let's get the blind to that.
[23:39]  I did.
[23:46]  Hey, Boris.
[23:47]  Thanks for building that cloud code.
[23:49]  And I was wondering what was the hardest implementation,
[23:51]  like part of the implementation for you of building it?
[23:57]  I think there's a lot of tricky parts.
[24:00]  I think one part that is especially tricky
[24:03]  is the things that we do to make bash command safe.
[24:07]  Bash is inherently pretty dangerous.
[24:08]  And it can change system state in unexpected ways.
[24:11]  But at the same time, if you have to manually approve
[24:16]  every single bash command, it's super annoying as an engineer.
[24:19]  And you can't really be productive
[24:20]  because you're just constantly approving every command.
[24:22]  And just kind of navigating how to do this safely
[24:25]  in a way that scales across the different kinds of code bases
[24:27]  people have, because not everyone runs their code
[24:29]  in a Docker container was pretty tricky.
[24:33]  And essentially, the thing we landed on
[24:34]  is there's some commands that are read only.
[24:36]  There's some static analysis that we do
[24:38]  in order to figure out which commands can be combined
[24:40]  in safe ways.
[24:41]  And then we have this pretty complex tiered permission system
[24:45]  so that you can allow a list and block
[24:46]  with commands at different levels.
[24:50]  And Boris, you mentioned giving an image to Cloud Code,
[24:54]  which made me wonder if there's some sort of multimodal
[24:57]  functionality that I'm not aware of,
[24:59]  is that are you just pointing it at an image
[25:01]  on the file system or something?
[25:03]  Yeah, so Cloud Code is fully multimodal.
[25:05]  It has been from the start.
[25:06]  It's in a terminal, so it's a little hard to discover.
[25:10]  But yeah, you can take an image
[25:11]  and just drag and drop it in that'll work.
[25:13]  You can give it a file path that'll work.
[25:15]  You can copy and paste the image in, and that works too.
[25:20]  So I'll use this pretty often for if I have
[25:22]  like a mock of something, I'll just drag and drop
[25:24]  in the mock, I'll tell it to implement it.
[25:26]  I'll give it up to a tier server
[25:27]  so it can iterate against it.
[25:29]  And yeah, it's just fully automated.
[25:34]  Hey, why did you build a CLI tool instead of an IDE?
[25:40]  Yeah, it's a good question.
[25:41]  I think there's probably two reasons.
[25:42]  One is we started this add-on-thropic.
[25:46]  And add-on-thropic people use a broad range of IDs.
[25:48]  And some people use VS Code, other people
[25:51]  used Z or X Code or VAM or EMAX.
[25:55]  And it was just hard to build something
[25:56]  that works for everyone.
[25:58]  And so terminal is just a common denominator.
[26:01]  The second thing is add-on-thropic.
[26:03]  We see up close how fast the model was getting better.
[26:08]  And so I think there's a good chance that by the end of the year,
[26:10]  people aren't using IDs anymore.
[26:13]  And so we want to get ready for this future.
[26:14]  And we want to avoid over investing in UI
[26:17]  and other layers on top, given
[26:19]  that the way the models are progressing,
[26:21]  it may not be used for work pretty soon.
[26:28]  Yeah.
[26:29]  How much of you, I don't know if this is on?
[26:32]  How much of you used code for machine learning modeling?
[26:36]  Almost that auto-amel experience.
[26:38]  I was curious what the experience has been so far with that.
[26:41]  Yeah, I think the question was, how much are we using
[26:44]  Quad Code for machine learning and modeling?
[26:47]  We actually use it for this a bunch.
[26:49]  So both engineers and researchers
[26:51]  add-on-thropic use Quad Code every day.
[26:54]  I think about 80% of people add-on-thropic
[26:56]  that are technical use Quad Code every day.
[26:59]  And hopefully you can see that in the product
[27:00]  and the amount of love and dog fooding we've put into it.
[27:04]  But this includes researchers who use tools like the notebook tool
[27:07]  to edit and run notebooks.
[27:09]  OK, very cool.
[27:10]  Thank you.
[27:13]  All right, and that's it.
[27:14]  Thanks.
