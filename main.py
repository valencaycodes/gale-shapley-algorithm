import streamlit as st
import random

# ---------------------- Gale‑Shapley core ----------------------
def gale_shapley_step(males, females, male_prefs, female_prefs, engagements, next_proposal, free_males):
    if not free_males:
        return engagements, next_proposal, free_males

    new_free = []
    for male in free_males:
        pref_list = male_prefs[male]
        if next_proposal[male] >= len(pref_list):
            continue
        female = pref_list[next_proposal[male]]
        next_proposal[male] += 1

        if female not in engagements:
            engagements[female] = male
        else:
            current_male = engagements[female]
            rank_new = female_prefs[female].index(male)
            rank_curr = female_prefs[female].index(current_male)
            if rank_new < rank_curr:
                engagements[female] = male
                new_free.append(current_male)
            else:
                new_free.append(male)

    free_males[:] = new_free
    return engagements, next_proposal, free_males

# ---------------------- Streamlit App ----------------------
st.title("Gale‑Shapley Algorithm")

# Fixed names
males = ["Arjun", "Ravi", "Karan", "Vikram", "Sahil", "Amit", "Rahul", "Dev", "Manish", "Rohan"]
females = ["Priya", "Anita", "Kavya", "Meera", "Sneha", "Pooja", "Ritika", "Shreya", "Nisha", "Ayesha"]

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
        st.session_state.engagements, st.session_state.next_proposal, st.session_state.free_males = gale_shapley_step(
            males, females, male_prefs, female_prefs,
            st.session_state.engagements, st.session_state.next_proposal, st.session_state.free_males
        )
        st.session_state.round += 1
        st.write(f"### Round {st.session_state.round} completed")

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

# Show current engagements visually with Graphviz DOT string
st.subheader("Current Engagements")

dot = "digraph G { rankdir=LR; bgcolor=white;"

# Add nodes with clean theme
for m in males:
    dot += f'"{m}" [shape=box, style=filled, fillcolor=lightblue, fontcolor=black];'
for f in females:
    dot += f'"{f}" [shape=ellipse, style=filled, fillcolor=lightpink, fontcolor=black];'

# Add edges for current engagements
for f, m in st.session_state.engagements.items():
    dot += f'"{m}" -> "{f}" [color=red, penwidth=2];'

dot += "}"

st.graphviz_chart(dot)

