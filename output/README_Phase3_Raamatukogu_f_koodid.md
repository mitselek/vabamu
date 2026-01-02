# Phase 3 Deliverables: Raamatukogu & F-koodid

**Kuupäev**: 2. jaanuar 2026  
**Issue**: [#16 - ENTU Data Scope: Eksemplar Processing & Follow-up Questions](https://github.com/mitselek/vabamu/issues/16)

## Ülevaade

Phase 3 laieneb Phase 2 ulatust (41,913 eksponaati) kahe täiendava ekspordi võrra:

1. **Raamatukogu kogu** - 4,583 raamatueksemplari
2. **F-prefiksiga koodid** - 829 kirjet, mis vajavad käsitsi töötlemist

## Toodetud failid

### 1. Raamatukogu (Eksemplar)

**Fail**: `vabamu_Raamatukogu.xlsx` (ja `.csv`)  
**Kirjeid**: 4,583

#### Koosseis

| Kategooria        | Arv   | % |
|-------------------|------:|--:|
| Raamatukogu kuuluvusega | 2,806 | 61.2% |
| Kuuluvuseta (vastuvõtuaktidest) | 1,776 | 38.7% |
| Auviste kogu | 1 | 0.02% |

#### Andmeallikas

- **Allikas**: `entust/eksemplar.csv`
- **Tüüp**: Raamatueksemplarid (eraldatud objektitüüp, mitte eksponaadid)
- **Välju**: 57 välja (vs eksponaadil 44 välja)

#### Eksemplar-spetsiifilised väljad

Eksemplar sisaldab raamatutele omaseid välju, mida eksponaadil ei ole:

- `author` - Autor
- `publisher` - Kirjastus
- `publishing_date` - Avaldamiskuupäev
- `publishing_place` - Avaldamiskoht
- `pages` - Lehekülgede arv
- `isbn` - ISBN kood
- `edition` - Trükiarv
- `series` - Seeria
- `translator` - Tõlkija
- `illustrator` - Illustraator
- `editor` - Toimetaja

#### Kuuluvuseta Eksemplarid

**Märkus**: 1,776 kuuluvuseta eksemplari:
- 99% (1,757 kirjet) on pärit **"Estri import" aktist** (2015-08-09)
- Kõik on seotud vastuvõtuaktidega (`vastuv6tuakt`)
- **Eesmärk**: Tuleviku kontroll ja paberkandjate kokku viimine (~5 aasta perspektiivis)

**Bonus**: Leiti 1 Auviste kogu kirje, mis oleks muidu olnud "kadunud museaal" 😄

#### Töötlus

- **Skript**: `scripts/process_eksemplar.py`
- **Konversioon**: Sama konversioonitorustik kui eksponaadidel (`convert_row` → `muis_writer`)
- **Edukus**: 100% (4,583/4,583 kirjet konverteeritud)
- **Legend-väljad**: 4 avalikku + 9 mitteavaliku = 13 kirjet legendidega

### 2. F-prefiksiga Koodid

**Fail**: `vabamu_Fotokogu_f_koodid.xlsx` (ja `.csv`)  
**Kirjeid**: 829

#### Koosseis

F-prefiksiga koodid on vanad fotokogu koodid formaadis `f000XXX/YYY`:

- **Näide**: `f000046/001`, `f000048/010`
- **Algne kuuluvus**: Fotokogu
- **Probleemid**:
  - Sisaldab fotokogusse mittekuuluvat pabermaterjali
  - Vajab käsitsi töötlemist enne RIK-i massimporti
  - Liisi otsus: "Palju käsitööd enne RIKi massimporti"

#### MuIS-i Import Nõuded

F-prefiksiga koodide puhul on vaja teisendada:

```
ENTU:  f000046/001
MuIS:  TRT="F", TRS="46", TRN="001"
```

**Väljad**:
- **TRT** (kolmas veerg): "F" (mitte "_")
- **TRS** (neljas veerg): Number ilma nullideta
- **TRN** (viies veerg): Alamüksuse number

#### Töötlus

- **Skript**: `scripts/extract_f_codes.py`
- **Filter**: Regex `^f\d{6}/\d{3}$`
- **Edukus**: 829 kirjet tuvastatud ja ekstraktitud

#### Mõju Fotokogu Failile

**Fotokogu fail uuendatud**:
- **Enne**: 3,990 kirjet (sisaldas f-koode)
- **Pärast**: 3,161 kirjet (f-koodid eemaldatud)
- **Eraldatud**: 829 f-koodi

**Uuendatud fail**: `vabamu_Fotokogu.xlsx` (regenereeritud)

## Tehniline Info

### MUIS Format

Mõlemad failid kasutavad **91-veeru MUIS formaati**:

- **Veergud 1-89**: Standard MUIS väljad
- **Veerg 90**: `Avalik legend` (public_legend)
- **Veerg 91**: `Mitteavaliku legend` (legend)

### Konversioonitorustik

```
entust/eksemplar.csv 
  → convert_row() (Phase 1-9)
  → orchestrator format (dict)
  → muis_writer() (91 columns)
  → vabamu_Raamatukogu.csv
  → csv_to_excel()
  → vabamu_Raamatukogu.xlsx
```

```
entust/eksponaat.csv (Fotokogu filter)
  → regex filter: ^f\d{6}/\d{3}$
  → convert_row()
  → split:
     ├─ f-koodid → vabamu_Fotokogu_f_koodid.xlsx
     └─ tavalised → vabamu_Fotokogu.xlsx (uuendatud)
```

## Liisi Otsused (Issue #16)

### 1. Eksemplar Eksport

✅ **OTSUS**: Eksportida eraldi MUISi tabelisse

**Põhjendused**:
- Kuuluvuseta kirjete arv (1,776) on kasulik tuleviku kontrolliks
- Aitab paberil olevate dokumentide ja digitaalsete kirjete kokku viimisel
- Bonus: Leiti üks Auvis 😄

### 2. F-esiliitega Kirjed

✅ **OTSUS**: Eraldi tabel (Option A)

**Põhjendused**:
- Palju käsitööd enne RIKi massimporti
- Pakendamisel selgus: fotokogusse mittekuuluv pabermaterjal
- Ei pea ümber tegema juba valmis Fotokogu eksport-tabelit

## Järgnevad Sammud

### Raamatukogu

1. [ ] Liisi ülevaatamine ja kinnitamine
2. [ ] RIK-ile edastamine koos teiste Phase 2 failidega
3. [ ] Kuuluvuseta kirjete käsitlus (~5 aasta perspektiivis)

### F-koodid

1. [ ] **Käsitsi ülevaatamine**: Kontrollida, millised kirjed on tegelikult fotod
2. [ ] **Pabermaterjali eraldumine**: Välistada mittekuuluvad kirjed
3. [ ] **MuIS-i import**: Pärast puhastamist
4. [ ] **Märkused**: Lisada README-sse f-koodide käsitsi töötlemise juhend

## Skriptid

- `scripts/process_eksemplar.py` - Eksemplar töötlus
- `scripts/extract_f_codes.py` - F-koodide eraldamine
- `scripts/convert_row.py` - Ühtne konversioonitorustik (phases 1-9)
- `scripts/muis_writer.py` - 91-veeru MUIS CSV kirjutaja

## Viited

- **Issue**: [#16 - ENTU Data Scope](https://github.com/mitselek/vabamu/issues/16)
- **Email**: `docs/kirjavahetus/2025-12-19_1757_Liisi_vastus_eksemplarid_f_koodid.md`
- **Statistika**: `output/handover 1/teel ette tulnud statistikat.md`

---

**Märkus**: See on Phase 3 täiendus Phase 2 tarnele (41,913 eksponaati 17 failis).

