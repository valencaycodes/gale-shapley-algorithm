import streamlit as st
import random
import matplotlib.pyplot as plt

# ---------------------- Gale‑Shapley core ----------------------
def gale_shapley_step(males, females, male_prefs, female_prefs, engagements, next_proposal, free_males):
    if not free_males:
        return engagements, next_proposal, free_males, []

    events = []
    new_free = []

    for male in free_males:
        pref_list = male_prefs[male]
        if next_proposal[male] >= len(pref_list):
            continue
        female = pref_list[next_proposal[male]]
        next_proposal[male] += 1

        event = f"{male} proposes to {female}"

        if female not in engagements:
            engagements[female] = male
            event += f" → {female} accepts (was free)"
        else:
            current_male = engagements[female]
            rank_new = female_prefs[female].index(male)
            rank_curr = female_prefs[female].index(current_male)
            if rank_new < rank_curr:
                engagements[female] = male
                event += f" → {female} switches (prefers {male})"
                new_free.append(current_male)
            else:
                event += f" → {female} rejects (prefers {current_male})"
                new_free.append(male)
        events.append(event)

    free_males[:] = new_free
    return engagements, next_proposal, free_males, events

# ---------------------- Streamlit App ----------------------
st.title("💍 Gale‑Shapley Stable Marriage Game")

# Fixed simulation data
n = 10
males = [f"M{i+1}" for i in range(n)]
females = [f"F{i+1}" for i in range(n)]

# Generate random preferences
random.seed()
male_prefs = {m: random.sample(females, len(females)) for m in males}
female_prefs = {f: random.sample(males, len(males)) for f in females}

# Initialize state
if "engagements" not in st.session_state:
    st.session_state.engagements = {}
    st.session_state.next_proposal = {m: 0 for m in males}
    st.session_state.free_males = list(males)
    st.session_state.round = 0
    st.session_state.finished = False
    st.session_state.bet_pair = None
    st.session_state.bet_placed = False

# Betting controls
st.sidebar.header("🎲 Place Your Bet")
male_choice = st.sidebar.selectbox("Choose a Male", males)
female_choice = st.sidebar.selectbox("Choose a Female", females)
if st.sidebar.button("Place Bet"):
    st.session_state.bet_pair = (male_choice, female_choice)
    st.session_state.bet_placed = True
    st.sidebar.success(f"You bet that {male_choice} ⟷ {female_choice} will end up together!")

# Next round button
if st.button("➡️ Next Round"):
    if not st.session_state.finished:
        st.session_state.engagements, st.session_state.next_proposal, st.session_state.free_males, events = gale_shapley_step(
            males, females, male_prefs, female_prefs,
            st.session_state.engagements, st.session_state.next_proposal, st.session_state.free_males
        )
        st.session_state.round += 1
        st.write(f"### Round {st.session_state.round}")
        for e in events:
            st.write(e)

        if not st.session_state.free_males:
            st.session_state.finished = True
            st.success("✅ Algorithm finished: all men are matched stably!")
            if st.session_state.bet_placed:
                male, female = st.session_state.bet_pair
                matched = st.session_state.engagements.get(female) == male
                if matched:
                    st.success(f"🎉 YOU WIN! {male} and {female} are a pair.")
                else:
                    st.error(f"😢 Sorry, {male} and {female} did NOT end up together.")

# Show current engagements visually
st.subheader("Current Engagements")

fig, ax = plt.subplots(figsize=(8, 6))
ax.axis("off")

# Coordinates for men (left) and women (right)
male_coords = {m: (0, i) for i, m in enumerate(males)}
female_coords = {f: (1, i) for i, f in enumerate(females)}

# Draw names
for m, (x, y) in male_coords.items():
    ax.text(x, y, m, ha="right", va="center", fontsize=12, color="blue")
for f, (x, y) in female_coords.items():
    ax.text(x, y, f, ha="left", va="center", fontsize=12, color="purple")

# Draw connections
for f, m in st.session_state.engagements.items():
    x1, y1 = male_coords[m]
    x2, y2 = female_coords[f]
    ax.plot([x1, x2], [y1, y2], "r-", linewidth=2)

st.pyplot(fig)
