# Liisi vastus: Eksemplarid ja F-koodid

**Kuupäev:** 19. detsember 2025, 17:57  
**Saatja:** Liisi Ploom (liisi.ploom@vabamu.ee)  
**Teema:** Eksemplaride eksport ja F-esiliitega kirjed

---

## Liisi vastus

Tere! Jah, mõistlik on need eraldi MUISi tabelisse eksportida. Aga hea teada, et neid kuuluvuseta asju nii palju on- see on hea asi hilisemaks kontrolliks, kui hakkame paberil olevad dokumente digitaalsega kokku viima-kontrollima nii umbes 5 aasta jooksul, kui läheb hästi...

Aga tundub, et siit tuleb kasu ka- üks Auvis on seal sees, mis meie jaoks oleks hiljem tähendanud kadunud museaali 😄 Vähemalt teame, kus see jalutamas käis.

Mis puudutab aga f-esiliitega kirjeid, siis oleks ilmselt parem, kui need eraldi tabelis (nagu teiste kuuluvustega sai- fotokogu, arhiivraamatukogu jne). Seal on eriti palju käsitööd meil enne massimpordi RIKi andmist vaja teha, kuna neid asju pakendades selgus, on seal fotokogusse mittekuuluvat pabermaterjali selle esiliitega sisse sattunud. Seljuhul ei peaks juba tehtud Fotokogu eksport-tabelit ümber tegema- see näeb väga hea juba praegu välja 🙂

Liisi Ploom  
Peavarahoidja/Head of Collections  
Tel: + 372 5400 4028  
liisi.ploom@vabamu.ee

---

## Otsused

### 1. Eksemplaride (Raamatukogu) eksport

✅ **Otsus:** Eksportida eraldi MUISi tabelisse

**Põhjendus:**

- Kuuluvuseta kirjete arv (1,776) on kasulik tuleviku kontrolliks
- Paberil olevate dokumentide ja digitaalsete kirjete kokku viimine (~5 aasta perspektiivis)
- Leiti üks Auvis, mis oleks muidu olnud "kadunud museaal"

### 2. F-esiliitega kirjed (~580 kirjet)

✅ **Otsus:** Eraldi tabel (Option A)

**Põhjendus:**

- Palju käsitööd enne RIKi massimporti
- Pakendamisel selgus: fotokogusse mittekuuluv pabermaterjal on sisse sattunud
- Ei pea ümber tegema juba valmis Fotokogu eksport-tabelit (näeb hea välja)

---

## Järgmised sammud

**Phase 3 - Eksemplaride töötlemine:**

1. [ ] Töötleda eksemplar.csv (4,583 kirjet)
   - 2,806 Raamatukogu
   - 1,776 kuuluvuseta (määrata Raamatukogu?)
   - 1 Auviste kogu
2. [ ] Genereerida eraldi Excel fail: `vabamu_Raamatukogu.xlsx`

**F-koodide eraldamine:**

1. [ ] Ekstraktida f-esiliitega kirjed Fotokogu failist
2. [ ] Luua eraldi fail: `vabamu_Fotokogu_f_koodid.xlsx`
3. [ ] Eemaldada f-koodid põhi-Fotokogu failist
4. [ ] Uuesti genereerida: `vabamu_Fotokogu.xlsx` (ilma f-koodideta)

---

**Viide:** Issue #16
