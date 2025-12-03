# Manual Conversion Guide - First Records

## Record 1: Photo (020027/117)

### ENTU Source Data

```text
code: 020027/117
name: 020027/117 /dokument/foto
tyyp: Foto
description: Enne lahkumist poiste maja ees, 28. mai 1956. Kaupo Juurme,
              Miia Saviauk, Jaan Sarv, tundmatu, Arnold Kohv, Riita Vint
              ja Ellen Rander.
dimensions: 168x121
donator: Miia Jõgiaas
kuuluvus: Fotokogu
date: (empty)
year: (empty)
public_legend: „Minu nooruse vanglad", lk-d 161-167... (long text)
```

### MUIS Target Conversion

#### System Fields (columns 1-3)

- `museaali_ID`: (empty - MuIS generates)
- `Importimise staatus`: (empty)
- `Kommentaar`: (empty)

#### Number (columns 4-12)

- `ACR`: **VBM** (fixed - Vabamu)
- `TRT`: **\_** (underscore - default)
- `TRS`: **20027** (parse from "020027/117" - strip leading zeros)
- `TRJ`: **117** (parse after "/")
- `TRL`: (empty)
- `KT`: **F** (Fotokogu → "F")
  - **MAPPING QUESTION**: Need to confirm collection code mapping
- `KS`: (empty)
- `KJ`: (empty)
- `KL`: (empty)

#### Basic Info (columns 13-16)

- `Nimetus`: **Enne lahkumist poiste maja ees, 28. mai 1956** (from description, truncate if needed)
- `Püsiasukoht`: (empty - no asukoht data)
- `Tulmelegend`: (empty)
- `Originaal?`: **y** (assume original unless stated otherwise)

#### Acquisition (columns 17-21)

- `Vastuvõtu nr`: (empty - no vastuv6tuakt)
- `Esmane üldinfo`: (empty)
- `Kogusse registreerimise aeg`: (empty - no date)
  - **EDGE CASE**: No date in record
- `Üleandja`: **Jõgiaas, Miia** (from donator: "Miia Jõgiaas")
  - **PERSON FORMAT**: Need to reverse "Firstname Lastname" → "Lastname, Firstname"
- `Muuseumile omandamise viis`: **saadud annetusena** (default for donated items)

#### Measurements (columns 22-33)

From dimensions: "168x121"

- `Parameeter 1`: **kõrgus**
- `Ühik 1`: **mm**
- `Väärtus 1`: **168**
- `Parameeter 2`: **laius**
- `Ühik 2`: **mm**
- `Väärtus 2`: **121**
- `Parameeter 3`: (empty)
- `Ühik 3`: (empty)
- `Väärtus 3`: (empty)
- `Parameeter 4`: (empty)
- `Ühik 4`: (empty)
- `Väärtus 4`: (empty)

#### Materials (columns 34-39)

- All empty (no material data for photos)

#### Color & Technique (columns 40-46)

- `Värvus`: (empty - could infer "must-valge" if known)
- `Tehnika 1-3`: (empty)
- `Tehnika 1-3 kommentaar`: (empty)

#### Nature (columns 47-48)

- `Olemus 1`: **fotomaterjal** (tyyp: Foto → fotomaterjal)
  - **MAPPING QUESTION**: Confirm tyyp → Olemus mapping
- `Olemus 2`: (empty)

#### References (columns 49-50)

- `Viite tüüp`: (empty)
- `Väärtus`: (empty)

#### Archaeological/Archive (columns 51-54)

- `Leiukontekst`: (empty)
- `Leiu liik`: (empty)
- `Pealkirja keel`: **et** (Estonian)
- `Ainese keel`: **et** (Estonian)

#### Condition (columns 55-56)

- `Seisund`: **hea** (assume good if not stated)
- `Kahjustused`: (empty)

#### Event 1 (columns 57-67) - Creation/Photo taken

- `Sündmuse liik`: **loomine** (or **valmistamine**?)
  - **MAPPING QUESTION**: Which event type for photos?
- `Toimumiskoha täpsustus`: (empty - no location data)
- `Dateering kp`: (empty - no date)
- `Dateering kuni`: (empty)
- `Dateering tähtpäev`: (empty)
- `Riik`: **Eesti** (default)
- `Admin üksus`: (empty)
- `Osaleja`: (empty - no autor)
- `Osaleja roll`: (empty)
- `Osaleja päritolu`: (empty)
- `Viide toimumisaja kohta`: (empty)

#### Event 2 (columns 68-78) - Acquisition

- `Sündmuse liik`: **omandamine**
- All other fields: (empty - no acquisition date/details)
- `Osaleja`: **Jõgiaas, Miia** (donor)
- `Osaleja roll`: **annetaja**

#### Publication (columns 79-80)

- `Avalik?`: **y** (assume public)
- `Avalikusta praegused andmed?`: **y**

#### Description (columns 81-84)

- `Teksti tüüp 1`: **kirjeldus**
- `Tekst 1`: **Enne lahkumist poiste maja ees, 28. mai 1956. Kaupo Juurme, Miia Saviauk, Jaan Sarv, tundmatu, Arnold Kohv, Riita Vint ja Ellen Rander.**
- `Teksti tüüp 2`: **märkus**
- `Tekst 2`: **„Minu nooruse vanglad", lk-d 161-167...** (truncated public_legend)

#### Alternative Names/Numbers (columns 85-88)

- All empty

---

## Edge Cases Discovered - Record 1

### 1. Person Name Format

**ENTU**: "Miia Jõgiaas" (Firstname Lastname)
**MUIS**: "Jõgiaas, Miia" (Lastname, Firstname)
**Solution**: Manual reversal needed

### 2. No Date Information

**ENTU**: date field empty, year field empty
**MUIS**: Dateering fields empty
**Question**: Leave empty or use museum registration date?

### 3. Collection Code Mapping

**ENTU**: kuuluvus = "Fotokogu"
**MUIS**: KT = "F"?
**Need to confirm**: Full collection code mapping

### 4. Photo Event Type

**Question**: Should Event 1 be "loomine" or "valmistamine" for photographs?

### 5. Dimensions Unit

**ENTU**: "168x121" (no unit specified)
**Assumption**: mm (millimeters)
**Question**: Confirm with reference data

---

## Quick Reference: Common Patterns

### Number Parsing

```text
ENTU: "020027/117"
→ TRS: 20027 (strip leading zeros)
→ TRJ: 117
```

### Person Name Reversal

```text
ENTU: "Firstname Lastname"
→ MUIS: "Lastname, Firstname"
```

### Dimensions (HxW format)

```text
ENTU: "168x121"
→ Parameeter 1: kõrgus, Ühik 1: mm, Väärtus 1: 168
→ Parameeter 2: laius, Ühik 2: mm, Väärtus 2: 121
```

### Collection Codes (DRAFT - needs validation)

```text
Fotokogu → F
Dokumendikogu → D
Tekstiilikogu → T?
Märgikogu → M?
```

### Object Type → Olemus (DRAFT)

```text
Foto → fotomaterjal
Dokument → ?
Ese → ?
```

---

## Next Steps

1. Complete Record 1 conversion in spreadsheet
2. Convert Record 2 (different pattern - no dimensions)
3. Convert Record 3 (Ese type - different olemus)
4. Document all new edge cases
5. Build complete mapping tables

**Time spent**: ~20 minutes for first record analysis
**Estimated**: ~3-5 minutes per record once pattern established
