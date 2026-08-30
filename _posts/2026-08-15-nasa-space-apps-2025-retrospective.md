---
layout: post
title: "NASA Space Apps Challenge 2025: The Story of Moon Forces"
description: "A story of NASA Space Apps 2025, a Moon colony, a chicken, a duck, and a game built under pressure."
date: 2026-08-15 00:00:00 +0600
categories:
  - devlog
  - news
tags:
  - nasa
  - space-apps
  - moon-forces
  - unity
  - gamedev
  - global-nominee
author: "Sabit Hasan Turzo"
image: "/assets/images/blog/nasa-retrospective.png"
featured: false
---

![youtube:Moon Forces Cinematic Showcase (NASA Space Apps 2025)](https://youtu.be/GMz0_QiFvX4)

A story of NASA Space Apps 2025, a Moon colony, a chicken, a duck, and a game built under pressure.

When NASA Space Apps Challenge 2025 arrived, Team Space Kitty did not begin with a huge game design document or a long development schedule.

They had participated in NASA Space Apps before, and they decided to return for another challenge.

This time, NASA presented “Your Home in Space: The Habitat Layout Creator,” a challenge about designing space habitats and thinking about important systems such as life support, power, food, waste management, sleeping areas, and other needs of people living in space.

The Space Kitty team took that idea in a different direction.

Instead of building only a habitat-layout tool, they decided to make a small Moon-based city-building and resource-management game.

They called it Moon Forces.

And they built most of it in only about four to five days.

## From a NASA Challenge to a Moon Colony

The original idea did not begin with the name Moon Forces.

The team first saw NASA's habitat challenge and decided to create a colony-building simulation around it. Tasrif Ibn Mizan, the team's game designer, already had experience thinking about city-building games and resource-management mechanics.

So the team went with a simple idea:

Build a colony on the Moon.

Keep it alive.

Manage its resources.

And don't let everything collapse.

The funny part is that the team did not spend a huge amount of time studying every line of the challenge description before starting.

They essentially saw the habitat problem and thought:

“Let's make a Moon colony game.”

The detailed systems came during development.

The name came even later.

“Moon Forces” was suggested by ChatGPT, the team liked how it sounded, and the name stayed. Even the logo was generated with the help of ChatGPT.

So, yes - the AI got a tiny credit in the origin story of a NASA Global Nominee project.

![Moon Forces Logo & Title Banner](/assets/images/projects/moon-forces/Moon%20Forces%20Nasa%20Space%20App%20Challenge%202025%20logo%20banner.png)

## Four People, Four Different Jobs

Team Space Kitty consisted of four members:

Tasrif Ibn Mizan - Lead and Game Designer  
Jafrin Alam Prima - Researcher  
Afnan Mayeen Adib - Editor  
Sabit Hasan Turzo - Game Developer  

The team was connected to RenderPhoenix, but Space Kitty was not exactly the same team as RenderPhoenix. Sabit and Tasrif were from RenderPhoenix, while the other two members joined the NASA competition team separately.

The team itself had a much more relaxed personality than its name might suggest.

While many teams at the competition looked extremely serious, Space Kitty had something a little different going on.

Sabit used a chicken avatar.

Tasrif used a duck avatar.

And their team name was simply Space Kitty.

Behind the cute avatars, however, they were working on a real-time simulation with limited time.

## The First Piece of the Game

Sabit was still relatively new to Unity.

He had only around six or seven months of Unity experience when development began.

But he had an approach that helped him work quickly: he usually built things that were already within his ability, and whenever something new was needed, he learned it.

He used Unity and Playmaker to build the game.

The first major system he created was the building system.

Players could select specific areas on the lunar surface. Clicking one of those areas opened a user interface where the player could choose which habitat or facility to build.

At first, the system was simple.

There was no giant free-form city-building grid.

There were selected locations, a building menu, and a Moon surface waiting for structures.

While Sabit worked on the game systems and UI, Tasrif was creating the 3D habitat models.

Sabit initially used placeholder objects.

When Tasrif pushed the finished models to GitHub, Sabit replaced the placeholders with the actual assets.

The project slowly started turning into something that looked like a real lunar settlement.

The GitHub repository documents the project as a Unity-based city-building and resource-management game, with C# and ShaderLab/HLSL used for development and effects.

![Moon Forces Top-Down Colony Layout](/assets/images/projects/moon-forces/Moon%20Forces%20Nasa%20Space%20App%20Challenge%202025%20top%20view.png)

## Building a Colony Means Managing Everything

Moon Forces was built around a simple problem:

Every building needs something.

And every new building can create another problem.

Players begin with a limited amount of resources and must construct facilities to keep the colony running.

The game includes resources such as:

- Oxygen
- Water
- Food
- Crops
- Electricity
- Trash
- Metal
- Population

The player might build a greenhouse to help produce resources and oxygen.

They might build water-related facilities.

They need solar panels to generate electricity.

They need habitats for incoming space crews.

But building more things does not automatically make the colony better.

It can actually make the situation worse.

Build too many habitats, and resource consumption increases.

Build too many greenhouses, and electricity demand increases.

Build too many water generators, and electricity becomes harder to maintain.

Suddenly, the player has a much larger colony - but also a much bigger problem.

That became the main challenge of Moon Forces:

Growth had a cost.

## When the Game Finally Felt Like a Game

For Sabit, there was a particular moment when Moon Forces stopped feeling like a collection of systems and started feeling like an actual game.

It was when the world began moving on its own.

The team added a day-and-night system.

The Sun rotated.

Days passed.

Rockets arrived at the Moon and returned toward Earth.

Rovers moved around the habitat.

The world was no longer sitting still.

Something was happening.

The resource systems were also running at the same time.

Buildings consumed resources.

Other buildings produced them.

The player had to keep the colony balanced.

For Sabit, this was the point where the project became a game because there was finally a loop:

Start -> build -> resources change -> day passes -> colony continues -> next day begins.

The loop keeps going.

And that feeling of a living system was more important than simply having lots of features.

![Moon Forces Gameplay & Settlement Overview](/assets/images/projects/moon-forces/Moon%20Forces%20Nasa%20Space%20App%20Challenge%202025%20banner%20screenshot.png)

## The Moon's Long Days Were Part of the Challenge

The game included a simple day-and-night cycle.

One in-game day lasted about 180 seconds, with speed controls planned around faster simulation. The project documentation describes a 14-day/14-night monthly cycle and solar panels that generate electricity during the daytime.

The day/night system was not intended to simulate every detail of the real Moon.

Instead, it created a gameplay problem.

When night arrived, the solar panels stopped producing electricity.

That meant the player had to think ahead.

If electricity production was too low, the colony could quickly run into trouble.

The player had to balance production and consumption rather than simply building as much as possible.

## Rovers That Made the Moon Feel Alive

The rovers were not an enormous scientific simulation.

They were there to make the colony feel like a place where things were happening.

They moved around the habitats and explored the lunar surface.

They could look as if they were collecting or testing samples and moving through the settlement.

Sabit used Unity's navigation system to give the vehicles paths around the environment.

It was a small feature, but visually it changed the project.

A static Moon surface became a world with movement.

## There Was No Winning the Moon

Interestingly, Moon Forces did not have a traditional victory condition in its final version.

There was no:

“Congratulations! You colonized the Moon!”

Instead, the days simply kept increasing.

The player continued managing the colony for as long as possible.

But if an important resource reached zero, the game ended.

That created a survival-style loop rather than a traditional campaign.

The project documentation also describes resource failure as a loss condition, while its original GDD listed a future win condition as something that had not yet been fully defined.

And that is important because Moon Forces was never meant to be a finished commercial game.

It was a focused simulation project created for NASA Space Apps.

The team had once considered publishing it on the Play Store, but that never happened.

## Four or Five Days to Build It

Perhaps the most surprising part of the project is how quickly it was made.

The team had only around four to five days to build the game.

There was no long production cycle.

No year-long development.

No large studio.

Just a small team, a challenge, and a deadline.

Sabit says that development itself did not feel extremely difficult because he usually worked within his abilities and learned new things when necessary.

The biggest challenge was not necessarily the code.

It was the clock.

And then something unexpected happened.

## When the Team Lost Its Game Designer

Near the end of development, Tasrif suddenly had a serious problem at home.

A problem with his landlord meant that he had to leave his home, and basic utilities such as electricity and gas were shut off.

For several days, he was completely out of contact.

The team was almost finished with the game.

But there was still final work to do.

Tasrif had already created additional habitat models, but because he was no longer available, the team could not properly integrate all of those extra habitats into the final version.

Sabit continued working.

He polished the existing game.

He added more UI.

He worked on the menus.

He added sounds.

And eventually, he built the final game.

Meanwhile, Jafrin remained heavily involved from the competition side.

She continuously contacted Sabit, monitored the development, and handled the NASA Space Apps dashboard and submission information.

Afnan worked on the project's video presentation.

And according to the team, that video became one of the fun parts of the project.

So while one member was dealing with an unexpected personal crisis, another was finishing the game, another was managing the submission, and another was turning the project into a presentation.

It was not exactly a calm development cycle.

## Then Came Submission Day

Once Moon Forces was submitted, the team was done.

They did not expect it to become a commercial game.

They were not waiting for millions of players.

The project had done what they wanted it to do:

They had taken a NASA challenge and turned it into an interactive lunar habitat simulation.

Then something unexpected happened.

## From Dhaka to the Global Stage

Before the global results arrived, Space Kitty received another piece of news.

The team had competed in the Dhaka Division, where they placed 2nd Runner-Up after competing among more than 850 participants/projects in the division, according to the team's recollection.

Sabit was actually offline when the news arrived.

Instead of hearing it directly from the organizers, he received a WhatsApp message from a friend:

Congratulations.

He was surprised.

Soon, the team attended the prize-giving ceremony at BASIS in Karwan Bazar.

There were students everywhere wearing NASA shirts.

The team received prizes, a crest, and medals.

For a small team that had built its project in only a few days, it was a memorable moment.

But there was another announcement still to come.

Weeks later, Space Kitty learned that Moon Forces had become a NASA Space Apps 2025 Global Nominee.

NASA maintains a dedicated Global Nominees category for the 2025 competition.

The team did not make it to the Global Finalists or Global Winners stage.

But they had already taken their small Moon colony much further than they expected.

## A Game That Proved Something

For Sabit, perhaps the biggest achievement was not the medal or the Global Nominee title.

It was discovering what he could actually build.

He had only around six or seven months of Unity experience.

Then, in roughly four or five days, he helped turn an idea into a working simulation.

He built the building system.

He created the resource systems.

He built UI.

He implemented the day/night cycle.

He worked with navigation systems.

He added the final polish.

And when one teammate became unavailable, he finished the project.

Moon Forces showed him that he could push a game from an empty project toward something playable in a very short amount of time.

That was a lesson that could not easily be learned from tutorials alone.

## Why Hackathons Matter

The team also discovered something bigger through NASA Space Apps.

International hackathons bring people from very different places together to work on the same problems.

Someone from the United States can be working on the same NASA challenge as someone from Bangladesh.

The location does not decide who gets to participate.

The same problem is presented to everyone.

Everyone gets the opportunity to try.

For Space Kitty, that was one of the most exciting parts of the experience.

NASA Space Apps gave a small team from Bangladesh a chance to build something, submit it to an international competition, and eventually see its name among the global nominees.

## And Then There Was Space Kitty

There is also a small detail that probably says more about the team than any formal description could.

While other teams were taking the competition very seriously, Space Kitty showed up with a chicken avatar, a duck avatar, and a cute team name.

They had fun.

They experimented.

They made a game.

They did not build everything they originally imagined.

They did not have time to add every habitat.

They did not implement a victory condition.

They did not turn the project into a commercial release.

But they finished.

And that mattered.

## Back to NASA Space Apps

Moon Forces was not the end of the story.

On August 29, 2026, the team registered again for NASA Space Apps.

This time, they are coming back with experience.

They have already participated in previous challenges.

They know how the competition works.

They know what a few days of development feels like.

They know what can go wrong.

And, perhaps most importantly, they now know one thing they did not know in 2025:

Read the full challenge description first.

Because this time, Team Space Kitty is coming back prepared.

And maybe this time, the chicken and duck are bringing a little more firepower - in the completely metaphorical game-development sense.

## Project links

- [NASA Space Apps 2025 - Your Home in Space: The Habitat Layout Creator](https://www.spaceappschallenge.org/2025/challenges/your-home-in-space-the-habitat-layout-creator/)
- Team Space Kitty - NASA Space Apps 2025
- [Moon Forces - GitHub Repository](https://github.com/cristoparker/Space-Kitty-Project)
- [Moon Forces - Cinematic Shots Video](https://youtu.be/GMz0_QiFvX4)

One thing I especially like about this version: it doesn't oversell Moon Forces as some massive finished game. It tells the actual story - four people, 4-5 days, a NASA challenge, a bunch of systems, an unexpected team problem, one developer finishing the build, and then somehow ending up as a Global Nominee. That's much more interesting than pretending everything went perfectly.
