# FACEIT to Liquipedia Match Parser

## How It Works

### 1. Input FACEIT Match ID

```
match_id=1-68ce4542-876a-4862-92bc-a18407d6d970
```
---

### 2. Input Team 1 first sides (ct or t)

```
team1_first_sides=t ct t
```
---

### 3. Generate Liquipedia Code

```
{{Match
    |opponent1={{TeamOpponent|novaq}}|opponent2={{TeamOpponent|the continental}}
    |date=November 30, 2025 - 18:12 {{Abbr/ALMT}}|finished=true
    |map1={{Map|map=Dust II|finished=true
        |t1firstside=t|t1t=5|t1ct=2|t2t=6|t2ct=7}}
    |map2={{Map|map=Mirage|finished=true
        |t1firstside=t|t1t=9|t1ct=4|t2t=2|t2ct=3}}
    |map3={{Map|map=Ancient|finished=true
        |t1firstside=t|t1t=7|t1ct=6|t2t=4|t2ct=5}}
    |faceit=1-68ce4542-876a-4862-92bc-a18407d6d970
}}
