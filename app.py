import streamlit as st
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import math

# -------------------------------------------------
# Ρυθμίσεις σελίδας + logo
# -------------------------------------------------
st.set_page_config(
    page_title="Ερωτηματολόγιο Αντλίας Θερμότητας",
    page_icon="logo.png",  # αρχείο logo στο repo (προαιρετικό)
    layout="centered",
)

# Logo (αν δεν υπάρχει, απλά το αγνοούμε)
try:
    st.image("logo.png", width=180)
except Exception:
    pass

st.title("🔥 Αλλαγή Συστήματος Θέρμανσης – Επιλογή Αντλίας Θερμότητας")
st.markdown(
    "Συμπληρώστε τις παρακάτω πληροφορίες ώστε να μπορέσουμε "
    "να σας προτείνουμε την κατάλληλη αντλία θερμότητας για τον χώρο σας."
)

st.markdown("---")

# =========================
# Διαθέσιμα μοντέλα αντλιών
# =========================
MODELS = [
    {"name": "Αντλία 8 kW", "kw": 8},
    {"name": "Αντλία 9 kW", "kw": 9},
    {"name": "Αντλία 10 kW", "kw": 10},
    {"name": "Αντλία 12 kW", "kw": 12},
    {"name": "Αντλία 16 kW", "kw": 16},
    {"name": "Αντλία 26 kW", "kw": 26},
]

# =========================
# Αποστολή email με σύνοψη
# =========================
def send_email(summary_text: str):
    """
    Στέλνει τη σύνοψη στο email που έχουμε ορίσει στα secrets.
    Περιμένει:
    st.secrets["email"]["user"]
    st.secrets["email"]["password"]
    st.secrets["email"]["to"]
    """
    try:
        email_user = st.secrets["email"]["user"]
        email_password = st.secrets["email"]["password"]
        email_to = st.secrets["email"]["to"]

        msg = MIMEText(summary_text, _charset="utf-8")
        msg["Subject"] = "Νέο ερωτηματολόγιο αντλίας θερμότητας"
        msg["From"] = email_user
        msg["To"] = email_to

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(email_user, email_password)
            server.send_message(msg)

    except Exception as e:
        # Αν δεν έχουν στηθεί τα secrets ή κάτι πάει στραβά, απλά δείξε μήνυμα
        st.warning(f"Δεν στάλθηκε email αυτόματα (σφάλμα: {e})")


# =========================
# Helper: Εκτίμηση ισχύος αντλίας
# =========================
def estimate_heat_pump_kw(
    area_m2,
    year_category,
    renovation_done,
    renovation_options,
    house_type,
    apt_floor_position,
    emission_type,
    boiler_power_known,
    boiler_power_unit,
    boiler_power_value,
    fuel_consumption_known,
    fuel_consumption_type,
    fuel_consumption_value,
):
    """
    Πολύ απλή εμπειρική εκτίμηση ισχύος σε kW.
    Δεν αντικαθιστά μελέτη μηχανικού – είναι για εμπορική προ-πρόταση.
    ΣΗΜΑΝΤΙΚΟ: η ισχύς λέβητα και η κατανάλωση ΔΕΝ επηρεάζουν
    τον υπολογισμό, μπαίνουν μόνο ως πληροφορία.
    """
    if area_m2 is None or area_m2 <= 0:
        return None, "Δεν δόθηκαν m², δεν μπορεί να γίνει εκτίμηση."

    # Βάση W/m² ανά εποχή/ποιότητα κατασκευής
    if year_category == "Πριν το 1980":
        base_w_per_m2 = 110
    elif year_category == "1980–2000":
        base_w_per_m2 = 90
    elif year_category == "2001–2009":
        base_w_per_m2 = 75
    else:  # 2010 και μετά
        base_w_per_m2 = 60

    # Μείωση λόγω ανακαινίσεων
    if renovation_done == "Ναι":
        reduction = 0
        if renovation_options:
            if "Θερμομόνωση κελύφους" in renovation_options:
                reduction += 0.15
            if "Θερμομόνωση δώματος / ταράτσας" in renovation_options:
                reduction += 0.10
            if "Αντικατάσταση κουφωμάτων" in renovation_options:
                reduction += 0.10
        reduction = min(reduction, 0.30)  # max -30%
        base_w_per_m2 *= (1 - reduction)

    # Προσαρμογή ανά τύπο κατοικίας & όροφο
    if house_type == "Μονοκατοικία" or apt_floor_position.startswith("Δεν ισχύει"):
        base_w_per_m2 *= 1.10  # περισσότερες απώλειες
        apt_note = "Μονοκατοικία – ελαφρώς αυξημένες απώλειες."
    else:
        # Διαμέρισμα
        if apt_floor_position == "Ενδιάμεσος όροφος":
            base_w_per_m2 *= 0.85  # προστατευμένο
            apt_note = "Διαμέρισμα ενδιάμεσο – λιγότερες απώλειες."
        elif apt_floor_position == "Τελευταίος όροφος / ρετιρέ":
            base_w_per_m2 *= 1.00
            apt_note = "Διαμέρισμα τελευταίος όροφος – κανονικές προς αυξημένες απώλειες."
        else:
            apt_note = "Διαμέρισμα."

    # Προσαρμογή ανά τύπο συστήματος εκπομπής
    if emission_type == "Ενδοδαπέδια":
        emis_note = "Ενδοδαπέδια – χαμηλές θερμοκρασίες, μπορείς να δουλεύεις με χαμηλότερα kW."
        emis_factor = 0.9
    elif emission_type == "Fan coil":
        emis_note = "Fan coil – χαμηλές/μέσες θερμοκρασίες, καλό για αντλία."
        emis_factor = 0.95
    elif emission_type == "Μικτό σύστημα":
        emis_note = "Μικτό σύστημα – κράτα λίγο παραπάνω απόθεμα."
        emis_factor = 1.05
    else:  # Καλοριφέρ
        emis_note = "Καλοριφέρ – πιθανότατα χρειάζονται υψηλότερες θερμοκρασίες."
        emis_factor = 1.05

    base_w_per_m2 *= emis_factor

    # Αρχική εκτίμηση από m² (μόνο από τα γεωμετρικά/θερμικά στοιχεία)
    design_kw_from_area = area_m2 * base_w_per_m2 / 1000  # W → kW

    notes = []
    notes.append(f"Βάση: ~{base_w_per_m2:.0f} W/m² μετά τις διορθώσεις.")
    notes.append(apt_note)
    notes.append(emis_note)

    # Ισχύς λέβητα και κατανάλωση: ΜΟΝΟ ως πληροφοριακά στοιχεία
    if boiler_power_known == "Ναι" and boiler_power_value and boiler_power_value > 0:
        if boiler_power_unit == "kW":
            kw_from_boiler = boiler_power_value
        else:  # kcal/h
            kw_from_boiler = boiler_power_value / 860.0
        notes.append(f"Δήλωση ισχύος υπάρχοντος λέβητα: ~{kw_from_boiler:.1f} kW (μόνο ως ένδειξη).")

    if fuel_consumption_known == "Ναι" and fuel_consumption_value and fuel_consumption_value > 0:
        if fuel_consumption_type and fuel_consumption_type.startswith("Ποσότητα"):
            notes.append(f"Δηλωμένη κατανάλωση καυσίμου: {fuel_consumption_value:.0f} λίτρα/κιλά (ενδεικτικό).")
        elif fuel_consumption_type:
            notes.append(f"Δηλωμένο κόστος καυσίμου: {fuel_consumption_value:.0f} € (ενδεικτικό).")

    # Τελικό kW ΜΟΝΟ από m²/έτος/ανακαινίσεις/τύπο κατοικίας/εκπομπή
    avg_kw = design_kw_from_area
    low_kw = max(0, avg_kw * 0.85)
    high_kw = avg_kw * 1.15

    return (low_kw, high_kw, avg_kw), " ".join(notes)


def pick_model_for_kw(hp_result):
    """Διαλέγει μοντέλο από τη λίστα MODELS με βάση την εκτιμώμενη ισχύ."""
    if hp_result is None:
        return None

    _, _, avg_kw = hp_result
    target_kw = avg_kw * 1.05  # μικρό safety factor

    suitable = [m for m in MODELS if m["kw"] >= target_kw]
    if suitable:
        chosen = sorted(suitable, key=lambda x: x["kw"])[0]
    else:
        chosen = sorted(MODELS, key=lambda x: x["kw"])[-1]

    return chosen


# =========================
# ΕΡΩΤΗΣΕΙΣ (χωρίς st.form)
# =========================

# 1. Επιθυμίες & Τρόπος Αγοράς
st.subheader("1. Επιθυμίες & Τρόπος Αγοράς")

col1, col2 = st.columns(2)
with col1:
    install_interest = st.radio(
        "Σας ενδιαφέρει και η εγκατάσταση;",
        ["Ναι", "Όχι"],
        horizontal=True,
    )
with col2:
    program_purchase = st.radio(
        "Η αγορά θα γίνει μέσω προγράμματος επιδότησης;",
        ["Ναι", "Όχι", "Δεν γνωρίζω ακόμη"],
        horizontal=True,
    )

funding_rate_choice = None
if program_purchase == "Ναι":
    funding_rate_choice = st.radio(
        "Ποιο είναι περίπου το ποσοστό χρηματοδότησης;",
        ["50%", "60%", "Δεν γνωρίζω / δεν έχει οριστεί"],
        horizontal=True,
    )

col3, col4 = st.columns(2)
with col3:
    interest_type = st.radio(
        "Ενδιαφέρεστε για:",
        ["Μόνο Αντλία Θερμότητας", "Αντλία & Ηλιακός"],
    )
with col4:
    has_engineer_study = st.radio(
        "Έχετε μελέτη μηχανικού για την απαιτούμενη ισχύ;",
        ["Ναι", "Όχι"],
        horizontal=True,
    )

# Δόσεις
wants_installments = st.radio(
    "Σας ενδιαφέρει αγορά με δόσεις;",
    ["Όχι", "Ναι"],
    horizontal=True,
)
monthly_pref = None
if wants_installments == "Ναι":
    monthly_pref = st.radio(
        "Επιθυμητή μηνιαία δόση (περίπου):",
        ["50–100 €", "100–150 €", "200–250 €"],
        horizontal=True,
    )

# Αντλία & Ηλιακός → άτομα στο σπίτι
solar_people_band = None
if interest_type == "Αντλία & Ηλιακός":
    solar_people_band = st.radio(
        "Για τον ηλιακό, πόσα άτομα θα μένουν στο σπίτι;",
        ["3–4 άτομα", "4–5 άτομα", "Πάνω από 5 άτομα"],
        horizontal=True,
    )

st.markdown("---")

# 2. Στοιχεία Κατοικίας
st.subheader("2. Στοιχεία Κατοικίας")

col5, col6 = st.columns(2)
with col5:
    house_type = st.radio(
        "Τύπος κατοικίας:",
        ["Μονοκατοικία", "Διαμέρισμα"],
    )
with col6:
    area_m2 = st.number_input(
        "Εμβαδόν κατοικίας (m²)",
        min_value=0.0,
        step=1.0,
    )

year_category = st.selectbox(
    "Χρονολογία κατασκευής:",
    [
        "Πριν το 1980",
        "1980–2000",
        "2001–2009",
        "2010 και μετά",
    ],
)

apt_floor_position = st.radio(
    "Θέση κατοικίας στο κτήριο (αν είναι μονοκατοικία, διάλεξε 'Δεν ισχύει'):",
    ["Δεν ισχύει (μονοκατοικία)", "Ενδιάμεσος όροφος", "Τελευταίος όροφος / ρετιρέ"],
    horizontal=False,
)

renovation_done = st.radio(
    "Έχει γίνει κάποια ανακαίνιση / ενεργειακή αναβάθμιση στο σπίτι;",
    ["Όχι", "Ναι"],
    horizontal=True,
)

renovation_options = []
renovation_other = ""
if renovation_done == "Ναι":
    renovation_options = st.multiselect(
        "Τι έχει γίνει;",
        [
            "Θερμομόνωση κελύφους",
            "Θερμομόνωση δώματος / ταράτσας",
            "Αντικατάσταση κουφωμάτων",
            "Αλλαγή λεβητοστασίου / συστήματος",
            "Άλλο",
        ],
    )
    if "Άλλο" in renovation_options:
        renovation_other = st.text_input("Περιγράψτε άλλες επεμβάσεις:")

col7, col8 = st.columns(2)
with col7:
    power_type = st.radio(
        "Ρεύμα κατοικίας:",
        ["Μονοφασικό", "Τριφασικό", "Δεν γνωρίζω"],
    )
with col8:
    usage_type = st.radio(
        "Τι ζητάτε από την αντλία;",
        ["Μόνο Θέρμανση", "Θέρμανση & ΖΝΧ", "Θέρμανση, ΖΝΧ & Ψύξη"],
    )

znx_people = None
if "ΖΝΧ" in usage_type:
    znx_people = st.number_input(
        "Αν χρειάζεστε ΖΝΧ, πόσα άτομα θα μένουν στο σπίτι (αριθμός);",
        min_value=0,
        step=1,
    )

st.markdown("---")

# 3. Υφιστάμενο Σύστημα Θέρμανσης
st.subheader("3. Υφιστάμενο Σύστημα Θέρμανσης")

change_radiators = st.radio(
    "Θα χρειαστεί αλλαγή ή προσθήκη σε κάποιο θερμαντικό σώμα;",
    ["Ναι", "Όχι", "Δεν γνωρίζω"],
    horizontal=True,
)

distribution_type = st.radio(
    "Τώρα με τι σύστημα ζεσταίνεστε;",
    ["Κεντρικό", "Αυτόνομο"],
    horizontal=True,
)

emission_type = st.radio(
    "Με τι θερμαίνεται ο χώρος;",
    ["Καλοριφέρ (σώματα)", "Ενδοδαπέδια", "Fan coil", "Μικτό σύστημα"],
)

boiler_type = st.selectbox(
    "Τύπος λέβητα / πηγής θερμότητας:",
    [
        "Λέβητας πετρελαίου",
        "Λέβητας φυσικού αερίου",
        "Λέβητας pellet",
        "Ξυλολέβητας",
        "Άλλο",
    ],
)
boiler_other = ""
if boiler_type == "Άλλο":
    boiler_other = st.text_input("Περιγραφή άλλου τύπου λέβητα / συστήματος:")

boiler_power_known = st.radio(
    "Γνωρίζετε την ονομαστική ισχύ του υπάρχοντος λέβητα (kW ή kcal/h);",
    ["Ναι", "Όχι"],
    horizontal=True,
)

boiler_power_unit = None
boiler_power_value = None
if boiler_power_known == "Ναι":
    boiler_power_unit = st.selectbox("Μονάδα ισχύος:", ["kW", "kcal/h"])
    boiler_power_value = st.number_input(
        "Ισχύς λέβητα",
        min_value=0.0,
        step=0.1,
    )

st.markdown("### Κατανάλωση καυσίμου προηγούμενης σεζόν")

fuel_consumption_known = st.radio(
    "Γνωρίζετε περίπου την κατανάλωση καυσίμου την προηγούμενη σεζόν;",
    ["Ναι", "Όχι"],
    horizontal=True,
)

fuel_consumption_type = None
fuel_consumption_value = None
if fuel_consumption_known == "Ναι":
    fuel_consumption_type = st.radio(
        "Σε τι μονάδα μπορείτε να την δώσετε;",
        ["Ποσότητα (λίτρα / κιλά)", "Ποσό σε €"],
    )
    if fuel_consumption_type.startswith("Ποσότητα"):
        fuel_consumption_value = st.number_input(
            "Ποσότητα καυσίμου (λίτρα / κιλά)",
            min_value=0.0,
            step=1.0,
        )
    else:
        fuel_consumption_value = st.number_input(
            "Κόστος καυσίμου την προηγούμενη σεζόν (€)",
            min_value=0.0,
            step=50.0,
        )

st.markdown("---")

# 4. Πρόσθετα Συστήματα & Τοποθέτηση
st.subheader("4. Πρόσθετα Συστήματα & Τοποθέτηση")

col9, col10 = st.columns(2)
with col9:
    has_solar = st.radio(
        "Έχετε ηλιακό θερμοσίφωνα;",
        ["Ναι", "Όχι"],
        horizontal=True,
    )
with col10:
    has_pv = st.radio(
        "Υπάρχουν φωτοβολταϊκά;",
        ["Ναι", "Όχι"],
        horizontal=True,
    )

has_outdoor_space = st.radio(
    "Υπάρχει διαθέσιμος εξωτερικός χώρος για την αντλία θερμότητας;",
    ["Ναι", "Όχι"],
    horizontal=True,
)
outdoor_desc = st.text_area(
    "Αν ναι, περιγράψτε τον χώρο (μπαλκόνι, ταράτσα, αυλή κ.λπ.):",
    height=80,
)

noise_limits = st.radio(
    "Υπάρχουν περιορισμοί θορύβου (γειτονικά σπίτια, πολυκατοικία κ.λπ.);",
    ["Ναι", "Όχι"],
    horizontal=True,
)
noise_desc = st.text_area(
    "Αν ναι, περιγράψτε:",
    height=80,
)

comments = st.text_area(
    "Σχόλια / Παρατηρήσεις (π.χ. ώρες λειτουργίας, ιδιαίτερες ανάγκες):",
    height=100,
)

st.markdown("---")

# 5. Στοιχεία Επικοινωνίας
st.subheader("5. Στοιχεία Επικοινωνίας")

col11, col12 = st.columns(2)
with col11:
    name = st.text_input("Ονοματεπώνυμο")
    phone = st.text_input("Τηλέφωνο")
with col12:
    email = st.text_input("Email")
    address = st.text_input("Διεύθυνση ακινήτου (πόλη / περιοχή)")

# Κουμπί υποβολής
submitted = st.button("✅ Υποβολή ερωτηματολογίου", type="primary")

# =========================
# Μετά την υποβολή
# =========================
if submitted:
    st.success("Η υποβολή καταχωρήθηκε. Δείτε παρακάτω τη σύνοψη και την προτεινόμενη ισχύ αντλίας.")

    hp_result, hp_notes = estimate_heat_pump_kw(
        area_m2=area_m2,
        year_category=year_category,
        renovation_done=renovation_done,
        renovation_options=renovation_options,
        house_type=house_type,
        apt_floor_position=apt_floor_position,
        emission_type=emission_type,
        boiler_power_known=boiler_power_known,
        boiler_power_unit=boiler_power_unit,
        boiler_power_value=boiler_power_value,
        fuel_consumption_known=fuel_consumption_known,
        fuel_consumption_type=fuel_consumption_type,
        fuel_consumption_value=fuel_consumption_value,
    )

    chosen_model = pick_model_for_kw(hp_result) if hp_result is not None else None

    # ===== Εκτίμηση κόστους (με τιμές καταλόγου & voucher) =====
    total_cost = None
    customer_cost = None
    monthly_info = ""
    subsidy_rate = 0.0

    # ποσοστό επιδότησης
    if program_purchase == "Ναι":
        if funding_rate_choice == "60%":
            subsidy_rate = 0.60
        else:
            subsidy_rate = 0.50  # default 50% αν δεν δηλωθεί κάτι άλλο
    else:
        subsidy_rate = 0.0

    if chosen_model is not None:
        kw = chosen_model["kw"]

        # ΤΙΜΕΣ ΑΠΟ ΤΟΝ ΚΑΤΑΛΟΓΟ (προσαρμόζεις όπου χρειάζεται)
        base_prices = {
            8: 3240,   # Immergas 8kW
            9: 3490,   # Hyundai 9kW
            10: 4000,  # ενδεικτική τιμή 10kW
            12: 4350,  # περίπου μέση τιμή για 12kW
            16: 4590,  # περίπου τιμή 16kW
            26: 7410,  # Immergas 26kW
        }
        pump_cost = base_prices.get(kw, 4350)

        # Εργασίες & υλικά (υδραυλικά + ηλεκτρολογικά)
        hyd_labor = 500 + 20 * kw        # σταθερά 500
        elec_labor = 300 + 10 * kw       # σταθερά 300
        hyd_materials = 500 + 15 * kw
        elec_materials = 300 + 10 * kw

        # Ηλιακός (αν έχει επιλεγεί)
        solar_cost = 0
        if interest_type == "Αντλία & Ηλιακός":
            if solar_people_band == "3–4 άτομα":
                solar_cost = 1800
            elif solar_people_band == "4–5 άτομα":
                solar_cost = 2200
            elif solar_people_band == "Πάνω από 5 άτομα":
                solar_cost = 2600
            else:
                solar_cost = 2000

        total_cost = pump_cost + hyd_labor + elec_labor + hyd_materials + elec_materials + solar_cost

        # Υπόλοιπο πελάτη μετά την επιδότηση (αυτό είναι που χρηματοδοτούμε)
        principal = total_cost * (1 - subsidy_rate)
        customer_cost = principal

        # Δόσεις με επιτόκιο 13%
        if wants_installments == "Ναι" and principal > 0 and monthly_pref is not None:
            mid_map = {
                "50–100 €": 75,
                "100–150 €": 125,
                "200–250 €": 225,
            }
            target_monthly = mid_map.get(monthly_pref)

            if target_monthly and target_monthly > 0:
                r = 0.13 / 12.0  # μηνιαίο επιτόκιο 13% ετησίως
                # Αν r * P >= target, πάμε στο μέγιστο δόσεων
                if r * principal >= target_monthly:
                    months = 84
                else:
                    # n = ln(target / (target - rP)) / ln(1+r)
                    months_real = math.log(
                        target_monthly / (target_monthly - r * principal)
                    ) / math.log(1 + r)
                    months = int(round(months_real))

                # Περιορισμός 6–84 μήνες
                months = min(max(months, 6), 84)

                # Πραγματική δόση με τον κλασικό τύπο δανείου
                monthly_payment = principal * r / (1 - (1 + r) ** (-months))

                monthly_info = (
                    f"Για υπόλοιπο περίπου {principal:,.0f} € μετά την επιδότηση, "
                    f"με επιτόκιο 13% βγαίνουν περίπου {months} δόσεις "
                    f"των ~{monthly_payment:,.0f} €."
                )

    # =========================
    # Σύνοψη για εσένα + Email
    # =========================
    lines = []
    lines.append("=== ΕΡΩΤΗΜΑΤΟΛΟΓΙΟ ΑΝΤΛΙΑΣ ΘΕΡΜΟΤΗΤΑΣ ===")
    lines.append(f"Ημερομηνία: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    lines.append("")
    lines.append("1) Επιθυμίες & Τρόπος Αγοράς")
    lines.append(f"- Εγκατάσταση: {install_interest}")
    lines.append(f"- Αγορά μέσω προγράμματος: {program_purchase}")
    if program_purchase == "Ναι":
        lines.append(f"- Ποσοστό χρηματοδότησης (δηλωμένο): {funding_rate_choice or '50% (default)'}")
    lines.append(f"- Ενδιαφέρον: {interest_type}")
    if interest_type == "Αντλία & Ηλιακός":
        lines.append(f"- Ηλιακός: άτομα στο σπίτι: {solar_people_band}")
    lines.append(f"- Μελέτη μηχανικού: {has_engineer_study}")
    lines.append(f"- Δόσεις: {wants_installments}")
    if wants_installments == "Ναι":
        lines.append(f"  Επιθυμητή μηνιαία δόση: {monthly_pref}")
    lines.append("")
    lines.append("2) Στοιχεία Κατοικίας")
    lines.append(f"- Τύπος κατοικίας: {house_type}")
    lines.append(f"- Θέση στο κτήριο: {apt_floor_position}")
    lines.append(f"- Εμβαδόν: {area_m2} m²")
    lines.append(f"- Χρονολογία κατασκευής: {year_category}")
    lines.append(f"- Ανακαίνιση/ενεργειακή αναβάθμιση: {renovation_done}")
    if renovation_done == "Ναι":
        lines.append(f"  Επεμβάσεις: {', '.join(renovation_options) if renovation_options else '—'}")
        if renovation_other:
            lines.append(f"  Άλλες επεμβάσεις: {renovation_other}")
    lines.append(f"- Ρεύμα: {power_type}")
    lines.append(f"- Χρήση αντλίας: {usage_type}")
    if "ΖΝΧ" in usage_type:
        lines.append(f"- Άτομα για ΖΝΧ (αριθμός): {znx_people}")
    lines.append("")
    lines.append("3) Υφιστάμενο Σύστημα Θέρμανσης")
    lines.append(f"- Αλλαγή/προσθήκη σωμάτων: {change_radiators}")
    lines.append(f"- Τρόπος θέρμανσης (κεντρικό/αυτόνομο): {distribution_type}")
    lines.append(f"- Τύπος εκπομπής: {emission_type}")
    lines.append(f"- Τύπος λέβητα/πηγής: {boiler_type}")
    if boiler_type == "Άλλο" and boiler_other:
        lines.append(f"  Περιγραφή: {boiler_other}")
    lines.append(f"- Γνωστή ισχύς λέβητα: {boiler_power_known}")
    if boiler_power_known == "Ναι" and boiler_power_value is not None:
        lines.append(f"  Ισχύς λέβητα: {boiler_power_value} {boiler_power_unit}")
    lines.append("")
    lines.append("Κατανάλωση καυσίμου προηγούμενης σεζόν")
    lines.append(f"- Γνωστή κατανάλωση: {fuel_consumption_known}")
    if fuel_consumption_known == "Ναι" and fuel_consumption_value is not None:
        if fuel_consumption_type and fuel_consumption_type.startswith("Ποσότητα"):
            lines.append(f"  Ποσότητα: {fuel_consumption_value} λίτρα/κιλά")
        elif fuel_consumption_type:
            lines.append(f"  Ποσό: {fuel_consumption_value} €")
    lines.append("")
    lines.append("4) Πρόσθετα Συστήματα & Τοποθέτηση")
    lines.append(f"- Ηλιακός θερμοσίφωνας: {has_solar}")
    lines.append(f"- Φωτοβολταϊκά: {has_pv}")
    lines.append(f"- Διαθέσιμος εξωτερικός χώρος: {has_outdoor_space}")
    if outdoor_desc:
        lines.append("  Περιγραφή χώρου:")
        lines.append("  " + outdoor_desc.replace("\n", "\n  "))
    lines.append(f"- Περιορισμοί θορύβου: {noise_limits}")
    if noise_desc:
        lines.append("  Περιγραφή θορύβου:")
        lines.append("  " + noise_desc.replace("\n", "\n  "))
    if comments:
        lines.append("")
        lines.append("Σχόλια / Παρατηρήσεις:")
        lines.append(comments)

    lines.append("")
    lines.append("5) Στοιχεία Επικοινωνίας")
    lines.append(f"- Ονοματεπώνυμο: {name}")
    lines.append(f"- Τηλέφωνο: {phone}")
    lines.append(f"- Email: {email}")
    lines.append(f"- Διεύθυνση ακινήτου: {address}")

    lines.append("")
    lines.append("6) Ενδεικτική προτεινόμενη ισχύς αντλίας (υπολογισμός καταστήματος)")
    if hp_result is not None:
        low_kw, high_kw, avg_kw = hp_result
        lines.append(f"- Εκτιμώμενο εύρος: {low_kw:.1f} – {high_kw:.1f} kW (κέντρο ~{avg_kw:.1f} kW)")
        lines.append(f"- Σημείωση: {hp_notes}")
        if chosen_model is not None:
            lines.append(f"- Προτεινόμενο μοντέλο (βάσει γκάμας): {chosen_model['name']} (~{chosen_model['kw']} kW)")
        lines.append("⚠ Η εκτίμηση είναι εμπειρική και δεν αντικαθιστά μελέτη μηχανικού.")
    else:
        lines.append("- Δεν μπορεί να γίνει εκτίμηση (λείπουν βασικά στοιχεία m²).")

    lines.append("")
    lines.append("7) Ενδεικτική τάξη μεγέθους κόστους (με ΦΠΑ)")
    if total_cost is not None:
        lines.append(f"- Συνολικό ενδεικτικό κόστος εξοπλισμού & εργασιών: ~{total_cost:,.0f} €")
        if program_purchase == "Ναι":
            lines.append(f"- Επιδοτούμενο ποσοστό που χρησιμοποιήθηκε στον υπολογισμό: {int(subsidy_rate * 100)}%")
        lines.append(f"- Εκτιμώμενο κόστος για τον πελάτη (μετά την επιδότηση): ~{customer_cost:,.0f} €")
        if wants_installments == "Ναι" and monthly_info:
            lines.append(f"- Δόσεις (ενδεικτικά): {monthly_info}")
    else:
        lines.append("- Δεν υπολογίστηκε κόστος (λείπουν στοιχεία για την αντλία).")

    summary_text = "\n".join(lines)

    # Αποστολή email
    send_email(summary_text)

    # Εμφάνιση στο app
    if chosen_model is not None and hp_result is not None:
        st.markdown("### 💡 Προτεινόμενο μοντέλο αντλίας")
        st.write(f"**{chosen_model['name']}** (ονομαστική ισχύς ~{chosen_model['kw']} kW)")

    if total_cost is not None:
        st.markdown("### 💰 Ενδεικτική τάξη μεγέθους κόστους")
        st.write(f"Συνολικό περίπου κόστος εξοπλισμού & εργασιών: **~{total_cost:,.0f} €**")
        st.write(f"Εκτιμώμενο κόστος για τον πελάτη: **~{customer_cost:,.0f} €**")
        if wants_installments == "Ναι" and monthly_info:
            st.write(monthly_info)

    st.markdown("### 📄 Σύνοψη απαντήσεων")
    st.text(summary_text)

    st.download_button(
        "⬇️ Κατέβασμα σύνοψης (txt)",
        data=summary_text.encode("utf-8"),
        file_name="questionnaire_heat_pump.txt",
        mime="text/plain",
    )

    st.info(
        "Η προτεινόμενη ισχύς και το κόστος είναι ενδεικτικά, για εμπορική συζήτηση. "
        "Για τελική επιλογή και προσφορά απαιτείται μελέτη από μηχανικό."
    )
else:
    st.info("Συμπλήρωσε τα στοιχεία και πάτησε «Υποβολή ερωτηματολογίου».")