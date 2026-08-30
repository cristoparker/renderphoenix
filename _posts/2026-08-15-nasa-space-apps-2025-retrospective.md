---
layout: post
title: "NASA Space Apps Challenge 2025: The Story of Moon Forces"
description: "A story of NASA Space Apps 2025, a Moon colony, a chicken, a duck, and a game built under pressure in four to five days."
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

*A story of NASA Space Apps 2025, a Moon colony, a chicken, a duck, and a game built under pressure.*

When the **NASA Space Apps Challenge 2025** arrived, Team Space Kitty did not begin with a huge game design document or a long development schedule.

They had participated in NASA Space Apps before, and they decided to return for another challenge. This time, NASA presented **“Your Home in Space: The Habitat Layout Creator,”** a challenge about designing space habitats and thinking about important systems such as life support, power, food, waste management, sleeping areas, and other needs of people living in space.

The Space Kitty team took that idea in a different direction: instead of building only a habitat-layout tool, they decided to make a small Moon-based city-building and resource-management game.

They called it **Moon Forces**. And they built most of it in only about **four to five days**.

---

## From a NASA Challenge to a Moon Colony

The original idea did not begin with the name *Moon Forces*.

The team first saw NASA's habitat challenge and decided to create a colony-building simulation around it. **Tasrif Ibn Mizan**, the team's lead and game designer, already had experience thinking about city-building games and resource-management mechanics.

So the team went with a simple idea:
- Build a colony on the Moon.
- Keep it alive.
- Manage its resources.
- And don't let everything collapse.

The funny part is that the team did not spend a huge amount of time studying every line of the challenge description before starting. They essentially saw the habitat problem and thought:

> *“Let's make a Moon colony game.”*

The detailed systems came during development. The name came even later: **“Moon Forces”** was suggested by ChatGPT, the team liked how it sounded, and the name stayed. Even the logo was generated with the help of ChatGPT.

So, yes—the AI got a tiny credit in the origin story of a NASA Global Nominee project. :3

---

## Four People, Four Different Jobs

**Team Space Kitty** consisted of four members:

- **Tasrif Ibn Mizan** — Lead and Game Designer
- **Sabit Hasan Turzo** — Game Developer
- **Jafrin Alam Prima** — Researcher & Submission Lead
- **Afnan Mayeen Adib** — Media & Video Editor

The team was connected to RenderPhoenix, but Space Kitty was not exactly the same team as RenderPhoenix. Sabit and Tasrif were from RenderPhoenix, while the other two members joined the NASA competition team separately.

The team itself had a much more relaxed personality than its name might suggest. While many teams at the competition looked extremely serious, Space Kitty had something a little different going on:

- **Sabit** used a **chicken** avatar. 🐔
- **Tasrif** used a **duck** avatar. 🦆
- And their team name was simply **Space Kitty**. 🐱

Behind the cute avatars, however, they were working on a real-time simulation with limited time.

---

## The First Piece of the Game

Sabit was still relatively new to Unity, having only around six or seven months of Unity experience when development began.

But he had an approach that helped him work quickly: he usually built things that were already within his ability, and whenever something new was needed, he learned it. He used **Unity** and **Playmaker** to build the game.

The first major system he created was the **building system**:
- Players could select specific areas on the lunar surface.
- Clicking one of those areas opened a user interface where the player could choose which habitat or facility to build.
- At first, the system was simple—no giant free-form city-building grid, just selected locations, a building menu, and a Moon surface waiting for structures.

While Sabit worked on the game systems and UI, Tasrif was creating the 3D habitat models. Sabit initially used placeholder objects. When Tasrif pushed the finished models to GitHub, Sabit replaced the placeholders with the actual assets.

The project slowly started turning into something that looked like a real lunar settlement. The GitHub repository documents the project as a Unity-based city-building and resource-management game, with C# and ShaderLab/HLSL used for development and visual effects.

---

## Building a Colony Means Managing Everything

*Moon Forces* was built around a simple problem: **Every building needs something, and every new building can create another problem.**

Players begin with a limited amount of resources and must construct facilities to keep the colony running. The game tracks 8 intertwined resources:

- 💨 **Oxygen**
- 💧 **Water**
- 🥗 **Food**
- 🌾 **Crops**
- ⚡ **Electricity**
- 🗑️ **Trash**
- 🔩 **Metal**
- 👨‍🚀 **Population**

The player might build a greenhouse to help produce resources and oxygen. They might build water-related facilities. They need solar panels to generate electricity. They need habitats for incoming space crews.

But building more things does not automatically make the colony better—it can actually make the situation worse:
- Build too many habitats, and resource consumption increases.
- Build too many greenhouses, and electricity demand increases.
- Build too many water generators, and electricity becomes harder to maintain.

Suddenly, the player has a much larger colony—but also a much bigger problem. That became the main challenge of *Moon Forces*: **Growth had a cost.**

---

## When the Game Finally Felt Like a Game

For Sabit, there was a particular moment when *Moon Forces* stopped feeling like a collection of systems and started feeling like an actual game: **it was when the world began moving on its own.**

The team added dynamic ambient systems:
- A day-and-night cycle where the Sun rotated and days passed.
- Rockets arrived at the Moon and returned toward Earth.
- Rovers moved around the habitat autonomously.

The world was no longer sitting still—something was happening. The resource systems were also running simultaneously: buildings consumed resources, other buildings produced them, and the player had to keep the colony balanced.

For Sabit, this was the point where the project became a true game because there was finally a complete loop:

$$\text{Start} \longrightarrow \text{Build} \longrightarrow \text{Resources Change} \longrightarrow \text{Day Passes} \longrightarrow \text{Colony Continues} \longrightarrow \text{Next Day}$$

And that feeling of a living system was more important than simply having lots of features.

---

## The Moon's Long Days Were Part of the Challenge

The game included a simple day-and-night cycle. One in-game day lasted about 180 seconds, with speed controls planned around faster simulation. The project documentation describes a 14-day/14-night monthly cycle and solar panels that generate electricity during the daytime.

The day/night system was not intended to simulate every single detail of the real Moon. Instead, it created an engaging gameplay problem:

When night arrived, the solar panels stopped producing electricity. That meant the player had to think ahead. If electricity production was too low, the colony could quickly run into trouble. The player had to balance production and consumption rather than simply building as much as possible.

---

## Rovers That Made the Moon Feel Alive

The rovers were not an enormous scientific simulation. They were there to make the colony feel like a place where things were happening.

They moved around the habitats and explored the lunar surface, looking as if they were collecting or testing samples and moving through the settlement. Sabit used Unity's **NavMesh navigation system** to give the vehicles paths around the environment.

It was a small feature, but visually it changed the project completely: a static Moon surface became a world with movement.

---

## There Was No Winning the Moon

Interestingly, *Moon Forces* did not have a traditional victory condition in its final version. There was no:

> *“Congratulations! You colonized the Moon!”*

Instead, the days simply kept increasing. The player continued managing the colony for as long as possible. But if an important resource reached zero, the game ended.

That created a survival-style loop rather than a traditional campaign. The project documentation describes resource failure as a loss condition, while its original GDD listed a future win condition as something that had not yet been fully defined.

And that is important because *Moon Forces* was never meant to be a finished commercial game—it was a focused simulation project created under hackathon conditions for NASA Space Apps. The team had once considered publishing it on the Play Store, but prioritized competition delivery.

---

## Four or Five Days to Build It

Perhaps the most surprising part of the project is how quickly it was made: the team had only around **four to five days** to build the game.

No long production cycle. No year-long development. No large studio. Just a small team, a challenge, and a deadline.

Sabit says that development itself did not feel overwhelming because he worked within his abilities and learned new things when necessary. The biggest challenge was not necessarily the code—**it was the clock.**

And then something unexpected happened.

---

## When the Team Lost Its Game Designer

Near the end of development, Tasrif suddenly had a serious problem at home. A dispute with his landlord meant that he had to leave his home immediately, and basic utilities such as electricity and gas were shut off. For several days, he was completely out of contact.

The team was almost finished with the game, but there was still final work to do. Tasrif had already created additional habitat models, but because he was no longer available, the team could not properly integrate all of those extra habitats into the final version.

Sabit continued working:
- He polished the existing game.
- He added more UI and tuned the menus.
- He added sound effects.
- And eventually, he built the final game executable.

Meanwhile, **Jafrin** remained heavily involved from the competition side, continuously communicating with Sabit, monitoring the development, and handling the NASA Space Apps dashboard and submission data. **Afnan** worked on the project's video presentation—which became one of the most engaging and fun parts of the submission.

So while one member was dealing with an unexpected personal crisis, another was finishing the game, another was managing the submission, and another was turning the project into a presentation. It was not exactly a calm development cycle!

---

## Then Came Submission Day

Once *Moon Forces* was submitted, the team was done. They did not expect it to become a commercial game or wait for millions of players. The project had accomplished what they set out to do: **take a NASA challenge and turn it into an interactive lunar habitat simulation.**

Then came the unexpected recognition.

---

## From Dhaka to the Global Stage

Before the global results arrived, Space Kitty received exciting news:

The team had competed in the **Dhaka Division**, where they placed **2nd Runner-Up** after competing among **more than 850 participants/projects** in the division.

Sabit was actually offline when the news arrived. Instead of hearing it directly from the organizers, he received a WhatsApp message from a friend:

> *“Congratulations!”*

Soon, the team attended the prize-giving ceremony at the **BASIS Auditorium** in Karwan Bazar. There were students everywhere wearing NASA Space Apps shirts. The team received prizes, a crest, and medals. For a small team that had built its project in only a few days, it was a memorable moment.

```text
NASA Space Apps Challenge 2025
├── Dhaka Division: 2nd Runner-Up (Top 3 out of 850+ participants)
└── Global Phase: Selected as NASA Space Apps 2025 Global Nominee
```

Weeks later, Space Kitty learned that **Moon Forces had become an official NASA Space Apps 2025 Global Nominee**—standing out among thousands of submissions globally.

The team did not make it to the Global Finalists or Global Winners stage, but they had already taken their small Moon colony much further than anyone expected.

---

## A Game That Proved Something

For Sabit, perhaps the biggest achievement was not the medal or the Global Nominee title—it was discovering what he could actually build.

He had only around six or seven months of Unity experience. Then, in roughly four or five days, he helped turn an idea into a working simulation:
- Built the building and placement system.
- Created the multi-resource simulation logic.
- Designed and coded the UI.
- Implemented the dynamic day/night cycle.
- Integrated NavMesh vehicle navigation.
- Added sound and final polish.
- And when a teammate became unavailable, pushed the build across the finish line.

*Moon Forces* showed him that he could push a game from an empty project toward something playable in a very short amount of time. That was a lesson that could not easily be learned from tutorials alone.

---

## Why Hackathons Matter

The team also discovered something bigger through NASA Space Apps: **international hackathons bring people from very different places together to work on the same problems.**

Someone from the United States can be working on the same NASA challenge as someone from Bangladesh. The location does not decide who gets to participate; the same problem is presented to everyone, and everyone gets the opportunity to try.

For Space Kitty, that was one of the most exciting parts of the experience: NASA Space Apps gave a small team from Bangladesh a chance to build something, submit it to an international competition, and eventually see its name among the global nominees.

---

## And Then There Was Space Kitty

There is also a small detail that probably says more about the team than any formal description could:

While other teams were taking the competition very seriously, Space Kitty showed up with a **chicken avatar**, a **duck avatar**, and a cute team name.

They had fun. They experimented. They made a game. They did not build everything they originally imagined, they did not have time to add every habitat, they did not implement an elaborate victory screen, and they did not turn the project into a commercial release.

**But they finished. And that mattered.**

---

## Back to NASA Space Apps 2026

*Moon Forces* was not the end of the story.

On **August 29, 2026**, the team registered again for NASA Space Apps.

This time, they are coming back with experience:
- They have already participated in previous challenges.
- They know how the competition works.
- They know what a few days of intense development feels like.
- They know what can go wrong.
- And, perhaps most importantly, they now know one thing they did not know in 2025: **Read the full challenge description first!** 😂

Team Space Kitty is coming back prepared. And maybe this time, the chicken and duck are bringing a little more firepower—in the completely metaphorical game-development sense. 🐔🦆🚀

---

### Project Links

- 🌌 [NASA Space Apps 2025 — Your Home in Space: The Habitat Layout Creator](https://www.spaceappschallenge.org/2025/challenges/your-home-in-space-the-habitat-layout-creator/)
- 💻 [Moon Forces — GitHub Repository](https://github.com/cristoparker/Space-Kitty-Project)
- 🚀 [Moon Forces Project Portfolio Case Study](/work/nasa-space-apps-2025/)
