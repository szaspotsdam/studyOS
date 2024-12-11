# Status basierend auf der Häufigkeit der UID ändern

        uid_counter = {}
        for anmeldung in anmeldungen:
            uid = anmeldung[0]
            if uid not in uid_counter:
                uid_counter[uid] = 0
            uid_counter[uid] += 1
        
        for i in range(len(anmeldungen)):
            uid = anmeldungen[i][0]
            status = "✅" if uid_counter[uid] % 2 == 1 else "❌"
            anmeldungen[i] = (*anmeldungen[i], status)
            uid_counter[uid] -= 1

# WICHTIG!!! In der list.html die {{ anmeldung[3] }} nicht vergessen!!!
