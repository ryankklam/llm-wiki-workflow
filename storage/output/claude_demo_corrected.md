# 抄作业！Claude负责人亲自演示28分钟干货！

## 视频信息
- **标题**：抄作业！Claude负责人亲自演示28分钟干货！
- **作者**：Unknown
- **平台**：小红书
- **小红书ID**：5cS2uUjm6wL
- **日期**：2026-05-26
- **原始链接**：http://xhslink.com/o/5cS2uUjm6wL

---

## 开场介绍

[00:00] Hello everyone

[00:05] I'm Boris, I'm a member of technical staff here at Anthropic

[00:09] and I created Claude Code, and here to talk to you a little bit about some practical tips and tricks for using Claude Code.

[00:16] It's going to be very practical, I'm not going to go too much into the history or the theory or anything like this.

[00:22] And yeah, before we start, actually can we get a quick show of hands who has used Claude Code before?

[00:29] Yeah, alright that's what we like to see.

[00:31] For everyone that didn't raise your hands, I know you're not supposed to do this while people are talking, but if you can open your laptop and type this, and this will help you install Claude Code, just so you can follow along for the rest of the talk.

[00:52] All you need is Node.js, if you have it that should work.

[00:58] If you want to install all of the plugins... yeah if you don't have to follow along, but if you don't have it yet, this is your chance to install it so you can follow along.

---

## Claude Code 简介

[01:11] So what is Claude Code?

[01:13] Claude Code is a new kind of AI assistant, and there's been different generations of AI assistants for coding.

[01:20] Most of them have been about completing like a line at a time, completing a few lines of code at a time.

[01:26] Claude Code is not for that, it's fully agentic, so it's meant for building features, for writing entire functions, entire files, fixing entire bugs at the same time.

[01:38] And what's kind of cool about Claude Code is it works with all of your tools, and you don't have to change out your workflow, you don't have to swap everything to start using it.

[01:45] So whatever IDE you use, if you use VS Code, or if you use Xcode, or if you use JetBrains IDE... there's some people that are on the topic that you can't pry them from their cold dead hands, but they use Claude Code, because Claude Code works with every single IDE, every terminal out there.

[02:03] It will work locally, over remote SSH, over Tmux, whatever environment you're in, you can run it.

---

## 开始使用 Claude Code

[02:12] It's general purpose, and this is something where if you haven't used these kind of free form coding assistants in the past, it can be kind of hard to figure out how to get started.

[02:21] Because you open it up and you just see a prompt bar and you might wonder like, what do I do with this? What do I type in?

[02:27] It's a power tool so you can use it for a lot of things, but also because it can do so much, we don't try to guide you towards a particular workflow, because really you should be able to use it however you want as an engineer.

[02:42] As you open up Claude Code for the first time, there's a few things that we recommend doing to get your environment set up, and these are pretty straightforward.

[02:50] So run terminal setup, this will give you Shift+Enter for new lines, so you don't have to do like backslashes enter new lines. This is... you know, it makes it a little bit nicer to use.

[02:58] Do `/theme` to set light mode or dark mode or Daltonize themes.

[03:03] You can do `/install-github-app`, so today we announced a GitHub app where you can add mention Claude on any GitHub issue or pull request. So to install it just run this command in your terminal.

[03:17] You can customize the set of allowed tools that you can use, so you're not prompted for it every time. This is pretty convenient, for stuff that I'm prompted about a bunch, I'll definitely customize it in this way so I don't have to accept it every time.

[03:30] And something that I actually do is for a lot of my prompts, I won't hand type them into Claude Code. If you're on macOS, you can go into your system settings under accessibility as dictation, and you can enable it.

[03:41] And so something I do is you just hit like the dictation key twice and you can just speak your prompt, and it helps a lot to have specific prompts. So this is actually pretty awesome, you can just talk to Claude Code and like you would another engineer, and you don't have to type a lot of code.

---

## 核心使用技巧：代码库问答 (Codebase Q&A)

[03:59] So when you're starting out with Claude Code, it's so freeform and it can do everything, what do you start with?

[04:04] The thing I recommend above everything else is starting with code based Q&A, so just asking your question, asking questions about your code base.

[04:12] This is something that we teach new hires at Anthropic. So on the first day in technical onboarding, you learn about Claude Code, you download it, you get it set up, and then you immediately start asking questions about the code base.

[04:23] And in the past when you were doing technical onboarding, it's something that taxes the team a lot, right? You have to ask other engineers on the team questions, you have to look around the code, and this takes a while. You have to figure out how to use the tools, this takes a long time.

[04:36] With Claude Code you can just ask Claude Code, and it will explore the code base, it will answer these kind of questions.

[04:42] And so at Anthropic, onboarding used to take about two or three weeks for technical hires, it's now about two or three days.

[04:51] What's also kind of cool about Q&A is we don't do any sort of indexing, so there's no remote database with your code, we don't upload it anywhere. Your code stays local, we do not train generative models on the code, so it's there, you control it.

[05:04] There's no indices or anything like this, and what that means is also there's no setup. So you start Claude, you download it, you start it, there's no indexing, you don't have to wait, you can just use it right away.

---

## 进阶使用技巧

[05:16] This is a technical talk, so I'm going to show some very specific prompts and very specific code samples that you can use and hopefully improve and up level your Claude Code experience.

[05:25] So some kind of questions that you can ask is you know like how is this particular piece of code used, or how do I instantiate this thing.

[05:31] And Claude Code won't just do like a text search and try to answer this, it will often go a level deeper and it will try to find examples of how is this class instantiated, how is it used, and it will give you a much deeper answer.

[05:43] So something that you would get out of a wiki or documentation, instead of just like Command+F.

[05:49] Something that I do a lot also is ask it about git history. So for example, you know, why does this function have 15 arguments and why are the arguments named this weird way?

[05:58] And this is something I bet in all of our codebases you have some function like this or some class like this.

[06:04] And Claude Code can look through git history and it will look to figure out how did these arguments get introduced and who introduced them and what was the situation, what are the issues that those commits linked to, and it will look through all this and summarize it.

[06:15] And you don't have to tell it that in all this detail, you just ask it, so just say look through git history and it will know to do this.

[06:23] The reason it knows it by the way is not because we prompted it to, there's nothing in the System Prompt about looking through git history. It knows it because the model was awesome, and if you tell it to use git, it will know how to use git. So we're lucky to be building on such a good model.

[06:38] I often ask about GitHub issues, so you know, I can use web fetch and I can fetch issues and work up context on issues too, and this is pretty awesome.

[06:48] And this is something that I do every single Monday in our weekly stand up, is I ask "what did I ship this week?" and Claude Code looks to the log, it knows my username and it will just give me a nice readout of everything I shipped, and I'll just copy and paste that into a doc.

[07:01] So yeah that's tip number one. For people that have not used Claude Code before, if you're just showing it to someone for the first time, onboarding your team, the thing we definitely recommend is start with code base Q&A.

[07:12] Don't start by using fancy tools, don't start by editing code, just start by asking questions about the code base.

[07:17] And that will teach people how to prompt, and it will start teaching on this boundary of like what can Claude Code do, what is it capable of, versus what do you need to hold its hand with a little bit more, what can be one-shotted, what can be two-shotted, three-shotted, what do you need to use interactive mode for in a REPL.

---

## 代码编辑与 Agent 工作流

[07:35] Once you're pretty comfortable with Q&A, you can dive into editing code, this is the next thing.

[07:43] And the cool thing about any sort of agent like using an LLM in an agentic way is you give it tools and it's just like magic, it figures out how to use the tools.

[07:53] And with Claude Code, we give it a pretty small set of tools, it's not a lot. And so it has a tool to edit files, it has a tool to run bash commands, it has a tool to search files, and it will string these together to explore the code, brainstorm, and then finally make edits.

[08:09] And you don't have to prompt it specifically to use this tool and this tool and this tool, you just say you know do this thing and it'll figure out how to do it, it'll string it together in the right way that makes sense for Claude Code.

[08:22] There's a lot of ways to use this. Something I like to do sometimes is before having Claude jump in to write code, I'll ask it to brainstorm a little bit or make a plan. This is something we highly recommend.

[08:33] And something I see sometimes is people, you know they take Claude Code and they ask it hey implement this enormous like a 3,000-line feature, and sometimes it gets this right on the first shot, but sometimes what happens is the thing that it builds is not at all the thing that you want it.

[08:48] And the easiest way to get the result you want is ask it to think first, so brainstorm ideas, make a plan, run it by me, ask for approval before you write code.

[08:58] And you don't have to use plan mode, you don't have to use any special tools to do this, all you have to do is ask Claude and it'll know to do this. So just say "before you write code make a plan", that's it.

[09:10] This is also I want to share this one, "commit and push for me", this is a really common incantation that I use.

[09:15] There's nothing special about it, but Claude is kind of smart enough to interpret this. So it'll make a commit, it'll push it to the branch, make a branch and then make a pull request for me on GitHub.

[09:22] You don't have to explain anything, it'll look through the code, it'll look through the history, it'll look through the Git log by itself to figure out the commit format and all the stuff, and it'll make the commit and push it the right way.

[09:31] Again, we're not system prompting it to do this, it just knows how to do this, the model was good.

---

## 工具集成：Bash 工具与 MCP

[09:39] As you get a little bit more advanced, you're going to want to start to plug in your team's tools, and this is where Claude Code starts to really shine.

[09:47] And there's generally two kinds of tools. So one is bash tools, and an example of this, I just made up this like "brew CLI", this isn't a real thing, but you can say use this CLI to do something, and you can tell Claude Code about this, and you can tell it to use for example like `--help` to figure out how to use it.

[10:03] And this is efficient, if you find yourself using it a lot, you can also dump this into your Claude.md which we'll talk about in a bit, so Claude can remember this across sessions.

[10:11] But this is a common pattern we follow at Anthropic and we see external customers use too.

[10:16] And same thing with MCP, Claude Code can use bash tools, you can use MCP tools. So just tell it about the tools, and you can add MCP tools, and you can tell it how to use it, and it'll just start using it.

[10:29] And this is extremely powerful, because when you start to use Claude Code on a new code base, you can just give it all of your tools, all the tools your team already uses for this code base, and Claude Code can use it on your behalf.

---

## 工作流模式

[10:41] There's a few common workflows, and this is the one that I talked about already, so kind of do a little bit of exploration, do a little bit of planning, and ask me for confirmation before you start to write code.

[10:55] These other two on the right are extremely powerful. When Claude has some way to check its work, so for example by writing unit tests or screenshotting with Puppeteer, or screenshotting the iOS simulator, then it can iterate, and this is incredible.

[11:13] Because if you give it for example a mock and you say build this web UI, it'll get it pretty good, but if you let it iterate two or three times, often it gets it almost perfect.

[11:23] So the trick is give it some sort of tool that it can use for feedback to check its work, and then based on that it will iterate by itself, and you're going to get a much better result.

[11:33] So whatever your domain is, if it's unit tests or integration tests, or screenshots for apps or web, or anything, just give it a way to see its result and it'll iterate and get better.

[11:46] So these are the next steps: teach Claude how to use your tools, and figure out the right workflow. If you want Claude to jump in and code, if you want it to brainstorm a little bit, make a plan, if you want it to iterate, kind of have some sense of that, so you know how to prompt Claude to do what you want.

---

## Claude.md：上下文管理

[12:04] As you go deeper, beyond tools you want to start to give Claude more context, the smarter the decisions will be.

[12:10] Because as an engineer working in a code base, you have a ton of context in your head about your systems and all the history and everything else. So there's different ways to give this to Claude, and as you give Claude more context, it will do better.

[12:22] There's different ways to do this. The simplest one is what we call Claude.md, and Claude.md is the special file name.

[12:28] The simplest way to put it is in the project root, so the same directory you start Claude Code, put a Claude.md in there, and that will get automatically read into context at the start of every session.

[12:40] And essentially the first user turn will include the Claude.md.

[12:46] You can also have a local Claude.md, and this one you don't usually check into source control. So Claude.md you should check into source control, share with your team so that you can read it once and share it with your team. This one you don't check in, it's just for you.

[13:02] The kinds of things you put in Claude.md: common MCP tools, architectural decisions, important files, anything that you would typically need to know in order to work in this code base.

[13:12] Try to keep it pretty short, because if it gets too long, it's just going to use up a bunch of context and it's usually not that useful. So just try to keep it as short as you can.

[13:22] For example in our code base, we have common bash commands, we have a style guide, we have a few core files.

[13:30] All the other Claude.md files... these are the Claude.md files that will get pulled in automatically, but then also you can put Claude.md files in nested directories, and those will get automatically pulled when Claude works in those directories.

[13:48] And of course if your company maybe wants a Claude.md that shares across all the different code bases, and you want to manage it on behalf of your users, you can put it in your enterprise root and that will get pulled in automatically.

---

## 快速参考与快捷键

[18:50] This is just a quick reference sheet.

[18:51] So anytime you can hit Shift+Tab to accept edits, and this switches you into auto accept edits mode, so bash commands still need approval, but edits are auto accepted, and you can always ask Claude to undo them later.

[19:04] For example, I'll do this if I know Claude's on the right track, or if it's writing unit tests and iterating on tests, or usually just switch into auto accept mode so I don't have to okay every single edit.

[19:14] Anytime you want Claude to remember something, so for example if it's not using a tool correctly and you want it to use it correctly from now on, just type the pound sign and then tell it what to remember, and it'll remember it, it'll incorporate it into Claude.md automatically.

[19:28] If you ever want to drop down to bash mode so just run a bash command, you can hit the exclamation mark and type in your command that'll run locally, but that also goes into the context window so Claude will see it on the next turn.

[19:39] And this is pretty good for long running commands if you know exactly what you want to do, or any command that you want to get into context and Claude will see the command and the output.

[19:48] You can add mention thousand folders.

[19:50] Anytime you can hit escape to stop what Claude is doing. No matter what Claude is doing, you can always safely hit escape. It's not going to corrupt the session, it's not going to mess anything up.

[19:59] So maybe Claude is doing a file edit, I'll hit escape, I'll tell it what to do differently, or maybe it suggested a 21 edit and I'm like actually 19 of these lines look perfect but one line you should change. I'll hit escape, I'll tell it that and then I'll tell it to redo that.

[20:13] You can hit escape twice to jump back in history, and then after you're done with the session you can start Claude with `--resume` to resume that session if you want, or `--continue`.

[20:25] And then anytime if you want to see more output, hit Control+R and that'll show you the entire output, the same thing that Claude sees in its context window.

---

## Claude Code SDK

[20:39] The next thing I want to talk about is the Claude Code SDK.

[20:41] So we talked about this at the top, right after this, Saad is doing a session I think just across the hallway, and he's going to go super deep on the SDK.

[20:49] If you haven't played around with it, if you use the `-p` flag in Claude, this is what the SDK is, and we've been adding a bunch of features over the last few weeks to make it even better.

[21:01] So yeah, you can build on top of this, you can do cool stuff. This is exactly the thing that Claude Code uses, it's exactly the same SDK.

[21:08] And so for example something you can do is `claude -p`, so this is the CLI SDK. You can pass a prompt, you can pass some allowed tools which could include specific bash commands, and you can tell which format you want. So you might want JSON or you might want streaming JSON if you want to process this somehow.

[21:26] So this is awesome for building on. We use this in CI all the time, we use this for incident response, we use this in all sorts of pipelines. So really convenient, just think of it as like a Unix utility. You give it a prompt, it gives you JSON, you can use this in any way, you can pipe into it and pipe out of it.

[21:45] The piping is also pretty cool. So you can use like for example `git status` and pipe this in and use `jq` to select the result. The combinations are endless.

[21:55] And it's sort of this new idea, it's like a super intelligent Unix utility. And I think we barely scratch the surface of how to use this, we're just figuring this out.

[22:04] You can read from like a GCP bucket, read like a giant log and pipe it in and tell Claude to figure out what's interesting about this log. You can fetch data from like the Sentry CLI, you can also pipe it in and have Claude do something with it.

---

## 高级用法：并行会话

[22:24] The final thing, and this is probably like the most advanced use cases we see.

[22:27] I'm sort of a Claude normie, so I'll have usually like one Claude running at a time, and maybe I'll have like a few terminal tabs for a few different repos running at a time.

[22:35] When I look at power users in and out of Anthropic, almost always they're going to have like SSH sessions, they'll have like Tmux tunnels into their Claude sessions.

[22:45] They're going to have a bunch of checkouts of the same repo so that they can run a bunch of Claudes in parallel in that repo, or they're using git worktrees to have some kind of isolation as they do this.

[22:54] And we're actively working on making this easier to use, but for now, like these are some ideas for how to do more work in parallel with Claude.

[23:02] You can run as many sessions as you want, and there's a lot that you can get done in parallel.

[23:09] So yeah, that's it. I wanted to also leave some time for Q&A. So I think this is the last slide that I have. And yeah, if folks have questions, there's mics on both sides. And yeah, we'd love to answer any questions.

---

## Q&A 环节

[23:35] Let's get the mic to that.

[23:46] Hey, Boris. Thanks for building Claude Code. And I was wondering what was the hardest implementation, like part of the implementation for you of building it?

[23:57] I think there's a lot of tricky parts. I think one part that is especially tricky is the things that we do to make bash command safe.

[24:07] Bash is inherently pretty dangerous, and it can change system state in unexpected ways. But at the same time, if you have to manually approve every single bash command, it's super annoying as an engineer, and you can't really be productive because you're just constantly approving every command.

[24:22] And just kind of navigating how to do this safely in a way that scales across the different kinds of code bases people have, because not everyone runs their code in a Docker container, was pretty tricky.

[24:33] And essentially, the thing we landed on is there's some commands that are read only, there's some static analysis that we do in order to figure out which commands can be combined in safe ways. And then we have this pretty complex tiered permission system so that you can allow list and block list commands at different levels.

[24:50] And Boris, you mentioned giving an image to Claude Code, which made me wonder if there's some sort of multimodal functionality that I'm not aware of, is that are you just pointing it at an image on the file system or something?

[25:03] Yeah, so Claude Code is fully multimodal, it has been from the start. It's in a terminal, so it's a little hard to discover. But yeah, you can take an image and just drag and drop it in, that'll work. You can give it a file path, that'll work. You can copy and paste the image in, and that works too.

[25:20] So I'll use this pretty often for if I have like a mock of something, I'll just drag and drop in the mock, I'll tell it to implement it. I'll give it up to a tier server so it can iterate against it. And yeah, it's just fully automated.

[25:34] Hey, why did you build a CLI tool instead of an IDE?

[25:40] Yeah, it's a good question. I think there's probably two reasons. One is we started this at Anthropic, and at Anthropic people use a broad range of IDEs. And some people use VS Code, other people use Zed or Xcode or Vim or Emacs.

[25:55] And it was just hard to build something that works for everyone, and so terminal is just a common denominator.

[26:01] The second thing is at Anthropic, we see up close how fast the model was getting better. And so I think there's a good chance that by the end of the year, people aren't using IDEs anymore. And so we want to get ready for this future, and we want to avoid over investing in UI and other layers on top, given that the way the models are progressing, it may not be used for work pretty soon.

[26:28] Yeah.

[26:29] How much of you, I don't know if this is on? How much are you using Claude Code for machine learning modeling? Almost that auto-ML experience. I was curious what the experience has been so far with that.

[26:41] Yeah, I think the question was, how much are we using Claude Code for machine learning and modeling? We actually use it for this a bunch. So both engineers and researchers at Anthropic use Claude Code every day.

[26:54] I think about 80% of people at Anthropic that are technical use Claude Code every day. And hopefully you can see that in the product and the amount of love and dog fooding we've put into it.

[27:04] But this includes researchers who use tools like the notebook tool to edit and run notebooks.

[27:09] OK, very cool. Thank you.

[27:13] All right, and that's it. Thanks.

---

## 关键要点总结

1. **Claude Code 是什么**：Anthropic 推出的 AI 编程助手，完全 Agentic，可编写完整功能、文件和修复 Bug
2. **入门建议**：从代码库问答 (Codebase Q&A) 开始，这是 Anthropic 新员工培训的第一步
3. **工作流模式**：先探索/规划，获得确认后再编写代码；提供反馈工具让 Claude 自我迭代
4. **工具集成**：支持 Bash 工具和 MCP (Model Context Protocol) 工具
5. **Claude.md**：项目根目录下的特殊文件，用于存储上下文、常用命令、架构决策等
6. **快捷键**：
   - Shift+Tab：自动接受编辑
   - # ：让 Claude 记住某事（自动写入 Claude.md）
   - ! ：执行 Bash 命令
   - Esc：停止当前操作
   - Ctrl+R：查看完整输出
7. **SDK**：`claude -p` 命令可将 Claude 作为 Unix 工具使用，支持 JSON 输出和管道操作
8. **多模态**：支持图片输入（拖拽、文件路径、复制粘贴）
