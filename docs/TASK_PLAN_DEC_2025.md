# Task Plan: December 2025 Updates

**Date**: December 10, 2025  
**Status**: Planning Phase  
**Based on**: Liisi's Dec 4 & Dec 9 correspondence

---

## New Requirements Summary

### From Dec 4 Correspondence (2025-12-04_1242)

1. **v2 sample approved** - "ver2 tabel on ok"
2. **Add CK column**: ENTU `dateering` field → MUIS CK column (any format ok)
3. **ENTU availability**: Need to confirm data access beyond 31.12.2025
4. **Filtering question**: Impact if excluding "Raamatukogu" + "Maha kantud"

### From Dec 9 Correspondence (2025-12-09_1100)

1. **Contract approved**: €2,040 / 51 hours
2. **Billing preference**: 3 separate invoices (€480 + €1,080 + €480)
3. **Filtering clarified**: "Maha kantud" + "Raamatukogu" → Include but different handling
   - Not for MUIS mass import
   - Simplified format: 2 fields (number + name) - **IF it reduces work**
   - Alternative: Same full format as others - **IF simpler to implement**

---

## Data Analysis Results

### Kuuluvus Field Statistics (41,913 total records)

| Kuuluvus              | Count  | % of Total | MUIS Import?    |
| --------------------- | ------ | ---------- | --------------- |
| Dokumendikogu         | 10,247 | 12.78%     | ✅ Yes          |
| Ajaloolised esemed    | 7,159  | 8.93%      | ✅ Yes          |
| Kasutuskogu           | 5,241  | 6.54%      | ✅ Yes          |
| Fotokogu              | 3,990  | 4.98%      | ✅ Yes          |
| Pisitrükised          | 2,856  | 3.56%      | ✅ Yes          |
| **Maha kantud**       | 2,591  | 3.23%      | ❌ Archive only |
| **Arhiivraamatukogu** | 2,223  | 2.77%      | ❌ Archive only |
| Tekstiilikogu         | 2,219  | 2.77%      | ✅ Yes          |
| Märgikogu             | 2,169  | 2.71%      | ✅ Yes          |
| Plakatikogu           | 918    | 1.14%      | ✅ Yes          |
| Auviste kogu          | 603    | 0.75%      | ✅ Yes          |
| Numismaatikakogu      | 537    | 0.67%      | ✅ Yes          |
| Kunstikogu            | 358    | 0.45%      | ✅ Yes          |
| Digifotokogu          | 349    | 0.44%      | ✅ Yes          |
| Militaaria            | 338    | 0.42%      | ✅ Yes          |
| Digidokumendikogu     | 103    | 0.13%      | ✅ Yes          |
| (Other/duplicates)    | ~7     | <0.01%     | ✅ Yes          |

### Filtering Impact

**Scenario 1: No filtering (current baseline)**

- Total records: 41,913
- Excel files: ~5 files (10,000 rows/file)
- Estimated Phase 2 hours: 6-10 (currently budgeted: 12)

**Scenario 2: Exclude "Arhiivraamatukogu" + "Maha kantud"**

- Excluded: 4,814 records (6.00%)
- Remaining: 75,363 records (94.00%)
- Excel files: ~8 files (10,000 rows/file)
- Estimated Phase 2 hours: 5-9
- **Savings: ~1 hour (€40)**

**Scenario 3: Include all but separate handling**

- Total records: 41,913
- MUIS format: 75,363 records → ~8 files
- Archive format (2 columns): 4,814 records → 1 file
- Estimated Phase 2 hours: 6-11 (add 1 hour for separate writer)
- **Cost: Same or +1 hour (+€40)**

---

## Recommendation: Unified Format

**Analysis**: Implementing separate 2-column format for "Arhiivraamatukogu"/"Maha kantud" would:

- Require additional writer logic (~2 hours development)
- Require separate testing (~1 hour)
- More complex codebase maintenance
- Only saves ~1 hour in Phase 2 processing
- Net cost: +2 hours development vs -1 hour processing = **+1 hour net cost**

**Recommended approach**: **Same 88-column MUIS format for all kuuluvus values**

**Benefits**:

- Simpler code - single writer path
- Less testing needed
- Future-proof if Vabamu changes mind
- Same processing time as baseline
- All data available for future needs
- Fits within current scope (51 hours)

**Liisi's approval path**:

> "Kui aga näete, et sellise eristuse tegemine võtab rohkem tööd, siis võivad kõik kuuluvuste alusel tekkivad tabelid olla ühes vormingus."

This is **exactly** this case - separate format takes more work, so unified format is approved.

---

## Task Breakdown

### Task 1: Add CK Column (dateering field)

**Priority**: HIGH  
**Estimated effort**: 2-3 hours  
**Status**: Not started  
**Scope impact**: ✅ Within budget (fits in Phase 1 buffer)

**Subtasks**:

1. Add `dateering` field to ENTU model extraction (if not already there)
2. Map `dateering` → CK column in `muis_writer.py`
3. Update MUIS column headers to include CK
4. Test with 100 sample records
5. Generate v2.1 sample for Liisi validation

**Technical notes**:

- CK is column position 90 (after Alt number at 88-89)
- No formatting required - pass through as-is from ENTU
- Formats accepted: "xxxx", "xxxx-ndad", "xxxx-xxxx"
- Can be empty if not in ENTU

**Files to modify**:

- `scripts/models.py` - Add `dateering` field to EntuEksponaat if missing
- `scripts/parsers/muis_writer.py` - Add CK column mapping
- `scripts/convert_row.py` - Pass dateering to MuisMuseaal model
- `tests/test_muis_writer.py` - Add CK column tests

---

### Task 2: Query Argo about ENTU Availability

**Priority**: CRITICAL  
**Estimated effort**: 0.5 hours (email + follow-up)  
**Status**: Not started  
**Blocking**: Phase 1 start - need to know timeline

**Question to Argo**:

> Tere Argo,
>
> Liisi küsimus: Kui kaua on ENTU andmed kättesaadavad? Kas ka pärast 31.12.2025?
>
> See on kriitiline projekti planeerimise jaoks. Kui server läheb kinni enne projekti lõppu, peame tegema täieliku ekspordi varem.
>
> Mihkel

**Risk assessment**:

- If ENTU closes before project completion → Need full export NOW
- If ENTU available through Q1 2026 → Normal timeline ok
- If uncertain → Plan for worst case (immediate export)

---

### Task 3: Implement Kuuluvus-based File Splitting

**Priority**: HIGH  
**Estimated effort**: 4-6 hours  
**Status**: Not started (Phase 1)  
**Scope impact**: ✅ Within budget (already in Phase 1 plan)

**Requirements** (from Nov 12 correspondence):

> "tabelid moodustuksid kuuluvuse alusel (nt fotokogu, ajaloolised esemed jne)"

**Implementation**:

1. Group records by `kuuluvus` field
2. Generate separate Excel file per kuuluvus
3. Filename format: `vabamu_KUULUVUS_YYYY-MM-DD.xlsx`
4. Max 10,000 rows per file (split if needed)
5. All files use same 88-column MUIS format

**Expected output** (~16 files):

```text
vabamu_Dokumendikogu.xlsx        (10,247 rows → 2 files)
vabamu_Ajaloolised_esemed.xlsx   (7,159 rows → 1 file)
vabamu_Kasutuskogu.xlsx          (5,241 rows → 1 file)
vabamu_Fotokogu.xlsx             (3,990 rows → 1 file)
vabamu_Pisitrykised.xlsx         (2,856 rows → 1 file)
vabamu_Arhiivraamatukogu.xlsx    (2,223 rows → 1 file) ⚠️ Not for MUIS import
vabamu_Tekstiilikogu.xlsx        (2,219 rows → 1 file)
vabamu_Margikogu.xlsx            (2,169 rows → 1 file)
vabamu_Maha_kantud.xlsx          (2,591 rows → 1 file) ⚠️ Not for MUIS import
vabamu_Plakatikogu.xlsx          (918 rows → 1 file)
vabamu_Auviste_kogu.xlsx         (603 rows → 1 file)
vabamu_Numismaatikakogu.xlsx     (537 rows → 1 file)
vabamu_Kunstikogu.xlsx           (358 rows → 1 file)
vabamu_Digifotokogu.xlsx         (349 rows → 1 file)
vabamu_Militaaria.xlsx           (338 rows → 1 file)
vabamu_Digidokumendikogu.xlsx    (103 rows → 1 file)
```

**Files to modify**:

- `scripts/batch_processor.py` (new file) - Main batch processing logic
- `scripts/parsers/muis_writer.py` - Add Excel writing with openpyxl
- Add dependency: `openpyxl` to requirements.txt

**Note**: Flag "Arhiivraamatukogu" and "Maha kantud" files with README noting they are archive-only (not for MUIS mass import).

---

### Task 4: Invoice #1 (Phase 0.5)

**Priority**: HIGH  
**Estimated effort**: 0.5 hours (invoice creation)  
**Status**: Ready to issue  
**Amount**: €480

**Work completed**:

- Phase 0.5: 100 sample records conversion (v1)
- Issue #10: 6 feedback changes (v2)
- Edge case documentation
- Total: 12 hours @ €40/hr

**Action**: Create invoice and send to Liisi

---

### Task 5: Respond to Liisi

**Priority**: HIGH  
**Estimated effort**: 0.5 hours  
**Status**: Draft pending  
**Scope impact**: None

**Response draft**:

> Tere Liisi!
>
> Aitäh kinnituse eest! Hakkan kohe tööle.
>
> **1. CK veerg (aasta/dateering)**  
> Jah, saame lisada ENTU "dateering" välja CK veergu. Ei vaja vormindamist - läheb nii nagu ENTUs on (xxxx, xxxx-ndad, xxxx-xxxx kujul). Implementeerin selle järgmise 2-3 päeva jooksul ja saadan uue näidistabeli kontrollimiseks.
>
> **2. ENTU kättesaadavus**  
> Küsin Argolt kohe kinnitust. See on meile ka oluline teada planeerimise jaoks.
>
> **3. "Maha kantud" ja "Arhiivraamatukogu" käsitlus**  
> Analüüsisin andmeid:
>
> - "Maha kantud": 2,591 kirjet (3.23%)
> - "Arhiivraamatukogu": 2,223 kirjet (2.77%)
> - Kokku: 4,814 kirjet (6% koguarvust)
>
> **Soovitus**: Teeme kõik kuuluvused **samas vormingus** (88 veergu). Põhjused:
>
> - Eraldi 2-veerulise formaadi tegemine võtaks rohkem aega (+2h arendus)
> - Täisformaat annab tulevikus paindlikkust
> - Mahub praegusesse skoopi (51h)
> - Täidab Sinu tingimuse: "kui eristus võtab rohkem tööd, siis ühes vormingus"
>
> Märgime failid README-s, et need 2 kuuluvust on ainult arhiiviks (mitte MUISi massiimporti). Sobib?
>
> **4. Arved**  
> Esitan 3 arvet etappide kaupa:
>
> - Arve #1 (€480): Faas 0.5 - saadan kohe (töö tehtud)
> - Arve #2 (€1,080): Faas 1 - pärast automaatika valmimist (~2 nädalat)
> - Arve #3 (€480): Faas 2 - pärast tootmiskäivitust (~4 nädalat)
>
> Kõik jõuab 2025 aastasse ära maksta!
>
> Tervitades,  
> Mihkel

---

## Updated Budget Analysis

### Original Estimate (Dec 4)

| Phase     | Hours  | Cost       | Status      |
| --------- | ------ | ---------- | ----------- |
| Phase 0.5 | 12     | €480       | Complete |
| Phase 1   | 27     | €1,080     | Updated  |
| Phase 2   | 12     | €480       | Pending     |
| **TOTAL** | **51** | **€2,040** | On track    |

### Phase 1 Breakdown (Updated)

| Task                           | Original | New Requirement | Updated |
| ------------------------------ | -------- | --------------- | ------- |
| Person extraction & MuIS coord | 3h       | -               | 3h      |
| Dimension pattern extension    | 3h       | -               | 3h      |
| Batch processing               | 4h       | -               | 4h      |
| Kuuluvus-based file splitting  | 3h       | -               | 5h      |
| **CK column implementation**   | -        | **NEW**         | **3h**  |
| Error handling & logging       | 3h       | -               | 3h      |
| Progress tracking              | 2h       | -               | 2h      |
| Full validation & QA           | 4h       | -               | 4h      |
| **Phase 1 Total**              | **22h**  | **+3h**         | **27h** |

**Analysis**:

- CK column addition (+3h) fits within Phase 1 buffer (27h budgeted, 22h baseline)
- No additional cost to client
- Unified format decision saves development time
- All within approved €2,040 budget

### Phase 2 Impact

**Baseline** (41,913 records, all kuuluvus):

- Processing: 2-3h (automated, ~1 sec/record)
- Excel generation: 2-3h (16 files by kuuluvus)
- Validation sampling: 1-2h
- Error resolution: 1-2h
- Final delivery: 1h
- **Total: 7-11h** (budgeted: 12h)

**No scope change needed** - filtering doesn't reduce workload enough to warrant separate handling.

---

## Risks & Mitigations

### Risk 1: ENTU Closes Before Completion

**Probability**: MEDIUM  
**Impact**: CRITICAL  
**Mitigation**:

- Query Argo immediately (Task 2)
- If closing soon: Do complete export to local backup
- Store full export in `entust_backup/` directory
- Continue development from backup

### Risk 2: CK Column Validation Issues

**Probability**: LOW  
**Impact**: MEDIUM  
**Mitigation**:

- Generate v2.1 sample quickly (100 records)
- Send to Liisi for approval before full batch
- Iterative feedback cycle (like Issue #10)

### Risk 3: Kuuluvus File Split Complexity

**Probability**: LOW  
**Impact**: MEDIUM  
**Mitigation**:

- Start with proof of concept (2-3 kuuluvus groups)
- Test Excel generation with openpyxl early
- Validate file structure against MUIS requirements
- Buffer in Phase 1 budget (5h vs 3h baseline)

---

## Timeline ⚡ ACCELERATED

### Sprint 1: Dec 10-14, 2025

**Rationale**: Argo and Liisi responsive, can compress Weeks 1-2 into one focused week

**Day 1 - Wednesday Dec 10** - Administrative & Quick Wins (4h):

- ✅ Query Argo about ENTU availability (done today)
- Issue Invoice #1 (€480)
- Respond to Liisi with plan confirmation
- Start CK column implementation (2h)
- Set up openpyxl for Excel (1h)

**Day 2 - Thursday Dec 11** - Core Development (8h):

- Complete CK column mapping (1h remaining)
- Generate v2.1 sample with CK column (1h)
- Send to Liisi for quick validation
- Implement kuuluvus-based file splitting (3h)
- Start batch processing logic (3h)

**Day 3 - Friday Dec 12** - More Development (8h):

- Complete batch processing (2h remaining)
- Person extraction setup (3h)
- Extended dimension patterns (3h)

**Day 4 - Weekend Dec 13-14** - Finalization (8h):

- Error handling & logging (3h)
- Progress tracking & reporting (1h)
- Integration testing & bug fixes (3h)
- Code review and optimization (1h)
- Wait for Liisi feedback on v2.1 if not yet received
- Documentation cleanup
- Any minor tweaks if needed

**Total effort**: ~28 hours over 5 days (more sustainable pace)

**Deliverable**: Working batch processor, ready for validation by EOD Dec 14 (Sunday)

**Dependencies**:

- Liisi turnaround on v2.1 approval (by Dec 12-13)
- Argo response on ENTU (assume available through Q1 2026)

### Sprint 2: Dec 15-18, 2025

**Phase 1 validation & testing** (2-3 hours):

- Full validation & QA (1-2h)
- **Test run** (1,000-5,000 records to validate pipeline)
- Fix any bugs discovered (if any)

**Deliverable**:

- ✅ All code complete and tested
- ✅ Pipeline validated on test subset
- ✅ Ready for production run
- 📄 **Issue Invoice #2 (€1,080)** - Development work complete

**Invoice #2 justification**:

- Software engineering complete (27h @ €40/hr)
- Tested and validated pipeline
- Ready to process full dataset
- This is the "factory building" phase - all tools and logic locked down

---

### Finiš: Dec 19-22, 2025

**Phase 2: Production Run** (12 hours):

- **Production execution**: Process all 41,913 records (2-3h)
- **Excel generation**: Generate ~16 files by kuuluvus (2-3h)
- **Quality validation**: Sample 1% of records (~420) for accuracy (2h)
- **Error resolution**: Manual review of flagged records (2h)
- **Final delivery prep**: Documentation, README, handoff (2h)
- **Client validation**: Support Liisi with file review (1h)

**Deliverable**:

- ✅ All 41,913 records converted to MUIS format
- ✅ ~16 Excel files organized by kuuluvus
- ✅ Validation report (error log, statistics)
- ✅ README documenting archive-only files
- ✅ Files delivered to Vabamu
- 📄 **Issue Invoice #3 (€480)** - Production execution complete

**Invoice #3 justification**:

- Production processing (12h @ €40/hr)
- Final quality assurance
- Official deliverable files
- This is the "factory production run" phase

### Follow-up: January 2026

**Process monitoring** (buffer, no separate billing):

- Available to respond to any discovered issues/gaps
- Support as needed
- Covered by existing phase allocations

**Total timeline**:

- **Original**: 6 weeks (Dec 10 - Jan 20)
- **Accelerated**: Core dev 5 days (Dec 10-14), validation Dec 15-18, production Dec 19-22
- **Advantage**: ALL invoices (#1, #2, #3) within 2025 - can be paid before year-end
- **More sustainable**: 5-day sprint vs 3-day crunch
- **Client benefit**: Complete before Christmas, full dataset ready for 2026 start

---

## Success Criteria

### Phase 1 Complete When:

- CK column implemented and validated by Liisi
- Batch processor handles all 80K records
- Kuuluvus-based file splitting working
- Error handling logs issues correctly
- Test run generates valid Excel files
- Person extraction complete (if ENTU available)

### Phase 2 Complete When:

- All 41,913 records processed
- ~16 Excel files generated by kuuluvus
- Validation sampling shows >99% quality
- README documents archive-only files
- Error log reviewed and acceptable
- Liisi confirms files are MUIS-ready

### Project Complete When:

- All files delivered to Vabamu
- MUIS accepts files for import
- Documentation complete
- All invoices paid
- Repository cleaned and archived

---

## Next Immediate Actions

**⚡ ACCELERATED SPRINT: Dec 10-14**:

**Day 1 - Wednesday Dec 10** (5 hours):

1. Email Argo about ENTU availability (30 min) - DONE
2. Create Invoice #1 for €480 (30 min) - **MUST DO TODAY**
3. Draft and send response to Liisi (30 min) - **MUST DO TODAY**
4. Start CK column implementation (2h)
5. Set up openpyxl for Excel (1h)

**Day 2 - Thursday Dec 11** (8 hours):

1. Complete CK column + generate v2.1 sample (2h)
2. Send to Liisi for validation
3. Implement kuuluvus-based file splitting (3h)
4. Start batch processing logic (3h)

**Day 3 - Friday Dec 12** (8 hours):

1. Complete batch processing (2h)
2. Person extraction setup (3h)
3. Extended dimension patterns (3h)

**Day 4-5 - Weekend Dec 13-14** (8 hours total):

1. Error handling & logging (3h)
2. Progress tracking & reporting (1h)
3. Integration testing & bug fixes (3h)
4. Code review and optimization (1h)

- Wait for any Liisi feedback
- Documentation polish
- Minor tweaks if needed

**By EOD Sunday Dec 14**:

- Phase 1 development complete (~29h)
- Ready for validation & QA (Dec 15-18)
- Invoice #1 (€480) issued
- Can issue Invoice #2 by Dec 18

**Next Phase Timeline**:

- **Dec 15-18**: Validation, testing, bug fixes → Invoice #2 (€1,080)
- **Dec 19-22**: Production run, final delivery → Invoice #3 (€480)
- **January 2026**: Available for support as needed

**Status**: SPRINT MODE ACTIVATED 🚀 (sustainable pace edition)
