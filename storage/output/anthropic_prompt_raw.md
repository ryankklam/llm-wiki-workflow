[00:00] Hello everyone
[00:02] Thank you so much for joining me this afternoon in the breakout room
[00:07] The last session today of Code with Claude
[00:10] I hope you've all had a fantastic day so far
[00:12] My name is Margot Van Laar
[00:14] I am an applied AI engineer at Anthropic here in London
[00:18] And this afternoon we're going to be talking about the prompting playbook
[00:23] And prompting is arguably one of the fast skills
[00:27] If not the fast skill that we had to learn as engineers
[00:30]  when we fast started to work with LLMs
[00:33]  and even now it continues to be one of the most critical skills to building effective AI systems
[00:42]  So today we're going to discuss some best practices
[00:46]  In the context of two practical scenarios that you're probably encountering at work
[00:53]  The first is where you have an existing prompt in production
[00:57]  that you've been maintaining for some time
[01:00]  and possibly you're migrating it to a new model
[01:03]  or making a change to the architecture
[01:05]  and for some reason it's no longer working as well
[01:08]  The second scenario is where we're building an entirely new
[01:11]  agente use case from the ground up
[01:13]  and we need to build the prompt from 0 to 1
[01:17]  Now in order to illustrate these best practices
[01:22]  I don't just want to give you a list of dos and don'ts
[01:25]  I want to walk through a practical example that's been inspired by real prompts
[01:31]  that I've seen some of our customers work with who are building on cloth
[01:36]  So the prompt that we'll look at today is a miniaturised example
[01:42]  The prompts that you're working with are probably a lot longer
[01:45]  and more complex than the one we'll see today
[01:48]  but it's representative of some common problems that you might encounter when maintaining a prompt
[01:55]  So imagine that we have a prompt that multiple people have been collaborating on, contributing to
[02:03]  There's no clear owner, it covers a lot of different areas like policy, like tone, processes
[02:10]  We have some patches for previous models that we've made are greater to all mix together
[02:17]  It's built up and it's complex
[02:20]  And when we're migrating to a new model
[02:23]  we're finding that suddenly a lot of our test cases are no longer working as well as we expected
[02:30]  So what's actually going on here?
[02:32]  Well, in order to start unpacking that question
[02:35]  we need a starting point and that starting point is evaluations
[02:40]  We need evaluations to provide that rigor to understand whether a change to our prompt is actually correlating to an improvement in its performance
[02:52]  And we have different models which have different capabilities and different behaviours
[02:58]  And when you migrate to a different model it could be that your system is no longer working as well for two reasons
[03:06]  First of all, if the new model might be capable but it's behaving differently
[03:12]  And therefore we can tune our prompting to fix that behaviour
[03:16]  The second case is where actually the model that we're changing to isn't as capable and no amount of prompting is going to fix that
[03:24]  So we need to have an EVA suite to act as a way of testing that regression
[03:31]  So that we can apply our prompting best practices to that
[03:36]  So in the example that we're going to be looking at today, as I said, it's going to be a miniaturised example
[03:43]  We'll have five test cases in our EVA
[03:46]  In reality you'll have a lot more test cases in your EVA suite
[03:51]  But the key thing here is that it's representative of three key cases that we need to cover
[03:58]  So three key cases include having a control case which is a case which should always pass
[04:04]  It's something that we know the model handles well, it's unambiguous
[04:09]  The second is edge cases
[04:12]  And these are cases where we've seen the model fail before
[04:16]  And by including instructions into the prompt, we're making sure that same behaviour doesn't slip through again in the future
[04:25]  And finally and critically, we need to make sure that the model has a good understanding of its capabilities
[04:33]  Where it should be handing off to a human or where it should be point blank refusing to answer a request
[04:43]  So in the example that we're going to be looking at today, we'll be using a prompt for a customer support but for a telco company called Meridian Mobile
[04:55]  And these are the five test cases that we are going to be looking at today
[05:00]  We have a simple control case looking at what's the data limit in the basic plan
[05:07]  We're also looking at edge cases such as its ability to do calculations, such as calculating pro-ration bills
[05:17]  If I switch my plan halfway through the month, what will my bill look like?
[05:24]  We want to check that it's accurately addressing key questions which are covered by our policy
[05:30]  We need to make sure that it's escalating to a human whenever there is a billing error
[05:37]  And finally we want to make sure that our model isn't withholding any information that it has access to which it should be handing over to the customer
[05:47]  So what we're going to do in this process is we'll take our prompt and we'll run it on our V0 of the eFEL
[05:57]  And we'll see what our failure modes are and systematically target those failure modes one at a time to see if we can resolve those failure modes by prompting
[06:06]  And along the way we'll learn a little bit more about the kind of anti-patterns and traps to avoid
[06:13]  And this is representative of how we would apply these best prompting techniques in practice
[06:19]  We are rarely writing a prompt from scratch, we're often debugging an existing prompt
[06:27]  And best practice before we start targeting those failure modes specifically is to kind of apply our general prompting 101 best practices applying general hygiene to clean up before we do the eVEL run
[06:41]  So let's have a little look at the example that we're going to be using
[06:46]  So what we're looking at here first of all before we look at the prompt is just this five coded web app that I've made for the presentation today so that we can look at how we're iterating on the prompt together in this page here
[06:59]  I can easily run my eVELs on all five test cases and inspect the results in a little bit more detail
[07:08]  So before we have a look at the prompt I'm just going to run the eVELs in the background
[07:15]  This is a pretty good first pass at a prompt
[07:19]  When we look at this we've defined the bots role at the top
[07:25]  When we scroll down we've given it some data, we've given it some information on how to reason over the answers that it should be giving to the customer
[07:37]  It's giving us some critical instructions around the tone it should use how to do calculations etc. And then finally we're passing in our customer account context and our user message
[07:50]  So let's have a look at how our first pass at the eVELs did
[07:55]  So we can see as we expect our control case all of our test cases have passed
[08:01]  This is what we expect for this unambiguous test case but it's performing pretty poorly in these other areas
[08:10]  Now before we zoom in on those specific failure modes here let's do some general cleanup of our prompt
[08:23]  So as we mentioned when we look through this prompt there's a couple oddities here already
[08:29]  So for example first one is we're telling the bot that it's a human which just isn't true
[08:36]  We can see as we scroll down there's clearly some information here that has been copied directly from a website
[08:42]  So the key giveaway here is a reference to a hero image
[08:46]  There's even some references to cookies at the bottom
[08:51]  So we need to remove a bit of redundant information
[08:56]  When we look at the instructions here they're all grouped into one big paragraph
[09:01]  So we've got some reasoning here we've got instructions about the role, some critical instructions as well
[09:08]  Without a real way of unpacking policy from guidelines from tone etc.
[09:21]  Preempted some changes we want to make to this prompt and this is just a diff view of some of those changes
[09:27]  So what we've done is first of all added some structures
[09:30]  So you can see that we've added XML tags here to define the role, to separate general guidelines, to separate policy, to separate tone of voice etc.
[09:48]  So if we run that eVal.n on this new updated prompt, we should hopefully see an improvement in the output as is
[10:07]  So we can see just by clearing up the prompt we've already improved the model's performance on this prepaid scenario
[10:16]  There is an interesting regression there in that fifth hotspot case
[10:20]  And I don't want to worry too much about that now
[10:23]  There's going to be some natural level of variance in the different runs of the eVal
[10:29]  And we'll come back to that case specifically to see if we can make the prompt consistently better in that area
[10:35]  So what did we learn from this then?
[10:38]  Simply clearing up the prompt with a better structure, with a better role description has improved the performance
[10:45]  And this is the best practice that you can return to at any stage of writing and maintaining your prompts
[10:51]  Especially as your prompts get more detailed and more complex
[10:55]  A general root of thumb that I like to follow is if you're reading a prompt and you can't tell guidelines from policy from data
[11:03]  Most likely the model isn't able to either
[11:07]  So before looking at some of those cases in more detail, there's a little bit more general cleanup we can do
[11:15]  Specifically here looking at creating an output contract
[11:20]  This is a key best practice to follow if you're struggling with your output format consistency
[11:26]  Now in this case we have a customer support but we wanted to reply in a conversational tone
[11:31]  So it's unlikely to be a big issue in this case but it's something to bear in mind if you're dealing with more complex output structures like nested JSONs for example
[11:44]  So again if we go back to the prompts and see what fixes we can apply here
[11:51]  First of all we've added a section at the end where we have to find an output format for the model telling it to use XML tags to output the response
[12:04]  But the prompt is not always the most effective way of handling issues
[12:10]  We can also change things in the harness to ensure consistency to a higher degree
[12:16]  So what we've added here to the API call is a stop sequence which is going to detect that closing XML tag and tell the model to stop generating a response at that point
[12:30]  Now when I run the e-vail here I don't necessarily expect to see any clear improvement in performance
[12:37]  But it's a general best practice that we should be following and as I said is something that we should remember in particular when we have more complex output schemers
[12:49]  One thing to point out here as well if you do have a more complex output schema something like structured outputs can be incredibly helpful to ensure that consistency in a more programmatic way
[13:01]  Okay so after the cleanup then we can see that we now have two test cases which are consistently passing but we have three key failure modes, the pro-ration, the billing error and the hotspot
[13:14]  So let's isolate these one by one to iterate on the prompt and see the effect of that
[13:30]  First of all then the hotspot question so the question is how much hotspot data is on my unlimited plan
[13:37]  What we expect the model to do is state directly the amount of hotspot data that the customer has
[13:44]  And the reason this is a slightly complex case is because the customer test case that we're dealing with is on a legacy plan
[13:52]  So actually the current policy doesn't apply to them so if we see what's going on in the actual test case here the customer data which we're feeding to the prompt
[14:05]  Includes the amount of hotspot data that customer has they have five gigabytes but they also have a grandfather plan
[14:13]  So what we're seeing the model is actually telling the customer is the general the unlimited plan includes four gigabytes but since you're on a legacy plan you should go check this out yourself
[14:29]  So let's have a look at the prompt for in to see why the model is deflecting this question to the customer account URL rather than actually giving the information itself
[14:51]  Now if we read this from originally it said we changed our plans recently and the policy doc shows the current plan data and customers on grandfather's plan have different rates never give a customer the wrong plan details instead point them to the URL
[15:06]  So it's clear that this instruction this later will never give customer the wrong information is the instruction that the bought has been optimizing for
[15:16]  And you might recognize this as being very similar to a patch that you might have introduced in a previous model that you were using to avoid where the model was giving the customer the wrong information about that plan
[15:32]  Now as our models have evolved they have gotten much better at instruction following so it's likely that instructions like these have now become redundant and are actually being overfitted too
[15:46]  So what we're going to tell the model instead is give this balanced view where it says you know customers on grandfather's plan have different allowances but it's captured in the customer information that's given and that is the accurate source of truth
[16:01]  So running the eval here we should hopefully be addressing all of the test cases for the hotspot case now I am running this live so there could be some variability here but we see here that now clearly all of our test cases are passing
[16:22]  So what did we learn from this? Well we worry a lot about hallucinations or the invention of facts and numbers but actually the opposite can also happen the model can withhold information that it actually has access to
[16:41]  Now we saw here that this is likely a result of a patch that we introduced for a previous model and a best practice that we could follow here is actually using version control
[16:52]  Wherever we are making defensive changes in the prompt we are tracking the reason why we've introduced these sometimes they're necessary but in the future these kind of changes can produce unwanted effects so that we can backtrack on them
[17:12]  So the next failing test case then is this pro-ration calculation where a customer asks what if I upgrade to the 30 gigabyte plan what will my next build be and what we want the model to do is to perform some calculation and return exactly what the next build would be rather than giving some sort of failed output which is what we can see it's doing right now
[17:39]  if we look at what the model is returning it's clearly reasing through it it's doing a little bit of mental mass here and there but it's not really giving the customer a concrete answer and I wouldn't rely on this as being able to accurately give the customer a response
[17:55]  So if we look at the prompt then to see how we can fix this in the original prompt we can see that all the instructions that were given to it is telling it don't ever give a customer a vague answer
[18:20]  critical always calculates any pro-rated amounts correctly now telling the model to do a good job isn't particularly helpful when we don't give the model the capability to actually do a good job
[18:36]  we want to avoid the model doing mental maths so what we're going to introduce is give the model a tool so as saying in the prompt whenever you're doing any calculations please use the calculate pro-ration tool to do so
[18:50]  in order to introduce that tool we need to introduce it into the API to tell the model you have access to this tool we need to define the tool schema which tells the model what this tool does and when to use it
[19:06]  and then finally we need to actually implement the tool which is the maths behind how it should be doing that calculation
[19:15]  so running that evil then for another pass
[19:22]  we can see that all the test cases are now passing it's clearly done the maths using the tool in the background and retining the correct response
[19:39]  so the key lesson to take away here is instructions don't add capability telling the model it's critical to do a calculation right doesn't make it better at mental maths
[19:53]  so the correct approach was to give it a tool overall giving it the ability to reason over a harder problems and using tools to actually execute them reliably
[20:06]  so now we have one final failing test case which we need to address which is this billing error here
[20:15]  in this scenario there is a billing conflict and what we really want is the agent to escalate this to a human
[20:24]  and what we're seeing at doing instead is it's trying to explain to the customer what the reason behind it might be
[20:34]  and it's trying to kind of diagnose the problem itself
[20:39]  so in order to fix this behaviour let's again have a look what it was told in the prompt
[20:55]  we see in the initial instructions it was giving it says avoid escalating or transferring to a care specialist unless absolutely necessary as it cost approximately
[21:05]  eight dollars and it counts against our team's fast contract resolution
[21:09]  now this is only giving one side of the story right we're telling it what the cost is to escalating but not the benefit which means it's going to overfit again to not escalating the scenario
[21:23]  and second of all we've got this clear conflict between what we've defined in the eval in terms of what we want the model to do to do this escalation
[21:33]  thus is what we're actually telling it to do and the fix that's relevant here is to give it both sides of the story by saying it costs eight dollars to escalate a case
[21:46]  but actually if you get this wrong then it's going to cost you a refund as well as customer trust
[21:56]  again here we observed how the model optimizes for a goal and this kind of instruction is a common instruction to give it's quite similar to the one we saw earlier
[22:08]  where we didn't want it to overfit to a certain type of behavior but it's the kind of instruction that can be followed quite differently by different generations of models
[22:18]  and specifically as models become more intelligent we need to remember to state both sides of the trade-offs because our models are becoming better themselves at making those trade-offs themselves
[22:32]  so if we just go back to our eval then and run our final test case we should see that all of our evals are now passing correctly
[22:52]  so overall we looked at applying general hygiene principles how that can provide an initial uplift to the prompt making sure we're removing any redundant instructions which were initially intended as patches for previous model behavior
[23:07]  making sure we're giving it tools to do certain tasks reliably
[23:14]  now there's one other scenario that we introduced at the start which is one that you might also encounter in your work which is where we're building a new agent from scratch
[23:27]  and the example that we'll look at here is an agent whose purpose it is to create a week long retail staff schedule based on employee availability and other constraints
[23:41]  and when we're building a new agent from scratch we need to consider not just the prompt but also the model that we're using and the harness that we're using
[23:53]  so in this next example we're going to compare a number of approaches to explore the impact of those three different areas
[24:03]  so again I've just five coded up this web app so that we can walk through this problem in this demo
[24:12]  here I've just laid out what the problem is that we're addressing we have our eight employees on the right we have this schedule that we need to staff with the head count
[24:22]  and we have our constraints that must be satisfied in every scenario
[24:31]  now because we have these hard rules rather than using an L&M judge like we did in the previous case to do the grading
[24:39]  we can actually use a just a Python function which programmatically checks for every schedule that's generated how many violations were made
[24:53]  so to begin with we want to start simple we're going to use a simple prompt we're going to use the bare bones that we think will need with a model on it 4.6 to see how it performs and how we're going to help climb against that
[25:08]  so here is our baseline prompt we've already applied some of that general hygiene and those best practices that we saw earlier on using XML tags to structure the prompt
[25:19]  we've given it an output format as well now that we're giving a schedule we're asking it to output adjacent which if we don't give that output structure might lead to passing errors downstream
[25:34]  when we run the simple model on a first iteration of the eVALS all cases failed now just what we're looking at here is in our tests that we're essentially repeating
[25:55]  we're doing five trials here and these numbers are showing how many violations were made in each trial
[26:06]  in the outputs we can see that it's made a decent attempt at reasoning through the problem but it's burning a lot of tokens and it's clearly not checking its work as it's not getting to the right impact
[26:23]  so let's try a larger model a model which we know is better at reasoning so we're going to run it through opus 4.7 instead keeping everything else the same
[26:39]  now interestingly whilst all test cases are still failing you can see that the overall number of violations that opus is made has reduced significantly from Sonnet 4.6
[26:54]  so we're possibly onto something here right this isn't good enough to ship because it's still failing but clearly giving it more reasoning capability is helping drive it towards a better result
[27:08]  so what we're going to try next is using opus with adaptive thinking instead so it can decide for itself how much reasoning it needs to use to solve this issue
[27:25]  so no change to the prompt really just a change to the API here
[27:34]  so this now seems to reliably generate compliance schedules but it requires a lot more tokens
[27:43]  we're tripling essentially in the number of tokens that we're using here and we're tripling the latency
[27:50]  so we want to try and see if we can optimize that cost latency trade off a little bit more
[27:56]  this is latency 100 seconds obviously I'm running this one async for the purposes of time opus 4.7 hasn't magically gotten much faster since the last time you used it
[28:11]  so let's see if we can optimize a little bit more for the token latency trade off
[28:19]  what we haven't tried yet is using Sonnet 4.6 so a smaller model but we're a better prompt
[28:25]  we looked a lot at the prompt optimization in that last section so I've added a couple details to the prompt
[28:32]  in particular how to reason through this problem and most critically telling it to check its work before outputting it
[28:46]  so when I ran that e-file we see that it passes in two out of the five cases
[28:57]  now the failure modes that we're seeing is actually not violations of the scheduling requirements
[29:07]  but the model hasn't been able to finish the tasks within the output limit that we set
[29:16]  so whilst we could increase the max tokens that this model is able to use to get all five test cases passing
[29:26]  we see here that we're using even more tokens and this run hasn't even higher latency
[29:31]  so this is probably not the route that we want to go down
[29:35]  now as a final pass then we want to look at doing this a little bit more agentically
[29:44]  so we're going to use this generate evaluate repair loop where essentially the generator now creates a first draft of the schedule
[29:54]  and then we have a separate prompt which reports any specific violations that it made
[30:01]  so not programmatically checking it but checking it with an LLM
[30:05]  so we're checking for every rule and we're providing evidence of every violation
[30:11]  and we then have a third repair prompt which receives any violations that were made
[30:20]  and tries to make targeted fixes to it so we have three very simple prompts
[30:27]  but they're now running independently rather than trying to do everything in one large prompt
[30:37]  so we can see in this case our agentic approach has solved all of our test cases
[30:46]  with a much lower number of tokens and with a lower latency than trying Sonnet 4.6 with a better prompt
[30:56]  so going forward it seems like there's two appropriate approaches to take here
[31:02]  using Opus 4.7 with adaptive thinking or using this agentic loop
[31:07]  now moving forward we'd probably want to do a little bit more optimization on this loop
[31:13]  to try and get it to be more efficient but there's one key benefit as well from using this generate evaluate repair loop
[31:20]  and that is that you can put in software requirements at runtime
[31:26]  so in the evaluation prompt we can say Harry doesn't like working with Sally
[31:31]  so as much as possible try and separate them from working together
[31:35]  or we need a fudge shift on Wednesday for example
[31:39]  so it means that you're not having to make changes to the Python function
[31:44]  which is doing the evaluation in the back end every time to satisfy for any soft constraints
[31:49]  which might depend just on a case by case basis
[31:56]  so to wrap up then pulling all of those learnings together what did we see?
[32:03]  Well we looked at two scenarios, two scenarios which I as an engineer see most in my day today
[32:10]  which is where we're maintaining a prompt, we're migrating to a new model which has some different behaviors
[32:16]  and we're building a new use case from scratch. We saw that general hygiene principles following those cat
[32:25]  and immediately uplift the performance against a set of eVals
[32:30]  and that we need those eVals to be able to rigorously see any impacts of changing our prompt on the output
[32:37]  then we saw this process of targeting failure modes one by one
[32:42]  adding structure, avoiding long ban lists etc. were all things that helped push our model to the correct behavior
[32:51]  and then finally with our new agentic bot that we were building
[32:57]  we saw the impact of splitting into three separate prompt systems
[33:03]  so rather than using one prompt to address everything we're actually isolating different tasks
[33:10]  where it's easy and repeatable to separate out the steps that it needs to take every time
[33:16]  Thank you so much for attending this afternoon I hope you have a fantastic rest of your day
