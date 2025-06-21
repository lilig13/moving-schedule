import streamlit as st
import datetime

st.set_page_config(page_title="Moving Schedule", layout="centered")
st.title("📋 Moving Schedule")

# --- Initial Data ---
people_list = ["Lulu", "Yeni", "Angelo", "Jeremiah", "Alonso", "Keaneu",
               "Jackson", "Alex", "Walker", "Dayanna", "Sophia"]

materials_list = [
    "1.5 Boxes", "3.0 Boxes", "4.5 Boxes (Tall)", "4.5 Boxes (Long)", "2 PC Mirror",
    "Tape (Pack)", "Stretch wrap (Roll)", "Big Bubble Wrap (Feet)", "Small Bubble Wrap (Feet)",
    "Paper Pad (Brown Paper)", "Mattress Bag", "TV Mount (Small)", "TV Mount (Large)",
    "Felt Pad (Pack)", "Newsprint (White Paper)", "Clear Trash Bags (Box)",
    "Black Trash Bags (Box)", "Rug Gripper Thick Pads"
]

# --- Utilities ---
def format_materials(material_dict):
    return "\n".join([f"{amt} x {mat}" for mat, amt in material_dict.items()]) if material_dict else "None"

def render_team_section(index):
    team_label = f"Team {index + 1}"
    with st.expander(team_label, expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            role = st.selectbox("Role", ["PM", "CM"], key=f"role_{index}")
        with col2:
            name = st.selectbox("Name", people_list, key=f"name_{index}")

        tl = st.selectbox("Team Lead (TL)", people_list, key=f"tl_{index}")
        members = st.multiselect("Team Members", people_list, key=f"members_{index}")

        move_from = st.text_input("Move From", key=f"from_{index}")
        move_to = st.text_input("Move To", key=f"to_{index}")
        client = st.text_input("Client Name", key=f"client_{index}")
        contact = st.text_input("Point of Contact", key=f"contact_{index}")
        leave_by = st.time_input("Leave By Time", value=datetime.time(7 + index, 0), key=f"leave_{index}")

        selected_mats = st.multiselect("Materials", materials_list, key=f"mats_{index}")
        mat_amounts = {mat: st.number_input(f"Amount for {mat} ({team_label})", 1, key=f"amt_{mat}_{index}") for mat in selected_mats}

        return {
            "label": team_label,
            "role": role,
            "name": name,
            "tl": tl,
            "members": members,
            "from": move_from,
            "to": move_to,
            "client": client,
            "contact": contact,
            "leave_by": leave_by.strftime("%I:%M %p").lstrip("0"),
            "materials": mat_amounts
        }

# --- Session State ---
if "team_count" not in st.session_state:
    st.session_state.team_count = 2

if "intime_count" not in st.session_state:
    st.session_state.intime_count = 2

# --- Date ---
date_input = st.date_input("Date", value=datetime.date.today())
formatted_date = date_input.strftime("%B %d")

# --- In-Times ---
with st.expander("In-Times", expanded=True):
    for i in range(st.session_state.intime_count):
        with st.expander(f"In-Time Team {i + 1}", expanded=True):
            col1, col2 = st.columns([1, 3])
            time = st.time_input(f"Time {i+1}", value=datetime.time(7 + i, 0), key=f"time_{i}")
            members = st.multiselect(f"Team Members {i+1}", people_list, key=f"intime_members_{i}")

    if st.button("➕ Add Another In-Time"):
        st.session_state.intime_count += 1
        st.rerun()

# --- Teams Section ---
teams_data = []
for i in range(st.session_state.team_count):
    team_data = render_team_section(i)
    teams_data.append(team_data)

if st.button("➕ Add Another Team"):
    st.session_state.team_count += 1
    st.rerun()

# --- Generate Schedule ---
if st.button("✅ Generate Schedule"):
    in_times_text = ""
    for i in range(st.session_state.intime_count):
        t = st.session_state[f"time_{i}"].strftime("%I:%M %p").lstrip("0")
        m = ", ".join(st.session_state[f"intime_members_{i}"])
        in_times_text += f"{t} {m}\n"

    schedule = f"{formatted_date}\n\nHi everyone!\nIn times are the following:\n\n{in_times_text.strip()}\n\n"

    for team in teams_data:
        team_section = f"""{team['label']}:
Role: {team['role']} - {team['name']}
Team Lead (TL): {team['tl']}
Team Members: {', '.join(team['members'])}
Moving From: {team['from']}
Moving To: {team['to']}
Client Name: {team['client']}
Point of Contact: {team['contact'] or 'N/A'}
🚨 Leave by {team['leave_by']} 🚨
Materials:
{format_materials(team['materials'])}
"""
        schedule += "—————————\n" + team_section + "\n"

    schedule += "—————————\nTrailer 52\n\nFriendly reminder, please clock in as soon as everyone is in the truck."

    st.text_area("Generated Schedule", value=schedule, height=600)
    st.download_button("📥 Download Schedule", data=schedule, file_name="move_schedule.txt")
