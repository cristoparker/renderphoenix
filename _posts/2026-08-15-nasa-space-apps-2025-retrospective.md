---
layout: post
title: "NASA Space Apps Challenge 2025: Engineering a Lunar Settlement"
description: "A retrospective on how RenderPhoenix was named Global Nominee at the NASA Space Apps Challenge 2025 with an interactive lunar city and habitat simulation."
date: 2026-08-15 00:00:00 +0600
categories:
  - technical
  - development
tags:
  - nasa
  - space-apps
  - simulation
  - 3d
  - moon
author: "RenderPhoenix"
image: "/assets/images/blog/nasa-retrospective.png"
featured: false
---

In 2025, members of RenderPhoenix participated in the **NASA Space Apps Challenge 2025**, tackling the challenge of designing functional, sustainable lunar habitats. Our submission achieved **Global Nominee**.

## The Challenge: Lunar Settlement Simulation

Humanity's return to the Moon requires solving complex engineering constraints: solar radiation exposure, extreme temperature swings between lunar day and night, regolith shielding, and closed-loop life support systems.

Our team designed a real-time 3D interactive simulator allowing users to construct modular subterranean and surface lunar habitats while balancing power, oxygen generation, and thermal regulation.

## Key Technical Achievements

- **Modular Node Architecture**: Designed interconnected habitat modules (hydroponics, solar farm, life support, communications spire).
- **Environmental Constraints**: Integrated real lunar topographic and solar radiation data into the simulation environment.
- **Performant 3D Web Rendering**: Achieved fluid framerates across devices with low polygon count geometry and optimized shader pipelines.

```csharp
// Conceptual radiation shielding calculation snippet
public float CalculateRadiationShielding(float regolithThicknessMeters, float solarFlareIntensity)
{
    float attenuationFactor = Mathf.Exp(-0.15f * regolithThicknessMeters);
    return Mathf.Clamp01(1.0f - (solarFlareIntensity * attenuationFactor));
}
```

Participating in the NASA Space Apps Challenge demonstrated how our world-building background translates into scientific visualization and interactive simulation.
