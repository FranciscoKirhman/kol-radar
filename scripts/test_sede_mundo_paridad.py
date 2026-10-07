#!/usr/bin/env python3
"""Paridad Python/ES5 de redacción de sedes, incluidas clínicas y epónimos."""
import json
import subprocess
from pathlib import Path

from recolectar_mundo_ctgov import sanitize_facility

ROOT = Path(__file__).resolve().parent.parent
HTML = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
START = HTML.index("  var MARCADORES_SEDE_MUNDO =")
END = HTML.index("  // FIN SANEAMIENTO MUNDO", START)
JS = HTML[START:END] + "\n" + """
var input = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", function (chunk) { input += chunk; });
process.stdin.on("end", function () {
  var cases = JSON.parse(input);
  process.stdout.write(JSON.stringify(cases.map(function (c) {
    return sanearSedeMundo(c.text, c.allowed);
  })));
});
"""

PRIVATE = [
    "Clinica Privada Dr. Nombre Uno ( Site 0503)",
    "Clinica Dr. Nombre Dos", "Clinica Dr. Nombre Tres",
    "Clinica Medica Del Dr Nombre Cuatro",
    "Private clinic of Dr. Name Five", "Private clinic of Dr. Name Six",
    "Aesthetic dermatology clinic of Prof. J. Name Seven", "Eye Clinic Dr. Name Eight",
    "Dr. Name Nine's Clinic", "Dr. Name Ten's Clinic/ ABC Research International",
    "Dr. Name Eleven's Clinic", "Dr Name Twelve's Clinic",
    "Dr. Name Thirteen Dental Polyclinic", "Clinic for Psychiatric Diseases Dr. Name Fourteen",
    "Clinic for rehabilitation dr Name Fifteen",
]
HOSPITALS = [
    "Dr. Sulaiman Al Habib Hospital", "Hospital Dr Diego Paroissien",
    "Hospital Militar Central Cirujano Mayor Dr. Cosme Argerich",
    "Dr. Abdulah Nakas General Hospital", "General Hospital Dr. Abdulah Nakas",
    "Institute of Physical Medicine Dr. Miroslav Zotovic",
    "Multiprofile Hospital Dr. Stamen Iliev", "University Hospital Prof Dr Stoyan Kirkovich",
    "Pediatric Hospital Dr. Juan Manuel Márquez", "Hospital Dr. Rafael Ángel Calderón Guardia",
    "Dr. Suat Gunsel University of Kyrenia Hospital", "Hospital Dr Luis Eduardo Aybar",
    "Hospital de Clínicas Dr. Manuel Quintela", "Hospital Dr. Sótero del Río",
    "Centro Médico Dra. Laura Maffei",
]
EXTRAS = [
    "Malaria Research and Training Center Department of Epidemiology University of Bamako, Mali Tel/Fax 223-2022-8109",
    "National Institute of Health, email: med@example.org",
    "Hospital Central, Dr. Persona Actual", "Mayo Clinic",
]


def main():
    cases = [{"text": text, "allowed": False} for text in PRIVATE + HOSPITALS + EXTRAS]
    cases.append({"text": "Clinica Dr. Nombre Dos", "allowed": True})
    python = [sanitize_facility(c["text"], c["allowed"]) for c in cases]
    done = subprocess.run(["node", "-e", JS], input=json.dumps(cases, ensure_ascii=False),
                          text=True, capture_output=True, check=True)
    javascript = json.loads(done.stdout)
    assert python == javascript, [(cases[i], p, j) for i, (p, j) in enumerate(zip(python, javascript)) if p != j]
    assert all(not x["facility_text"] for x in python[:len(PRIVATE)])
    assert all(x["facility_text"] for x in python[len(PRIVATE):len(PRIVATE) + len(HOSPITALS)])
    assert "223-2022-8109" not in python[-5]["facility_text"]
    assert "@" not in python[-4]["facility_text"]
    assert python[-3]["facility_text"] == "Hospital Central"
    assert python[-1]["facility_text"] == "Clinica Dr. Nombre Dos"
    print("PASA: 15 clínicas privadas, 15 epónimos institucionales, contactos y paridad Python/ES5.")


if __name__ == "__main__":
    main()
