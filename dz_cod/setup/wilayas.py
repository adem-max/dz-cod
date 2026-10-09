"""The 69 wilayas of Algeria, with example shipping rates.

Source of the list:
- Wilayas 01 to 58: law 84-09 as amended in 2019 (58 wilayas).
- Wilayas 59 to 69: law 26-06 of 4 April 2026 (JO n° 25 of 5 April 2026)
  and presidential decree 26-206 of 25 May 2026 (JO n° 40), which set their
  names and numbers. The new wilayas take over from their "parent" wilaya
  progressively until 31 December 2026.

Couriers may keep using the old 58-wilaya codes for a while, so each new
wilaya remembers its parent wilaya (field `parent_wilaya`).

The rates below are EXAMPLES grouped by zone. Replace them with the real rate
card of each client's courier (Wilaya list -> edit the 4 rate columns).
"""

# Example rates in DZD per zone: (home delivery, stop desk)
ZONE_RATES = {
	1: (400, 250),  # Alger
	2: (550, 350),  # Around Alger
	3: (650, 400),  # Rest of the north
	4: (750, 450),  # High plateaus
	5: (950, 600),  # South
	6: (1400, 900),  # Far south
}

# (code, name, zone, parent wilaya code for the 2026 wilayas)
WILAYAS = [
	("01", "Adrar", 5, None),
	("02", "Chlef", 3, None),
	("03", "Laghouat", 4, None),
	("04", "Oum El Bouaghi", 3, None),
	("05", "Batna", 4, None),
	("06", "Béjaïa", 3, None),
	("07", "Biskra", 4, None),
	("08", "Béchar", 5, None),
	("09", "Blida", 2, None),
	("10", "Bouira", 3, None),
	("11", "Tamanrasset", 6, None),
	("12", "Tébessa", 4, None),
	("13", "Tlemcen", 3, None),
	("14", "Tiaret", 4, None),
	("15", "Tizi Ouzou", 3, None),
	("16", "Alger", 1, None),
	("17", "Djelfa", 4, None),
	("18", "Jijel", 3, None),
	("19", "Sétif", 3, None),
	("20", "Saïda", 4, None),
	("21", "Skikda", 3, None),
	("22", "Sidi Bel Abbès", 3, None),
	("23", "Annaba", 3, None),
	("24", "Guelma", 3, None),
	("25", "Constantine", 3, None),
	("26", "Médéa", 3, None),
	("27", "Mostaganem", 3, None),
	("28", "M'Sila", 4, None),
	("29", "Mascara", 3, None),
	("30", "Ouargla", 5, None),
	("31", "Oran", 3, None),
	("32", "El Bayadh", 4, None),
	("33", "Illizi", 6, None),
	("34", "Bordj Bou Arréridj", 3, None),
	("35", "Boumerdès", 2, None),
	("36", "El Tarf", 3, None),
	("37", "Tindouf", 6, None),
	("38", "Tissemsilt", 3, None),
	("39", "El Oued", 5, None),
	("40", "Khenchela", 4, None),
	("41", "Souk Ahras", 3, None),
	("42", "Tipaza", 2, None),
	("43", "Mila", 3, None),
	("44", "Aïn Defla", 3, None),
	("45", "Naâma", 4, None),
	("46", "Aïn Témouchent", 3, None),
	("47", "Ghardaïa", 5, None),
	("48", "Relizane", 3, None),
	("49", "Timimoun", 5, None),
	("50", "Bordj Badji Mokhtar", 6, None),
	("51", "Ouled Djellal", 4, None),
	("52", "Béni Abbès", 5, None),
	("53", "In Salah", 6, None),
	("54", "In Guezzam", 6, None),
	("55", "Touggourt", 5, None),
	("56", "Djanet", 6, None),
	("57", "El M'Ghair", 5, None),
	("58", "El Meniaa", 5, None),
	# Created by law 26-06 (2026). Parent wilayas: please double-check against
	# the Journal officiel, they come from press reports of the law.
	("59", "Aflou", 4, "03"),
	("60", "Barika", 4, "05"),
	("61", "El Kantara", 4, "07"),
	("62", "Bir El Ater", 4, "12"),
	("63", "El Aricha", 4, "13"),
	("64", "Ksar Chellala", 4, "14"),
	("65", "Aïn Ouessara", 4, "17"),
	("66", "Messaad", 4, "17"),
	("67", "Ksar El Boukhari", 3, "26"),
	("68", "Bou Saâda", 4, "28"),
	("69", "El Abiodh Sidi Cheikh", 4, "32"),
]


def wilaya_docname(code, name):
	"""Record name used for a wilaya, for example "16 - Alger"."""
	return f"{code} - {name}"
