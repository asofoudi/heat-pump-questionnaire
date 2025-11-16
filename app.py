import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="Ερωτηματολόγιο Αντλίας Θερμότητας",
    page_icon="🔥",
    layout="centered",
)

st.title("🔥 Αλλαγή Συστήματος Θέρμανσης – Επιλογή Αντλίας Θερμότητας")
st.markdown(
    "Συμπληρώστε τις παρακάτω πληροφορίες ώστε να μπορέσουμε "
    "να σας προτείνουμε την κατάλληλη αντλία θερμότητας για τον χώρο σας."
)

st.markdown("---")

with st.form("heat_pump_form"):
    # ===== 1. Επιθυμίες & Τρόπος Αγοράς =====
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

    st.markdown("---")

    # ===== 2. Στοιχεία Κατοικίας =====
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

    # 🔹 ΝΕΟ: Ανακαίνιση / ενεργειακή αναβάθμιση
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

    project_type = st.radio(
        "Το έργο αφορά:",
        ["Απλή αντικατάσταση", "Ανακαίνιση", "Νεόδμητο σπίτι"],
    )

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
            "Αν χρειάζεστε ΖΝΧ, πόσα άτομα θα μένουν στο σπίτι;",
            min_value=0,
            step=1,
        )

    st.markdown("---")

    # ===== 3. Υφιστάμενο Σύστημα Θέρμανσης =====
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

    # 🔹 ΝΕΟ: Γνωστή ισχύς λέβητα
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

    # 🔹 ΝΕΟ: Κατανάλωση καυσίμου προηγούμενης σεζόν
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

    # ===== 4. Πρόσθετα Συστήματα & Τοποθέτηση =====
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

    # ===== 5. Στοιχεία Επικοινωνίας =====
    st.subheader("5. Στοιχεία Επικοινωνίας")

    col11, col12 = st.columns(2)
    with col11:
        name = st.text_input("Ονοματεπώνυμο")
        phone = st.text_input("Τηλέφωνο")
    with col12:
        email = st.text_input("Email")
        address = st.text_input("Διεύθυνση ακινήτου (πόλη / περιοχή)")

    submitted = st.form_submit_button("✅ Υποβολή ερωτηματολογίου")

if submitted:
    st.success("Η υποβολή καταχωρήθηκε. Δείτε παρακάτω τη σύνοψη για τον φάκελο του πελάτη.")

    lines = []
    lines.append("=== ΕΡΩΤΗΜΑΤΟΛΟΓΙΟ ΑΝΤΛΙΑΣ ΘΕΡΜΟΤΗΤΑΣ ===")
    lines.append(f"Ημερομηνία: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    lines.append("")
    lines.append("1) Επιθυμίες & Τρόπος Αγοράς")
    lines.append(f"- Εγκατάσταση: {install_interest}")
    lines.append(f"- Αγορά μέσω προγράμματος: {program_purchase}")
    lines.append(f"- Ενδιαφέρον: {interest_type}")
    lines.append(f"- Μελέτη μηχανικού: {has_engineer_study}")
    lines.append("")
    lines.append("2) Στοιχεία Κατοικίας")
    lines.append(f"- Τύπος κατοικίας: {house_type}")
    lines.append(f"- Εμβαδόν: {area_m2} m²")
    lines.append(f"- Χρονολογία κατασκευής: {year_category}")
    lines.append(f"- Ανακαίνιση/ενεργειακή αναβάθμιση: {renovation_done}")
    if renovation_done == "Ναι":
        lines.append(f"  Επεμβάσεις: {', '.join(renovation_options) if renovation_options else '—'}")
        if renovation_other:
            lines.append(f"  Άλλες επεμβάσεις: {renovation_other}")
    lines.append(f"- Έργο: {project_type}")
    lines.append(f"- Ρεύμα: {power_type}")
    lines.append(f"- Χρήση αντλίας: {usage_type}")
    if "ΖΝΧ" in usage_type:
        lines.append(f"- Άτομα για ΖΝΧ: {znx_people}")
    lines.append("")
    lines.append("3) Υφιστάμενο Σύστημα Θέρμανσης")
    lines.append(f"- Αλλαγή/προσθήκη σωμάτων: {change_radiators}")
    lines.append(f"- Τρόπος θέρμανσης: {distribution_type}")
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
        if fuel_consumption_type.startswith("Ποσότητα"):
            lines.append(f"  Ποσότητα: {fuel_consumption_value} λίτρα/κιλά")
        else:
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

    summary_text = "\n".join(lines)

    st.markdown("### 📄 Σύνοψη απαντήσεων")
    st.text(summary_text)

    file_name = "questionnaire_heat_pump.txt"
    st.download_button(
        "⬇️ Κατέβασμα σύνοψης (txt)",
        data=summary_text.encode("utf-8"),
        file_name=file_name,
        mime="text/plain",
    )

    st.info(
        "Μπορείτε να εκτυπώσετε τη σύνοψη ή να την αποθηκεύσετε στον φάκελο του πελάτη "
        "μαζί με την πρόταση αντλίας."
    )
else:
    st.info("Συμπλήρωσε τα στοιχεία και πάτησε «Υποβολή ερωτηματολογίου».")

    st.info("Συμπλήρωσε τα στοιχεία και πάτησε «Υποβολή ερωτηματολογίου».")

