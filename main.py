import streamlit as st
import random

# ---------------------- Gale–Shapley core ----------------------
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
st.title("💍 Gale–Shapley Stable Marriage Game")

# Simulation setup
n = st.sidebar.slider("Number of pairs", 2, 15, 6)
males = [f"M{i+1}" for i in range(n)]
females = [f"F{i+1}" for i in range(n)]

# Generate random preferences
random.seed()
male_prefs = {m: random.sample(females, len(females)) for m in males}
female_prefs = {f: random.sample(males, len(males)) for f in females}

# State
if "engagements" not in st.session_state:
    st.session_state.engagements = {}
    st.session_state.next_proposal = {m: 0 for m in males}
    st.session_state.free_males = list(males)
    st.session_state.round = 0
    st.session_state.finished = False

# Show preferences
with st.expander("Male Preferences"):
    for m in males:
        st.write(f"{m}: {male_prefs[m]}")
with st.expander("Female Preferences"):
    for f in females:
        st.write(f"{f}: {female_prefs[f]}")

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

# Show current engagements
st.subheader("Current Engagements")
for f, m in st.session_state.engagements.items():
    st.write(f"{f} ⟷ {m}")
