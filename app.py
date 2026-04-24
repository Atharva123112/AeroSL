import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set page config
st.set_page_config(page_title="AeroRL Sandbox", layout="wide")

# Title and Context
st.title("✈️ AeroRL: Autonomous Post-Stall Combat Logic")
st.markdown("""
This sandbox demonstrates the core Q-Learning logic of the AeroRL project. 
Adjust the variables below to see how the AI evaluates the extreme energy penalty of a thrust-vectored maneuver (Post-Stall Flip) against standard aerodynamic turns.
""")

# --- Sidebar Controls ---
st.sidebar.header("Combat Variables")
ai_energy = st.sidebar.slider("AI Kinetic Energy", min_value=0, max_value=100, value=80, step=10, 
                              help="Below 30 is Low Energy. 0 is Stalled.")
target_x = st.sidebar.slider("Target Relative X (Horizontal)", min_value=-5, max_value=5, value=0,
                             help="Negative is Left, Positive is Right, 0 is directly in front/behind.")
target_y = st.sidebar.slider("Target Relative Y (Distance)", min_value=-5, max_value=5, value=2,
                             help="Positive is in front, Negative is behind.")

# --- The Logic Engine (Simplified Q-Table Representation) ---
def evaluate_actions(energy, x, y):
    """Calculates heuristic scores mimicking the learned Q-values."""
    scores = {"FORWARD": 0, "TURN": 0, "POST_STALL_FLIP": 0}
    
    distance = np.hypot(x, y)
    
    # 1. Evaluate FORWARD
    if y > 2 and abs(x) <= 2:
        scores["FORWARD"] = (energy * 0.5) - (distance * 2) + 20 # Good if enemy is far ahead
    else:
        scores["FORWARD"] = (energy * 0.5) - (distance * 5)
        
    # 2. Evaluate TURN
    if x != 0 and energy > 20:
        scores["TURN"] = ((energy - 10) * 0.5) - (distance * 3) + 30 # Good if enemy is off-center
    else:
        scores["TURN"] = ((energy - 10) * 0.5) - (distance * 5)
        
    # 3. Evaluate FLIP (The Kill Zone Logic)
    if 1 <= y <= 3 and -1 <= x <= 1 and energy > 60:
        # The Sweet Spot: Enemy is close behind, we have high energy
        scores["POST_STALL_FLIP"] = 100 + ((energy - 60) * 0.5)
    else:
        # Outside the zone: Massive penalty
        scores["POST_STALL_FLIP"] = ((energy - 60) * 0.5) - 50
        if energy <= 60:
             scores["POST_STALL_FLIP"] -= 100 # Near-stall penalty
             
    return scores

# Calculate scores based on user input
scores = evaluate_actions(ai_energy, target_x, target_y)
optimal_move = max(scores, key=scores.get)

# --- Main Layout ---
col1, col2 = st.columns([1.5, 1])

with col1:
    st.subheader("Tactical Grid")
    
    # Generate the Matplotlib Grid
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xlim(-6, 6)
    ax.set_ylim(-6, 6)
    ax.grid(True, linestyle='--', alpha=0.5)
    
    # Plot AI
    ax.plot(0, 0, '^', markersize=20, color='blue', label='AI Jet (Facing Up)')
    # Plot Target
    ax.plot(target_x, target_y, 'o', markersize=15, color='red', label='Target Drone')
    
    # Draw the "Kill Zone" box for visual reference
    import matplotlib.patches as patches
    kill_zone = patches.Rectangle((-1, 1), 2, 2, linewidth=2, edgecolor='green', facecolor='none', linestyle='--', label='Optimal Flip Zone')
    ax.add_patch(kill_zone)
    
    ax.legend(loc='lower right')
    st.pyplot(fig)

with col2:
    st.subheader("AI Decision Engine")
    
    st.metric(label="Current AI Energy", value=f"{ai_energy}/100")
    
    st.markdown("### Calculated Values")
    
    # Display scores cleanly
    for action, score in scores.items():
        if action == optimal_move:
            st.success(f"**{action}**: {score:.1f} (OPTIMAL)")
        else:
            st.info(f"{action}: {score:.1f}")
            
    st.markdown("---")
    if optimal_move == "POST_STALL_FLIP":
        st.warning("⚠️ **EXECUTING FLIP**: Target is in the optimal kill zone and energy reserves are sufficient to survive the maneuver.")
    elif optimal_move == "TURN":
        st.write("🔄 **EXECUTING TURN**: Adjusting heading to track off-center target.")
    else:
        st.write("⬆️ **MAINTAINING FORWARD**: Building kinetic energy or closing distance.")